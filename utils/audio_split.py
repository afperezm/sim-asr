import argparse
import functools
import glob
import os
from matplotlib import pyplot as plt
from pydub import AudioSegment
from pydub.silence import split_on_silence

TARGET_LENGTH = 15000  # 15 seconds


def parse_args():
    parser = argparse.ArgumentParser(
        description="Splitter of audio files in chunks by silence."
    )
    parser.add_argument(
        "--audio_dir",
        type=str,
        help="Audio data directory, where audio files are located.",
        required=True)
    parser.add_argument(
        "--out_dir",
        type=str,
        help="Output data directory, where to store audio chunks.",
        required=True)
    return parser.parse_args()


def match_target_amplitude(aChunk, target_dBFS):
    """Normalize given audio chunk"""
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)


def export_chunk(chunk, output_dir, basename):
    # Create a silence chunk that's 0.2 seconds (or 200 ms) long for padding
    silence_chunk = AudioSegment.silent(duration=200)
    # Add the padding chunk to beginning and end of the entire chunk
    audio_chunk = silence_chunk + chunk + silence_chunk
    # Normalize the entire chunk
    normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
    # Export the audio chunk
    print("  Exporting {0}.wav".format(basename))
    normalized_chunk.export(
        "{0}/{1}.wav".format(output_dir, basename),
        format="wav"
    )


def main():
    audio_dir = os.path.abspath(PARAMS.audio_dir)
    output_dir = os.path.abspath(PARAMS.out_dir)

    audio_files = glob.glob("{0}/*.wav".format(audio_dir))

    chunk_lengths = []

    for audio_file in sorted(audio_files):

        basename = os.path.splitext(os.path.basename(audio_file))[0]

        print("- Processing {0}".format(basename))

        if os.path.exists("{0}/{1}_chunk_{2:05d}.wav".format(output_dir, basename, 1)):
            print("  Skipping, already processed")

        audio = AudioSegment.from_wav(audio_file)

        # audio loudness
        dBFS = audio.dBFS

        chunks = split_on_silence(audio,
                                  # split on silences longer than 500ms (0.5 sec)
                                  min_silence_len=500,
                                  # anything under -16 dBFS is considered silence
                                  silence_thresh=dBFS - 16,
                                  # do not keep leading/trailing silences
                                  keep_silence=0
                                  )

        print("  Obtained {0} chunks".format(len(chunks)))

        chunks_group = []

        chunks_group_idx = 1

        for i, chunk in enumerate(chunks):
            # Append chunk length
            chunk_lengths.append(len(chunk))
            # Check whether group length would exceed target length
            if sum([len(c) for c in chunks_group]) + len(chunk) <= TARGET_LENGTH:
                # Add current chunk to group
                chunks_group.append(chunk)
            else:
                # Merge chunk group
                grouped_chunk = functools.reduce(lambda a, b: a + b, chunks_group, AudioSegment.silent(duration=0))
                # Export chunk group
                export_chunk(grouped_chunk, output_dir, "{0}_chunk_{1:05d}".format(basename, chunks_group_idx))
                # Initialize new chunk group
                chunks_group = [chunk]
                # Increase group counter
                chunks_group_idx += 1
            # Export chunk group if this is last chunk
            if i + 1 == len(chunks):
                # Merge chunk group
                grouped_chunk = functools.reduce(lambda a, b: a + b, chunks_group, AudioSegment.silent(duration=0))
                # Export chunk group
                export_chunk(grouped_chunk, output_dir, "{0}_chunk_{1:05d}".format(basename, chunks_group_idx))

    plt.hist(chunk_lengths)
    plt.savefig("histogram.png")


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

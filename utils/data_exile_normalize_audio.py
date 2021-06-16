import argparse
import glob
import os
from pydub import AudioSegment

TARGET_DBFS = -20


def match_target_amplitude(audio, target_dBFS):
    """Normalize given audio chunk"""
    change_in_dBFS = target_dBFS - audio.dBFS
    return audio.apply_gain(change_in_dBFS)


def main():
    audio_dir = os.path.abspath(PARAMS.audio_dir)
    output_dir = os.path.abspath(PARAMS.out_dir)

    audio_files = glob.glob("{0}/*.wav".format(audio_dir))

    for audio_file in sorted(audio_files):

        basename = os.path.splitext(os.path.basename(audio_file))[0]

        print("- Processing {0}".format(basename))

        if os.path.exists("{0}/{1}.wav".format(output_dir, basename)):
            print("  Skipping, already processed")

        audio = AudioSegment.from_wav(audio_file)

        # Normalize the entire audio
        normalized_audio = match_target_amplitude(audio, -20.0)

        # Export the audio chunk
        print("  Exporting {0}.wav".format(basename))
        normalized_audio.export(
            "{0}/{1}.wav".format(output_dir, basename),
            format="wav"
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Normalizer of audio files in chunks by silence."
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


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

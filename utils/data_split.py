import argparse
import csv
import glob
import os
import pickle
import srt
import string
import unicodedata
from pydub import AudioSegment


def main():
    subtitles_dir = os.path.abspath(PARAMS.subs_dir)
    audio_dir = os.path.abspath(PARAMS.audio_dir)
    output_dir = os.path.abspath(PARAMS.out_dir)
    waves_dir = os.path.join(output_dir, "wavs")

    if not os.path.exists(subtitles_dir):
        os.makedirs(subtitles_dir)

    if not os.path.exists(audio_dir):
        os.makedirs(subtitles_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(waves_dir):
        os.makedirs(waves_dir)

    output_tsv = os.path.join(output_dir, "output.tsv")
    output_tsv_file = open(output_tsv, "w", encoding="utf-8", newline="")
    output_tsv_writer = csv.writer(output_tsv_file, dialect=csv.excel_tab)

    durations = {}

    subtitles_srt = glob.glob("{0}/*.srt".format(subtitles_dir))

    for subtitle_srt in sorted(subtitles_srt):

        sub_srt_basename = os.path.splitext(os.path.basename(subtitle_srt))[0]
        sub_srt_basename = os.path.splitext(sub_srt_basename)[0]

        audio_wav = os.path.join(audio_dir, "{0}.wav".format(sub_srt_basename))

        if not os.path.isfile(audio_wav) or not os.access(audio_wav, os.R_OK):
            print("{0} - Missing associated audio file".format(sub_srt_basename))
            continue

        with open(subtitle_srt) as subtitle_srt_file:
            subtitle_contents = subtitle_srt_file.read()

        audio_subs = list(srt.parse(subtitle_contents))
        audio_wav_file = AudioSegment.from_wav(audio_wav)

        for idx, sub in enumerate(audio_subs):

            if sub.content in ["borrar", "uborrar"]:
                continue

            print("{0} - Processing segment {1}/{2}".format(sub_srt_basename, idx, len(audio_subs)))

            # Compose audio segment filename
            audio_segment = "{basename}-{idx:0>4d}.wav".format(basename=sub_srt_basename, idx=idx + 1)
            audio_segment = os.path.join(waves_dir, audio_segment)

            # Skip already processed segments
            if os.path.isfile(audio_segment):
                print("{0} - Skipping, already processed".format(sub_srt_basename))
                continue

            # Compute subtitle start and end time in milliseconds
            t1 = sub.start.total_seconds() * 1000
            t2 = sub.end.total_seconds() * 1000

            # Skip processing subtitle if it is too short or empty content
            if (sub.end - sub.start).total_seconds() < 2.0 or not sub.content:
                print("{0} - Skipping, too short or empty content".format(sub_srt_basename))
                continue

            # Export audio segment
            audio_segment_file = audio_wav_file[t1:t2].export(audio_segment, format="wav")
            audio_segment_file.close()

            # Remove diacritic characters and punctuation signs
            audio_transcript = sub.content.strip()

            # Write audio segment path and transcript to output csv file
            output_tsv_writer.writerow([os.path.relpath(audio_segment, waves_dir), audio_transcript])

            # Build list of audio subs duration
            durations[audio_segment] = [(sub.end - sub.start).total_seconds()]

            print("{0} - Done".format(sub_srt_basename))

    output_tsv_file.close()

    # Write durations dictionary to a pickle file in the output directory
    durations_pkl = os.path.join(output_dir, "audio_subs_duration.pkl")

    with open(durations_pkl, "wb") as durations_pkl_file:
        pickle.dump(durations, durations_pkl_file, protocol=pickle.HIGHEST_PROTOCOL)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Splitter of audio-aligned transcripts in SubRip file format."
    )
    parser.add_argument(
        "--subs_dir",
        type=str,
        help="Subtitles data directory, where audio-aligned transcripts are located.",
        required=True)
    parser.add_argument(
        "--audio_dir",
        type=str,
        help="Audio data directory, where audio-aligned transcripts associated audios are located.",
        required=True)
    parser.add_argument(
        "--out_dir",
        type=str,
        help="Output data directory, where to store split audio-aligned transcripts.",
        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

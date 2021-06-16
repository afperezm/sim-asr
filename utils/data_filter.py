import argparse
import glob
import os
import pickle
import srt


def main():
    subtitles_dir = os.path.abspath(PARAMS.subs_dir)
    output_dir = os.path.abspath(PARAMS.out_dir)
    cache_pkl = os.path.abspath(PARAMS.valid_cache)

    with open(cache_pkl, "rb") as cache_pkl_file:
        cached_transcripts = pickle.load(cache_pkl_file)

    if not os.path.exists(subtitles_dir):
        os.makedirs(subtitles_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    valid_sub_srt_template = os.path.join(output_dir, "{}.srt")

    subtitles_srt = glob.glob("{0}/*.srt".format(subtitles_dir))

    for subtitle_srt in sorted(subtitles_srt):

        sub_srt_basename = os.path.splitext(os.path.basename(subtitle_srt))[0]
        sub_srt_basename = os.path.splitext(sub_srt_basename)[0]

        print("{0} - Processing subtitle".format(sub_srt_basename))

        with open(subtitle_srt) as subtitle_srt_file:
            subtitle_contents = subtitle_srt_file.read()

        audio_subs = list(srt.parse(subtitle_contents))

        valid_keys = [key for key in cached_transcripts.keys() if key.startswith(sub_srt_basename)]
        valid_keys = [int(key.split('-')[-1]) for key in valid_keys]
        valid_keys = sorted(valid_keys)

        valid_subs = [srt.Subtitle(index=audio_sub.index,
                                   start=audio_sub.start,
                                   end=audio_sub.end,
                                   proprietary=audio_sub.proprietary,
                                   content='---' if idx + 1 in valid_keys else audio_sub.content) for idx, audio_sub in
                      enumerate(audio_subs)]

        valid_subtitle_srt = valid_sub_srt_template.format(sub_srt_basename)

        with open(valid_subtitle_srt, "wt") as valid_subtitle_srt_file:
            valid_subtitle_srt_file.write(srt.compose(valid_subs))

        print("{0} - Done".format(sub_srt_basename))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Filter validated audio-aligned transcripts in SubRip file format."
    )
    parser.add_argument(
        "--subs_dir",
        type=str,
        help="Subtitles data directory, where audio-aligned transcripts are located.",
        required=True)
    parser.add_argument(
        "--out_dir",
        type=str,
        help="Output data directory, where to store split audio-aligned transcripts.",
        required=True)
    parser.add_argument(
        "--valid_cache",
        type=str,
        help="Validation cache, pickle file location containing validated transcripts.",
        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

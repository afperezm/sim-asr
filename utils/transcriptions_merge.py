import argparse
import glob
import io
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description="Merger of transcription chunks"
    )
    parser.add_argument(
        "--transcripts_dir",
        type=str,
        help="Transcriptions directory, where transcription chunk files are located.",
        required=True
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        help="Output directory, where to store merged transcriptions.",
        required=True
    )
    return parser.parse_args()


def _merge_data(transcripts_dir, output_dir):

    print("Loading transcript chunk files...")

    transcripts_filename = sorted(glob.glob("{0}/*.txt".format(transcripts_dir)))

    print("Obtained {0} chunk files".format(len(transcripts_filename)))

    transcripts_basename = ['_'.join(os.path.basename(t).split('_')[:-2]) for t in transcripts_filename]

    unique_transcripts_basename = list(dict.fromkeys(transcripts_basename))

    print("Composing transcript chunks")

    for utb in unique_transcripts_basename:

        print("Processing {0}".format(utb))

        chunk_filenames = sorted(glob.glob("{0}/{1}*.txt".format(transcripts_dir, utb)))

        transcripts = []

        for chunk_filename in chunk_filenames:
            with io.open(chunk_filename, 'rt') as chunk_file:
                transcripts.append(chunk_file.read())

        with io.open("{0}/{1}.txt".format(output_dir, utb), 'wt') as transcript_file:
            transcript_file.write('\n\n'.join(transcripts))

        print("Done")


def main():
    transcripts_dir = PARAMS.transcripts_dir
    output_dir = PARAMS.output_dir
    _merge_data(transcripts_dir, output_dir)


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

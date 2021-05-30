import argparse
import csv
import os
import pickle
import progressbar

from deepspeech_training.util.downloader import SIMPLE_BAR


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reader of ASR."
    )
    parser.add_argument(
        "--data_dir",
        help="Data directory, where cached transcripts in pickle format are located.",
        required=True
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Confidence threshold to filter bad quality transcriptions",
        default=0.9
    )
    return parser.parse_args()


def main():
    # Retrieve program arguments
    data_dir = os.path.abspath(PARAMS.data_dir)
    threshold = PARAMS.threshold

    # Read cached transcripts from pickle file
    cache_pkl = os.path.join(data_dir, "cache.pkl")
    with open(cache_pkl, "rb") as cache_pkl_file:
        cached_dict = pickle.load(cache_pkl_file)

    # Save parsed transcripts to TSV format
    output_tsv = os.path.join(data_dir, "output_not_validated.tsv")
    print("Saving validated TSV file to: ", output_tsv)
    with open(output_tsv, "wt", encoding="utf-8", newline="") as output_tsv_file:
        output_tsv_writer = csv.writer(output_tsv_file, dialect=csv.excel_tab)
        bar = progressbar.ProgressBar(max_value=len(cached_dict), widgets=SIMPLE_BAR)
        for filename, transcript, confidence in bar([item for key, item in enumerate(cached_dict)]):
            if len(transcript.split("\t")) > 1:
                parsed_confidences = [float(c) for c in confidence.split("\t")[1].split("+")]
                avg_confidence = sum(parsed_confidences) / len(parsed_confidences)
                if avg_confidence >= threshold:
                    print(filename, transcript, confidence)
                    output_tsv_writer.writerow([filename.replace("***", "").strip(), transcript.split("\t")[1]])
                else:
                    print(f"Skipping {filename} since it has a confidence of {avg_confidence}")
            else:
                print(f"Skipping {filename} since it has no transcription")


if __name__ == '__main__':
    PARAMS = parse_args()
    main()

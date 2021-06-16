import argparse
import csv
import os
import pickle
import progressbar

from deepspeech_training.util.downloader import SIMPLE_BAR


# cat validate_data_09.61_11.65.log validate_data_11.65_12.log validate_data_12_15.log | grep '\*\*\* ' > filenames.txt
# cat validate_data_09.61_11.65.log validate_data_11.65_12.log validate_data_12_15.log | grep Score: > scores.txt
# cat validate_data_09.61_11.65.log validate_data_11.65_12.log validate_data_12_15.log | grep Subtitle: > subtitles.txt
# cat validate_data_09.61_11.65.log validate_data_11.65_12.log validate_data_12_15.log | grep Transcript: > transcripts.txt
# cat validate_data_09.61_11.65.log validate_data_11.65_12.log validate_data_12_15.log | grep Confidence: > confidences.txt

# filenames_txt = "filenames.txt"
# with open(filenames_txt, "rt") as filenames_txt_file:
#     filenames = [filename.strip() for filename in filenames_txt_file.readlines()]
#
# transcripts_txt = "transcripts.txt"
# with open(transcripts_txt, "rt") as transcripts_txt_file:
#     transcripts = [transcript.strip() for transcript in transcripts_txt_file.readlines()]
#
# subtitles_txt = "subtitles.txt"
# with open(subtitles_txt, "rt") as subtitles_txt_file:
#     subtitles = [subtitle.strip() for subtitle in subtitles_txt_file]
#
# confidences_txt = "confidences.txt"
# with open(confidences_txt, "rt") as confidences_txt_file:
#     confidences = [confidence.strip() for confidence in confidences_txt_file.readlines()]
#
# scores_txt = "scores.txt"
# with open(scores_txt, "rt") as scores_txt_file:
#     scores = [score.strip() for score in scores_txt_file.readlines()]
#
# assert len(filenames) == len(transcripts)
# assert len(filenames) == len(subtitles)
# assert len(filenames) == len(confidences)
# assert len(filenames) == len(scores)
# cache_dict = [(filenames[idx], transcripts[idx], confidences[idx]) for idx in range(len(filenames))]
# cache_pkl = "cache.pkl"
# with open(cache_pkl, "wb") as cache_pkl_file:
#     pickle.dump(cache_dict, cache_pkl_file, protocol=pickle.HIGHEST_PROTOCOL)


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
                    # print(filename, transcript, confidence)
                    print(f"Processing {filename}")
                    output_tsv_writer.writerow([filename.replace("***", "").strip(), transcript.split("\t")[1]])
                else:
                    print(f"Skipping {filename} since it has a confidence of {avg_confidence}")
            else:
                print(f"Skipping {filename} since it has no transcription")


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


if __name__ == '__main__':
    PARAMS = parse_args()
    main()

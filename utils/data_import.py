import csv
import os
import progressbar
import subprocess
import unicodedata

from deepspeech_training.util.downloader import SIMPLE_BAR
from deepspeech_training.util.importers import (
    get_counter,
    get_imported_samples,
    get_importers_parser,
    get_validate_label,
    print_import_report,
)
from ds_ctcdecoder import Alphabet
from multiprocessing import Pool


FIELDNAMES = ["wav_filename", "wav_filesize", "transcript"]
MAX_SECS = 30
SAMPLE_RATE = 16000
PARAMS = None
FILTER_OBJ = None


class LabelFilter:

    def __init__(self, normalize, alphabet, validate_func):
        self.normalize = normalize
        self.alphabet = alphabet
        self.validate_func = validate_func

    def filter(self, label):
        if self.normalize:
            label = unicodedata.normalize("NFKD", label.strip()).encode("ascii", "ignore").decode("ascii", "ignore")
        label = self.validate_func(label)
        if self.alphabet and label and not self.alphabet.CanEncode(label):
            label = None
        return label


def init_worker(params):
    global FILTER_OBJ  # pylint: disable=global-statement
    validate_label = get_validate_label(params)
    alphabet = Alphabet(params.filter_alphabet) if params.filter_alphabet else None
    FILTER_OBJ = LabelFilter(params.normalize, alphabet, validate_label)


def one_sample(sample):
    """ Take an audio file and validate wav and transcript """

    wav_filename = sample[0]
    transcript = sample[1]
    file_size = -1
    frames = 0

    if os.path.exists(wav_filename):
        file_size = os.path.getsize(wav_filename)
        frames = int(subprocess.check_output(["soxi", "-s", wav_filename], stderr=subprocess.STDOUT))
    else:
        print("{} doesn't exist".format(wav_filename))

    label = FILTER_OBJ.filter(transcript)
    counter = get_counter()
    rows = []

    if file_size == -1:
        # Excluding samples that failed upon conversion
        counter["failed"] += 1
    elif label is None:
        # Excluding samples that failed on label validation
        counter["invalid_label"] += 1
    elif int(frames / SAMPLE_RATE * 1000 / MAX_SECS / 2) < len(str(label)):
        # Excluding samples that are too short to fit the transcript
        counter["too_short"] += 1
    elif frames / SAMPLE_RATE > MAX_SECS:
        # Excluding very long samples to keep a reasonable batch-size
        counter["too_long"] += 1
    else:
        # This one is good - keep it for the output CSV
        rows.append((os.path.split(wav_filename)[-1], file_size, label))
        counter["imported_time"] += frames

    counter["all"] += 1
    counter["total_time"] += frames

    return counter, rows


def _maybe_convert_sets(data_dir, audio_dir):

    output_csv = os.path.join(data_dir, "output.csv")
    output_csv_template = os.path.join(data_dir, "output_{}.csv")

    print("Loading CSV file: ", output_csv)
    with open(output_csv, "rt") as output_csv_file:
        output_csv_reader = csv.reader(output_csv_file, dialect=csv.excel)
        samples = [(os.path.join(audio_dir, row[0]), row[1]) for row in output_csv_reader]

    counter = get_counter()
    num_samples = len(samples)
    rows = []

    print("Importing WAV files...")
    pool = Pool(initializer=init_worker, initargs=(PARAMS,))
    bar = progressbar.ProgressBar(max_value=num_samples, widgets=SIMPLE_BAR)
    for row_idx, processed in enumerate(pool.imap_unordered(one_sample, samples), start=1):
        counter += processed[0]
        rows += processed[1]
        bar.update(row_idx)
    bar.update(num_samples)
    pool.close()
    pool.join()

    imported_samples = get_imported_samples(counter)
    assert counter["all"] == num_samples
    assert len(rows) == imported_samples

    print_import_report(counter, SAMPLE_RATE, MAX_SECS)

    test_csv = output_csv_template.format("test")
    print("Saving DeepSpeech-formatted test CSV file to: ", test_csv)
    with open(test_csv, "wt", encoding="utf-8", newline="") as test_csv_file:
        test_writer = csv.DictWriter(test_csv_file, fieldnames=FIELDNAMES)
        test_writer.writeheader()
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for filename, file_size, transcript in bar([row for idx, row in enumerate(rows) if idx % 10 == 0]):
            test_writer.writerow({
                "wav_filename": filename,
                "wav_filesize": file_size,
                "transcript": transcript
            })

    dev_csv = output_csv_template.format("dev")
    print("Saving DeepSpeech-formatted dev CSV file to: ", dev_csv)
    with open(dev_csv, "wt", encoding="utf-8", newline="") as dev_csv_file:
        dev_writer = csv.DictWriter(dev_csv_file, fieldnames=FIELDNAMES)
        dev_writer.writeheader()
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for filename, file_size, transcript in bar([row for idx, row in enumerate(rows) if idx % 10 == 1]):
            dev_writer.writerow({
                "wav_filename": filename,
                "wav_filesize": file_size,
                "transcript": transcript
            })

    train_csv = output_csv_template.format("train")
    print("Saving DeepSpeech-formatted train CSV file to: ", train_csv)
    with open(train_csv, "wt", encoding="utf-8", newline="") as train_csv_file:
        train_writer = csv.DictWriter(train_csv_file, fieldnames=FIELDNAMES)
        train_writer.writeheader()
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for filename, file_size, transcript in bar([row for idx, row in enumerate(rows) if idx % 10 > 1]):
            train_writer.writerow({
                "wav_filename": filename,
                "wav_filesize": file_size,
                "transcript": transcript
            })


def _preprocess_data(data_dir, audio_dir):
    # Making paths absolute
    data_dir = os.path.abspath(data_dir)
    audio_dir = os.path.abspath(audio_dir)
    # Produce CSV files
    _maybe_convert_sets(data_dir, audio_dir)


def parse_args():
    parser = get_importers_parser(
        description="Importer for ASR-CO dataset."
    )
    parser.add_argument(
        "--data_dir",
        help='Directory containing the dataset',
        required=True
    )
    parser.add_argument(
        "--audio_dir",
        help="Directory containing the audio clips - defaults to \"<data_dir>/wavs\"",
    )
    parser.add_argument(
        "--filter_alphabet",
        help="Exclude samples with characters not in provided alphabet",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Converts diacritic characters to their base ones",
    )
    return parser.parse_args()


def main():
    data_dir = PARAMS.data_dir
    audio_dir = PARAMS.audio_dir if PARAMS.audio_dir else os.path.join(PARAMS.data_dir, "wavs")
    _preprocess_data(data_dir, audio_dir)


if __name__ == "__main__":
    PARAMS = parse_args()
    main()
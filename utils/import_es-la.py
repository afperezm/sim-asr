#!/usr/bin/env python3
import csv
import os
import random
import re
import subprocess
import zipfile
import unicodedata
from multiprocessing import Pool

import progressbar

from deepspeech_training.util.downloader import SIMPLE_BAR, maybe_download
from deepspeech_training.util.importers import (
    get_counter,
    get_imported_samples,
    get_importers_parser,
    get_validate_label,
    print_import_report,
)
from ds_ctcdecoder import Alphabet

ARCHIVE_DIR_NAME = "{language_pack}"
ARCHIVE_NAME = "{language_pack}.zip"
ARCHIVE_URL = "http://www.openslr.org/resources/{number}/" + ARCHIVE_NAME

LANGUAGE_PACKS = [(61, 'es_ar_female'), (61, 'es_ar_male'),
                  (71, 'es_cl_female'), (71, 'es_cl_male'),
                  (72, 'es_co_female'), (72, 'es_co_male'),
                  (73, 'es_pe_female'), (73, 'es_pe_male'),
                  (74, 'es_pr_female'), (75, 'es_ve_female'),
                  (75, 'es_ve_male')]

FIELDNAMES = ["wav_filename", "wav_filesize", "transcript"]
SAMPLE_RATE = 16000
MAX_SECS = 35

PARAMS = None
FILTER_OBJ = None
SKIP_LIST = None


class LabelFilter:

    def __init__(self, normalize, alphabet, validate_func):
        self.normalize = normalize
        self.alphabet = alphabet
        self.validate_func = validate_func

    def filter(self, label):
        if self.normalize:
            tilde_words = re.findall(r"([a-zA-Z]+ñ[a-zA-Z]+)+", label)
            label = unicodedata.normalize("NFKD", label.strip()).encode("ascii", "ignore").decode("ascii", "ignore")
            for word in tilde_words:
                label = label.replace(
                    unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode("ascii", "ignore"), word)
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
    """ Take an audio file, and optionally convert it to 16kHz WAV while trimming silences at beginning or end """

    wav_filename = sample[0]
    transcript = sample[1]
    file_size = -1
    frames = 0

    if os.path.exists(wav_filename):
        tmp_filename = os.path.splitext(wav_filename)[0] + '.tmp.wav'
        subprocess.check_call(['sox', wav_filename, '-r', str(SAMPLE_RATE), '-c', '1', '-b', '16', tmp_filename,
                               'silence', '1', '0.1', '1%', 'reverse', 'silence', '1', '0.1', '1%', 'reverse'],
                              stderr=subprocess.STDOUT)
        os.rename(tmp_filename, wav_filename)
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
        # This one is good - keep it for the target CSV
        rows.append((os.path.split(wav_filename)[0].split("/")[-1], os.path.split(wav_filename)[-1], file_size, label))
        counter["imported_time"] += frames

    counter["all"] += 1
    counter["total_time"] += frames

    return (counter, rows)


def _download_and_preprocess_data(target_dir):
    # Making path absolute
    target_dir = os.path.abspath(target_dir)

    for number, name in LANGUAGE_PACKS:
        # Conditionally download data
        archive_path = maybe_download(ARCHIVE_NAME.format(language_pack=name),
                                      target_dir,
                                      ARCHIVE_URL.format(language_pack=name, number=number))
        # Conditionally extract data
        _maybe_extract(target_dir,
                       ARCHIVE_DIR_NAME.format(language_pack=name),
                       archive_path)

    # Produce CSV files
    _maybe_convert_sets(target_dir, "es_LA")


def _maybe_extract(target_dir, extracted_data, archive_path):
    # If target_dir/extracted_data does not exist, extract archive in target_dir
    extracted_path = os.path.join(target_dir, extracted_data)
    if not os.path.exists(extracted_path):
        print('No directory "%s" - extracting archive...' % extracted_path)
        if not os.path.isdir(extracted_path):
            os.mkdir(extracted_path)
        zip_ref = zipfile.ZipFile(archive_path, 'r')
        zip_ref.extractall(extracted_path)
        zip_ref.close()
    else:
        print('Found directory "%s" - not extracting it from archive.' % archive_path)


def _maybe_convert_sets(target_dir, language_pack_name):

    # override existing CSV with normalized one
    target_csv_template = os.path.join(
        target_dir, ARCHIVE_NAME.format(language_pack=language_pack_name).replace(".zip", "_{}.csv")
    )
    if os.path.isfile(target_csv_template):
        return

    samples = []

    for name in [name for number, name in LANGUAGE_PACKS]:

        extracted_data = os.path.join(target_dir, ARCHIVE_DIR_NAME.format(language_pack=name))

        if any(
            map(lambda sk: sk in name, SKIP_LIST)
        ):  # pylint: disable=cell-var-from-loop
            continue

        wav_root_dir = os.path.join(target_dir, extracted_data)
        input_tsv = os.path.join(wav_root_dir, "line_index.tsv")

        print("Loading TSV file: ", input_tsv)
        with open(input_tsv, "rt") as input_tsv_file:
            input_tsv_reader = csv.reader(input_tsv_file, dialect=csv.excel_tab)
            samples.extend([(os.path.join(wav_root_dir, row[0] + ".wav"), row[1]) for row in input_tsv_reader])

    # Keep track of how many samples are good vs. problematic
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

    random.shuffle(rows)

    imported_samples = get_imported_samples(counter)
    assert counter["all"] == num_samples
    assert len(rows) == imported_samples

    train_csv = target_csv_template.format("train")
    print("Saving DeepSpeech-formatted train CSV file to: ", train_csv)
    with open(train_csv, "wt", encoding="utf-8", newline="") as train_csv_file:
        train_writer = csv.DictWriter(train_csv_file, fieldnames=FIELDNAMES)
        train_writer.writeheader()
        for directory, filename, file_size, transcript in [row for idx, row in enumerate(rows) if idx % 10 > 1]:
            train_writer.writerow({
                "wav_filename": "{}/{}".format(directory, filename),
                "wav_filesize": file_size,
                "transcript": transcript
            })

    dev_csv = target_csv_template.format("dev")
    print("Saving DeepSpeech-formatted dev CSV file to: ", dev_csv)
    with open(dev_csv, "wt", encoding="utf-8", newline="") as dev_csv_file:
        dev_writer = csv.DictWriter(dev_csv_file, fieldnames=FIELDNAMES)
        dev_writer.writeheader()
        for directory, filename, file_size, transcript in [row for idx, row in enumerate(rows) if idx % 10 == 1]:
            dev_writer.writerow({
                "wav_filename": "{}/{}".format(directory, filename),
                "wav_filesize": file_size,
                "transcript": transcript
            })

    test_csv = target_csv_template.format("test")
    print("Saving DeepSpeech-formatted test CSV file to: ", test_csv)
    with open(test_csv, "wt", encoding="utf-8", newline="") as test_csv_file:
        test_writer = csv.DictWriter(test_csv_file, fieldnames=FIELDNAMES)
        test_writer.writeheader()
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for directory, filename, file_size, transcript in bar([row for idx, row in enumerate(rows) if idx % 10 == 0]):
            test_writer.writerow({
                "wav_filename": "{}/{}".format(directory, filename),
                "wav_filesize": file_size,
                "transcript": transcript
            })

    print_import_report(counter, SAMPLE_RATE, MAX_SECS)


def parse_args():
    parser = get_importers_parser(
        description="Importer for African Accented French dataset. More information on http://www.openslr.org/57/."
    )
    parser.add_argument(dest="target_dir")
    parser.add_argument(
        "--filter_alphabet",
        help="Exclude samples with characters not in provided alphabet",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Converts diacritic characters to their base ones",
    )
    parser.add_argument(
        "--skip_list",
        type=str,
        default="",
        help="Comma separated list of directories to skip",
    )
    return parser.parse_args()


if __name__ == "__main__":
    PARAMS = parse_args()
    SKIP_LIST = filter(None, PARAMS.skiplist.split(","))

    _download_and_preprocess_data(target_dir=PARAMS.target_dir)

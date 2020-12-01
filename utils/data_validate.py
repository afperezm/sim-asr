import csv
import difflib
import io
import os
import progressbar
import re
import subprocess
import unicodedata

from deepspeech_training.util.downloader import SIMPLE_BAR
from deepspeech_training.util.helpers import secs_to_hours
from deepspeech_training.util.importers import (
    get_counter,
    get_imported_samples,
    get_importers_parser,
    get_validate_label
)
from ds_ctcdecoder import Alphabet
from google.cloud import speech
from multiprocessing import Pool

MIN_SECS = 12
MAX_SECS = 15
SAMPLE_RATE = 16000
SIMILARITY_THRESHOLD = 0.7

CLIENT = None
FILTER_OBJ = None
PARAMS = None


class SubtitleFilter:

    def __init__(self, normalize, alphabet, validate_func):
        self.normalize = normalize
        self.alphabet = alphabet
        self.validate_func = validate_func

    def filter(self, subtitle):
        if self.normalize:
            tilde_words = re.findall(r"([a-zA-Z]+ñ[a-zA-Z]+)+", subtitle)
            subtitle = unicodedata.normalize("NFKD", subtitle.strip()).encode("ascii", "ignore").decode("ascii",
                                                                                                        "ignore")
            for word in tilde_words:
                subtitle = subtitle.replace(
                    unicodedata.normalize("NFKD", word).encode("ascii", "ignore").decode("ascii", "ignore"), word)
        subtitle = self.validate_func(subtitle)
        if self.alphabet and subtitle and not self.alphabet.CanEncode(subtitle):
            subtitle = None
        return subtitle


def similarity_score(s1, s2):
    s1n = re.sub(r'\s*', '', s1).lower()
    s2n = re.sub(r'\s*', '', s2).lower()

    return difflib.SequenceMatcher(None, s1n, s2n).ratio()


def print_import_report(counter, sample_rate, min_secs, max_secs):
    print('Imported %d samples.' % (get_imported_samples(counter)))
    if counter['failed'] > 0:
        print('Skipped %d samples that failed on audio validation.' % counter['failed'])
    if counter['invalid_label'] > 0:
        print('Skipped %d samples that failed on transcript validation.' % counter['invalid_label'])
    if counter['too_short'] > 0:
        print('Skipped %d samples that were shorter than %d seconds.' % (counter['too_short'], min_secs))
    if counter['too_long'] > 0:
        print('Skipped %d samples that were longer than %d seconds.' % (counter['too_long'], max_secs))
    print('Final amount of imported audio: %s from %s.' % (
    secs_to_hours(counter['imported_time'] / sample_rate), secs_to_hours(counter['total_time'] / sample_rate)))


def init_worker(params):
    global CLIENT  # pylint: disable=global-statement
    global FILTER_OBJ  # pylint: disable=global-statement
    validate_label = get_validate_label(params)
    alphabet = Alphabet(params.filter_alphabet) if params.filter_alphabet else None
    CLIENT = speech.SpeechClient()
    FILTER_OBJ = SubtitleFilter(params.normalize, alphabet, validate_label)


def validate_one(sample):
    """ Take an audio file and validate wav and transcript """

    wav_filename = sample[0]
    subtitle = sample[1]
    frames = 0
    score = 0.0

    if os.path.exists(wav_filename):
        frames = int(subprocess.check_output(["soxi", "-s", wav_filename], stderr=subprocess.STDOUT))

    subtitle_filtered = FILTER_OBJ.filter(subtitle)
    transcript = None
    counter = get_counter()
    rows = []

    if subtitle_filtered is not None and MIN_SECS <= frames / SAMPLE_RATE <= MAX_SECS:
        with io.open(wav_filename, 'rb') as audio_file:
            audio_content = audio_file.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            speech_contexts=[{"phrases": subtitle_filtered.split()}],
            language_code='es-CO',
            max_alternatives=1,
            model='default',
            use_enhanced=False)

        response = CLIENT.recognize(config=config, audio=audio)

        transcript = "".join([result.alternatives[0].transcript for result in response.results])
        confidence = "+".join([str(result.alternatives[0].confidence) for result in response.results])

        score = similarity_score(subtitle_filtered, transcript)

        filename = os.path.split(wav_filename)[-1]
        print("*** {} ***\nSubtitle:\t{}\nTranscript:\t{}\nScore:\t\t{}\nConfidence:\t{}".format(filename,
                                                                                                 subtitle_filtered,
                                                                                                 transcript,
                                                                                                 score,
                                                                                                 confidence))

    if frames == 0:
        counter['failed'] += 1
    elif subtitle_filtered is None:
        counter['invalid_label'] += 1
    elif frames / SAMPLE_RATE < MIN_SECS:
        counter['too_short'] += 1
    elif frames / SAMPLE_RATE > MAX_SECS:
        counter['too_long'] += 1
    elif score < SIMILARITY_THRESHOLD:
        counter['invalid_label'] += 1
    else:
        directory = os.path.split(wav_filename)[0].split('/')[-1]
        filename = os.path.split(wav_filename)[-1]
        rows.append((directory, filename, subtitle, transcript))
        counter['imported_time'] += frames

    counter['all'] += 1
    counter['total_time'] += frames

    return counter, rows


def _validate_data(data_dir, audio_dir):
    # Making paths absolute
    data_dir = os.path.abspath(data_dir)
    audio_dir = os.path.abspath(audio_dir)

    # Load audio and transcript from TSV file
    output_tsv = os.path.join(data_dir, "output.tsv")
    print("Loading TSV file: ", output_tsv)
    with open(output_tsv, "rt") as output_tsv_file:
        output_tsv_reader = csv.reader(output_tsv_file, dialect=csv.excel_tab)
        samples = [(os.path.join(audio_dir, row[0]), row[1]) for row in output_tsv_reader]

    counter = get_counter()
    num_samples = len(samples)
    rows = []

    print("Importing WAV files...")
    pool = Pool(initializer=init_worker, initargs=(PARAMS,))
    bar = progressbar.ProgressBar(max_value=num_samples, widgets=SIMPLE_BAR)
    for row_idx, processed in enumerate(pool.imap_unordered(validate_one, samples), start=1):
        counter += processed[0]
        rows += processed[1]
        bar.update(row_idx)
    bar.update(num_samples)
    pool.close()
    pool.join()

    imported_samples = get_imported_samples(counter)
    assert counter['all'] == num_samples
    assert len(rows) == imported_samples

    print_import_report(counter, SAMPLE_RATE, MIN_SECS, MAX_SECS)

    output_tsv = os.path.join(data_dir, "output_validated.tsv")
    print("Saving validated TSV file to: ", output_tsv)
    with open(output_tsv, "wt", encoding="utf-8", newline="") as output_tsv_file:
        output_tsv_writer = csv.writer(output_tsv_file, dialect=csv.excel_tab)
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for directory, filename, subtitle, transcript in bar([row for idx, row in enumerate(rows)]):
            output_tsv_writer.writerow([filename, subtitle])


def parse_args():
    parser = get_importers_parser(
        description="Validator for ASR-CO dataset."
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
    _validate_data(data_dir, audio_dir)


if __name__ == '__main__':
    PARAMS = parse_args()
    main()

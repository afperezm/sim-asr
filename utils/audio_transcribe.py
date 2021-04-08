import argparse
import csv
import glob
import os
import progressbar
import random
import re
import string

from deepspeech_training.util.downloader import SIMPLE_BAR
from google.cloud import speech
from google.cloud import storage
from google.oauth2 import service_account
from multiprocessing import Pool

from google.cloud.speech_v1 import RecognizeResponse, SpeechRecognitionResult, SpeechRecognitionAlternative
from num2words import num2words
from pydub import AudioSegment

BUCKET_NAME = "procesamiento-1"
PARAMS = None
SPEECH_CLIENT = None
STORAGE_CLIENT = None


def init_worker(params):
    global SPEECH_CLIENT  # pylint: disable=global-statement
    speech_credentials = service_account.Credentials.from_service_account_file('speech_credentials.json')
    SPEECH_CLIENT = speech.SpeechClient(credentials=speech_credentials)
    bucket_credentials = service_account.Credentials.from_service_account_file('bucket_credentials.json')
    STORAGE_CLIENT = storage.Client(credentials=bucket_credentials)


def transcribe_one(audio_file):
    basename = os.path.splitext(os.path.basename(audio_file))[0]
    dirname = os.path.dirname(audio_file)

    rows = []

    print("{0} - Processing".format(basename))

    if os.path.exists("{0}/{1}.txt".format(dirname, basename)):

        print("{0} - Skipping, already processed".format(basename))

        transcript = ""
        confidence = ""

        rows.append((basename, transcript, confidence))

        return rows

    audio_segment = AudioSegment.from_file(audio_file)

    if audio_segment.duration_seconds > 60:

        # print("{0} - Skipping, audio is longer than 1 minute".format(basename))

        # transcript = ""
        # confidence = ""

        # Compose audio cloud name
        bucket = STORAGE_CLIENT.get_bucket(BUCKET_NAME)
        alphabet = string.ascii_lowercase
        cloud_name_simple = ''.join(random.choice(alphabet) for i in range(10)) + ".wav"

        # Upload audio file to google cloud
        blob = bucket.blob(cloud_name_simple)
        blob.upload_from_filename(audio_file)

        # Compose file name in cloud
        cloud_name = "gs://" + BUCKET_NAME + "/" + cloud_name_simple

        # Create speech recognition request
        audio = speech.RecognitionAudio(uri=cloud_name)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='es-CO',
            max_alternatives=1,
            model='default',
            use_enhanced=False)

        # Launch recognition request
        operation = SPEECH_CLIENT.long_running_recognize(config=config, audio=audio)

        print("{0} - Waiting for operation to complete...".format(basename))
        response = operation.result(timeout=900000)

        # Gather transcript and confidence results
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        confidence = "+".join([str(result.alternatives[0].confidence) for result in response.results])

        # Convert numbers to spoken format if any
        numbers = sorted(list(set(re.findall(r"(\d+)", transcript))), key=lambda n: len(n), reverse=True)
        for number in numbers:
            word_key = number
            word_value = num2words(number, lang="es_CO")
            transcript = transcript.replace(word_key, word_value)

    else:

        # Read utterance audio content
        audio_content = audio_segment.raw_data

        # Create speech recognition request
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='es-CO',
            max_alternatives=1,
            model='default',
            use_enhanced=False)

        # Launch recognition request
        response = SPEECH_CLIENT.recognize(config=config, audio=audio)

        # Create dummy recognition response
        # response = RecognizeResponse(results=[SpeechRecognitionResult(alternatives=[SpeechRecognitionAlternative(
        #     transcript="Muchas gracias por hacer el esfuerzo a todo el mundo", confidence=0.8635320067405701)])])

        # Gather transcript and confidence results
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        confidence = "+".join([str(result.alternatives[0].confidence) for result in response.results])

        # Convert numbers to spoken format if any
        numbers = sorted(list(set(re.findall(r"(\d+)", transcript))), key=lambda n: len(n), reverse=True)
        for number in numbers:
            word_key = number
            word_value = num2words(number, lang="es_CO")
            transcript = transcript.replace(word_key, word_value)

    with open("{0}/{1}.txt".format(dirname, basename), "w") as f:
        f.write(transcript)

    print("{0} - Processed".format(basename))

    print("{0} - Transcript:\t{1}".format(basename, transcript))

    print("{0} - Confidence:\t{1}".format(basename, confidence))

    rows.append((basename, transcript, confidence))

    return rows


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transcriber of audio chunks"
    )
    parser.add_argument(
        "--audio_dir",
        type=str,
        help="Audio chunks data directory, where audio chunk files are located.",
        required=True
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        help="Number of parallel processes to launch.",
        default=4)
    return parser.parse_args()


def _transcribe_data(audio_dir):
    # Making paths absolute
    audio_dir = os.path.abspath(audio_dir)

    audio_files = glob.glob("{0}/*.wav".format(audio_dir))

    num_files = len(audio_files)
    rows = []

    pool = Pool(initializer=init_worker, initargs=(PARAMS,), processes=PARAMS.num_workers)
    bar = progressbar.ProgressBar(max_value=num_files, widgets=SIMPLE_BAR)
    for row_idx, processed in enumerate(pool.imap_unordered(transcribe_one, audio_files), start=1):
        rows += processed
        bar.update(row_idx)
    bar.update(num_files)
    pool.close()
    pool.join()

    output_tsv = os.path.join(audio_dir, "transcriptions.tsv")
    print("Saving transcriptions TSV file to: ", output_tsv)
    with open(output_tsv, "wt", encoding="utf-8", newline="") as output_tsv_file:
        output_tsv_writer = csv.writer(output_tsv_file, dialect=csv.excel_tab)
        bar = progressbar.ProgressBar(max_value=len(rows), widgets=SIMPLE_BAR)
        for filename, transcript, confidence in bar([row for idx, row in enumerate(rows)]):
            output_tsv_writer.writerow([filename, transcript, confidence])


def main():
    audio_dir = PARAMS.audio_dir
    _transcribe_data(audio_dir)


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

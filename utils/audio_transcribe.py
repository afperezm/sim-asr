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
VALID_FILES = ['001-CO-00519', '001-HV-00080', '001-PR-02798', '001-PR-02854', '001-PR-02906', '001-PR-02908',
               '001-VI-00057', '001-VI-00059', '001-VI-00062', '001-VI-00063', '001-VI-00064', '093-VI-00004',
               '093-VI-00010', '093-VI-00020', '093-VI-00021', '1003-VI-00002', '1003-VI-00003', '1004-VI-00002',
               '1004-VI-00005', '101-VI-00019', '101-VI-00026', '101-VI-00027', '101-VI-00028', '101-VI-00029',
               '101-VI-00030', '1043-VI-00002', '1043-VI-00003', '1043-VI-00004', '1043-VI-00005', '1043-VI-00006',
               '1043-VI-00007', '1043-VI-00008', '1043-VI-00009', '104-VI-00001', '1052-CO-00602', '1052-CO-00660',
               '1052-EE-00214', '105-VI-00011', '105-VI-00012', '105-VI-00013', '1065-VI-00001', '1066-HV-00066',
               '1066-VI-00003', '1066-VI-00004', '1066-VI-00005', '1071-VI-00002', '1075-CO-00536', '1075-PR-02342',
               '1075-VI-00003', '107-CO-00600', '107-VI-00007', '107-VI-00008', '107-VI-00009', '107-VI-00010',
               '107-VI-00011', '1083-VI-00001', '1083-VI-00002', '1083-VI-00003', '1083-VI-00004', '1083-VI-00005',
               '1083-VI-00006', '1083-VI-00007', '1083-VI-00008', '1083-VI-00009', '1083-VI-00010', '1083-VI-00011',
               '1083-VI-00012', '1083-VI-00013', '1083-VI-00014', '1087-VI-00001', '1087-VI-00002', '1089-VI-00001',
               '1089-VI-00002', '1091-VI-00191', '1095-VI-00001', '1095-VI-00002', '1096-PR-02509', '1096-PR-02510',
               '1096-PR-02559', '1096-PR-02562', '1096-VI-00001', '1096-VI-00002', '1097-VI-00001', '1097-VI-00002',
               '1097-VI-00003', '1101-VI-00001', '1101-VI-00002', '1103-VI-00001', '1103-VI-00002', '1103-VI-00003',
               '1109-VI-00001', '1109-VI-00002', '1109-VI-00003', '1109-VI-00004', '1109-VI-00005', '1109-VI-00006',
               '1109-VI-00007', '1110-VI-00001', '1113-EE-00195', '1113-EE-00196', '1113-EE-00197', '1113-EE-00198',
               '1113-EE-00199', '1113-EE-00204', '1113-EE-00205', '1113-EE-00206', '1116-VI-00001', '111-PR-00677',
               '111-PR-02291', '111-PR-02449', '111-PR-02660', '111-VI-00010', '1122-VI-00001', '1131-VI-00001',
               '1139-VI-00001', '113-VI-00002', '113-VI-00003', '113-VI-00004', '113-VI-00006', '113-VI-00007',
               '113-VI-00008', '113-VI-00009', '113-VI-00010', '115-VI-00003', '115-VI-00053', '115-VI-00054',
               '115-VI-00056', '115-VI-00057', '115-VI-00060', '115-VI-00061', '115-VI-00062', '115-VI-00063',
               '115-VI-00064', '115-VI-00065', '115-VI-00066', '115-VI-00067', '115-VI-00068', '115-VI-00069',
               '115-VI-00070', '115-VI-00071', '115-VI-00072', '115-VI-00073', '115-VI-00074', '115-VI-00075',
               '115-VI-00076', '1163-VI-00001', '1170-VI-00001', '1194-VI-00001', '1194-VI-00002', '121-VI-00003',
               '121-VI-00004', '121-VI-00005', '126-AA-00002', '126-VI-00008', '126-VI-00031', '126-VI-00034',
               '126-VI-00040', '126-VI-00041', '126-VI-00044', '126-VI-00048', '126-VI-00049', '126-VI-00050',
               '126-VI-00051', '126-VI-00052', '126-VI-00053', '126-VI-00054', '126-VI-00057', '126-VI-00058',
               '126-VI-00059', '126-VI-00060', '126-VI-00062', '126-VI-00063', '126-VI-00064', '126-VI-00065',
               '126-VI-00066', '126-VI-00067', '126-VI-00068', '126-VI-00069', '127-PR-02844', '127-PR-03004',
               '127-VI-00005', '127-VI-00008', '127-VI-00009', '145-VI-00001', '145-VI-00002', '149-VI-00012',
               '149-VI-00013', '149-VI-00014', '179-PR-02507', '179-VI-00004', '179-VI-00005', '179-VI-00006',
               '179-VI-00007', '182-VI-00004', '182-VI-00009', '182-VI-00010', '182-VI-00012', '182-VI-00013',
               '182-VI-00014', '182-VI-00015', '182-VI-00016', '182-VI-00017', '183-PR-02104', '183-VI-00003',
               '202-CO-00626', '202-VI-00003', '202-VI-00013', '202-VI-00014', '245-PR-02582', '245-PR-02596',
               '245-PR-02599', '245-PR-02624', '245-PR-02631', '245-PR-02636', '245-VI-00005', '245-VI-00006',
               '245-VI-00007', '248-PR-02290', '248-PR-02483', '248-PR-02550', '248-PR-02563', '248-PR-02603',
               '248-VI-00002', '248-VI-00003', '248-VI-00012', '248-VI-00013', '250-VI-00002', '255-VI-00011',
               '255-VI-00013', '255-VI-00014', '255-VI-00015', '268-VI-00010', '268-VI-00011', '273-VI-00001',
               '277-PR-00594', '277-VI-00009', '277-VI-00013', '277-VI-00014', '277-VI-00015', '283-VI-00002',
               '283-VI-00003', '283-VI-00004', '284-PR-02348', '284-PR-02349', '284-VI-00003', '284-VI-00004',
               '290-PR-02182', '290-PR-02298', '290-PR-02350', '290-VI-00004', '290-VI-00012', '290-VI-00013',
               '290-VI-00014', '290-VI-00015', '290-VI-00016', '296-VI-00002', '297-VI-00003', '297-VI-00004',
               '298-VI-00003', '319-CO-00644', '319-VI-00004', '319-VI-00005', '319-VI-00006', '319-VI-00007',
               '319-VI-00008', '319-VI-00009', '319-VI-00010', '319-VI-00011', '319-VI-00012', '332-VI-00002',
               '350-VI-00003', '350-VI-00004', '350-VI-00005', '350-VI-00006', '351-PR-02439', '351-PR-02522',
               '351-PR-02527', '351-PR-02530', '351-PR-02532', '351-VI-00007', '351-VI-00008', '351-VI-00009',
               '351-VI-00011', '351-VI-00014', '351-VI-00016', '397-PR-02407', '397-PR-02409', '397-PR-02433',
               '397-PR-02434', '397-VI-00008', '397-VI-00011', '397-VI-00017', '398-VI-00007', '403-PR-02302',
               '403-PR-02344', '403-PR-02345', '412-PR-02324', '412-VI-00011', '412-VI-00013', '412-VI-00015',
               '412-VI-00016', '422-VI-00003', '436-VI-00004', '436-VI-00005', '453-VI-00017', '453-VI-00018',
               '453-VI-00024', '463-VI-00001', '463-VI-00009', '463-VI-00010', '464-VI-00011', '464-VI-00012',
               '464-VI-00013', '465-VI-00002', '465-VI-00007', '465-VI-00011', '465-VI-00012', '465-VI-00013',
               '465-VI-00014', '466-PR-02398', '466-VI-00001', '466-VI-00007', '466-VI-00008', '466-VI-00009',
               '466-VI-00010', '466-VI-00011', '466-VI-00012', '467-VI-00003', '467-VI-00004', '467-VI-00005',
               '467-VI-00006', '467-VI-00007', '467-VI-00008', '467-VI-00009', '467-VI-00010', '467-VI-00011',
               '467-VI-00012', '467-VI-00013', '467-VI-00014', '467-VI-00015', '467-VI-00016', '467-VI-00017',
               '469-CO-00568', '469-VI-00005', '469-VI-00006', '469-VI-00007', '469-VI-00009', '469-VI-00010',
               '469-VI-00011', '469-VI-00012', '469-VI-00013', '469-VI-00014', '469-VI-00015', '475-VI-00006',
               '476-CO-00601', '476-PR-02897', '476-PR-02929', '476-PR-02943', '476-PR-02999', '476-PR-03000',
               '476-VI-00003', '476-VI-00004', '485-VI-00001', '488-VI-00011', '488-VI-00012', '489-CO-00637',
               '494-VI-00001', '514-PR-02248', '514-PR-02318', '514-PR-02320', '514-VI-00009', '514-VI-00010',
               '514-VI-00014', '514-VI-00015', '514-VI-00016', '514-VI-00017', '518-VI-00004', '519-VI-00008',
               '519-VI-00009', '520-VI-00004', '520-VI-00006', '520-VI-00007', '520-VI-00008', '523-VI-00001',
               '525-VI-00001', '525-VI-00004', '527-VI-00001', '527-VI-00002', '530-VI-00003', '530-VI-00004',
               '541-VI-00012', '541-VI-00015', '548-VI-00002', '548-VI-00003', '548-VI-00004', '562-CO-00593',
               '562-VI-00013', '562-VI-00014', '562-VI-00017', '562-VI-00018', '562-VI-00019', '562-VI-00020',
               '562-VI-00021', '562-VI-00022', '562-VI-00023', '562-VI-00024', '564-VI-00003', '564-VI-00004',
               '564-VI-00005', '564-VI-00006', '565-PR-02249', '565-PR-02259', '565-PR-02377', '565-VI-00002',
               '565-VI-00013', '565-VI-00014', '565-VI-00015', '565-VI-00016', '568-VI-00009', '575-VI-00004',
               '578-VI-00004', '579-VI-00008', '579-VI-00009', '579-VI-00010', '579-VI-00011', '579-VI-00012',
               '579-VI-00013', '579-VI-00014', '580-VI-00013', '581-VI-00004', '581-VI-00009', '581-VI-00010',
               '581-VI-00011', '581-VI-00012', '581-VI-00013', '581-VI-00014', '581-VI-00015', '581-VI-00016',
               '585-VI-00004', '588-VI-00005', '589-PR-02858', '589-PR-02863', '589-PR-02864', '589-PR-02865',
               '589-PR-02866', '589-PR-02867', '589-PR-02868', '589-VI-00001', '589-VI-00002', '589-VI-00003',
               '589-VI-00004', '589-VI-00005', '589-VI-00006', '589-VI-00007', '589-VI-00008', '589-VI-00009',
               '589-VI-00010', '589-VI-00011', '589-VI-00012', '589-VI-00013', '589-VI-00014', '589-VI-00015',
               '589-VI-00016', '589-VI-00017', '589-VI-00018', '589-VI-00019', '589-VI-00020', '593-PR-02018',
               '593-PR-02190', '593-PR-02241', '593-PR-02258', '593-PR-02346', '593-PR-02695', '593-PR-02711',
               '593-PR-02761', '593-PR-02917', '593-VI-00007', '593-VI-00008', '593-VI-00009', '593-VI-00015',
               '593-VI-00016', '593-VI-00017', '593-VI-00018', '593-VI-00019', '593-VI-00020', '593-VI-00021',
               '593-VI-00022', '595-VI-00004', '595-VI-00005', '595-VI-00006', '596-VI-00001', '596-VI-00006',
               '596-VI-00008', '596-VI-00009', '596-VI-00010', '596-VI-00011', '609-PR-02969', '609-PR-02970',
               '613-CO-00584', '613-VI-00004', '613-VI-00005', '613-VI-00006', '613-VI-00007', '613-VI-00008',
               '613-VI-00009', '613-VI-00010', '641-CO-00629', '641-VI-00004', '641-VI-00006', '641-VI-00008',
               '641-VI-00009', '641-VI-00010', '641-VI-00012', '641-VI-00013', '641-VI-00014', '641-VI-00015',
               '641-VI-00016', '641-VI-00017', '641-VI-00018', '672-VI-00001', '672-VI-00002', '672-VI-00003',
               '672-VI-00004', '682-VI-00001', '738-VI-00003', '738-VI-00004', '738-VI-00005', '738-VI-00006',
               '738-VI-00007', '747-VI-00002', '747-VI-00003', '763-VI-00003', '763-VI-00004', '763-VI-00005',
               '764-VI-00001', '764-VI-00002', '764-VI-00003', '765-PR-02468', '765-PR-02469', '765-VI-00001',
               '765-VI-00002', '765-VI-00003', '766-PR-02540', '766-PR-02542', '766-VI-00001', '766-VI-00002',
               '766-VI-00003', '766-VI-00004', '818-VI-00002', '818-VI-00005', '827-CO-00490', '827-CO-00511',
               '831-PR-02600', '831-PR-02601', '831-PR-02637', '831-VI-00007', '831-VI-00008', '831-VI-00009',
               '831-VI-00010', '831-VI-00011', '831-VI-00012', '831-VI-00013', '831-VI-00014', '831-VI-00015',
               '831-VI-00016', '831-VI-00017', '831-VI-00018', '831-VI-00019', '831-VI-00020', '831-VI-00021',
               '831-VI-00022', '831-VI-00023', '831-VI-00024', '831-VI-00025', '831-VI-00026', '850-VI-00002',
               '850-VI-00003', '850-VI-00004', '850-VI-00005', '880-VI-00002', '880-VI-00004', '880-VI-00005',
               '880-VI-00006', '880-VI-00007', '880-VI-00008', '880-VI-00009', '902-CO-00533', '902-VI-00002',
               '909-VI-00002', '912-VI-00001', '918-VI-00001', '918-VI-00002', '918-VI-00003', '918-VI-00005',
               '919-VI-00003', '919-VI-00004', '925-VI-00002', '925-VI-00003', '925-VI-00004', '943-VI-00001',
               '943-VI-00002', '943-VI-00003', '944-VI-00001', '944-VI-00003', '944-VI-00004', '960-VI-00001',
               '961-VI-00003', '961-VI-00004', '961-VI-00005', '961-VI-00006', '961-VI-00007', '961-VI-00008',
               '961-VI-00009', '961-VI-00010', '980-VI-00002', '980-VI-00003', '988-VI-00001']


def init_worker(params):
    global SPEECH_CLIENT  # pylint: disable=global-statement
    global STORAGE_CLIENT  # pylint: disable=global-statement
    speech_credentials = service_account.Credentials.from_service_account_file('speech_credentials.json')
    SPEECH_CLIENT = speech.SpeechClient(credentials=speech_credentials)
    bucket_credentials = service_account.Credentials.from_service_account_file('bucket_credentials.json')
    STORAGE_CLIENT = storage.Client(credentials=bucket_credentials)


def transcribe_one(audio_file):
    basename = os.path.splitext(os.path.basename(audio_file))[0]
    dirname = os.path.dirname(audio_file)

    rows = []

    print("{0} - Processing".format(basename))

    if not os.path.basename(audio_file).split('_')[0] in VALID_FILES:

        print("{0} - Skipping, not spanish".format(basename))

        duration = ""
        transcript = ""
        confidence = ""

        rows.append((basename, transcript, confidence, duration))

        return rows

    if os.path.exists("{0}/{1}.txt".format(dirname, basename)):

        print("{0} - Skipping, already processed".format(basename))

        with open("{0}/{1}.txt".format(dirname, basename), "rt") as transcript_file:
            transcript = transcript_file.read()

        with open("{0}/{1}_confidence.txt".format(dirname, basename), "rt") as confidence_file:
            confidence = confidence_file.read()

        with open("{0}/{1}_duration.txt".format(dirname, basename), "rt") as f:
            duration = f.read()

        print("{0} - Transcript:\t{1}".format(basename, transcript))

        print("{0} - Confidence:\t{1}".format(basename, confidence))

        rows.append((basename, transcript, confidence, duration))

        return rows

    audio_segment = AudioSegment.from_file(audio_file)

    if audio_segment.duration_seconds > 60:

        print("{0} - Skipping, audio is longer than 1 minute".format(basename))

        duration = ""
        transcript = ""
        confidence = ""

        rows.append((basename, transcript, confidence, duration))

        return rows

    #     # Compose audio cloud name
    #     bucket = storage_client.get_bucket(BUCKET_NAME)
    #     alphabet = string.ascii_lowercase
    #     cloud_name_simple = ''.join(random.choice(alphabet) for i in range(10)) + ".wav"
    #
    #     # Upload audio file to google cloud
    #     blob = bucket.blob(cloud_name_simple)
    #     blob.upload_from_filename(audio_file)
    #
    #     # Compose file name in cloud
    #     cloud_name = "gs://" + BUCKET_NAME + "/" + cloud_name_simple
    #
    #     # Create speech recognition request
    #     audio = speech.RecognitionAudio(uri=cloud_name)
    #     config = speech.RecognitionConfig(
    #         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    #         sample_rate_hertz=16000,
    #         language_code='es-CO',
    #         max_alternatives=1,
    #         model='default',
    #         use_enhanced=False)
    #
    #     # Launch recognition request
    #     operation = speech_client.long_running_recognize(config=config, audio=audio)
    #
    #     print("{0} - Waiting for operation to complete...".format(basename))
    #     response = operation.result(timeout=900000)
    #
    #     # Gather transcript and confidence results
    #     transcript = " ".join([result.alternatives[0].transcript for result in response.results])
    #     confidence = "+".join([str(result.alternatives[0].confidence) for result in response.results])
    #
    #     # Convert numbers to spoken format if any
    #     numbers = sorted(list(set(re.findall(r"(\d+)", transcript))), key=lambda n: len(n), reverse=True)
    #     for number in numbers:
    #         word_key = number
    #         word_value = num2words(number, lang="es_CO")
    #         transcript = transcript.replace(word_key, word_value)

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

    duration = str(audio_segment.duration_seconds)

    with open("{0}/{1}.txt".format(dirname, basename), "wt") as f:
        f.write(transcript)

    with open("{0}/{1}_confidence.txt".format(dirname, basename), "wt") as f:
        f.write(confidence)

    with open("{0}/{1}_duration.txt".format(dirname, basename), "wt") as f:
        f.write(duration)

    print("{0} - Processed".format(basename))

    print("{0} - Transcript:\t{1}".format(basename, transcript))

    print("{0} - Confidence:\t{1}".format(basename, confidence))

    print("{0} - Duration:\t{1}".format(basename, duration))

    rows.append((basename, transcript, confidence, duration))

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
    parser.add_argument(
        "--threshold",
        type=float,
        help="Confidence threshold to filter bad quality transcriptions",
        default=0.9
    )
    return parser.parse_args()


def _transcribe_data(audio_dir):
    # Making paths absolute
    audio_dir = os.path.abspath(audio_dir)

    audio_files = sorted(glob.glob("{0}/*.wav".format(audio_dir)))

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
        for filename, transcript, confidence, duration in bar([row for idx, row in enumerate(rows)]):
            if len(transcript) == 0:
                print(f"Skipping {filename}, no transcription")
                continue
            parsed_duration = float(duration)
            if parsed_duration > 15.0:
                print(f"Skipping {filename}, audio too long")
                continue
            parsed_confidences = [float(c) for c in confidence.split("+")]
            avg_confidence = sum(parsed_confidences) / len(parsed_confidences)
            if avg_confidence < PARAMS.threshold:
                print(f"Skipping {filename}, low confidence")
                continue
            output_tsv_writer.writerow([filename, transcript])


def main():
    audio_dir = PARAMS.audio_dir
    _transcribe_data(audio_dir)


if __name__ == "__main__":
    PARAMS = parse_args()
    main()

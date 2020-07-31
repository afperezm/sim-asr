from pymongo import MongoClient
import argparse
import docx2txt
import html2text
import json
import librosa
import os
import paramiko
import pdftotext
import soundfile
import tempfile
import textract

src_path = "/var/www/html/expedientes/storage/app/public"
loc_path = "/rep/CaptureModule"
dst_path = "/home/andresf/data/asr-co"


def create_db_connection(host, username, password, auth_source, auth_mechanism):
    """Creates and returns a PyMongo connection object."""

    client = MongoClient(host,
                         username=username,
                         password=password,
                         authSource=auth_source,
                         authMechanism=auth_mechanism)

    return client


def get_resources_list(db_conn, db_name):
    """Executes an aggregation pipeline to extract the list of WAV and HTML records for VI type interviews."""

    pipeline = [
        {'$match': {'type': {'$in': ['Audio de la entrevista', 'Transcripción final']}}},
        {'$group': {'_id': '$identifier', 'records': {
            '$push': {'type': '$type', 'filename': '$filename', 'fileFormat': '$metadata.firstLevel.fileFormat',
                      'originalName': '$extra.nombre_original', 'accessLevel': '$metadata.firstLevel.accessLevel'}}}},
        {'$project': {'interview_type': {'$split': ['$_id', '-']}, 'records': 1, 'fileFormat': 1, 'originalName': 1,
                      'accessLevel': 1}},
        {'$unwind': '$interview_type'},
        {'$match': {'interview_type': {'$regex': 'VI'}}},
        {'$project': {'interview_type': 1, 'records': 1, 'fileFormat': 1, 'originalName': 1, 'accessLevel': 1}},
        {'$match': {'records': {'$elemMatch': {'type': 'Audio de la entrevista'}}}},
        {'$match': {'records': {'$elemMatch': {'type': 'Transcripción final'}}}},
        {'$match': {'records': {'$elemMatch': {'accessLevel': 4}}}},
    ]

    result = db_conn[db_name].records.aggregate(pipeline)

    return list(result)


def create_ssh_connection(hostname, username, key_filename, key_password=None):
    """Creates a Paramiko SSH connection object."""

    private_key = paramiko.RSAKey.from_private_key_file(key_filename, key_password)

    ssh_client = paramiko.SSHClient()

    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=hostname, username=username, pkey=private_key, timeout=10)

    return ssh_client


def validate_file(file_name, sftp_client):
    """Validate files on remote filesystem"""

    stat_info = sftp_client.stat(file_name.replace(loc_path, src_path))

    if stat_info.st_size == 0:
        raise OSError("File is empty")


def extract_text(file_name, file_format):
    """Extract and return text content from document file."""
    if file_format == "otr":
        with open(file_name) as json_file:
            content_json = json.load(json_file)
        content_html = content_json["text"]
        content_txt = html2text.html2text(content_html)
    elif file_format == "html":
        with open(file_name, "r") as f:
            content_html = f.read()
        content_txt = html2text.html2text(content_html)
    elif file_format == "pdf":
        with open(file_name, "rb") as f:
            content_pdf = pdftotext.PDF(f)
        content_txt = ''.join([page for page in content_pdf])
    elif file_format == "doc":
        content_txt = textract.process(file_name)
    elif file_format == "docx":
        content_txt = docx2txt.process(file_name)
    elif file_format == "odt":
        content_txt = textract.process(file_name)
    else:
        raise ValueError("Invalid file format {0}", file_format)

    if not content_txt:
        raise ValueError("Empty content")

    return content_txt


def extract_audio(file_name, file_format):
    """Extract and return audio file content."""
    if file_format not in ["aac", "m4a", "mp3", "mp4", "wav", "wma"]:
        raise ValueError("Invalid file format {0}", file_format)

    content, _ = librosa.load(file_name, sr=16000, mono=True)

    return content


def copy_records(resource_id, transcript_records, audio_records, ssh_client):
    """Copies transcript and audio records files from a remote server through SSH."""

    sftp_client = ssh_client.open_sftp()

    # Aggregate list of transcript records
    record = transcript_records[0]

    # Copy transcript

    # Validate file on remote location
    try:
        print("Verifying file {0}".format(record["filename"].replace(loc_path, src_path)))
        validate_file(record["filename"].replace(loc_path, src_path), sftp_client)
        print("Done")
    except OSError as e:
        print("Failed.", e)
        return False

    tmp = tempfile.NamedTemporaryFile(mode="w+")

    # Copy file to temporary location
    try:
        print("Copying file {0} to {1}".format(record["filename"].replace(loc_path, src_path), tmp.name))
        sftp_client.get(record["filename"].replace(loc_path, src_path), tmp.name)
        print("Done")
    except IOError as e:
        print("Failed.", e)
        return False

    # Extract copied file content
    try:
        print("Extracting transcript content")
        transcript_content = extract_text(tmp.name, record["fileFormat"])
        print("Done")
    except ValueError as e:
        print("Failed.", e)
        tmp.close()
        return False

    tmp.close()

    # Write extracted file content
    try:
        print("Writing extracted transcript file content to {0}/{1}.txt".format(dst_path, resource_id))
        with open("{0}/{1}.txt".format(dst_path, resource_id), "w") as f:
            f.write(transcript_content)
        print("Done")
    except IOError as e:
        print("Failed.", e)
        return False

    # Aggregate list of audio records
    record = audio_records[0]

    # Copy audio

    # Validate file on remote location
    try:
        print("Verifying file {0}".format(record["filename"].replace(loc_path, src_path)))
        validate_file(record["filename"].replace(loc_path, src_path), sftp_client)
        print("Done")
    except OSError as e:
        print("Failed.", e)
        return False

    tmp = tempfile.NamedTemporaryFile(mode="w+")

    # Copy file to temporary location
    try:
        print("Copying file {0} to {1}".format(record["filename"].replace(loc_path, src_path), tmp.name))
        sftp_client.get(record["filename"].replace(loc_path, src_path), tmp.name)
        print("Done")
    except IOError as e:
        print("Failed.", e)
        return False

    # Extract copied file content
    try:
        print("Extracting audio content")
        audio_content = extract_audio(tmp.name, record["fileFormat"])
        print("Done")
    except ValueError as e:
        print("Failed.", e)
        tmp.close()
        return False

    tmp.close()

    # Write extracted file content
    try:
        print("Writing extracted audio file content to {0}/{1}.wav".format(dst_path, resource_id))
        soundfile.write("{0}/{1}.wav".format(dst_path, resource_id), audio_content, 16000)
        print("Done")
    except IOError as e:
        print("Failed.", e)
        return False

    return True


def copy_resources(resources_list, ssh_client):
    """Performs file copying from a remote server through SSH using a key file for authentication."""

    os.makedirs(dst_path, exist_ok=True)

    for resource in resources_list:

        resource_id = resource['_id']
        audio_records = [record for record in resource['records'] if record['type'] == 'Audio de la entrevista']
        transcript_records = [record for record in resource['records'] if record['type'] == 'Transcripción final']

        num_audio_records = len(audio_records)
        num_transcript_records = len(transcript_records)

        if num_audio_records + num_transcript_records == 2:
            # Simple case: one audio and one transcription
            print(resource_id)
            print(audio_records)
            print(transcript_records)
            copy_result = copy_records(resource_id, transcript_records, audio_records, ssh_client)
            if not copy_result:
                print("Rollback records copying")
                if os.path.exists("{0}/{1}.txt".format(dst_path, resource_id)):
                    print("Remove transcript")
                    os.remove("{0}/{1}.txt".format(dst_path, resource_id))
                if os.path.exists("{0}/{1}.wav".format(dst_path, resource_id)):
                    print("Remove audio")
                    os.remove("{0}/{1}.wav".format(dst_path, resource_id))
                print("Done")
        elif num_audio_records + num_transcript_records > 2 and num_transcript_records == 1:
            # Relatively simple case: one transcription and many audios (merge audios since most likely split)
            print(resource_id)
            print(audio_records)
            print(transcript_records)
        # elif num_audio_records + num_transcript_records > 2 and num_audio_records == 1:
        #     # Relatively simple case: one audio and many transcriptions (choose best transcription format or merge?)
        #     print(resource_id)
        #     print(audio_records)
        #     print(transcript_records)


def main():
    parser = argparse.ArgumentParser(description="File synchronization through SSH")
    parser.add_argument("--mongo_host", type=str, help="MongoDB host", required=True)
    parser.add_argument("--mongo_user", type=str, help="MongoDB username", required=True)
    parser.add_argument("--mongo_pass", type=str, help="MongoDB password", required=True)
    parser.add_argument("--mongo_db", type=str, help="MongoDB database", required=True)
    parser.add_argument("--ssh_host", type=str, help="SSH host", required=True)
    parser.add_argument("--ssh_user", type=str, help="SSH username", required=True)
    parser.add_argument("--ssh_key_file", type=str, help="Path to SSH key file", required=True)
    parser.add_argument("--ssh_key_pass", type=str, help="SSH key password", required=False)

    args = parser.parse_args()

    # connect to the production database
    db_conn = create_db_connection(args.mongo_host, args.mongo_user, args.mongo_pass, args.mongo_db, "SCRAM-SHA-256")

    # retrieve list of files to copy
    resources_list = get_resources_list(db_conn, args.mongo_db)

    # close database connection
    db_conn.close()

    # create SSH client with auto add policy for new host keys
    ssh_conn = create_ssh_connection(args.ssh_host, args.ssh_user, args.ssh_key_file, args.ssh_key_pass)

    # execute files copy to local
    copy_resources(resources_list, ssh_conn)

    # close SSH connection
    ssh_conn.close()


if __name__ == '__main__':
    main()

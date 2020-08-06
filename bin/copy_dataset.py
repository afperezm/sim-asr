import threading

from fs.sshfs import SSHFS
from pymongo import MongoClient
from subprocess import check_call, CalledProcessError
import argparse
import concurrent.futures
import docx2txt
import html2text
import json
import os
import paramiko
import pdftotext
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
                      'originalName': '$extra.nombre_original', 'accessLevel': '$metadata.firstLevel.accessLevel',
                      'ident': '$ident'}}}},
        {'$project': {'interview_type': {'$split': ['$_id', '-']}, 'records': 1, 'fileFormat': 1, 'originalName': 1,
                      'accessLevel': 1, 'ident': 1}},
        {'$unwind': '$interview_type'},
        {'$match': {'interview_type': {'$regex': 'VI'}}},
        {'$project': {'interview_type': 1, 'records': 1, 'fileFormat': 1, 'originalName': 1, 'accessLevel': 1,
                      'ident': 1}},
        {'$match': {'records': {'$elemMatch': {'type': 'Audio de la entrevista'}}}},
        {'$match': {'records': {'$elemMatch': {'type': 'Transcripción final'}}}},
        {'$match': {'records': {'$elemMatch': {'accessLevel': 4}}}},
        {'$project': {'records': 1, 'audioRecords': {'$filter': {'input': '$records', 'as': 'record', 'cond': {'$eq': ['$$record.type', 'Audio de la entrevista']}}}, 'transcriptRecords': {'$filter': {'input': '$records', 'as': 'record', 'cond': {'$eq': ['$$record.type', 'Transcripción final']}}}}},
        {'$project': {'records': 1, 'numRecords': {'$size': '$records'}, 'numAudioRecords': {'$size': '$audioRecords'}, 'numTranscriptRecords': {'$size': '$transcriptRecords'}}},
        {'$match': {'numRecords': {'$eq': 2}}},
        {'$sort': {'_id': 1}},
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


def create_ssh_filesystem(hostname, username, key_filename, key_password=None):
    """Creates a filesystem object over SSH using Paramiko."""

    private_key = paramiko.RSAKey.from_private_key_file(key_filename, key_password)
    ssh_fs = SSHFS(hostname, user=username, pkey=private_key)

    return ssh_fs


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


def copy_records_with_rollback(ssh_client, resource):
    """Copies transcript and audio records files and rollback if copy fails."""

    resource_id = resource['_id']
    audio_records = [record for record in resource['records'] if record['type'] == 'Audio de la entrevista']
    transcript_records = [record for record in resource['records'] if record['type'] == 'Transcripción final']

    print("{0} - Copying records".format(resource_id))

    copy_result = copy_records(ssh_client, resource_id, transcript_records[0], audio_records[0])

    if copy_result:
        print("{0} - Done".format(resource_id))
    else:
        print("{0} - Failed".format(resource_id))
        if os.path.exists("{0}/{1}.txt".format(dst_path, resource_id)):
            print("{0} - Remove transcript".format(resource_id))
            os.remove("{0}/{1}.txt".format(dst_path, resource_id))
        if os.path.exists("{0}/{1}.wav".format(dst_path, resource_id)):
            print("{0} - Remove audio".format(resource_id))
            os.remove("{0}/{1}.wav".format(dst_path, resource_id))
        print("{0} - Done".format(resource_id))

    return copy_result


def copy_records(ssh_client, resource_id, transcript_record, audio_record):
    """Copies transcript and audio records files from a remote server through SSH."""

    # print(resource_id)
    # print(audio_record)
    # print(transcript_record)

    transcript_exists = os.path.isfile("{0}/{1}.txt".format(dst_path, resource_id))
    audio_exists = os.path.isfile("{0}/{1}.wav".format(dst_path, resource_id))

    if transcript_exists and audio_exists:
        print("{0} - Transcript and audio files already copied".format(resource_id))
        return True

    sftp_client = ssh_client.open_sftp()

    # Copy transcript
    print("{0} - Copying transcript".format(resource_id))

    # Validate file on remote location
    try:
        print("{0} - Verifying transcript file {1}".format(resource_id, transcript_record["filename"].replace(loc_path, src_path)))
        validate_file(transcript_record["filename"].replace(loc_path, src_path), sftp_client)
        print("{0} - Verifying transcript file - Done".format(resource_id))
    except OSError as e:
        print("{0} - Verifying transcript file - Failed.".format(resource_id), e)
        return False

    tmp = tempfile.NamedTemporaryFile(mode="w+")

    # Copy file to temporary location
    try:
        print("{0} - Copying transcript file".format(resource_id))
        sftp_client.get(transcript_record["filename"].replace(loc_path, src_path), tmp.name)
        print("{0} - Copying transcript file - Done".format(resource_id))
    except IOError as e:
        print("{0} - Copying transcript file - Failed.".format(resource_id), e)
        tmp.close()
        return False

    # Extract copied file content
    try:
        print("{0} - Extracting transcript content".format(resource_id))
        transcript_content = extract_text(tmp.name, transcript_record["fileFormat"])
        print("{0} - Extracting transcript content - Done".format(resource_id))
    except ValueError as e:
        print("{0} - Extracting transcript content - Failed.".format(resource_id), e)
        tmp.close()
        return False

    tmp.close()

    # Write extracted file content
    try:
        print("{0} - Writing extracted transcript file".format(resource_id))
        with open("{0}/{1}.txt".format(dst_path, resource_id), "w") as f:
            f.write(transcript_content)
        print("{0} - Writing extracted transcript file - Done".format(resource_id))
    except IOError as e:
        print("{0} - Writing extracted transcript file - Failed.".format(resource_id), e)
        return False

    print("{0} - Copying transcript - Done".format(resource_id))

    # Copy audio
    print("{0} - Copying audio".format(resource_id))

    # Validate file on remote location
    try:
        print("{0} - Verifying audio file".format(resource_id))
        validate_file(audio_record["filename"].replace(loc_path, src_path), sftp_client)
        print("{0} - Verifying audio file - Done".format(resource_id))
    except OSError as e:
        print("{0} - Verifying audio file - Failed.".format(resource_id), e)
        return False

    tmp = tempfile.NamedTemporaryFile(mode="w+")

    # Copy file to temporary location
    try:
        print("{0} - Copying audio file".format(resource_id))
        sftp_client.get(audio_record["filename"].replace(loc_path, src_path), tmp.name)
        print("{0} - Copying audio file - Done".format(resource_id))
    except IOError as e:
        print("{0} - Copying audio file - Failed.".format(resource_id), e)
        tmp.close()
        return False

    # Convert copied audio file
    try:
        print("{0} - Converting copied audio".format(resource_id))
        check_call(["ffmpeg", "-y", "-i", "{0}".format(tmp.name), "-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000",
                    "{0}/{1}.wav".format(dst_path, resource_id)])
        print("{0} - Converting copied audio - Done".format(resource_id))
    except CalledProcessError as e:
        print("{0} - Converting copied audio - Failed.".format(resource_id), e)
        tmp.close()
        return False

    tmp.close()

    print("{0} - Copying audio - Done".format(resource_id))

    return True


def copy_resources(ssh_client, resources_list, max_workers):
    """Performs file copying from a remote server through SSH using a key file for authentication."""

    os.makedirs(dst_path, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(copy_records_with_rollback, ssh_client=ssh_client, resource=resource): resource['_id'] for
            resource in resources_list}
        for future in concurrent.futures.as_completed(futures):
            resource_id = futures[future]
            try:
                if future.result():
                    print("{0} - Records copied".format(resource_id))
                else:
                    print("{0} - Records NOT copied".format(resource_id))
            except Exception as e:
                print("{0} - An error occurred while copying resources.".format(resource_id), e)

        # el
        # if num_audio_records > 1 and num_transcript_records == 1:
        #     # Relatively simple case: one transcription and many audios (merge audios since most likely split)
        #     print(resource_id)
        #     print(audio_records)
        #     print(transcript_records)
        #     any_none_orig_names = functools.reduce(operator.or_,
        #                                            list(map(lambda r: r['originalName'] is None, audio_records)))
        #     audio_records_sorted_1 = sorted(audio_records,
        #                                     key=lambda r: True if any_none_orig_names else r['originalName'])
        #     audio_records_sorted_2 = sorted(audio_records, key=lambda r: r['ident'])
        #     print("Consistent sorting: {0}".format(audio_records_sorted_1 == audio_records_sorted_2))
        #     file_format = audio_records[0]['fileFormat']
        #     all_same_format = functools.reduce(operator.and_,
        #                                        list(map(lambda r: r['fileFormat'] == file_format, audio_records)))
        #     print("All same format: {0}".format(all_same_format))
        # el
        # if num_transcript_records > 1 and num_audio_records == 1:
        #     # Relatively simple case: one audio and many transcriptions (choose best transcription format or merge?)
        #     print(resource_id)
        #     print(audio_records)
        #     # print(transcript_records)
        #     file_format = transcript_records[0]['fileFormat']
        #     all_formats_equal = functools.reduce(operator.and_, list(
        #         map(lambda r: r['fileFormat'] == file_format, transcript_records)))
        #     # print("All formats equal: {0}".format(all_formats_equal))
        #     # original_name = transcript_records[0]['originalName']
        #     # all_original_names_equal = functools.reduce(operator.and_, list(
        #     #     map(lambda r: r['originalName'] == original_name, transcript_records)))
        #     # print("All original names equal: {0}".format(all_original_names_equal))
        #     # if all_formats_equal and all_original_names_equal:
        #     #     # pick anyone
        #     #     num_sorted_audio_records += 1
        #     #     # Compute and compare md5 signatures
        #     #     md5_signatures = [compute_signature(ssh_client, record) for record in transcript_records]
        #     #     all_signatures_equal = all(md5_signature == md5_signatures[0] for md5_signature in md5_signatures)
        #     #     # print(md5_signatures)
        #     #     print("All signatures equal: {0}".format(all_signatures_equal))
        #     # el
        #     # if not all_formats_equal and num_transcript_records == 2:
        #         # pick html if any
        #         # print(num_transcript_records)
        #         # print((list(map(lambda r: r['fileFormat'], transcript_records))))
        #     # else:
        #     # if not all_formats_equal and num_transcript_records > 2:
        #     #     print(transcript_records)


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
    parser.add_argument("--num_workers", type=int, help="Number of workers", required=False, default=1)

    args = parser.parse_args()

    # connect to the production database
    db_conn = create_db_connection(args.mongo_host, args.mongo_user, args.mongo_pass, args.mongo_db, "SCRAM-SHA-256")

    # retrieve list of files to copy
    print("Retrieving resources list")
    resources_list = get_resources_list(db_conn, args.mongo_db)
    print("Obtained {0} resources".format(len(resources_list)))

    # close database connection
    db_conn.close()

    # create SSH client with auto add policy for new host keys
    ssh_conn = create_ssh_connection(args.ssh_host, args.ssh_user, args.ssh_key_file, args.ssh_key_pass)

    # execute files copy to local
    copy_resources(ssh_conn, resources_list, args.num_workers)

    # close SSH connection
    ssh_conn.close()


if __name__ == '__main__':
    main()

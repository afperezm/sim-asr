import threading

from fs.sshfs import SSHFS
from pymongo import MongoClient
from subprocess import check_call, CalledProcessError, DEVNULL, STDOUT
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

PARAMS = None


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

    pipeline = [
        {'$match': {'type': {'$in': ['Audio de la entrevista']}}},
        {'$group': {'_id': '$identifier', 'records': {'$push': {'type': '$type',
                                                                'filename': '$filename',
                                                                'fileFormat': '$metadata.firstLevel.fileFormat',
                                                                'originalName': '$extra.nombre_original',
                                                                'accessLevel': '$metadata.firstLevel.accessLevel',
                                                                'ident': '$ident'}}}},
        {'$match': {'_id': {
            '$in': ['001-CO-00465', '001-CO-00519', '001-CO-00608', '001-PR-02906', '001-PR-02908', '001-VI-00064',
                    '001-VI-00065', '093-VI-00003', '093-VI-00020', '093-VI-00021', '1003-VI-00002', '1004-VI-00002',
                    '101-VI-00019', '102-PR-00620', '102-VI-00001', '1036-PR-02447', '1048-CO-00513', '1048-VI-00006',
                    '105-VI-00002', '1052-EE-00214', '1065-VI-00001', '1065-VI-00002', '1065-VI-00004', '1065-VI-00005',
                    '1071-VI-00002', '1083-VI-00001', '1083-VI-00002', '1083-VI-00003', '1083-VI-00004',
                    '1083-VI-00005', '1083-VI-00006', '1083-VI-00007', '1083-VI-00008', '1083-VI-00009',
                    '1084-VI-00001', '1087-PR-02544', '1087-PR-02609', '1091-VI-01091', '1109-VI-00004',
                    '1109-VI-00005', '1109-VI-00006', '1109-VI-00007', '111-PR-00677', '111-PR-02291', '111-PR-02451',
                    '111-PR-02452', '1110-VI-00002', '1113-EE-00204', '1113-EE-00205', '1113-EE-00206', '1115-VI-00004',
                    '1115-VI-00005', '1139-VI-00001', '115-VI-00003', '115-VI-00053', '115-VI-00054', '115-VI-00056',
                    '115-VI-00057', '115-VI-00060', '115-VI-00061', '115-VI-00062', '115-VI-00063', '115-VI-00064',
                    '115-VI-00065', '115-VI-00066', '115-VI-00067', '115-VI-00068', '1154-PR-02954', '1156-PR-02913',
                    '1163-VI-00001', '1170-VI-00001', '1194-VI-00001', '1194-VI-00002', '121-VI-00001', '121-VI-00003',
                    '121-VI-00004', '121-VI-00005', '126-AA-00002', '126-HV-00010', '126-HV-00011', '126-VI-00008',
                    '126-VI-00031', '126-VI-00034', '126-VI-00040', '126-VI-00041', '126-VI-00044', '126-VI-00048',
                    '126-VI-00049', '126-VI-00050', '126-VI-00051', '126-VI-00052', '126-VI-00053', '126-VI-00054',
                    '126-VI-00055', '126-VI-00056', '126-VI-00061', '127-PR-03004', '127-VI-00009', '145-VI-00002',
                    '155-VI-00004', '179-VI-00004', '182-VI-00004', '182-VI-00012', '182-VI-00013', '182-VI-00014',
                    '182-VI-00016', '182-VI-00017', '183-VI-00004', '202-VI-00003', '248-VI-00002', '248-VI-00003',
                    '252-VI-00001', '255-VI-00011', '257-VI-00002', '261-PR-02240', '273-VI-00001', '277-PR-00594',
                    '277-VI-00009', '277-VI-00013', '277-VI-00014', '277-VI-00015', '290-PR-02182', '290-PR-02298',
                    '290-PR-02350', '290-VI-00004', '290-VI-00012', '290-VI-00013', '290-VI-00014', '290-VI-00015',
                    '290-VI-00016', '319-VI-00004', '319-VI-00005', '332-VI-00002', '350-VI-00003', '397-VI-00008',
                    '397-VI-00011', '398-VI-00007', '403-PR-02302', '403-PR-02344', '403-PR-02345', '412-PR-02324',
                    '412-VI-00011', '412-VI-00013', '445-VI-00003', '453-VI-00025', '453-VI-00026', '463-VI-00001',
                    '465-VI-00002', '465-VI-00008', '465-VI-00009', '465-VI-00010', '465-VI-00015', '465-VI-00016',
                    '466-VI-00001', '466-VI-00007', '466-VI-00008', '466-VI-00013', '475-VI-00006', '476-CO-00455',
                    '476-CO-00539', '476-CO-00566', '476-CO-00567', '476-CO-00598', '476-CO-00601', '476-PR-02897',
                    '476-PR-02929', '476-PR-02943', '476-VI-00004', '485-VI-00001', '494-VI-00001', '514-PR-02248',
                    '514-PR-02318', '514-PR-02320', '514-VI-00009', '514-VI-00010', '518-VI-00004', '519-VI-00001',
                    '519-VI-00008', '519-VI-00009', '520-VI-00004', '520-VI-00006', '520-VI-00007', '520-VI-00008',
                    '520-VI-00009', '523-VI-00001', '525-VI-00001', '525-VI-00004', '527-VI-00001', '527-VI-00002',
                    '541-VI-00012', '541-VI-00015', '548-VI-00002', '562-VI-00013', '562-VI-00014', '562-VI-00017',
                    '562-VI-00023', '562-VI-00024', '565-VI-00002', '565-VI-00013', '565-VI-00014', '565-VI-00015',
                    '565-VI-00016', '568-VI-00009', '575-VI-00004', '580-VI-00013', '581-VI-00004', '585-VI-00004',
                    '591-VI-00002', '593-PR-02011', '593-PR-02016', '593-PR-02018', '593-PR-02113', '593-PR-02197',
                    '593-PR-02241', '593-PR-02917', '593-VI-00007', '593-VI-00008', '593-VI-00009', '593-VI-00022',
                    '595-VI-00004', '595-VI-00005', '595-VI-00006', '596-VI-00001', '596-VI-00006', '596-VI-00008',
                    '596-VI-00009', '596-VI-00010', '608-PR-02015', '609-PR-02969', '609-PR-02970', '641-VI-00004',
                    '641-VI-00006', '641-VI-00008', '641-VI-00009', '641-VI-00010', '641-VI-00012', '641-VI-00015',
                    '641-VI-00016', '641-VI-00017', '641-VI-00018', '643-PR-00538', '644-VI-00003', '660-VI-00008',
                    '660-VI-00009', '672-VI-00001', '672-VI-00003', '682-VI-00001', '686-VI-00010', '737-VI-00017',
                    '738-VI-00003', '744-PR-02810', '747-VI-00002', '747-VI-00003', '763-VI-00003', '763-VI-00004',
                    '763-VI-00005', '818-VI-00002', '818-VI-00006', '827-CO-00490', '827-CO-00492', '827-CO-00511',
                    '827-VI-00003', '827-VI-00005', '831-VI-00020', '831-VI-00021', '831-VI-00022', '831-VI-00023',
                    '831-VI-00024', '831-VI-00025', '831-VI-00026', '850-VI-00002', '850-VI-00003', '850-VI-00004',
                    '850-VI-00005', '902-CO-00533', '902-VI-00002', '918-VI-00005', '943-VI-00001', '943-VI-00002',
                    '943-VI-00003', '944-VI-00001', '960-VI-00001', '978-VI-00007', '980-VI-00002', '980-VI-00003']}}},
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

    stat_info = sftp_client.stat(file_name.replace(PARAMS.root_path, PARAMS.src_path))

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

    audio_records = [record for record in resource['records'] if record['type'] == 'Audio de la entrevista']
    # transcript_records = [record for record in resource['records'] if record['type'] == 'Transcripción final']

    total_copy_result = True

    for idx, audio_record in enumerate(audio_records):

        resource_id = "{0}_{1}".format(resource['_id'], idx)

        print("{0} - Copying records".format(resource_id))

        copy_result = copy_records(ssh_client, resource_id, audio_record)
        total_copy_result &= total_copy_result

        if copy_result:
            print("{0} - Done".format(resource_id))
        else:
            print("{0} - Failed".format(resource_id))
            if os.path.exists("{0}/{1}.txt".format(PARAMS.loc_path, resource_id)):
                print("{0} - Remove transcript".format(resource_id))
                os.remove("{0}/{1}.txt".format(PARAMS.loc_path, resource_id))
            if os.path.exists("{0}/{1}.wav".format(PARAMS.loc_path, resource_id)):
                print("{0} - Remove audio".format(resource_id))
                os.remove("{0}/{1}.wav".format(PARAMS.loc_path, resource_id))
            print("{0} - Done".format(resource_id))

    return total_copy_result


def copy_records(ssh_client, resource_id, audio_record):
    """Copies transcript and audio records files from a remote server through SSH."""

    # print(resource_id)
    # print(audio_record)
    # print(transcript_record)

    # transcript_exists = os.path.isfile("{0}/{1}.txt".format(PARAMS.loc_path, resource_id))
    audio_exists = os.path.isfile("{0}/{1}.wav".format(PARAMS.loc_path, resource_id))

    # if transcript_exists and audio_exists:
    if audio_exists:
        print("{0} - Audio file already copied".format(resource_id))
        return True

    sftp_client = ssh_client.open_sftp()

    # # Copy transcript
    # print("{0} - Copying transcript".format(resource_id))
    #
    # # Validate file on remote location
    # try:
    #     print("{0} - Verifying transcript file".format(resource_id))
    #     validate_file(transcript_record["filename"].replace(PARAMS.root_path, PARAMS.src_path), sftp_client)
    #     print("{0} - Verifying transcript file - Done".format(resource_id))
    # except OSError as e:
    #     print("{0} - Verifying transcript file - Failed.".format(resource_id), e)
    #     return False
    #
    # tmp = tempfile.NamedTemporaryFile(mode="w+")
    #
    # # Copy file to temporary location
    # try:
    #     print("{0} - Copying transcript file".format(resource_id))
    #     sftp_client.get(transcript_record["filename"].replace(PARAMS.root_path, PARAMS.src_path), tmp.name)
    #     print("{0} - Copying transcript file - Done".format(resource_id))
    # except IOError as e:
    #     print("{0} - Copying transcript file - Failed.".format(resource_id), e)
    #     tmp.close()
    #     return False
    #
    # # Extract copied file content
    # try:
    #     print("{0} - Extracting transcript content".format(resource_id))
    #     transcript_content = extract_text(tmp.name, transcript_record["fileFormat"])
    #     print("{0} - Extracting transcript content - Done".format(resource_id))
    # except ValueError as e:
    #     print("{0} - Extracting transcript content - Failed.".format(resource_id), e)
    #     tmp.close()
    #     return False
    #
    # tmp.close()
    #
    # # Write extracted file content
    # try:
    #     print("{0} - Writing extracted transcript file".format(resource_id))
    #     with open("{0}/{1}.txt".format(PARAMS.loc_path, resource_id), "w") as f:
    #         f.write(transcript_content)
    #     print("{0} - Writing extracted transcript file - Done".format(resource_id))
    # except IOError as e:
    #     print("{0} - Writing extracted transcript file - Failed.".format(resource_id), e)
    #     return False
    #
    # print("{0} - Copying transcript - Done".format(resource_id))

    # Copy audio
    print("{0} - Copying audio".format(resource_id))

    # Validate file on remote location
    try:
        print("{0} - Verifying audio file".format(resource_id))
        validate_file(audio_record["filename"].replace(PARAMS.root_path, PARAMS.src_path), sftp_client)
        print("{0} - Verifying audio file - Done".format(resource_id))
    except OSError as e:
        print("{0} - Verifying audio file - Failed.".format(resource_id), e)
        return False

    tmp = tempfile.NamedTemporaryFile(mode="w+")

    # Copy file to temporary location
    try:
        print("{0} - Copying audio file".format(resource_id))
        sftp_client.get(audio_record["filename"].replace(PARAMS.root_path, PARAMS.src_path), tmp.name)
        print("{0} - Copying audio file - Done".format(resource_id))
    except IOError as e:
        print("{0} - Copying audio file - Failed.".format(resource_id), e)
        tmp.close()
        return False

    # Convert copied audio file
    try:
        print("{0} - Converting copied audio".format(resource_id))
        check_call(["ffmpeg", "-y", "-i", "{0}".format(tmp.name), "-map_metadata", "-1", "-acodec", "pcm_s16le", "-ac",
                    "1", "-ar", "16000", "{0}/{1}.wav".format(PARAMS.loc_path, resource_id)], stdout=DEVNULL, stderr=STDOUT)
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

    os.makedirs(PARAMS.loc_path, exist_ok=True)

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


def parse_args():
    parser = argparse.ArgumentParser(description="File synchronization through SSH")
    parser.add_argument("--src_path", type=str, help="Path at the source filesystem where files will be read from",
                        required=True)
    parser.add_argument("--root_path", type=str, help="Root path of the file paths stored in MongoDB", required=True)
    parser.add_argument("--loc_path", type=str, help="Path at the local filesystem where files will be copied",
                        required=True)
    parser.add_argument("--mongo_host", type=str, help="MongoDB host", required=True)
    parser.add_argument("--mongo_user", type=str, help="MongoDB username", required=True)
    parser.add_argument("--mongo_pass", type=str, help="MongoDB password", required=True)
    parser.add_argument("--mongo_db", type=str, help="MongoDB database", required=True)
    parser.add_argument("--ssh_host", type=str, help="SSH host", required=True)
    parser.add_argument("--ssh_user", type=str, help="SSH username", required=True)
    parser.add_argument("--ssh_key_file", type=str, help="Path to SSH key file", required=True)
    parser.add_argument("--ssh_key_pass", type=str, help="SSH key password", required=False)
    parser.add_argument("--num_workers", type=int, help="Number of workers", required=False, default=1)

    return parser.parse_args()


def main():
    # connect to the production database
    db_conn = create_db_connection(PARAMS.mongo_host, PARAMS.mongo_user, PARAMS.mongo_pass, PARAMS.mongo_db, "SCRAM-SHA-256")

    # retrieve list of files to copy
    print("Retrieving resources list")
    resources_list = get_resources_list(db_conn, PARAMS.mongo_db)
    print("Obtained {0} resources".format(len(resources_list)))

    # close database connection
    db_conn.close()

    # create SSH client with auto add policy for new host keys
    ssh_conn = create_ssh_connection(PARAMS.ssh_host, PARAMS.ssh_user, PARAMS.ssh_key_file, PARAMS.ssh_key_pass)

    # execute files copy to local
    copy_resources(ssh_conn, resources_list, PARAMS.num_workers)

    # close SSH connection
    ssh_conn.close()


if __name__ == '__main__':
    PARAMS = parse_args()
    main()

import argparse
import glob
import os
import progressbar

from aeneas.audiofile import AudioFileUnsupportedFormatError
from aeneas.executetask import ExecuteTask, ExecuteTaskInputError, ExecuteTaskExecutionError
from aeneas.task import Task
from multiprocessing import Pool

AUDIO_DIR = None
OUTPUT_DIR = None
TRANSCRIPTS_DIR = None


def init_worker(params):
    global AUDIO_DIR  # pylint: disable=global-statement
    global OUTPUT_DIR  # pylint: disable=global-statement
    global TRANSCRIPTS_DIR  # pylint: disable=global-statement
    AUDIO_DIR = params.audio_dir
    OUTPUT_DIR = params.out_dir
    TRANSCRIPTS_DIR = params.trans_dir


def align_transcript(transcript_file):

    basename = os.path.splitext(os.path.basename(transcript_file))[0]

    audio_file = "{0}/{1}.wav".format(AUDIO_DIR, basename)

    if not os.path.isfile(audio_file) or not os.access(audio_file, os.R_OK):
        # print("{0} - Missing associated audio file".format(basename))
        return [basename], [], [], []

    if os.path.isfile(u"{0}/{1}.wav.srt".format(OUTPUT_DIR, basename)):
        # print("{0} - Skipping, already processed.".format(basename))
        return [], [basename], [], []

    try:
        # print("{0} - Processing transcript".format(basename))

        # create Task object
        config_string = u"task_language=spa|is_text_type=plain|os_task_file_format=srt"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = u"{0}/{1}.wav".format(AUDIO_DIR, basename)
        task.text_file_path_absolute = u"{0}/{1}.txt".format(TRANSCRIPTS_DIR, basename)
        task.sync_map_file_path_absolute = u"{0}/{1}.wav.srt".format(OUTPUT_DIR, basename)

        # process Task
        ExecuteTask(task).execute()

        # output sync map to file
        if task.output_sync_map_file() is None:
            return [], [], [basename], []
        else:
            return [], [], [], [basename]
    except (AudioFileUnsupportedFormatError, ExecuteTaskInputError, ExecuteTaskExecutionError) as e:
        # print("{0} - Failed.".format(basename), e)
        return [], [], [basename], []


def main():
    parser = argparse.ArgumentParser(
        description="Aeneas-based transcripts aligner."
    )
    parser.add_argument(
        "--trans_dir",
        type=str,
        help="Transcripts data directory, where tag-clean transcripts are located.",
        required=True)
    parser.add_argument(
        "--audio_dir",
        type=str,
        help="Audio data directory, where tag-clean transcripts associated audios are located.",
        required=True)
    parser.add_argument(
        "--out_dir",
        type=str,
        help="Output data directory, where to copy audio-aligned transcripts.",
        required=True)
    parser.add_argument(
        "--num_workers",
        type=int,
        help="Number of parallel processes to launch.",
        default=4)

    args = parser.parse_args()

    transcript_files = sorted(glob.glob("{0}/*.txt".format(args.trans_dir)))
    num_transcript_files = len(transcript_files)

    missing = []
    skipped = []
    failed = []
    success = []

    pool = Pool(initializer=init_worker, initargs=(args,), processes=args.num_workers)
    bar = progressbar.ProgressBar(max_value=num_transcript_files)
    for row_idx, processed in enumerate(pool.imap_unordered(align_transcript, transcript_files), start=1):
        missing += processed[0]
        skipped += processed[1]
        failed += processed[2]
        success += processed[3]
        bar.update(row_idx)
    bar.update(num_transcript_files)
    pool.close()
    pool.join()

    print("{} transcripts missing audio".format(len(missing)))
    print("{} transcripts skipped since already processed".format(len(skipped)))
    print("{} transcripts failed upon alignment".format(len(failed)))
    print("{} transcripts successfully aligned".format(len(success)))


if __name__ == '__main__':
    main()

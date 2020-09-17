import argparse
import glob
import os

from aeneas.audiofile import AudioFileUnsupportedFormatError
from aeneas.executetask import ExecuteTask, ExecuteTaskInputError, ExecuteTaskExecutionError
from aeneas.task import Task


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

    args = parser.parse_args()

    transcript_files = glob.glob("{0}/*.txt".format(args.trans_dir))

    for transcript_file in sorted(transcript_files):

        basename = os.path.splitext(os.path.basename(transcript_file))[0]

        audio_file = "{0}/{1}.wav".format(args.audio_dir, basename)

        if not os.path.isfile(audio_file) or not os.access(audio_file, os.R_OK):
            print("{0} - Missing associated audio file".format(basename))
            continue

        print("{0} - Processing transcript".format(basename))

        if os.path.isfile(u"{0}/{1}.wav.srt".format(args.out_dir, basename)):
            print("{0} - Skipping, already processed.".format(basename))
            continue

        try:
            # create Task object
            config_string = u"task_language=spa|is_text_type=plain|os_task_file_format=srt"
            task = Task(config_string=config_string)
            task.audio_file_path_absolute = u"{0}/{1}.wav".format(args.audio_dir, basename)
            task.text_file_path_absolute = u"{0}/{1}.txt".format(args.trans_dir, basename)
            task.sync_map_file_path_absolute = u"{0}/{1}.wav.srt".format(args.out_dir, basename)

            # process Task
            ExecuteTask(task).execute()

            # output sync map to file
            task.output_sync_map_file()
        except (AudioFileUnsupportedFormatError, ExecuteTaskInputError, ExecuteTaskExecutionError) as e:
            print("{0} - Failed.".format(basename), e)
            continue

        print("{0} - Done.".format(basename))


if __name__ == '__main__':
    main()

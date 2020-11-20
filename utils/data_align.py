import argparse
import glob
import os
import progressbar
import re
import srt
import string
import tempfile

from aeneas.audiofile import AudioFileUnsupportedFormatError
from aeneas.executetask import ExecuteTask, ExecuteTaskInputError, ExecuteTaskExecutionError
from aeneas.task import Task
from collections import Counter
from datetime import datetime, timedelta
from multiprocessing import Pool
from pydub import AudioSegment

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

    with open(u"{0}/{1}.txt".format(TRANSCRIPTS_DIR, basename), "rt") as transcript_txt_file:
        contents = transcript_txt_file.read()

    block_headings = re.findall(r"(\[BLOQUE[^\]]+\])", contents)

    block_limits = [item for sublist in
                    [[contents.find(block_heading), contents.find(block_heading) + len(block_heading)] for block_heading
                     in block_headings] for item in sublist] + [len(contents)]

    content_fragments = [{**Counter({'content_start': block_limits[idx + 1], 'content_end': block_limits[idx + 2]}), **Counter(
        re.match(r'^\[BLOQUE: (?P<time_start>\d{1,2}(:\d{2})+)-(?P<time_end>\d{1,2}(:\d{2})+)\]$',
                 contents[block_limits[idx]:block_limits[idx + 1]]).groupdict())} for idx in
                         range(len(block_limits) - 1) if idx % 2 == 0]

    audio_wav_file = AudioSegment.from_wav(u"{0}/{1}.wav".format(AUDIO_DIR, basename))

    audio_subs = []

    for idx, fragment in enumerate(content_fragments):

        alignment_failed = False

        content_fragment = contents[fragment['content_start']:fragment['content_end']]
        content_fragment = re.sub(r'^[' + re.escape(string.punctuation) + r']+', '', content_fragment.strip()).strip()

        if not content_fragment:
            continue

        text_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".txt")
        text_temp_file.write(content_fragment)
        text_temp_file.flush()

        time_start = datetime.strptime(fragment['time_start'], '%H:%M:%S')
        if fragment['time_end'] == '23:59:59':
            time_end = datetime.strptime(str(timedelta(seconds=int(audio_wav_file.duration_seconds))), '%H:%M:%S')
        else:
            time_end = datetime.strptime(fragment['time_end'], '%H:%M:%S')

        t1 = (time_start - datetime(1900, 1, 1)).total_seconds()
        t2 = (time_end - datetime(1900, 1, 1)).total_seconds()

        audio_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".wav")
        audio_segment_file = audio_wav_file[t1 * 1000:t2 * 1000].export(audio_temp_file.name, format="wav")
        audio_temp_file.flush()
        audio_segment_file.close()

        subtitle_temp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".srt")

        try:
            # create Task object
            config_string = u"task_language=spa|is_text_type=plain|os_task_file_format=srt"
            task = Task(config_string=config_string)
            task.audio_file_path_absolute = audio_temp_file.name
            task.text_file_path_absolute = text_temp_file.name
            task.sync_map_file_path_absolute = subtitle_temp_file.name

            # process Task
            ExecuteTask(task).execute()

            # output sync map to file
            if task.output_sync_map_file() is None:
                alignment_failed = True
        except (AudioFileUnsupportedFormatError, ExecuteTaskInputError, ExecuteTaskExecutionError) as e:
            alignment_failed = True

        if not alignment_failed:
            with open(subtitle_temp_file.name) as subtitle_srt_file:
                subtitle_contents = subtitle_srt_file.read()

            audio_subs += [srt.Subtitle(index=audio_sub.index + len(audio_subs),
                                        start=audio_sub.start + timedelta(seconds=t1),
                                        end=audio_sub.end + timedelta(seconds=t1),
                                        proprietary=audio_sub.proprietary,
                                        content=audio_sub.content) for audio_sub in
                           list(srt.parse(subtitle_contents))]

        text_temp_file.close()
        audio_temp_file.close()
        subtitle_temp_file.close()

    if len(audio_subs) == 0:
        return [], [], [basename], []
    else:
        # Write whole composed subtitles list into a single file
        with open(u"{0}/{1}.wav.srt".format(OUTPUT_DIR, basename), "wt") as subtitle_srt_file:
            subtitle_contents = srt.compose(audio_subs)
            subtitle_srt_file.write(subtitle_contents)

        return [], [], [], [basename]


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

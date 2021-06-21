# Automatic Speech Recognition of Colombian Dialects

This repository contains code and scripts to train Mozilla's DeepSpeech ASR models using three different datasets of
Latin American Spanish:

- The first one is a 20 hours dataset of CrowdSourced Latin American Spanish [1] that contains six different dialectal
variations, namely Argentinean, Chilean, Colombian, Peruvian, Puerto Rican and Venezuelan.
- The second one is a 920 hours dataset of Colombian Spanish with multiple dialectal variations ranging from Caribbean
to Andean dialects. It is the result of a set of interviews carried out by the Colombia's "Commission for the
Clarification of Truth, Coexistence and Non-repetition" [2] between 2018 and 2020 to victims of the Colombian armed
conflict.
- The third one is a XXX hours dataset of Latin American Spanish result of using a few splits from the Mozilla Common
Voice Spanish dataset [3].

## Requirements
- Python >= 3.6
- DeepSpeech GPU Training 0.8.0
- Google Cloud Speech Client Library
- KenLM

## Installation

To install the requirements execute the following command inside a Python environment with DeepSpeech 0.8.0 training
library [4] and the Google Cloud Speech Client library for Python [5] installed:

```bash
$ pip3 install -r requirements.txt
```

In addition, to build your own language model [6] you need a fully functioning installation of KenLM [7].

## Content

We provide several scripts necessary for preparing the datasets and training and testing the models. The code is
organized in several folders as follows:

- The `utils` folder contains all scripts used to create the dataset of Colombian Dialects.
- The `importers` folder contains a few scripts to import the above aforementioned datasets into DeepSpeech format.
- The `scripts` folder contains a set of Bash scripts used to automate the process of training the ASR models using the
above imported datasets.

## Preparing the dataset

![workflow_overview](/uploads/29a585c3a3702cdb2d6dec541e4a5871/workflow_overview.png)

It consists of 5 pipeline stages as shown in the diagram above: clean intros, clean tags, align, split and validate.
There is a preliminary stage that consist of copying the data from a remote server to the local computer where they will
be further processed. Since the list of files available changes with every ETL execution, here we provide as well the
list of filenames that were imported at the time of dataset creation. Beware that with a few adjustments to newly
imported data not in the provided list the current dataset of Colombian Dialects can be extended.

To copy the files from a remote server through SSH we provide the `utils/data_copy.py` script which reads imported audio
records with a transcript located in a MongoDB database and copies them through SSH using a safe RSA key to authenticate
against the server. This scripts performs file conversion as well since the original audios and transcripts vary in
format, the output format is `.wav` and `.txt` correspondingly. The script can be run as follows:

```bash
usage: data_copy.py [-h] --src_path SRC_PATH --root_path ROOT_PATH --loc_path
                    LOC_PATH --mongo_host MONGO_HOST --mongo_user MONGO_USER
                    --mongo_pass MONGO_PASS --mongo_db MONGO_DB --ssh_host
                    SSH_HOST --ssh_user SSH_USER --ssh_key_file SSH_KEY_FILE
                    [--ssh_key_pass SSH_KEY_PASS] [--audios_only]
                    [--resources_list RESOURCES_LIST [RESOURCES_LIST ...]]
                    [--num_workers NUM_WORKERS]

File synchronization through SSH

optional arguments:
  -h, --help            show this help message and exit
  --src_path SRC_PATH   Path at the source filesystem where files will be read
                        from
  --root_path ROOT_PATH
                        Root path of the file paths stored in MongoDB
  --loc_path LOC_PATH   Path at the local filesystem where files will be
                        copied
  --mongo_host MONGO_HOST
                        MongoDB host
  --mongo_user MONGO_USER
                        MongoDB username
  --mongo_pass MONGO_PASS
                        MongoDB password
  --mongo_db MONGO_DB   MongoDB database
  --ssh_host SSH_HOST   SSH host
  --ssh_user SSH_USER   SSH username
  --ssh_key_file SSH_KEY_FILE
                        Path to SSH key file
  --ssh_key_pass SSH_KEY_PASS
                        SSH key password
  --audios_only         Flag to indicate copy audios only
  --resources_list RESOURCES_LIST [RESOURCES_LIST ...]
                        List of resources to copy
  --num_workers NUM_WORKERS
                        Number of workers
```

To speed up the copying process this script implements a thread based parallel processing strategy which allows to speed
up the copying process, the number of parallel workers can be specified with the CLI argument `num_workers`.

In the following example we assume the files were copied to a destination path in the local filesystem called
`$HOME/data/asr-co`.

Beware that the files imported can be different than the files imported at the time of creation of this dataset, you are
encouraged to validate it against the list of filenames we provide in `records.txt`.

### 1. Clean Introductions

The first stage is to clean transcriptions from introductions which are blocks of text that do not correspond to the
transcription itself but are rather metadata that is placed at the top of the transcriptions. Those transcriptions that
weren't cleaned, i.e. those without an introduction, are kept since they're easier to handle on alignment phase. The
script can be run by simply specifying the input and output directories:

```bash
$ python3 utils/data_clean_intros.py --in_dir $HOME/data/asr-co/ --out_dir $HOME/data/asr-co-intro-clean/
```

### 2. Clean Tags

The transcriptions have some metadata in the form of actor tags which identify the different speakers involved and
content tags which provide information about the transcription itself at given instants. This tags although informative
are not part of the transcription and thus must be removed to allow a correct alignment with the corresponding audio. To
this end we provide a script which to clean transcriptions from content and actor tags and segment result by blocks
derived from partial timestamps:

```bash
$ python3 utils/data_clean_tags.py --in_dir $HOME/data/asr-co-intro-clean/ --out_dir $HOME/data/asr-co-tag-clean/
```

The segmentation by blocks is a key step to allow a better alignment since it is easier for a forced-alignment algorithm
to align 15 minutes of audio than 2 hours. Such blocks are derived from timestamp hints included in the content tags and
depend entirely on the quality of the transcriptions themselves.

### 3. Align

Given a set of block segmented clean transcriptions and the corresponding audios, they are aligned using a DTW
forced-alignment algorithm. DTW is a time series alignment algorithm, which aims at aligning two sequences of feature
vectors by warping the time axis iteratively until an optimal match between the two sequences is found. Here it is used
the Aeneas Python/C library [8] where the audio is aligned against a spoken version of the probable transcription which
is generated using a Text-to-Speech engine. The script can be run by simply specifying the transcriptions, audio and
output directories:

```bash
$ python3 utils/data_align.py --trans_dir $HOME/data/asr-co-tag-clean/ --audio_dir $HOME/data/asr-co/ --out_dir $HOME/data/asr-co-aligned/
```

### 4. Split

The result of the alignment from the previous stage produces a set of subtitle files in SubRip (srt) format which
establish a time interval segmentation. In this stage those subtitle files are read and the audio is split accordingly
at the utterance level. The script can be run simply by specifying the subtitles directory (output directory from
previous stage), the audio and output directories:

```bash
$ python3 utils/data_split.py --subs_dir $HOME/data/asr-co-aligned/ --audio_dir $HOME/data/asr-co/ --out_dir $HOME/data/asr-co-segments/
```

### 5. Validate

Finally since the output of the forced alignment might be wrong even though it was done at block level using timestamp
hints from content tags, it is necessary to validate the audio segments with their corresponding transcriptions. The
split result is stored in a TSV manifest file which points at the audio segment path and the corresponding
transcription. To validate the alignments we follow the same approach of Pansori [9] where it is used a cloud-based ASR,
in particular we use the Google Cloud Speech-to-Text API since it provides the highest quality ASR services. In order to
run this script it is necessary to have a valid Google Cloud account with Speech-to-Text product enabled and set the
corresponding credentials by downloading a service account JSON [10] and setting an environment variable like this:

```bash
$ export GOOGLE_APPLICATION_CREDENTIALS="$HOME/Downloads/SIM_ASR-CO-e011d1108489.json"
```

The script can be run by setting the directory where the directory where splitting output is located, the path
to the `validate_locale_spa.py` source file and the path to the spanish alphabet used to filter out transcriptions with
non-spanish alphabet characters:

```bash
$ python -u utils/data_validate.py --data_dir $HOME/data/asr-co-segments/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet $HOME/data/asr-co-segments/alphabet.txt --normalize
```

This produces a TSV manifest `output_validate.tsv` with filtered transcriptions with a similarity score of 0.7 or above.

## Importing the datasets

Finally to import the newly created dataset into DeepSpeech manifest format to allow data ingestion, it was
created the script `importers/import_asr-co.py` which draw inspiration from the importer scripts for the Common Voice
and M-AILABS datasets. The script can be run similarly to the validate script by specifying the directory where
splitting output is located, the path to the `validate_locale_spa.py` source file and the path to the spanish alphabet
used to filter out transcriptions with non spanish alphabet characters:

```bash
$ python3 importers/import_asr-co.py --data_dir $HOME/data/asr-co-segments/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet $HOME/data/asr-co-segments/alphabet.txt --normalize
```

This produces three CSV files `output_train.csv`, `output_dev.csv`, and `output_test.csv` corresponding to the training,
validation and test splits of the dataset.

There are other two data importers provided, `importers/import_es-la.py` to import the data from the CrowdSourced Latin
American Spanish dataset and `importers/import_cv2.py` which is used to import the Latin American split from the Mozilla
Common Voice Spanish dataset. The latest one is a modified copy from the importer provided by the Mozilla DeepSpeech
implementation [11] with the addition that imports only data associated to Latin American accents (Mexicano,
Andino-Pacífico, Rioplatense, Caribe, Chileno, America central) and keeps tilde words.

## Preparing manually validated dataset

Manually validated transcripts are subtitle files in SubRip (srt) format locate in a shared Windows directory. The
process of importing this transcripts into a valid dataset starts with copying those subtitle files into a local
directory:

```bash
$ mkdir -p $HOME/data/entregadas_alineadas/
$ mkdir -p $HOME/data/asr-co-manual/
$ sudo mount -t cifs //192.168.1.8/alineacion_audios/entregadas_alineadas $HOME/data/entregadas_alineadas/ -o username=<cev.user>,uid=$(id -u),gid=$(id -g)
$ cp $HOME/data/entregadas_alineadas/*.srt $HOME/data/asr-co-manual/
```

The next step is to copy from the remote file server the audios related with those interviews. For that it is used the
`utils/data_copy.py` script with the parameters `--audios_only` and `--resources_list` to specify that only audio files
must be copied and the specific interviews that must be copied. The list of resources is whitespace separated list of
the resource identifiers of the interviews, e.g. 001-VI-00003 001-VI-00009. These two parameters can be used only
combined, used separately has no effect. Be sure that the `--loc_path` argument points to the
`$HOME/data/asr-co-manual/` path.

The above step will copy all related audio files for each of the interviews, remind that some of the are split in
multiple parts and sometimes are even repeated in different formats so they will be appended a _0, _1 and so on suffix.
This has to be solved since only one audio file is expected to be associated with each subtitle file (his is always
the case for the manually validated interviews since they are the result of a former copy process which warranties
this association). To solve for this it suffices to rename the associated first part audio files and remove the
remaining ones:

```bash
$ cd $HOME/data/asr-co-manual/
$ ls *_0.wav | cut -d"_" -f1 | xargs -I {} mv {}_0.wav {}.wav
$ rm -f *_*.wav
```

At this point there must be an equal number of subtitle files (.srt) and audio files (.wav) in the
`$HOME/data/asr-co-manual/` directory. If not be sure that all necessary interviews were included when running the
`utils/data_copy.py` script and if necessary run it again with only the missing interviews.

Once all subtitle and audio files are in place the next step is to split the audios at the corresponding subtitle
timestamps. This can be done using the formerly explained `utils/data_split.py` script:

```bash
$ python utils/data_split.py --subs_dir $HOME/data/asr-co-manual/ --audio_dir $HOME/data/asr-co-manual/ --out_dir $HOME/data/asr-co-manual/
```

This will split the audios in save them in `wavs` directory and create the manifest file `output.tsv` in TSV format. At
this point please consider normalizing the resulting audio segments using the `utils/data_exile_normalize_audio.py`:

```bash
$ mkdir -p $HOME/data/asr-co-manual/wavs_normalized/
$ python3 utils/data_exile_normalize_audio.py --audio_dir $HOME/data/asr-co-manual/wavs/ --out_dir $HOME/data/asr-co-manual/wavs_normalized/
```

If you use the normalized versions of the audio segments remember to rename the directories so that the paths in the
TSV manifest file are correct:

```bash
$ mv $HOME/data/asr-co-manual/wavs/ $HOME/data/asr-co-manual/wavs_raw/
$ mv $HOME/data/asr-co-manual/wavs_normalized/ $HOME/data/asr-co-manual/wavs/
```

The last step is to execute the importer for the folder containing the audio segments and the manifest file:

```bash
$ python importers/import_asr-co.py --data_dir $HOME/data/asr-co-manual/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet $HOME/data/asr-co-segments/alphabet.txt --normalize
```

This will create the files `output_train.csv`, `output_dev.csv` and `output_test.csv` which can be fed into to the
DeepSpeech model training script.

NB: Be aware that this import process does not run on previous importations and thus you have to run it all again every
time you execute it.

## Training your own model

To train the ASR models we rely on the Mozilla's implementation of DeepSpeech. We provide several Bash scripts located
in the `scripts` directory, they simplify the task of scheduling models training. After importing the datasets as
explained earlier it is only necessary to adjust the environment variables `data_dir`, `ckpt_dir` and `summ_dir` so that
they point to the directories where audio segments data is located, checkpoints will be stored and training summaries
will be stored. An example of how to run the trainer script for the M-AILABS dataset is as follows, first import the
dataset:

```bash
$ python3 importers/import_cv2.py $HOME/data/m-ailabs/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet $HOME/data/m-ailabs/alphabet.txt --normalize
```

Beware that before this you would have to create the `$HOME/data/m-ailabs/` directory and include the `alphabet.txt` that we
provide. Finally to run the trainer script in background and save the stdout and stderr output to a log file:

```bash
$ ./scripts/train_es_ES.sh &> $HOME/logs/train_es_ES.log &
```

## Export models

The above trained model can be exported to PB format so that it can be used freely at inference time. This can be done
with the `DeepSpeech.py` script from your local DeepSpeech folder by specifying the checkpoint to load and the export
directory and model authorship details. The command below shows the necessary parameters:

```bash
$ python DeepSpeech.py --alphabet_config_path $HOME/models/cclmtv_es/alphabet.txt \
                       --checkpoint_dir $HOME/checkpoints/ds-transfer-es_CO/ \
                       --load_evaluate "best" \
                       --n_hidden 2048 \
                       --export_dir $HOME/models/ds-transfer-es_CO/ \
                       --remove_export True \
                       --export_file_name "output_graph" \
                       --export_author_id "afperezm" \
                       --export_model_name "model" \
                       --export_model_version "0.0.1" \
                       --export_contact_info "andres.perez@mail.polimi.it" \
                       --export_license "Apache-2.0" \
                       --export_language "es_CO" \
                       --export_min_ds_version "v0.8.0" \
                       --export_max_ds_version "v0.8.2" \
                       --export_description "Entrevistas a victimas del conflicto armado"
```

The `output_graph.pb` model file generated with the above command will be loaded in memory to be dealt with when running
inference. This results in extra loading time and memory consumption. To avoid this is one can directly read data from
the disk by producing a mmap-able model.

TensorFlow has a tooling to achieve this called `convert_graphdef_memmapped_format` which can be downloaded using the
`util/taskcluster.py` script to download:

```bash
$ python util/taskcluster.py --source tensorflow \
                             --artifact convert_graphdef_memmapped_format \
                             --branch r1.15 \
                             --target .
```

This will download the `convert_graphdef_memmapped_format` tool to the folder where the `taskcluster.py` script was
executed. Finally producing a mmap-able model is as simple as:

```bash
$ convert_graphdef_memmapped_format --in_graph=$HOME/models/ds-transfer-es_CO/output_graph.pb \
                                    --out_graph=$HOME/models/ds-transfer-es_CO/output_graph.pbmm
```

## Long audio transcription

The produced model can be used to run DeepSpeech inference on a sample WAV file as explained in [DeepSpeech's
documentation](https://deepspeech.readthedocs.io/en/v0.8.2/) however this performs well only for short length audios. In
order to run this for longer audios one has to use the `transcribe.py` script included in the DeepSpeech installation
directory. It suffices to specify the source WAV file and destination JSON where the timestamped transcription will be
written, as well as the alphabet, model checkpoint and scorer to use:

```bash
$ python transcribe.py --src $HOME/data/asr-co-manual/audios/001-VI-00003.wav \
                       --dst $HOME/data/asr-co-manual/audios/001-VI-00003.json \
                       --force --alphabet_config_path $HOME/models/cclmtv_es/alphabet.txt \
                       --load_checkpoint_dir $HOME/checkpoints/cclmtv_es/ \
                       --load_evaluate "best" \
                       --scorer_path $HOME/models/cclmtv_es/kenlm_es.scorer \
                       --n_hidden 2048 \
                       --load_cudnn
```

## Using pre-trained models

We provide the three trained models in `.pbmm` format as well as the language model generated from the full dataset and
not only the validated ones. You can use these as explained in [12].

# References

[1] https://research.google/pubs/pub49150/

[2] https://comisiondelaverdad.co/

[3] https://commonvoice.mozilla.org/en/datasets

[4] https://deepspeech.readthedocs.io/en/r0.8/TRAINING.html

[5] https://cloud.google.com/speech-to-text/docs/libraries

[6] https://deepspeech.readthedocs.io/en/r0.8/Scorer.html

[7] https://github.com/kpu/kenlm/blob/master/BUILDING

[8] https://github.com/readbeyond/aeneas

[9] https://github.com/yc9701/pansori

[10] https://cloud.google.com/docs/authentication/production#best_practices

[11] https://github.com/mozilla/DeepSpeech

[12] https://deepspeech.readthedocs.io/en/r0.8/USING.html

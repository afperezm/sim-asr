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

- The `utils` folder contains all scripts used to create the ASR-CO dataset of Colombian Dialects.
- The `importers` folder contains two scripts to import into DeepSpeech format the CrowdSourced Spanish Latin-America
dataset [1] and the validated data of ASR-CO dataset of Colombian Dialects.
- The `scripts` folder contains a set of Bash scripts used to automate the process of training the ASR models using the
above imported datasets.

## Preparing the dataset

![workflow_overview](/uploads/29a585c3a3702cdb2d6dec541e4a5871/workflow_overview.png)

It consists of 5 pipeline stages as shown in the diagram above: clean intros, clean tags, align, split and validate.

### 1. Clean Introductions

Clean transcriptions from introductions and keep only the ones that weren't cleaned since they're easier to handle 
on alignment phase:

```bash
$ python3 utils/data_clean_intros.py --in_dir ~/data/asr-co/ --out_dir ~/data/asr-co-intro-clean/
```

### 2. Clean Tags

Clean transcriptions from content and actor tags and segment result by blocks derived from partial timestamps:

```bash
$ python3 utils/data_clean_tags.py --in_dir ~/data/asr-co-intro-clean/ --out_dir ~/data/asr-co-tag-clean/
```

### 3. Align

Align clean blocks of transcriptions with their corresponding audio using a DTW a forced-alignment algorithm:

```bash
$ python3 utils/data_align.py --trans_dir ~/data/asr-co-tag-clean/ --audio_dir ~/data/asr-co/ --out_dir ~/data/asr-co-aligned/
```

### 4. Split

Split resulting alignment at the utterance level:

```bash
$ python3 utils/data_split.py --subs_dir ~/data/asr-co-aligned/ --audio_dir ~/data/asr-co/ --out_dir ~/data/asr-co-segments/
```

### 5. Validate

## Importing the datasets

Import data into DeepSpeech manifest format to allow data ingestion:

```bash
$ python3 importers/import_asr-co.py --data_dir ~/data/asr-co-segments/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet ~/data/asr-co-segments/alphabet.txt --normalize
```

## Training your own model

## Using pre-trained models

# References

[1] https://research.google/pubs/pub49150/

[2] https://comisiondelaverdad.co/

[3] https://commonvoice.mozilla.org/en/datasets

[4] https://deepspeech.readthedocs.io/en/r0.8/TRAINING.html

[5] https://cloud.google.com/speech-to-text/docs/libraries

[6] https://deepspeech.readthedocs.io/en/r0.8/Scorer.html

[7] https://github.com/kpu/kenlm/blob/master/BUILDING

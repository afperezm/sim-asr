# Automatic Speech Recognition of Colombian Dialects

This repository contains code and scripts to train Mozilla's DeepSpeech ASR models using two different datasets of
Latin American Spanish:

- The first one is a 20 hours dataset of CrowdSourced Latin American Spanish [1] that contains six different dialectal
variations, namely Argentinean, Chilean, Colombian, Peruvian, Puerto Rican and Venezuelan.
- The second one is a 920 hours dataset of Colombian Spanish with multiple dialectal variations ranging from Caribbean
to Andean dialects. It is the result of a set of interviews carried out by the Colombia's "Commission for the
Clarification of Truth, Coexistence and Non-repetition" [2] between 2018 and 2020 to victims of the Colombian armed
conflict.

## Requirements
- Python >= 3.6
- DeepSpeech 0.8.0
- KenLM

## Installation

To install the requirements execute the following command:

```bash
pip3 install -r requirements.txt 
```

## Content

## Usage

Clean transcriptions from introductions and keep only the ones that weren't cleaned since they're easier to handle 
on alignment phase:

```
python3 utils/data_clean_intros.py --in_dir ~/data/asr-co/ --out_dir ~/data/asr-co-intro-clean/
```

Clean transcriptions from content and actor tags and segment result by blocks derived from partial timestamps:

```
python3 utils/data_clean_tags.py --in_dir ~/data/asr-co-intro-clean/ --out_dir ~/data/asr-co-tag-clean/
```

Align clean blocks of transcriptions with their corresponding audio using a DTW a forced-alignment algorithm:

```
python3 utils/data_align.py --trans_dir ~/data/asr-co-tag-clean/ --audio_dir ~/data/asr-co/ --out_dir ~/data/asr-co-aligned/
```

Split resulting alignment at the utterance level:

```
python3 utils/data_split.py --subs_dir ~/data/asr-co-aligned/ --audio_dir ~/data/asr-co/ --out_dir ~/data/asr-co-segments/
```

Import data into DeepSpeech manifest format to allow data ingestion:

```
python3 importers/import_asr-co.py --data_dir ~/data/asr-co-segments/ --validate_label_locale utils/validate_locale_spa.py --filter_alphabet ~/data/asr-co-segments/alphabet.txt --normalize
```

# References

[1] https://research.google/pubs/pub49150/

[2] https://comisiondelaverdad.co/

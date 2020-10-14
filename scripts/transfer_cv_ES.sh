#!/bin/bash

data_dir="/home/andresf/data/cv_ES"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar \
       --drop_source_layers 1 \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/es/clips/train.csv" \
       --train_batch_size 80 \
       --train_files "${data_dir}/es/clips/dev.csv" \
       --dev_batch_size 80 \
       --save_checkpoint_dir "${ckpt_dir}/ds-transfer-eng2spa-cv_ES/" \
       --load_checkpoint_dir "${ckpt_dir}/deepspeech-0.8.0-checkpoint/" \
       --summary_dir "${summ_dir}/ds-transfer-eng2spa-cv_ES/" \
       --scorer_path '' \
       --learning_rate 0.0001 \
       --n_hidden 2048 \
       --epochs 100 \
       --dropout_rate 0.22 \
       --train_cudnn

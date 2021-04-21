#!/bin/bash

data_dir="/home/andresf/data/cv_ES"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar --noearly_stop \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/es/clips/train.csv" \
       --train_batch_size 64 \
       --dev_files "${data_dir}/es/clips/dev.csv" \
       --dev_batch_size 64 \
       --checkpoint_dir "${ckpt_dir}/ds-train-cv_ES/" \
       --summary_dir "${summ_dir}/ds-train-cv_ES/" \
       --learning_rate 0.0001 \
       --dropout_rate 0.4 \
       --n_hidden 2048 \
       --epochs 100 \
       --train_cudnn

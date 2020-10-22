#!/bin/bash

data_dir="/home/andresf/data/es_LA"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar --noearly_stop \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/es_LA_train.csv" \
       --train_batch_size 64 \
       --dev_files "${data_dir}/es_LA_dev.csv" \
       --dev_batch_size 64 \
       --checkpoint_dir "${ckpt_dir}/ds-train-eng2spa-es_LA/" \
       --summary_dir "${summ_dir}/ds-train-eng2spa-es_LA/" \
       --learning_rate 0.0001 \
       --dropout_rate 0.4 \
       --n_hidden 2048 \
       --epochs 100 \
       --train_cudnn

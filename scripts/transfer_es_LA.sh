#!/bin/bash

data_dir="/home/andresf/data/es_LA"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar --noearly_stop \
       --drop_source_layers 1 \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/es_LA_train.csv" \
       --train_batch_size 80 \
       --dev_files "${data_dir}/es_LA_dev.csv" \
       --dev_batch_size 80 \
       --save_checkpoint_dir "${ckpt_dir}/ds-transfer-eng2spa/" \
       --load_checkpoint_dir "${ckpt_dir}/deepspeech-0.8.0-checkpoint/" \
       --summary_dir "${summ_dir}/ds-transfer-eng2spa/" \
       --scorer_path '' \
       --learning_rate 0.0001 \
       --n_hidden 2048 \
       --epochs 100 \
       --train_cudnn

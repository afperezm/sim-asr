#!/bin/bash

data_dir="/home/andresf/data/asr-co-segments"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar --noearly_stop \
       --drop_source_layers 1 \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/output_train_shuffled.csv" \
       --train_batch_size 128 \
       --dev_files "${data_dir}/output_dev_shuffled.csv" \
       --dev_batch_size 128 \
       --save_checkpoint_dir "${ckpt_dir}/ds-transfer-eng2spa-es_CO_lr1e-3/" \
       --load_checkpoint_dir "${ckpt_dir}/deepspeech-0.8.0-checkpoint/" \
       --summary_dir "${summ_dir}/ds-transfer-eng2spa-es_CO_lr1e-3/" \
       --scorer_path '' \
       --dropout_rate 0.05 \
       --learning_rate 0.001 \
       --n_hidden 2048 \
       --epochs 100 \
       --train_cudnn


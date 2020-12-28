#!/bin/bash

data_dir="/home/andresf/data/asr-co-segments"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar \
       --alphabet_config_path "${data_dir}/alphabet.txt" \
       --train_files "${data_dir}/output_train.csv" \
       --train_batch_size 32 \
       --dev_files "${data_dir}/output_dev.csv" \
       --dev_batch_size 32 \
       --checkpoint_dir "${ckpt_dir}/ds-train-es_CO/" \
       --summary_dir "${summ_dir}/ds-train-es_CO/" \
       --scorer_path '' \
       --dropout_rate 0.22 \
       --learning_rate 0.00095 \
       --n_hidden 2048 \
       --epochs 100 \
       --early_stop True \
       --es_epochs 25 \
       --reduce_lr_on_plateau True \
       --plateau_epochs 10 \
       --train_cudnn

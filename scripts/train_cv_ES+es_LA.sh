#!/bin/bash

data_dir="/home/andresf/data"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

#       --save_checkpoint_dir "${ckpt_dir}/ds-transfer-eng2spa-cv_ES+es_LA/" \
#       --load_checkpoint_dir "${ckpt_dir}/deepspeech-0.8.0-checkpoint/" \

python -u DeepSpeech.py --noshow_progressbar \
       --alphabet_config_path "${data_dir}/cv_ES/alphabet.txt" \
       --train_files "${data_dir}/cv_ES/es/clips/train.csv,${data_dir}/es_LA/es_LA_train.csv" \
       --train_batch_size 64 \
       --dev_files "${data_dir}/cv_ES/es/clips/dev.csv,${data_dir}/es_LA/es_LA_dev.csv" \
       --dev_batch_size 64 \
       --checkpoint_dir "${ckpt_dir}/ds-train-cv_ES+es_LA/" \
       --summary_dir "${summ_dir}/ds-train-cv_ES+es_LA/" \
       --scorer_path '' \
       --dropout_rate 0.3 \
       --learning_rate 0.0001 \
       --n_hidden 2048 \
       --epochs 100 \
       --early_stop True \
       --es_epochs 10 \
       --reduce_lr_on_plateau True \
       --plateau_epochs 5 \
       --train_cudnn

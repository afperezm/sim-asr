#!/bin/bash

data_dir="/home/andresf/data/asr-co-segments"
ckpt_dir="/home/andresf/checkpoints"
mdls_dir="/home/andresf/models"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar \
       --alphabet_config_path "${mdls_dir}/cclmtv_es/alphabet.txt" \
       --train_files "${data_dir}/output_train.csv" \
       --train_batch_size 64 \
       --dev_files "${data_dir}/output_dev.csv" \
       --dev_batch_size 64 \
       --save_checkpoint_dir "${ckpt_dir}/ds-transfer-es_CO/" \
       --load_checkpoint_dir "${ckpt_dir}/cclmtv_es/" \
       --summary_dir "${summ_dir}/ds-transfer-es_CO/" \
       --scorer_path '' \
       --dropout_rate 0.25 \
       --learning_rate 0.0001 \
       --n_hidden 2048 \
       --epochs 500 \
       --early_stop True \
       --es_epochs 25 \
       --reduce_lr_on_plateau True \
       --plateau_epochs 10 \
       --train_cudnn

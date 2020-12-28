#!/bin/bash

data_dir="/home/andresf/data"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

python -u DeepSpeech.py --noshow_progressbar \
       --alphabet_config_path "${data_dir}/m-ailabs/alphabet.txt" \
       --train_files "${data_dir}/m-ailabs/es_ES/es_ES_train.csv" \
       --train_batch_size 45 \
       --dev_files "${data_dir}/m-ailabs/es_ES/es_ES_dev.csv" \
       --dev_batch_size 45 \
       --checkpoint_dir "${ckpt_dir}/ds-train-eng2spa-es_ES/" \
       --summary_dir "${summ_dir}/ds-train-eng2spa-es_ES/" \
       --scorer_path '' \
       --dropout_rate 0.22 \
       --learning_rate 0.00095 \
       --n_hidden 2048 \
       --epochs 100 \
       --early_stop True \
       --es_epochs 10 \
       --reduce_lr_on_plateau True \
       --plateau_epochs 5 \
       --train_cudnn

#!/bin/bash

data_dir="/home/andresf/data"
ckpt_dir="/home/andresf/checkpoints"
summ_dir="/home/andresf/summaries"

for DROP in '0.4' '0.5' '0.6'; do
  for LEARN in '0.001' '0.0001' '0.00001'; do
    for BATCH in '32' '64'; do
      for HIDDEN in '2048'; do
        num=`ls "${ckpt_dir}" | grep ds-transfer-eng2spa-exp | wc -l`
        num=$(("$num + 1"))
        python -u DeepSpeech.py --noshow_progressbar --noearly_stop \
               --drop_source_layers 1 \
               --alphabet_config_path "${data_dir}/cv_ES/alphabet.txt" \
               --train_files "${data_dir}/cv_ES/es/clips/train.csv,${data_dir}/es_LA/es_LA_train.csv" \
               --train_batch_size "$BATCH" \
               --dev_files "${data_dir}/cv_ES/es/clips/dev.csv,${data_dir}/es_LA/es_LA_dev.csv" \
               --dev_batch_size "$BATCH" \
               --test_files "${data_dir}/es/clips/test.csv" \
               --test_batch_size "$BATCH" \
               --save_checkpoint_dir "${ckpt_dir}/ds-transfer-eng2spa-exp${num}/" \
               --load_checkpoint_dir "${ckpt_dir}/deepspeech-0.8.0-checkpoint/" \
               --summary_dir "${summ_dir}/ds-transfer-eng2spa-exp${num}/" \
               --scorer_path '' \
               --dropout_rate "$DROP" \
               --learning_rate "$LEARN" \
               --n_hidden "$HIDDEN" \
               --epochs 10 \
               --train_cudnn
      done
    done
  done
done

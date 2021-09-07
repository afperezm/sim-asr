#!/bin/bash

data_dir="/home/andresf/data"
ckpt_dir="/home/andresf/checkpoints"
mdls_dir="/home/andresf/models"

for model_id in 1 2 3 4 5; do

    python -u evaluate.py --noshow_progressbar \
                          --test_files "${data_dir}/asr-co-exilio/output_test.csv,${data_dir}/asr-co-manual/output_test.csv,${data_dir}/asr-co-segments/output_test.csv" \
                          --test_batch_size 64 \
                          --alphabet_config_path "${mdls_dir}/cclmtv_es/alphabet.txt" \
                          --load_checkpoint_dir "${ckpt_dir}/ds-transfer-es_CO_exp${model_id}/" \
                          --load_evaluate "best" \
                          --scorer_path "${mdls_dir}/cclmtv_es/kenlm_es.scorer" \
                          --n_hidden 2048 \
                          --load_cudnn

done

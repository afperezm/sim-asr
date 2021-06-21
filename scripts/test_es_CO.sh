#!/bin/bash

data_dir="/home/andresf/data"
ckpt_dir="/home/andresf/checkpoints"
mdls_dir="/home/andresf/models"

python -u evaluate.py --noshow_progressbar \
                      --test_files "${data_dir}/asr-co-exilio/output_test.csv,${data_dir}/asr-co-manual/output_test.csv,${data_dir}/asr-co-segments/output_test.csv" \
                      --test_batch_size 64 \
                      --alphabet_config_path "${mdls_dir}/cclmtv_es/alphabet.txt" \
                      --load_checkpoint_dir "${ckpt_dir}/cclmtv_es/" \
                      --load_evaluate "best" \
                      --scorer_path "${mdls_dir}/cclmtv_es/kenlm_es.scorer" \
                      --n_hidden 2048 \
                      --load_cudnn

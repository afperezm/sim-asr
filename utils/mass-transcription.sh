source ~/ds-train-venv/bin/activate

echo "----PROCESS BEGINGS---"
date
days="$(date +'%Y%m%d-%H%M')"
result_path=$HOME/audios_test_result
models=(cclmtv_es ds-transfer-es_CO_exp1 ds-transfer-es_CO_exp2 ds-transfer-es_CO_exp3 ds-transfer-es_CO_exp4 ds-transfer-es_CO_exp5)

for x in wav; do
	for i in ~/audios_test/*."${x}"; do
		filename=$(basename "${i%.*}")
   		echo "----------Working on "${filename}" file---------"
		mkdir $result_path/$filename
		for model in ${models[@]}; do
		trans_filename=${result_path}/${filename}/${filename}-${model}.json
		echo ${trans_filename}
		if test -f ${trans_filename};
			then
				echo "Wav already processed"
				doc_name=${result_path}/${filename}/${filename}-${model}.docx
				if test -f ${doc_name};
					then
						echo "Doc already created"
					else
						echo "Creating doc files for "${trans_filename}""
						python3 $HOME/workspace/sim-asr/utils/process_trans.py --input ${trans_filename} --output ${doc_name}
				fi
			else
				echo "Transcription for "${filename}" and model "${model}" starts at "${days}""
				python3 ~/workspace/DeepSpeech/transcribe.py --src ${i} --dst ${result_path}/${filename}/${filename}-${model}.json --force --alphabet_config_path $HOME/models/cclmtv_es/alphabet.txt --load_checkpoint_dir $HOME/checkpoints/${model}/ --load_evaluate "best" --scorer_path $HOME/models/cclmtv_es/kenlm_es.scorer  --n_hidden 2048 --load_cudnn
				echo "Transcription for "${filename}" finished at "${days}""
		fi
		done	
	done
done



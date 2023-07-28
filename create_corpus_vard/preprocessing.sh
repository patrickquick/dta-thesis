#!/bin/bash

# MUST BE RUN INSIDE VARD WORKING FOLDER

raw_corpus="/Users/pfq/Dropbox/DTA/Thesis_Internship/preprocessing_and_text_normalisation/letters.json"
annotations="/Users/pfq/Dropbox/DTA/Thesis_Internship/preprocessing_and_text_normalisation/process_export_keys.csv"
vard_dir="v_corpus_full/"
varded_dir="v_working_dir/"
gs_dir="v_corpus_gs/"
master_dir="master_corpus/"
tagged_dir="annotated_corpus/"
ner_dir="ner_corpus/"

python create_corpus.py --json_file "$raw_corpus" --corpus "$vard_dir"

f_score_weights="0.1 0.5 1.0 1.5 1.9 2.0"
thresholds="0 25 50 75 100"

for f_score_weight in $f_score_weights
do
	for threshold in $thresholds
	do
		echo VARD f-score weight: "$f_score_weight"
		echo VARD threshold: "$threshold"
		java -Xms256M -Xmx512M -jar clui.jar "$varded_dir" "$threshold" "$f_score_weight" "$vard_dir" true "$varded_dir" false
		mkdir "${varded_dir}Tagged/"
		mv "${varded_dir}varded(${threshold}%) - Changes Tagged"/* "${varded_dir}Tagged/"
		rmdir "${varded_dir}varded(${threshold}%) - Changes Tagged"
		rm -r "${varded_dir}varded(${threshold}%) - Changes Unmarked"
		python postprocess.py --corpus_varded "$varded_dir" --processed_corpus "$vard_dir" --fscore "$f_score_weight" --threshold "$threshold"
	done
done

python gs.py --fscores "$f_score_weights" --thresholds "$thresholds" --processed_corpus "$vard_dir" --gs_corpus "$gs_dir"
python annotation_reconciler.py --gs_corpus "$gs_dir" --master_corpus "$master_dir" --annotations "$annotations"
python comp_ner_corpus.py --master_corpus "$master_dir" --tagged_corpus "$tagged_dir"
python xml_csv.py --tagged_corpus "$tagged_dir" --ner_corpus "$ner_dir"

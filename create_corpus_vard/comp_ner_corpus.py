import argparse
import os
import shutil
import pandas as pd

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script to copy only the letters with annotations to a new directotry

p = argparse.ArgumentParser()
p.add_argument('--master_corpus', type=str, help='Input directory of fully pre-processed letters')
p.add_argument('--tagged_corpus', type=str, help='Output directory to copy annotated letters only')
args = p.parse_args()

master_corpus = os.path.realpath(args.master_corpus)
tagged_corpus = os.path.realpath(args.tagged_corpus)
isExist = os.path.exists(tagged_corpus)
if not isExist:
    os.mkdir(tagged_corpus)
else:
	print("The directory already exists. You are overwriting files.")

targets = ['NAME', 'LOCATION', 'NATION', 'MARKET', 'DATE', 'TIME', 'PRICE', 'GOD']
for xml_file in os.listdir(master_corpus):
    if xml_file.endswith(".xml"):
        input_path = os.path.join(master_corpus, xml_file)
        shared_attrs = pd.read_xml(input_path, xpath="./*/*").columns.intersection(targets)
        if shared_attrs.size >= 1:
            output_file = os.path.join(tagged_corpus, xml_file)
            shutil.copy(input_path, output_file)
            print(f'Copying letter {xml_file} to annotated letters directory')

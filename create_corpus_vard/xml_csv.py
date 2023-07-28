import pandas as pd
import os
from natsort import natsort_key
import argparse

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script to create a csv file of the annotated corpus for each VARD run, including an identical csv with the original data

p = argparse.ArgumentParser()
p.add_argument('--tagged_corpus', type=str, help='Input directory of annotated letters in xml')
p.add_argument('--ner_corpus', type=str, help='Output directory for csv files')
args = p.parse_args()

tagged_corpus = os.path.realpath(args.tagged_corpus)
ner_corpus = os.path.realpath(args.ner_corpus)
isExist = os.path.exists(ner_corpus)
if not isExist:
    os.mkdir(ner_corpus)
else:
	print("The directory already exists. You are overwriting files.")
xml_list = os.listdir(tagged_corpus)

def tag_writer(tag_dict, df):
    for k,v in tag_dict.items():        
        if f'{k}' in df.columns:
            for f in df[f'{k}']:
                if f == 1 or 2:
                    v.append(f)
        else:
            for f in range(0,len(df)):
                v.append('O')

unic = open(os.path.join(tagged_corpus, xml_list[0]),"r",encoding="utf-8")
df_unic = pd.read_xml(unic, xpath=".//VARD_unicity")
unicity_list = df_unic.columns
targets = ['NAME', 'LOCATION', 'NATION', 'MARKET', 'DATE', 'TIME', 'PRICE', 'GOD']
word_id = []
word = []
df_values = [word_id, word]
df_index = ['word_id', 'word']
tag_dict = {k:[] for k in targets}
outname = 'raw_ner_corpus.csv'
fullname = os.path.join(ner_corpus, outname)

# NER corpus with original data
for file in xml_list:
    xml_file = open(os.path.join(tagged_corpus, file),"r",encoding="utf-8")
    df = pd.read_xml(xml_file, xpath=".//word")
    df = df.fillna(value={'word':''}).fillna('O').reset_index(drop=True)
    # NOTE: nan word values are left as nan, all other nan values filled with 'O' as per BIO

    for f in df['word_id']:
        word_id.append(f)
    for f in df['word']:
        word.append(f)
    tag_writer(tag_dict, df)

for k,v in tag_dict.items():
    df_values.append(v)
    df_index.append(k)

print(f'Constructing NER corpus with original data')

# create df of corpus and tags
df = pd.DataFrame(df_values, index=df_index).transpose().sort_values(by="word_id", key=natsort_key, ignore_index=False)

# create single column with annotations
df['labels'] = df[targets].apply(lambda row: next((col + '-B' for col in targets if row[col] == 'B'),
                                                  next((col + '-I' for col in targets if row[col] == 'I'), 'O')), axis=1)

# save to csv
df.to_csv(fullname, index=False, encoding='utf-8')

# NER corpus with VARD processed data
for i in unicity_list:
    word_id = []
    word = []
    df_values = [word_id, word]
    df_index = ['word_id', 'word']
    tag_dict = {k:[] for k in targets}
    outname = f'{i}.csv'
    fullname = os.path.join(ner_corpus, outname)

    for file in xml_list:
        xml_file = open(os.path.join(tagged_corpus, file),"r",encoding="utf-8")
        df = pd.read_xml(xml_file, xpath=".//word")
        df = df.fillna(value={'word':''}).fillna('O').reset_index(drop=True)
        # NOTE: nan word values are left as nan, all other nan values filled with 'O' as per BIO

        for f in df['word_id']:
            word_id.append(f)
        if i in df.columns:
            for f,g in zip(df[f'{i}'], df['word']):
                if f == 'O':
                    word.append(g)
                else:
                    word.append(f)
        else:
            for f in df['word']:
                word.append(f)
        tag_writer(tag_dict, df)

    for k,v in tag_dict.items():
        df_values.append(v)
        df_index.append(k)
    
    print(f'Constructing NER corpus for {i}')

    # create df of corpus and tags
    df = pd.DataFrame(df_values, index=df_index).transpose().sort_values(by="word_id", key=natsort_key, ignore_index=False)

    # create single column with annotations
    df['labels'] = df[targets].apply(lambda row: next((col + '-B' for col in targets if row[col] == 'B'),
                                                      next((col + '-I' for col in targets if row[col] == 'I'), 'O')), axis=1)
    
    # save to csv
    df.to_csv(fullname, index=False, encoding='utf-8')
    
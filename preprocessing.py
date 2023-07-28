import os
import pandas as pd
import string
import spacy

# NER subcorpus directory, one csv file per VARD run + original
ner_corpus_dir = "/Users/pfq/Dropbox/DTA/Thesis_Internship/thesis/VARD2.5.4/ner_corpus"

# define function to generate POS tags with spaCy at the token level
# a tag was selected that has least chance of interfering with other features constructed in the CRF models
# for example 'XXX' or 'OTHER' would mistakenly correlate with features that take account of
# i. roman numerals and ii. instances of other tokens like 'her' or 'otwell' once sliced

nlp = spacy.load('en_core_web_sm')

def get_pos(word):
    doc = nlp(word)
    return doc[0].pos_ if doc else 'UNKN'

# preprocess the datasets and save them to csv

# define columns with entity labelling
cols = ['NAME', 'LOCATION', 'NATION', 'MARKET', 'DATE', 'TIME', 'PRICE', 'GOD']

for file in os.listdir(ner_corpus_dir):
    print(file)

    # block for handling the original corpus
    if file.startswith('raw'):
        filepath = os.path.join(ner_corpus_dir, file)
        df = pd.read_csv(filepath, sep=',')
        
        # dropna() will drop empty values in word, which are a result of line breaks in the letters
        df = df.dropna().reset_index(drop=True)

        # convert extraneous sequences of '.' in tokens to '.'
        df['word'] = df['word'].str.replace(r'\.{1,}', '.', regex=True)

        # further tokenize the text, splitting trailing punctuation into new tokens and updating individual entity labels
        # code left in a verbose form for readability
        new_rows = []
        for index, row in df.iterrows():
            row_copy_1 = df.loc[index].copy()
            row_copy_2 = df.loc[index].copy()
            word = row['word'] # 'London,'
            if len(word) > 1: # ignore single character strings 
                
                # block to handle all but the last token
                if index+1 < len(df):
                    if word[-1] in string.punctuation:
                        word_1 = word[:-1] # 'London'
                        word_2 = word[-1] # ','

                        for column in cols:
                            next_label = df.at[index+1, column]
                            if next_label == 'I':
                                row_copy_2[column] = 'I'
                            else:
                                row_copy_2[column] = 'O'

                        row_copy_1['new_word'] = word_1
                        row_copy_2['new_word'] = word_2
                        row_copy_2['word_id'] += f'.{1}'
                        row_copy_2['word'] = ''
                        new_rows.append(row_copy_1)
                        new_rows.append(row_copy_2)
                    else:
                        row['new_word'] = word
                        new_rows.append(row)
                
                # block to handle the last token
                else:
                    if word[-1] in string.punctuation:
                        word_1 = word[:-1] # 'London'
                        word_2 = word[-1] # ','

                        for column in cols:
                            row_copy_2[column] = 'O'

                        row_copy_1['new_word'] = word_1
                        row_copy_2['new_word'] = word_2
                        row_copy_2['word_id'] += f'.{1}'
                        row_copy_2['word'] = ''
                        new_rows.append(row_copy_1)
                        new_rows.append(row_copy_2)
                    else:
                        row['new_word'] = word
                        new_rows.append(row)
            else:
                row['new_word'] = word
                new_rows.append(row)

        df = pd.concat(new_rows, axis=1).transpose().reset_index(drop=True)

        # generate POS tags with spaCy using tokenized words
        df['POS'] = df['new_word'].apply(get_pos)

        # rename columns: 'word' is the column with which we will work
        df.rename(columns={'new_word': 'word', 'word': 'word_original'}, inplace=True)

    # block for handling the VARDed subcorpora
    else:
        filepath = os.path.join(ner_corpus_dir, file)
        df = pd.read_csv(filepath, sep=',')

        # dropna() will drop empty values in word, which are a result of line breaks in the letters
        df = df.dropna()

        # because VARD has replaced some single tokens with multiple tokens we need to first adjust the word indexing in word_id
        # to accomodate this we split any word values with whitespace on whitespace creating new rows and sensibly update the BIO labels
        new_rows = []
        for index, row in df.iterrows():
            tokens = row['word'].split()
            if len(tokens) == 1:
                row['token'] = row['word']
                new_rows.append(row)
            else:
                for i, token in enumerate(tokens):
                    row_copy = df.loc[index].copy()
                    row_copy['token'] = token
                    if i > 0:
                        for column in cols:
                            if row_copy[column] == 'B':
                                row_copy[column] = 'I'
                        row_copy['word_id'] += f'.{i}'
                        row_copy['word'] = ''
                    new_rows.append(row_copy)
        df = pd.concat(new_rows, axis=1).transpose().reset_index(drop=True)

        # convert extraneous sequences of '.' in tokens to '.'
        df['token'] = df['token'].str.replace(r'\.{1,}', '.', regex=True)

        # further tokenize the text, splitting trailing punctuation into new tokens and updating individual entity labels
        # code left in a verbose form for readability
        new_rows = []
        for index, row in df.iterrows():
            row_copy_1 = df.loc[index].copy()
            row_copy_2 = df.loc[index].copy()
            word = row['token'] # 'London,'
            if len(word) > 1: # ignore single character strings

                # block to handle all but the last token
                if index+1 < len(df):
                    if word[-1] in string.punctuation:
                        word_1 = word[:-1] # 'London'
                        word_2 = word[-1] # ','

                        for column in cols:
                            next_label = df.at[index+1, column]
                            if next_label == 'I':
                                row_copy_2[column] = 'I'
                            else:
                                row_copy_2[column] = 'O'

                        row_copy_1['new_word'] = word_1
                        row_copy_2['new_word'] = word_2
                        row_copy_2['word_id'] += f'.{1}'
                        row_copy_2['token'] = ''
                        row_copy_2['word'] = ''
                        new_rows.append(row_copy_1)
                        new_rows.append(row_copy_2)
                    else:
                        row['new_word'] = word
                        new_rows.append(row)
                        
                # block to handle the last token
                else:
                    if word[-1] in string.punctuation:
                        row_copy_1 = df.loc[index].copy()
                        row_copy_2 = df.loc[index].copy()

                        word_1 = word[:-1] # 'London'
                        word_2 = word[-1] # ','

                        for column in cols:
                            row_copy_2[column] = 'O'

                        row_copy_1['new_word'] = word_1
                        row_copy_2['new_word'] = word_2
                        row_copy_2['word_id'] += f'.{1}'
                        row_copy_2['token'] = ''
                        row_copy_2['word'] = ''
                        new_rows.append(row_copy_1)
                        new_rows.append(row_copy_2)
                    else:
                        row['new_word'] = word
                        new_rows.append(row)
            else:
                row['new_word'] = word
                new_rows.append(row)

        df = pd.concat(new_rows, axis=1).transpose().reset_index(drop=True)

        # generate POS tags with spaCy using tokenized words
        df['POS'] = df['new_word'].apply(get_pos)

        # rename columns: 'word' is the column with which we will work
        df.rename(columns={'new_word': 'word', 'token': 'old_word', 'word': 'word_original'}, inplace=True)

    # update the 'labels' column based on the new labels in individual entity columns
    df['labels'] = df[cols].apply(lambda row: next((col + '-B' for col in cols if row[col] == 'B'),
                                                   next((col + '-I' for col in cols if row[col] == 'I'), 'O')), axis=1)

    # specify directory to save processed files
    outdir = './data'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # specify file path
    file_path = os.path.join(outdir, file)

    # write preprocessed df to file as csv
    df.to_csv(file_path, index=False)

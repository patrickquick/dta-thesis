from lxml import etree
import pandas as pd
import os
import argparse

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script to reconcile the annotated data with the letters in their xml format

p = argparse.ArgumentParser()
p.add_argument('--gs_corpus', type=str, help='Input directory of gs-processed xml-formatted letters.')
p.add_argument('--master_corpus', type=str, help='Output directory for fully pre-processed letters.')
p.add_argument('--annotations', type=str, help="CSV file exported from Back2TheFuture containing annotations. Must minimally include: 'letters._id', 'free_annotations.annotations.NER', 'free_annotations.span'")
args = p.parse_args()

annotations = os.path.realpath(args.annotations)
gs_corpus = os.path.realpath(args.gs_corpus)
master_corpus = os.path.realpath(args.master_corpus)
isExist = os.path.exists(master_corpus)
if not isExist:
    os.mkdir(master_corpus)
else:
	print("The directory already exists. You are overwriting files.")

df = pd.read_csv(annotations, sep='\t')
df = df.dropna()

for xml_file in os.listdir(gs_corpus):
    if not xml_file.endswith(".xml"):
        continue
    letter_id = os.path.splitext(xml_file)[0]
    input_file = open(os.path.join(gs_corpus, xml_file),"r",encoding="utf-8")
    output_file = os.path.join(master_corpus, xml_file)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_file, parser)
    root = tree.getroot()

    for wn,word in enumerate(root.findall('.//word')):
        for id,span,tag in zip(df['letters._id'],df['free_annotations.span'],df['free_annotations.annotations.NER']):
            f = span.split('/')
            start,end = f
            start = int(start)
            end = int(end)
            if letter_id == id:
                if wn == start:
                    word.attrib[f'{tag}'] = 'B'
                    print(f"Reconciling a {tag} tag in letter {letter_id}")
                if wn != start and wn == end:
                    word.attrib[f'{tag}'] = 'I'
                    print(f"Reconciling a {tag} tag in letter {letter_id}")
                else:
                    if wn in range(start+1,end):
                        word.attrib[f'{tag}'] = 'I'
                        print(f"Reconciling a {tag} tag in letter {letter_id}")
                    else:
                        continue

    with open(output_file,"w",encoding="utf-8") as g:
        g.write(etree.tostring(tree, pretty_print=True, encoding="unicode"))

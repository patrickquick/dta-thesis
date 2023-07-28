from lxml import etree
import os
import argparse
from collections import Counter

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script to write only the unique corpus-level VARD runs to file, preserving their xml structure

p = argparse.ArgumentParser()
p.add_argument('--fscores', type=str, help='f-score weight for calculating replacement scores.')
p.add_argument('--thresholds', type=str, help='The normalisation threshold.')
p.add_argument('--processed_corpus', type=str, help='Input directory of post-processed xml-formatted letters.')
p.add_argument('--gs_corpus', type=str, help='Create output directory for gs-processed xml-formatted letters.')
args = p.parse_args()

processed_corpus = os.path.realpath(args.processed_corpus)
gs_corpus = os.path.realpath(args.gs_corpus)
isExist = os.path.exists(gs_corpus)
if not isExist:
    os.mkdir(gs_corpus)
else:
	print("Your output directory already exists. You are overwriting files.")

# list of all possible VARD attribute combinations based on the input passed to VARD in shell script
attributes = []
for f in args.fscores.split():
    for t in args.thresholds.split():
        attributes.append(f'VARD_fscore_{f}_threshold_{t}')

# check unicity of VARD runs at the corpus level
full_corpus_word_list = {}
for attribute in attributes:
    vard_run_word_list = []
    print(f"Checking unicity of {attribute} at corpus level.")
    for xml_file in os.listdir(processed_corpus):
        if not xml_file.endswith(".xml"):
            continue
        input_file = open(os.path.join(processed_corpus, xml_file),"r",encoding="utf-8")
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(input_file, parser)
        root = tree.getroot()
        for word in root.findall('.//word'):
            if attribute in word.attrib:
                vard_run_word_list.append(word.attrib[f'{attribute}'])
            else:
                vard_run_word_list.append(word.text)
    full_corpus_word_list[f'{attribute}'] = vard_run_word_list

# create dictionary with unique VARD runs as keys
r = {}
for k,v in full_corpus_word_list.items():
    if not tuple(v) in r.values():
       r[k] = tuple(v)
{k: list(v) for k, v in r.items()}

for xml_file in os.listdir(processed_corpus):
    if not xml_file.endswith(".xml"):
        continue
    letter_id = os.path.splitext(xml_file)[0]
    input_file = open(os.path.join(processed_corpus, xml_file),"r",encoding="utf-8")
    output_file = os.path.join(gs_corpus, xml_file)
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(input_file, parser)
    root = tree.getroot()
    VARD_count = Counter()

    # count instances of words normalised by VARD
    print(f"Counting instances of word tokens normalised by VARD in letter {letter_id}")
    for word in root.findall('.//word'):
        for attr in attributes:
            if attr in word.attrib:
                VARD_count[f'{attr}'] += 1
            else:
                pass

    # creat set with all VARD runs used
    r_all = []
    for word in root.findall('.//word'):
        for attr in word.attrib:
            if attr == 'word_id':
                continue
            else:
                r_all.append(attr)
    r_all = set(r_all)

    # rewrite xml master corpus with unique VARD runs only
    for word in root.findall('.//word'):
        for attr in word.attrib:
            if attr == 'word_id': 
                continue
            if not attr in r.keys():
                del word.attrib[f'{attr}']
            else:
                continue

    # write sum of instances of normalisation per VARD run to new element
    VARD_element = etree.SubElement(root, "VARD")
    VARD_1 = etree.SubElement(VARD_element, "VARD_count")
    for k,v in VARD_count.most_common():
        VARD_1.attrib[f'{k}'] = str(v)

    # write VARD run unicity record to new element
    VARD_2 = etree.SubElement(VARD_element, "VARD_unicity")
    for f in r_all:
        if f in r.keys():
            VARD_2.attrib[f'{f}'] = "Y"
        else:
            VARD_2.attrib[f'{f}'] = "N"

    with open(output_file,"w",encoding="utf-8") as g:
        g.write(etree.tostring(tree, pretty_print=True, encoding="unicode"))

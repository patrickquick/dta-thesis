import json
from lxml import etree
import os
import argparse

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script to create directory of xml-formatted letters; one file per letter in the corpus
# xml-formatted letters are required for VARD processing

def replacer(word):
    '''
    A function to replace extraneous characters present in the letters.
    Replaces '_', '/', '[', ']' with ''.
    '''
    chars = "_/[]"
    for char in chars:
        word = word.replace(char, '')
    word = word.replace('&amp;', '&')
    return word

p = argparse.ArgumentParser()
p.add_argument('--json_file', type=str, help='Path to json file containing letters.')
p.add_argument('--corpus', type=str, help='Create output directory for xml-formatted letters.')
args = p.parse_args()

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, args.corpus)
os.mkdir(output_dir)
output_dir = os.path.realpath(args.corpus)

with open(args.json_file) as json_file:
    letters = json.load(json_file)
    for letter in letters:
        root = etree.Element("root")
        letter_element = etree.SubElement(root, "letter")
        text = letter['text']
        letter_id = letter['_id']
        letter_element.attrib['letter_id'] = letter_id
        for ln, line in enumerate(text):
            for wn, word in enumerate(line.split(' ')):
                word_element = etree.SubElement(letter_element, "word")
                word_element.text = replacer(word)
                word_id = f'{letter_id}.{ln}.{wn}'
                word_element.attrib['word_id'] = word_id
        tree = etree.ElementTree(root)
        xml_letter = os.path.join(output_dir, f'{letter_id}.xml')
        with open(xml_letter, 'w', encoding="utf-8") as f:
            f.write(etree.tostring(tree, pretty_print=True, encoding="unicode"))

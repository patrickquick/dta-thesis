from lxml import etree
import os
import argparse

# MUST BE RUN INSIDE VARD WORKING FOLDER

# script for updating xml files with VARD runs

p = argparse.ArgumentParser()
p.add_argument('--corpus_varded', type=str, help='Path to VARDed corpus.')
p.add_argument('--processed_corpus', type=str, help='Create output directory for post-processed xml-formatted letters.')
p.add_argument('--fscore', type=str, help='f-score weight for calculating replacement scores.')
p.add_argument('--threshold', type=str, help='The normalisation threshold.')
args = p.parse_args()

corpus_varded = os.path.realpath(args.corpus_varded)
processed_corpus = os.path.realpath(args.processed_corpus)
isExist = os.path.exists(processed_corpus)
if not isExist:
    os.mkdir(processed_corpus)
else:
	print("Your output directory already exists. You are overwriting files previously created by VARD.\n")

for f in os.listdir(corpus_varded):
    if not f.endswith("Tagged"):
        continue
    corpus_varded_tagged = os.path.join(corpus_varded, f)
    xml_list = os.listdir(corpus_varded_tagged)
    for xml_file in xml_list:
        output_file = os.path.join(processed_corpus, xml_file)
        input_file = open(os.path.join(corpus_varded_tagged, xml_file),"r",encoding="utf-8")
        tree = etree.parse(input_file)
        root = tree.getroot()
        
        for word in root.findall('.//word'):
            children = word.getchildren() # get all the children of word i.e. get <normalised> element
            if len(children) > 0: # if there is an element (<normalised>)
                child = children[0] # child = whole <normalised> element
                original = child.get('orig') # original text
                corrected = child.text # corrected text
                tail = child.tail # remainder text to be attached to the original and corrected text: str
                word.remove(child) # remove <normalised> element
                new_attribute = f'VARD_fscore_{args.fscore}_threshold_{args.threshold}'
                if child.tail != None:
                    word.text = original + tail
                    word.set(new_attribute, child.text + tail)                
                else:
                    word.text = original
                    word.set(new_attribute, child.text)

            for text in root.iter():
                if text.text is None:
                    text.text = ''
                else:
                    pass
                
        with open(output_file,"w",encoding="utf-8") as g:
            g.write(etree.tostring(root, pretty_print=True, encoding="unicode"))

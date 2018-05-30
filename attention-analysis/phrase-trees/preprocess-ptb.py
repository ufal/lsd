#!/usr/bin/env python3

from nltk.corpus import ptb
import nltk.tree
import argparse
import glob

ap = argparse.ArgumentParser()
ap.add_argument("--ptbfiles", help="PennTreebank files")
ap.add_argument("--trees", help="Output trees")
ap.add_argument("--words", help="Output words, sentence per line")
args= ap.parse_args()

tree_file = open(args.trees, 'w')
word_file = open(args.words, 'w')
    
#TODO can not -> cannot

for filename in sorted(glob.glob('/home/marecek/nltk_data/corpora/ptb/' + args.ptbfiles)):
    #print("Processing " + filename)
    trees = ptb.parsed_sents(filename)
    for i in range(len(trees)):
        # remove traces and other empty nodes
        for sub in trees[i].subtrees():
            for n, child in enumerate(sub):
                if isinstance(child, str):
                    continue
                if (all(leaf.startswith("*") for leaf in child.leaves()) or child.label() == '-NONE-'):
                    del sub[n]
        # extract list of POS tags and remove POS tags from the trees
        sent_tags = list()
        for sub in trees[i].subtrees():
            sub.set_label("X")
            for n, child in enumerate(sub):
                if isinstance(child, str):
                    continue
                leaves = child.leaves()
                # delete all brackets containing only one token
                if (len(leaves) == 1):
                    sent_tags.append(child.label())
                    sub[n] = leaves[0]
        tree_file.write(str(trees[i]) + '\n')
        # save tokens
        word_file.write(' '.join(trees[i].leaves()) + '\n')

tree_file.close
word_file.close





#!/usr/bin/env python3

import codecs
import sys
import argparse

sys.path.append('/lnet/troja/projects/emnlp18-nonautoregressive/neuralmonkey')

from neuralmonkey.vocabulary import from_t2t_vocabulary, Vocabulary
from neuralmonkey.processors import wordpiece as wp

ap = argparse.ArgumentParser()
ap.add_argument("--dictionary", help="Dictionary")
args= ap.parse_args()

vocabulary = from_t2t_vocabulary(args.dictionary)

for line in sys.stdin:
    sentence = line.split()
    sent_wps = wp.wordpiece_encode(sentence, vocabulary)
    print(" ".join(sent_wps))


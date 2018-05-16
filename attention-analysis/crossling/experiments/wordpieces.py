#!/usr/bin/env python3

import codecs
import sys

sys.path.append('../neuralmonkey')

from neuralmonkey.vocabulary import from_t2t_vocabulary, Vocabulary
from neuralmonkey.processors import wordpiece as wp

#source_file = codecs.open("exp-nm-transformer/generated/06.src", "r", "utf-8")
sentence = list()

vocabulary = from_t2t_vocabulary("../data/wordpieces.txt")

for line in sys.stdin:
    sentence = line.split()
    sent_wps = wp.wordpiece_encode(sentence, vocabulary)
    print("|".join(sent_wps))


#!/usr/bin/env python3

import codecs
import sys

sys.path.append('../neuralmonkey')

from neuralmonkey.vocabulary import from_t2t_vocabulary, Vocabulary
from neuralmonkey.processors import wordpiece as wp

sentence = list()

vocabulary = from_t2t_vocabulary("../data/wordpieces200.all.txt")

#UTF8Reader = codecs.getreader('utf8')
#sys.stdin = UTF8Reader(sys.stdin)

for line in sys.stdin:
    sentence = line.split()
    sent_wps = wp.wordpiece_encode(sentence, vocabulary)
    print(" ".join(sent_wps))


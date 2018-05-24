#!/usr/bin/env python3

import codecs
import sys

sys.path.append('/home/marecek/troja/neuralmonkey')

from neuralmonkey.vocabulary import from_t2t_vocabulary, Vocabulary
from neuralmonkey.processors import wordpiece as wp

vocabulary = from_t2t_vocabulary("/home/popel/work/qt21/data/vocab.encs.32768")

for line in sys.stdin:
    sentence = line.split()
    sent_wps = wp.wordpiece_encode(sentence, vocabulary)
    print(" ".join(sent_wps))


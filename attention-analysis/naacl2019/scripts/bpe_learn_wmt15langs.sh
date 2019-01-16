#!/bin/bash

cat data/europarl/intersect.{enS,deS,frS}.tok.true.train | data/subword-nmt/subword_nmt/learn_bpe.py -s 100000 > data/bpe_enS-deS-frS_100k.dict

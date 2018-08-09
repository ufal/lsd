#!/bin/bash

cat data/europarl/intersect.{cs,en,de,fi,fr}.tok.true.train | data/subword-nmt/subword_nmt/learn_bpe.py -s 50000 > data/bpe.dict

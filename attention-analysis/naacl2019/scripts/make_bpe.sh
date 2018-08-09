#!/bin/bash

cat data/europarl_tok/intersect.*.tok | data/subword-nmt/subword_nmt/learn_bpe.py -s 50000 > data/bpe.dict

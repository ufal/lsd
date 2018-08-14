#!/bin/bash

for lang in cs de en fi fr; do \
    cat data/europarl/intersect.$lang.tok.true.train | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_cs-en-de-fi-fr_100k.dict > data/europarl/intersect.$lang.bpe100k.train; \
    cat data/europarl/intersect.$lang.tok.true.dev | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_cs-en-de-fi-fr_100k.dict > data/europarl/intersect.$lang.bpe100k.dev; \
    cat data/europarl/intersect.$lang.tok.true.test | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_cs-en-de-fi-fr_100k.dict > data/europarl/intersect.$lang.bpe100k.test; \
done

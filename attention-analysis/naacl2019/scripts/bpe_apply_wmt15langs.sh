#!/bin/bash

for lang in cs de en fi fr; do \
    cat data/europarl/intersect.$lang.tok.true.train | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_wmt15langs.dict > data/europarl/intersect.$lang.bpe.train; \
    cat data/europarl/intersect.$lang.tok.true.dev | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_wmt15langs.dict > data/europarl/intersect.$lang.bpe.dev; \
    cat data/europarl/intersect.$lang.tok.true.test | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_wmt15langs.dict > data/europarl/intersect.$lang.bpe.test; \
done

#!/bin/bash

for lang in enS deS frS; do \
    cat data/europarl/intersect.$lang.tok.true.train | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_enS-deS-frS_100k.dict > data/europarl/intersect.$lang.bpeEDF100k.train; \
    cat data/europarl/intersect.$lang.tok.true.dev | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_enS-deS-frS_100k.dict > data/europarl/intersect.$lang.bpeEDF100k.dev; \
    cat data/europarl/intersect.$lang.tok.true.test | data/subword-nmt/subword_nmt/apply_bpe.py -c data/bpe_enS-deS-frS_100k.dict > data/europarl/intersect.$lang.bpeEDF100k.test; \
done

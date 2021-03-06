#!/bin/bash

qsub -V -cwd -b y -j y -q gpu-ms.q -l gpu=1,gpu_ram=11G,hostname=dll\* -N bert-emb \
    source ~/troja/virtualenv/tensorflow/bin/activate \; \
    ./conllu_bert_embeddings.py --casing uncased --language english --size large test2.conllu test2.npz

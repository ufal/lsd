#!/usr/bin/env python3
#coding: utf-8

import random

with open('cs-ud-train.forms') as fh:
    forms = fh.readlines()

with open('cs-ud-train.tags') as fh:
    tags = fh.readlines()

ids = list(range(68000))

for size in (1,5,10,50,100,500,1000,5000):
    random.shuffle(ids)
    for split in range(10):
        name = str(split)+'.'+str(size)
        with open('train/cs-ud-train.forms.ssplit'+name, 'w') as ffh, open('train/cs-ud-train.tags.ssplit'+name, 'w') as tfh:
            for line in range(size):
                aid = ids[split*size + line]
                print(forms[aid], file=ffh, end='')
                print(tags[aid], file=tfh, end='')


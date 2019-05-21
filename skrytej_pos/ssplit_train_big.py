#!/usr/bin/env python3
#coding: utf-8

import random

with open('cs-ud-train.forms') as fh:
    forms = fh.readlines()

with open('cs-ud-train.tags') as fh:
    tags = fh.readlines()

ids = list(range(68000))

for size in (10000,30000):
    for split0 in range(0,10,2):        
        random.shuffle(ids)
        for split in (0, 1):
            split_name = split0+split
            name = str(split_name)+'.'+str(size)
            with open('train/cs-ud-train.forms.ssplit'+name, 'w') as ffh, open('train/cs-ud-train.tags.ssplit'+name, 'w') as tfh:
                for line in range(size):
                    aid = ids[split*size + line]
                    print(forms[aid], file=ffh, end='')
                    print(tags[aid], file=tfh, end='')


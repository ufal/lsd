#!/usr/bin/env python3
#coding: utf-8

import sys

import logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

ID = 0
FORM = 1
LEMMA = 2
POS = 3

# TODO truecase

def printword(fields):
    print(fields[FORM], end=' ')

skipwords = set()
for line in sys.stdin:
    if line.startswith('#'):
        # comment
        pass
    elif line == '\n':
        # end of sentence
        print()
        skipwords = set()
    else:
        fields = line.split('\t')
        if '.' in fields[ID]:
            # ellipsis
            pass
        elif '-' in fields[ID]:
            # multitoken
            printword(fields)
            start, end = (int(x) for x in fields[ID].split('-', maxsplit=2))
            skipwords = set(range(start, end+1))
        else:
            # regular token
            if int(fields[ID]) in skipwords:
                pass
            else:
                printword(fields)

print()

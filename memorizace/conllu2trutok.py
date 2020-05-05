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

def printword(fields):
    # !!! hack: assume multiword tokens are function words and therefore
    # lower
    # TODO correct: check case of first part of multitoken word and set case
    # accordingly
    if fields[LEMMA] == fields[FORM]:
        # no need to truecase
        form = fields[FORM]
    elif fields[LEMMA].islower() or fields[LEMMA] == '_':
        form = fields[FORM].lower()
    elif fields[LEMMA].isupper():
        form = fields[FORM].upper()
    elif fields[LEMMA].istitle():
        form = fields[FORM].title()
    else:
        logging.warn('Cannot truecase {} with lemma {}'.format(
            fields[FORM], fields[LEMMA]))
        form = fields[FORM]
    print(form, end=' ')

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

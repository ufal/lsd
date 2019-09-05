#!/usr/bin/env python3
#coding: utf-8

import sys

import logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

for line in sys.stdin:
    pairs = line.split()
    newpairs = list()
    for pair in pairs:
        e, f = pair.split('-')
        e = int(e)+1
        f = int(f)+1
        newpairs.append('{}-{}'.format(e, f))
    print(*newpairs)

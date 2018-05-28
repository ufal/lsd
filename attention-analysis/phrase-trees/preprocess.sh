#!/bin/bash

MOSESDECODER=/home/libovicky/spec_work/mosesdecoder

source ~/troja/nm/bin/activate
./preprocess-ptb.py --ptbfiles wsj/23/wsj_*.mrg --trees trees --words words.ptb
./ptb2nematus.py --input words.ptb --output words.tok --alignment ali
cat words.tok | $MOSESDECODER/scripts/recaser/truecase.perl -model nematus_truecase.en > words.nemaprep
cat words.nemaprep | ./wordpieces.py --dictionary /lnet/troja/projects/emnlp18-nonautoregressive/data/ende/wordpieces.txt > words.wps


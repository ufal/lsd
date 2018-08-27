#!/bin/bash

# Usage: parse.sh cs < cs.tok > cs.conllu

D=/net/projects/LSD/naacl2019-data

$D/udpipe --input=horizontal --tag --parse $D/tokenizers/$1.udpipe


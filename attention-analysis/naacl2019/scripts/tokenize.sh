#!/bin/bash

# Usage: tokenize.sh cs < cs.text > cs.tok

D=/net/projects/LSD/naacl2019-data/tokenizers

$D/udpipe --tokenize --output=horizontal $D/$1.udpipe


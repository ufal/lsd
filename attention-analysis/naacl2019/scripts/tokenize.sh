#!/bin/bash

# Usage: tokenize.sh cs < cs.text > cs.tok

D=/net/projects/LSD/naacl2019-data

$D/udpipe --tokenizer=presegmented  --output=horizontal $D/tokenizers/$1.udpipe


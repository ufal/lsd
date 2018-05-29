#!/bin/bash

cat sent-per-file/s1[0123]*.tree > trees-for-eval
cat sent-per-file/s1[0123]*.gtree > gtrees-for-eval
echo "With punctuation"
python2 parseval.py trees-for-eval gtrees-for-eval
cat trees-for-eval | ./postprocess-trees.py > trees2-for-eval
cat gtrees-for-eval | ./postprocess-trees.py > gtrees2-for-eval
echo "Without punctuation"
python2 parseval.py trees2-for-eval gtrees2-for-eval


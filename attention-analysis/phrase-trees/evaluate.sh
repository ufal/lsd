#!/bin/bash


source ~/troja/nm/bin/activate
#cat sent-per-file/s10[0123]*.tree > trees-for-eval
#cat sent-per-file/s10[0123]*.gtree > gtrees-for-eval
#cat sent-per-file-out/s[1234]?.tree > trees-for-eval
#cat sent-per-file/s[1234]?.gtree > gtrees-for-eval
rm -f trees-for-eval
rm -f gtrees-for-eval
for i in 4 13 16 17 25 28 29 32 37 39 41 43 49 62 70 74 77 78 89 91 93 101 103 118 127 129 132 139 144 148 150 154 155 165 168 170 171 175 178 185 189 193; do
    cat sent-per-file-out/s$i.tree >> trees-for-eval;
    cat sent-per-file/s$i.gtree >> gtrees-for-eval;
done
echo "With punctuation"
#python2 parseval.py trees-for-eval gtrees-for-eval
./evaluate-trees.py trees-for-eval gtrees-for-eval
cat trees-for-eval | ./postprocess-trees.py > trees2-for-eval
cat gtrees-for-eval | ./postprocess-trees.py > gtrees2-for-eval
cat b1 | ./postprocess-trees.py > b12
cat b2 | ./postprocess-trees.py > b22
echo "Without punctuation"
./evaluate-trees.py trees2-for-eval gtrees2-for-eval
#echo "Left baseline:"
#./evaluate-trees.py b12 gtrees2-for-eval
#echo "Right baseline:"
#./evaluate-trees.py b22 gtrees2-for-eval

#python2 parseval.py -t -i trees2-for-eval gtrees2-for-eval


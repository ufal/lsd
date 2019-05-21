#!/bin/bash
#
set -o xtrace

#t=embsonly
#t=$1

for t in embsonly embsonly_new hidden hidden-new
do

for m in 0 2 4 6 8
do
    n=$((m+1))
for l in 1 5 10 50 100 500 1000 5000 10000 30000
do
    ./eval_output_ssplit.py \
        cs-ud-dev.forms \
        cs-ud-dev.tags \
        output/cs-ud-dev.tagger-$t-ssplit$m-$l.output \
        output/cs-ud-dev.tagger-$t-ssplit$n-$l.output \
        train/cs-ud-train.forms.ssplit$m.$l \
        train/cs-ud-train.forms.ssplit$n.$l \
        cs-ud-dev.invocabforms
done > eval/$t.$m-$n.eval
done

paste eval/$t.*.eval > eval/$t.eval
rm eval/$t.*.eval

done


#!/bin/bash
#
set -o xtrace

#t=embsonly
#t=$1
for t in embsonly 
do

for m in 0 2 4 6 8
do
    n=$((m+1))
for l in 50 100 500 1000 5000 10000 30000
do
    ./eval_output_ssplit_sizes_nodev.py \
        cs-ud-dev.forms \
        cs-ud-dev.tags \
        output/cs-ud-dev.tagger-$t-ssplit$m-$l.output \
        output/cs-ud-dev.tagger-$t-ssplit$n-$l.output \
        train/cs-ud-train.forms.ssplit$m.$l \
        train/cs-ud-train.forms.ssplit$n.$l \
        cs-ud-dev.invocabforms \
        cs-ud-train.forms.495.types
done > eval/$t.$m-$n.evals
done

paste eval/$t.*.evals > eval/$t.evals
rm eval/$t.*.evals

done

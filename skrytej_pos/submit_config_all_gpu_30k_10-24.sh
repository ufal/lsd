#!/bin/bash

c=$1

for n in $(seq 10 24)
do
    s=ssplit$n
    for l in 30000
    do
        qsub -N t-$c-$s-$l-gpu tagger-SSS-LLL-HHH.shcg $s $l $c
    done
done


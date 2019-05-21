#!/bin/bash

c=$1

for n in 10 11 12
do
    s=ssplit$n
    for l in 10000
    do
        qsub -N t-$c-$s-$l-gpu tagger-SSS-LLL-HHH.shcg $s $l $c
    done
done


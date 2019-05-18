#!/bin/bash

c=$1

for n in 0 1 2 3 4 5 6 7 8 9
do
    s=ssplit$n
    for l in 1 5 10 50 100 500 1000 5000 10000 30000
    do
        qsub -N t-$c-$s-$l-gpu tagger-SSS-LLL-HHH.shcg $s $l $c
    done
done


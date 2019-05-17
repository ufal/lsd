#!/bin/bash

for n in 0 1 2 3 4 5 6 7 8 9
do
    s=ssplit$n
    for l in 1 5 10 50 100 500 1000 5000
    do
        qsub -N te-$s-$l tagger-SSS-LLL-HHH.shc $s $l embsonly
    done
done


#!/bin/bash

for s in split1 split2
do
    for l in 1 5 10 50 100 500 1000 5000 10000 30000
    do
        qsub -N ten-$s-$l tagger-SSS-LLL-HHH.shc $s $l embsonly_new
    done
done

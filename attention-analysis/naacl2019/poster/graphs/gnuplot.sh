#!/bin/bash

t=las
for l in all br bxr fo hsb hy kk kmr pcm th
do
    c=`grep '\t2\t' las_$l.tsv|cut -f1`
    sed -e s/LLL/$l/g -e s/CCC/$c/g LAS_LLL_CCC.gnuplot > las_$l.gnuplot
done


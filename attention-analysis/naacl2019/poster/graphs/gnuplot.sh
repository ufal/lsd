#!/bin/bash

for t in las mlas blex
do
for l in all br bxr fo hsb hy kk kmr pcm th
do
    echo $l
    sed s/LLL/$l/g LLL-$t.gnuplot > $t-$l.gnuplot
    gnuplot < $t-$l.gnuplot
done
done

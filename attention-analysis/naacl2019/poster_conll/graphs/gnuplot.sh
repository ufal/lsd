#!/bin/bash

echo START

for t in las mlas blex
do
echo
echo $t
echo
for l in all br bxr fo hsb hy kk kmr pcm th
do
    echo $l
    sed s/LLL/$l/g LLL-$t.GNUPLOT > $t-$l.gnuplot
    gnuplot < $t-$l.gnuplot
done
done

echo
echo DONE

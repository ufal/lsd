#!/bin/bash

b=$1
c=none

while [ $b != $c ]
do

c=$b
s=,$c,

l=$(echo $c
for r in ${c//,/ }
do
    k=${s/,$r,/,}
    echo ${k:1:-1}
done)

for n in $l
do
    qsub run.shc $n
done > /dev/null

qsub -hold_jid run.shc -sync y -o /dev/null -e /dev/null -b y true > /dev/null

b=$(for n in $l
do
    echo $(cat results/$n) $n
done | sort -n | tail -n 1 | cut -d' ' -f2)

echo $(cat results/$b) $b

done


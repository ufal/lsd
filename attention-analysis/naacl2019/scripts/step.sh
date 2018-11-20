#!/bin/bash

c=$1
s=,$c,

for r in ${c//,/ }
do
    k=${s/,$r,/,}
    qsub run.shc ${k:1:-1}
done

qsub -hold_jid run.shc -sync y -b y echo "DONE"  

for r in ${c//,/ }
do
    k=${s/,$r,/,}
    n=${k:1:-1}
    echo `cat results/$n` $n
done | sort -n


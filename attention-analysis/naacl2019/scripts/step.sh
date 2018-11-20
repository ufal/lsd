#!/bin/bash

b=$1
c=none

mkdir -p results

function md5 () {
    echo $1 | md5sum | cut -d' ' -f1
}

while [ $b != $c ]
do

c=$b
s=,$c,

# try removing each head, but also add the full setup
l=$(echo $c
for r in ${c//,/ }
do
    k=${s/,$r,/,}
    echo ${k:1:-1}
done)

# run
for n in $l
do
    qsub run.shc $n
done > /dev/null

# wait
qsub -hold_jid run.shc -sync y -o /dev/null -e /dev/null -b y true > /dev/null

# top score and setup
t=$(for n in $l
do
    m=$(md5 $n)
    echo $(cat results/$m) $n
done | sort -n | tail -n 1)

echo $t

# best setup
b=${t#* }

done


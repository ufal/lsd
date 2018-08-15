#!/bin/bash

# Usage:   
# Creates: /net/projects/LSD/naacl2019-data/truecasers/cs.truecaser

D=/net/projects/LSD/naacl2019-data/

./truecase-train.sh $1 $D/europarl/intersect.$1.tok.train
for T in dev test train
do
    ./truecase.sh $1 \
        < $D/europarl/intersect.$1.tok.$T \
        > $D/europarl/intersect.$1.tok.true.$T \
        &
done


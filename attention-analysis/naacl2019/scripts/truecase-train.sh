#!/bin/bash

# Usage:   truecase-train.sh cs cs.tok.train
# Creates: /net/projects/LSD/naacl2019-data/truecasers/cs.truecaser

D=/net/projects/LSD/naacl2019-data/

$D/mosesdecoder/scripts/recaser/train-truecaser.perl --corpus $2 --model $D/truecaser/$1.truecaser


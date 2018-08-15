#!/bin/bash

# Usage: truecase.sh cs < cs.tok > cs.true

D=/net/projects/LSD/naacl2019-data/

$D/mosesdecoder/scripts/recaser/truecase.perl --model $D/truecasers/$1.truecaser


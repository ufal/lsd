#!/bin/bash

# e.g. split1
s=$1
# e.g. 50
l=$2

qsub -N te-$s-$l tagger-embsonly-SSS-LLL.shc $s $l


#!/bin/bash

# e.g. split1
s=$1
# e.g. 50
l=$2

qsub -N ten-$s-$l tagger-embsonly_new-SSS-LLL.shc $s $l


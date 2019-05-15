#!/bin/bash

# e.g. split1
s=$1
# e.g. 50
l=$2

qsub -N th-$s-$l tagger-hidden-SSS-LLL.shc $s $l


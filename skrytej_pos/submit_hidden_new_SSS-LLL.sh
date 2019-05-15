#!/bin/bash

# e.g. split1
s=$1
# e.g. 50
l=$2

qsub -N thn-$s-$l tagger-hidden-new-SSS-LLL.shc $s $l


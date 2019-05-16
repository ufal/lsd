#!/bin/bash

# e.g. split1
s=$1
# e.g. 50
l=$2

qsub -N te-$s-$l tagger-SSS-LLL-HHH.shc $s $l embsonly


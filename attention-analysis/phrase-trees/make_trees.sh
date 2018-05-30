#!/bin/bash

source /home/marecek/troja/nm/bin/activate
for i in sent-per-file/s10[0123]*.txt; do
    sentnum=`echo $i | sed 's/sent-per-file\/s//;' | sed 's/\.txt//;'`; \
    echo "Processing sentence $sentnum."
    ./attentions2tree.py --attentions sent-per-file/s$sentnum.att.npz --labels sent-per-file/s$sentnum.wps --alignment sent-per-file/s$sentnum.ali --tree sent-per-file/s$sentnum.tree
    #python2 parseval.py sent-per-file/s$sentnum.tree sent-per-file/s$sentnum.gtree > sent-per-file/s$sentnum.score
done

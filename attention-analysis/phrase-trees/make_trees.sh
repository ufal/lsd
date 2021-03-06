#!/bin/bash

DATA_DIR=/ha/home/marecek/projects/lsd/attention-analysis/phrase-trees
OUT_DIR=/ha/home/rosa/lsd/attention-analysis/phrase-trees

mkdir -p $OUT_DIR/sent-per-file-out

source /home/marecek/troja/nm/bin/activate
#for i in 41; do
for i in 4 13 16 17 25 28 29 32 37 39 41 43 49 62 70 74 77 78 89 91 93 101 103 118 127 129 132 139 144 148 150 154 155 165 168 170 171 175 178 185 189 193; do
#for i in sent-per-file/s[1234]?.txt; do
    #sentnum=`echo $i | sed 's/sent-per-file\/s//;' | sed 's/\.txt//;'`; \
    sentnum=$i
    echo "Processing sentence $sentnum."
    #./attentions2tree.py --attentions sent-per-file-out/s$sentnum.att.npz --labels sent-per-file/s$sentnum.wps --alignment sent-per-file/s$sentnum.ali --heatmaps sent-per-file-out/s$sentnum --tree sent-per-file-out/s$sentnum.tree --weights outputproj.att.npz
    ./attentions2tree_sent-per-file.py \
        --attentions $DATA_DIR/sent-per-file-out/s$sentnum.att.npz \
        --labels     $DATA_DIR/sent-per-file/s$sentnum.wps \
        --alignment  $DATA_DIR/sent-per-file/s$sentnum.ali \
        --heatmaps    $OUT_DIR/sent-per-file-out/s$sentnum \
        --tree        $OUT_DIR/sent-per-file-out/s$sentnum.tree \
        --deptree     $OUT_DIR/sent-per-file-out/s$sentnum.deptree \
        --staredness  $OUT_DIR/sent-per-file-out/s$sentnum.staredness \

    #python2 parseval.py sent-per-file/s$sentnum.tree sent-per-file/s$sentnum.gtree > sent-per-file/s$sentnum.score

done

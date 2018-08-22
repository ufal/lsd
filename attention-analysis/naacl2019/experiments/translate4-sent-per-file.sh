#!/bin/bash

EXP_DIR=/net/projects/LSD/naacl2019-data/experiments/$SRC$TGT1$TGT2$TGT3$TGT4-${NUMHEADS}h-$TOKENS
TEST_DATA=/net/projects/LSD/naacl2019-data/europarl/intersect.$SRC.$TOKENS.test
VARIABLES=`cat $EXP_DIR/variables.data.best` 

echo "[vars]
src=\"$SRC\"
tgt1=\"$TGT1\"
tgt2=\"$TGT2\"
tgt3=\"$TGT3\"
tgt4=\"$TGT4\"
numheads=$NUMHEADS
tokens=\"$TOKENS\"" > $EXP_DIR/get-attentions.ini
cat get-attentions4_no-vars.ini >> $EXP_DIR/get-attentions.ini

mkdir -p $EXP_DIR/sent-per-file

split -l1 -a4 -d $TEST_DATA $EXP_DIR/sent-per-file/src

for src in $EXP_DIR/sent-per-file/src*; do
    sentnum=`echo $src | sed 's/.*sent-per-file\/src//;'`; \
    transl1=$EXP_DIR/sent-per-file/transl1$sentnum; \
    transl2=$EXP_DIR/sent-per-file/transl2$sentnum; \
    transl3=$EXP_DIR/sent-per-file/transl3$sentnum; \
    transl4=$EXP_DIR/sent-per-file/transl4$sentnum; \
    att=$EXP_DIR/sent-per-file/att$sentnum; \
    datafile=$EXP_DIR/sent-per-file/data$sentnum.ini; \
    echo "[main]
test_datasets=[<test_data>]
variables=[\"$EXP_DIR/$VARIABLES\"]

[test_data]
class=dataset.load_dataset_from_files
s_source=\"$src\"
s_target1_out=\"$transl1\"
s_target2_out=\"$transl2\"
s_target3_out=\"$transl3\"
s_target4_out=\"$transl4\"
s_att_out=\"$att\"
" > $datafile; \
    
    while [ ! -e $att.npz ] ; do
        /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-run $EXP_DIR/get-attentions.ini $datafile
        sleep 5
    done
done

cat $EXP_DIR/sent-per-file/transl1* > $EXP_DIR/translations1.txt
cat $EXP_DIR/sent-per-file/transl2* > $EXP_DIR/translations2.txt
cat $EXP_DIR/sent-per-file/transl3* > $EXP_DIR/translations3.txt
cat $EXP_DIR/sent-per-file/transl4* > $EXP_DIR/translations4.txt
../scripts/concatenate_attentions.py $EXP_DIR/sent-per-file/att* $EXP_DIR/attentions.npz
cp $TEST_DATA $EXP_DIR/source.txt


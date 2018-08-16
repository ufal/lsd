#!/bin/bash

EXP_DIR=/net/projects/LSD/naacl2019-data/experiments/$SRC$TGT-${NUMHEADS}h-$TOKENS
TEST_DATA=/net/projects/LSD/naacl2019-data/europarl/intersect.$SRC.$TOKENS.test
VARIABLES=`cat $EXP_DIR/variables.data.best`

echo "[vars]
src=\"$SRC\"
tgt=\"$TGT\"
numheads=$NUMHEADS
tokens=\"$TOKENS\"" > $EXP_DIR/get-attentions.ini
cat get-attentions_no-vars.ini >> $EXP_DIR/get-attentions.ini

mkdir -p $EXP_DIR/sent-per-file

split -l1 -a4 -d $TEST_DATA $EXP_DIR/sent-per-file/src

for src in $EXP_DIR/sent-per-file/src*; do
    sentnum=`echo $src | sed 's/.*sent-per-file\/src//;'`; \
    transl=$EXP_DIR/sent-per-file/transl$sentnum; \
    att=$EXP_DIR/sent-per-file/att$sentnum; \
    datafile=$EXP_DIR/sent-per-file/data$sentnum.ini; \
    echo "[main]
test_datasets=[<test_data>]
variables=[\"$EXP_DIR/$VARIABLES\"]

[test_data]
class=dataset.load_dataset_from_files
s_source=\"$src\"
s_target_out=\"$transl\"
s_att_out=\"$att\"
" > $datafile
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-run $EXP_DIR/get-attentions.ini $datafile
done

cat $EXP_DIR/sent-per-file/transl* > $EXP_DIR/translations.txt
../scripts/concatenate_attentions.py $EXP_DIR/sent-per-file/att* $EXP_DIR/attentions.npz
cp $TEST_DATA $EXP_DIR/source.txt


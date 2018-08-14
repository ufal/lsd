#!/bin/bash

EXP_DIR=/net/projects/LSD/naacl2019-data/experiments/encs_16h
TEST_DATA=/net/projects/LSD/naacl2019-data/europarl/intersect.en.bpe.test
ATTENTION_INI=encs_16h_att.ini
VARIABLES=`cat $EXP_DIR/variables.data.best` 

mkdir -p $EXP_DIR/sent-per-file

split -l1 -a4 -d $TEST_DATA $EXP_DIR/sent-per-file/src
for src in $EXP_DIR/sent-per-file/src*; do
    sentnum=`echo $src | sed 's/.*sent-per-file\/src//;'`; \
    transl=`echo $src | sed 's/src/transl/;'`; \
    att=`echo $src | sed 's/src/att/;'`; \
    inifile=`echo $src | sed 's/src/data/;'`; \
    echo "[main]
test_datasets=[<test_data>]
variables=[\"$EXP_DIR/$VARIABLES\"]

[test_data]
class=dataset.load_dataset_from_files
s_source=\"$src\"
s_target_out=\"$transl\"
s_att_out=\"$att\"
" > $inifile.ini
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-run $ATTENTION_INI $inifile.ini
done

cat $EXP_DIR/sent-per-file/transl* > $EXP_DIR/translations.txt
../scripts/concatenate_attentions.py $EXP_DIR/sent-per-file/att* $EXP_DIR/attentions.npz


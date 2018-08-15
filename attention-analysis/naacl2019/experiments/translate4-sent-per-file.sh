#!/bin/bash

EXP_DIR=/net/projects/LSD/naacl2019-data/experiments/encsdefifr_16h
TEST_DATA=/net/projects/LSD/naacl2019-data/europarl/intersect.en.tok.true.test
ATTENTION_INI=encsdefifr_16h_att.ini
VARIABLES=`cat $EXP_DIR/variables.data.best` 

mkdir -p $EXP_DIR/sent-per-file

split -l1 -a4 -d $TEST_DATA $EXP_DIR/sent-per-file/src
for src in $EXP_DIR/sent-per-file/src*; do
    sentnum=`echo $src | sed 's/.*sent-per-file\/src//;'`; \
    transl1=`echo $src | sed 's/src/transl1/;'`; \
    transl2=`echo $src | sed 's/src/transl2/;'`; \
    transl3=`echo $src | sed 's/src/transl3/;'`; \
    transl4=`echo $src | sed 's/src/transl4/;'`; \
    att=`echo $src | sed 's/src/att/;'`; \
    inifile=`echo $src | sed 's/src/data/;'`; \
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
" > $inifile.ini
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-run $ATTENTION_INI $inifile.ini
done

cat $EXP_DIR/sent-per-file/transl1* > $EXP_DIR/translations1.txt
cat $EXP_DIR/sent-per-file/transl2* > $EXP_DIR/translations2.txt
cat $EXP_DIR/sent-per-file/transl3* > $EXP_DIR/translations3.txt
cat $EXP_DIR/sent-per-file/transl4* > $EXP_DIR/translations4.txt
../scripts/concatenate_attentions.py $EXP_DIR/sent-per-file/att* $EXP_DIR/attentions.npz


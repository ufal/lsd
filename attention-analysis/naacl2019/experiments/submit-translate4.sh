SRC="en"
TGT1="cs"
TGT2="de"
TGT3="fi"
TGT4="fr"
NUMHEADS=16
TOKENS="bpe100k"

qsub -cwd -b y -j y -q "cpu-troja.q@*" -hard -l mem_free=20g -l act_mem_free=20g -l h_vmem=20g -N TR_$SRC$TGT1$TGT2$TGT3$TGT4-${NUMHEADS}h-$TOKENS \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-cpu-troja/bin/activate \; \
    SRC="$SRC" TGT1="$TGT1" TGT2="$TGT2" TGT3="$TGT3" TGT4="$TGT4" NUMHEADS=$NUMHEADS TOKENS="$TOKENS" translate4-sent-per-file.sh

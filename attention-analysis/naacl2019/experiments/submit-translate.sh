SRC="enS"
TGT="frS"
NUMHEADS=16
TOKENS="bpeEDF100k"

qsub -cwd -b y -j y -q "cpu-troja.q@*" -hard -l mem_free=10g -l act_mem_free=10g -l h_vmem=10g -N TR_$SRC$TGT-${NUMHEADS}h-$TOKENS \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-cpu-troja/bin/activate \; \
    SRC="$SRC" TGT="$TGT" NUMHEADS=$NUMHEADS TOKENS="$TOKENS" translate-sent-per-file.sh

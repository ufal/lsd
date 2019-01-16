SRC="deS"
TGT="frS"
NUMHEADS=16
TOKENS="bpeEDF100k"
VOCSIZE=110000

qsub -V -cwd -b y -j y -q gpu-ms.q -l gpu=1,gpu_ram=11G,hostname=dll\* -N $SRC$TGT-${NUMHEADS}h-$TOKENS \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-gpu/bin/activate \; \
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-train translation.ini \
    -v src=\\\"$SRC\\\" -v tgt=\\\"$TGT\\\" -v numheads=$NUMHEADS -v tokens=\\\"$TOKENS\\\" -v vocsize=$VOCSIZE

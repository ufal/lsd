SRC="en"
TGT1="cs"
TGT2="de"
TGT3="fi"
TGT4="fr"
NUMHEADS=16
TOKENS="bpe100k"
VOCSIZE=110000

qsub -V -cwd -b y -j y -q gpu-ms.q -l gpu=1,gpu_ram=11G,hostname=dll\* -N $SRC$TGT1$TGT2$TGT3$TGT4-${NUMHEADS}h-$TOKENS \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-gpu/bin/activate \; \
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-train translation4.ini \
    -v src=\\\"$SRC\\\" -v tgt1=\\\"$TGT1\\\" -v tgt2=\\\"$TGT2\\\" -v tgt3=\\\"$TGT3\\\" -v tgt4=\\\"$TGT4\\\" -v numheads=$NUMHEADS -v tokens=\\\"$TOKENS\\\" -v vocsize=$VOCSIZE

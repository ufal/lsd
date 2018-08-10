qsub -V -cwd -b y -j y -q gpu-ms.q -l gpu=1,gpu_ram=11G,hostname=dll\* -N TR_encs_16h \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-gpu/bin/activate \; \
    /net/projects/LSD/naacl2019-data/neuralmonkey/bin/neuralmonkey-run encs_16h_att.ini encs_16h_data.ini

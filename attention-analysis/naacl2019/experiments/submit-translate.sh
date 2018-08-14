qsub -cwd -b y -j y -q "cpu-troja.q@*" -hard -l mem_free=10g -l act_mem_free=10g -l h_vmem=10g -N TR_encs_16h_words \
    source /net/work/people/helcl/virtualenv/tensorflow-1.4-cpu-troja/bin/activate \; \
    translate-sent-per-file.sh

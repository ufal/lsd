#!/bin/bash
#
# SGE CONFIGURATION
#
# !!! Memory limit
#$ -hard
#$ -l mem_free=1g
#$ -l act_mem_free=1g
#$ -l h_vmem=1g
#
# Run in this directory
#$ -cwd
#
# Use bash
#$ -S /bin/bash
#
# Export environment variables
#$ -V
#
# Logs
#$ -o /home/rosa/logs
#$ -e /home/rosa/logs
# Do not merge stderr with stdout
#$ -j n
#
# run in troja or ms (but not gpu)
#$ -q '(troja*|ms*)'
#
# send mail: b started, e ended, a aborted or rescheduled, s suspended
# -M rosa@ufal.mff.cuni.cz -m beas
#
# 1 thread
#$ -pe smp 1

# Print each command to STDERR before executing (expanded), prefixed by "+ "
set -o xtrace

renice 10 $$ >&2

# language -- en, cs
l=$1

./udpipe --tokenize --tokenizer=presegmented --output=horizontal $l.udpipe 1.7_fiction_notok/??.$l --outfile=1.7_fiction_udtok_sol7/'{}'.$l


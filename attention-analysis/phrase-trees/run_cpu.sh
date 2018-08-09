#!/bin/bash

qsub -q "cpu-troja.q@*" -hard -l mem_free=8g -l act_mem_free=8g -l h_vmem=8g -cwd -e log_cpu.e -o log_cpu.o translate.sh

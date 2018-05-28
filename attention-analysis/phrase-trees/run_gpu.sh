#!/bin/bash

qsub -q 'gpu.q@dll*' -l gpu_ram=8G -l gpu=1 -cwd -e log.e -o log.o translate.sh

#!/bin/bash

#qsub -q 'gpu.q@dll*' -p 0 -l gpu_ram=8G -l gpu=1 -cwd -e log.e -o log.o translate.sh
qsub -q 'gpu-ms.q@dll*' -p 0 -l gpu_ram=8G -l gpu=1 -cwd -e log.e -o log.o transl-outputproj.sh

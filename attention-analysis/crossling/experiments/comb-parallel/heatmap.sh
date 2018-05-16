#!/bin/bash

source ~/troja/nm/bin/activate
../mixture-visualization.py --attentions dev.att.npz --src_labels dev.src.wps --mt_labels dev.mt.wps --pe_labels dev.pe.wps --heatmaps heatmap --scheme parallel

#!/bin/bash

source /home/marecek/troja/nm/bin/activate
./attentions2tree.py --attentions att.onesentence.npz --alignment ali2.onesentence --labels wps.onesentence --heatmaps heatmap --tree parsed

#!/bin/bash

source ~/troja/nm/bin/activate
../mixture-visualization.py --attentions val.att.npz --en_labels en.val.wps --de_labels de.val.wps --fr_labels fr.val.wps --es_labels es.val.wps --cs_labels cs.val.wps --heatmaps 4lang-flat --scheme flat 

#!/usr/bin/env bash

sed \
    -e 's/(/-LRB-/g' \
    -e 's/)/-RRB-/g' \
    -e 's/\[/-LSB-/g' \
    -e 's/\]/-RSB-/g' \
    -e 's/{/-LCB-/g' \
    -e 's/}/-RCB-/g' \

# also ' is sometimes changed to `

# spaces change but the nonspace characters stay -- so counting positions and ignoring spaces should give the matching...
    
    #-e 's/\([[:alnum:]]\)\([[:punct:]]\)/\1 \2/g' \
    #-e 's/\([[:punct:]]\)\([[:alnum:]]\)/\1 \2/g' \


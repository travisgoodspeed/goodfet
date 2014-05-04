#!/bin/zsh


grep 'aa 55' *.txt | sed 's/\(.*\):.* ff .. .. \(..\) \(..\).*/CALDCO_16MHZ 0x\2 CALBC1_16MHZ 0x\3   \1/'

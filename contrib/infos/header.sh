#!/bin/zsh

echo "// CALDCO_16MHZ, CALBC1_16MHZ"
echo "#define    dco_calibrations_count" `grep 'aa 55' *.txt | wc -l`
echo "const char dco_calibrations[" $((2*`grep 'aa 55' *.txt | wc -l`)) "];"



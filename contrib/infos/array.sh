#!/bin/zsh

echo "// CALDCO_16MHZ, CALBC1_16MHZ"
echo "const char dco_calibrations[]={"
(grep 'aa 55' *.txt | sed 's/\(.*\):.* ff .. .. \(..\) \(..\).*/  0x\2, 0x\3,  \/\/ \1/') | sort
#echo "  0x00         // Null terminator"
echo "};"

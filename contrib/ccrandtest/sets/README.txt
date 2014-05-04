
adctsth.bin	High ADC Byte
adctstl.bin	Low  ADC Byte
random01.bin	PRNG Bytes, Left Handed
random02.bin	PRNG Bytes, Right Handed

Note that random*.bin repeat every 2^15-1 bytes, just under 32kB.
This is because the PRNG has a 16 bit state, two states are skipped,
and only one byte is sampled per tick of the PRNG clock.


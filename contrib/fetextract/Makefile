#MSP430 FET Firmware Extractor
#by Travis Goodspeed

#This extracts the MSP430 FET UIF firmware from MSP430.dll.
#Please note that the resulting file is (C) Texas Instruments,
#and they might object to its distribution.

CC=gcc -g


PORT=/dev/ttyUSB0
BSL=tos-bsl --invert-reset --invert-test -c $(PORT)

app=MSP430FET.hex


run: all
all: MSP430FET.hex


install: $(app)
	$(BSL) -e -p $(app)
	$(BSL) -P $(app) -v $(app)
erase:
	$(BSL) -e 

MSP430FET.hex: fetextract MSP430.dll
	./fetextract
	msp430-objcopy -I binary -O ihex MSP430FET.bin foo.hex
	grep -v "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" <foo.hex >MSP430FET.hex
	rm foo.hex

MSP430FET.asm: MSP430FET.hex
	msp430-objdump -D -m msp430 MSP430FET.hex > MSP430FET.asm

MSP430.dll:
	wget http://www.soft-switch.org/downloads/mspgcc/MSP430.dll
	#echo "f0685a0eca0545dfc542530afff8159f  MSP430.dll" | \
	#md5sum -c || \
	#rm MSP430.dll

clean:
	rm -f fetextract *~ MSP430FET.hex MSP430.dll MSP430FET.bin

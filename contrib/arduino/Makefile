all: blink.hex
clean:
	rm -f *~ *.out *.hex
blink.out: blink.c
	avr-gcc -DF_CPU=16000000UL -mmcu=atmega168 -o blink.out blink.c
blink.hex: blink.out
	avr-objcopy -O ihex -R .eeprom blink.out blink.hex
install: blink.hex
	#328 devices need a faster rate.
	#sudo avrdude -V -F -c stk500v1 -p m168 -b 19200 -P /dev/cu.usbserial-* -U flash:w:blink.hex
	sudo avrdude -V -F -c stk500v1 -p m328p -b 57600 -P /dev/tty.usbserial-* -U flash:w:blink.hex

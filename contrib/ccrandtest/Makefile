
randtest.hex: randtest.c
	sdcc randtest.c
	packihx <randtest.ihx >randtest.hex
install: randtest.hex
	goodfet.cc flash randtest.hex
clean:
	rm *.hex *.ihx

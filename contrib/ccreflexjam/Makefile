

clean:
	rm -f *.hex *.asm *.ihx *.lnk *.lst *.map *.mem *.rel *.rst *.sym
all:
	sdcc --xram-loc 0xF000 ccreflexjam.c
	packihx <ccreflexjam.ihx >ccreflexjam.hex
install: all
	goodfet.cc erase
	goodfet.cc flash ccreflexjam.hex

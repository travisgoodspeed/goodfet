# These targets are compiled to execute at the beginning of RAM.  Each
# should conclude with HALT (0xA5).  Sometimes grabbing code from
# foo.rst will be smaller, especially if no ljmps occur.


# Input and output should be taken from a buffer at 0xFE00.
# "char __xdata at 0xfe00 packet[256] ;"
# Use lower RAM if needed.

CC=sdcc --code-loc 0xF000 
objs=crystal.ihx txpacket.ihx rxpacket.ihx txrxpacket.ihx reflex.ihx rxpacketp25.ihx reflexframe.ihx carrier.ihx specan.ihx

all: $(objs)

%.ihx : %.c
	$(CC) $<
clean:
	rm -f *.ihx *.rel *.hex *.sym *.asm *.lst *.lnk *.map *.mem *.rst *.adb
install: $(objs)
	cp $(objs) ../../../client/shellcode/chipcon/cc1110/
	#Shellcode installed.

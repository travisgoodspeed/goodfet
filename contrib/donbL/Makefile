#
#
#

mcu?=atmega1284p

CC=avr-gcc

LIBS=

#DEBUG=-g -ggdb3 -Werror

# note that the fuses should be set so BOOTRST is programmed and the BOOTSZ
# bits equate to 1024 words of NRWW

# import rules for the specific target mcu
include ./mk/$(mcu).mk

# ensure the type is correct
BL_BYTE_BASE_DEF=$(BL_BYTE_BASE)ULL

CFLAGS=$(DEBUG) -mmcu=$(mcu) -W -Os -mcall-prologues -Wall -Wextra -Wuninitialized -fpack-struct -fshort-enums -funsigned-bitfields -I. -Wl,--section-start=.text=$(BL_BYTE_BASE) -D BL_BYTE_BASE=$(BL_BYTE_BASE_DEF)

BIN=donbL
HEX=$(BIN).hex
CHIP=lib/chip.c
IHEXPY=intelhex.pyc
OBJS=\
	bl.o

all: $(CHIP) $(BIN)

$(CHIP):
	cp lib/$(mcu).c $(CHIP)

clean:
	rm -f $(BIN) $(OBJS) $(HEX) $(EEHEX) $(BLHEX) $(CHIP)
	rm -f $(IHEXPY)

install: all hex flash

# XXX NOTE: the stupid avr-objcopy doesn't copy out sections that are small (i.e. 2 bytes in size) 
hex:
	avr-strip $(BIN)
	avr-objcopy -j .text -j .data -O ihex $(BIN) $(HEX)

flash: flashjtag

flashisp:
	avrdude -e -c stk500v2 -p $(PLATFORM) -P usb -U flash:w:$(HEX) -U lfuse:w:$(LFUSE):m -U hfuse:w:$(HFUSE):m -U efuse:w:$(EFUSE):m

flashjtag:
	avrdude -e -c jtag2 -p $(PLATFORM) -P usb -U flash:w:$(HEX) -U lfuse:w:$(LFUSE):m -U hfuse:w:$(HFUSE):m -U efuse:w:$(EFUSE):m

$(BIN): $(OBJS)
	$(CC) -o $@ $(CFLAGS) $(OBJS) $(LIBS)


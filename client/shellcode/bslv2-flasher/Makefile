AS=msp430-as
OBJCOPY=msp430-objcopy

all: flasher.bin

%.bin: %.elf
	$(OBJCOPY) -O binary $*.elf $*.bin
%.elf: %.s
	$(AS) -mcpu=430xv2 -a -o $*.elf $*.s >$*.lst

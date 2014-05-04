ifeq ($(mcu),atmega328p)
PLATFORM=m328p
BL_BYTE_BASE=0x7800
LFUSE=0xe0
HFUSE=0xda
EFUSE=0xff
endif


ifeq ($(mcu),atmega644p)
PLATFORM=m644p
BL_BYTE_BASE=0xf800
LFUSE=0xe0
HFUSE=0x9c
EFUSE=0xff
endif


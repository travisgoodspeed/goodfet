ifeq ($(mcu),atmega1284p)
PLATFORM=m1284p
BL_BYTE_BASE=0x1f800
LFUSE=0xe0
HFUSE=0x9c
EFUSE=0xff
endif


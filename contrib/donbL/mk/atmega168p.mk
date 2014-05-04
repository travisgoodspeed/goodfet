ifeq ($(mcu),atmega168p)
PLATFORM=m168p
BL_BYTE_BASE=0x3800
LFUSE=0xe0
HFUSE=0xdf
EFUSE=0xf8
endif


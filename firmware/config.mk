##################################
## These are production boards.
##################################

#Unset by default, but can be explicitly overwritten.
config ?= undef

ifneq (,$(findstring $(board),apimote1 apimote))
mcu ?= msp430f2618
platform := apimote
config := monitor spi ccspi
MSP430BSL?=goodfet.bsl --speed=38400 --swap-reset-test
CFLAGS += -Duseuart1 -Dapimote
endif

ifneq (,$(findstring $(board),apimote2))
mcu ?= msp430f2618
platform := apimote2
config := monitor spi ccspi
MSP430BSL?=goodfet.bsl --speed=38400
CFLAGS += -Duseuart1 -Dapimote
endif

ifneq (,$(findstring $(board),goodthopter01 goodthopter10 goodthopter11 goodthopter12))
mcu ?= msp430f2274
platform := goodfet
config := monitor spi
endif

ifneq (,$(findstring $(board),goodfet20 goodfet10 goodfet11))
mcu ?= msp430f1611
platform := goodfet
CONFIG_i2c := n
endif

ifneq (,$(findstring $(board),goodfet21,goodfet22))
mcu ?= msp430f2618
platform := goodfet
endif

ifneq (,$(findstring $(board),goodfet30 goodfet31 goodfet32))
mcu ?= msp430f2274
platform := goodfet
# This will link to fit in a '2254, so unneeded packages should be omited.
CONFIG_ccspi = n
CONFIG_nrf = y
endif

ifneq (,$(findstring $(board),goodfet40 goodfet41 goodfet42))
mcu ?= msp430f2618
platform := goodfet
CONFIG_nrf = y
CONFIG_ccspi = y
endif

ifneq (,$(findstring $(board),stm32f4discovery))

periph ?= /opt/STM32F4xx_StdPeriph_Driver
discovery ?= /opt/STM32F4-Discovery_FW_V1.1.0

usbcore ?= $(discovery)/Libraries/STM32_USB_Device_Library/Core
usbsrc ?= $(usbcore)/src
otginc ?= /opt/STM32F4-Discovery_FW_V1.1.0/Libraries/STM32_USB_OTG_Driver/inc
otgsrc ?= /opt/STM32F4-Discovery_FW_V1.1.0/Libraries/STM32_USB_OTG_Driver/src

pincs ?=  -I$(periph)/inc -I$(usbcore)/inc -I$(otginc) -I$(discovery)/Libraries/CMSIS/ST/STM32F4xx/Include  -I$(discovery)/Libraries/CMSIS/Include -Dassert_param\(x\)= -DUSE_USB_OTG_FS -I/opt/STM32F4-Discovery_FW_V1.1.0/Utilities/STM32F4-Discovery
psrc ?=  /opt/STM32F4xx_StdPeriph_Driver/src


GCC     = arm-none-eabi-gcc
CC      = arm-none-eabi-gcc
LD      = arm-none-eabi-ld -v
AR      = arm-none-eabi-ar
AS      = arm-none-eabi-as
CP      = arm-none-eabi-objcopy
OD	= arm-none-eabi-objdump
CFLAGS  = -c -fno-common -O1 -g -mcpu=cortex-m3 -mthumb $(pincs)
AFLAGS  = -ahls -mapcs-32
LFLAGS  = -Ttmplink.cmd -nostartfiles
CPFLAGS = -Obinary
ODFLAGS	= -S
LDFLAGS = 


mcu ?= stm32f407
platform := stm32f4discovery
config = monitor

# This is a pain.
#usblibs =  $(usbsrc)/usbd_core.o $(usbsrc)/usbd_req.o $(usbsrc)/usbd_ioreq.o $(usbsrc)/usbd_core.o $(otgsrc)/usb_dcd.o $(otgsrc)/usb_dcd_int.o $(otgsrc)/usb_hcd.o $(otgsrc)/usb_hcd_int.o $(otgsrc)/usb_otg.o
extralibs = lib/cortexm3.o lib/system_stm32f4xx.o lib/stm32f4xx_rcc.o $(psrc)/stm32f4xx_gpio.o $(psrc)/stm32f4xx_usart.o $(usblibs) 

endif

ifneq (,$(findstring $(board),facedancer10 facedancer11 facedancer20 facedancer21 nsb2013))
mcu ?= msp430f2618
platform := goodfet
config = monitor spi maxusb
endif

ifeq ($(board),z1)
mcu ?= msp430f2617
platform := z1
config = monitor spi ccspi
MSP430BSL?=goodfet.bsl --z1  --speed=38400
endif

ifneq (,$(findstring $(board),goodfet24))
mcu ?= msp430f2618
platform := goodfet
CONFIG_glitch = y
CONFIG_nrf = y
endif

ifneq (,$(findstring $(board),nhb12b))
mcu ?= msp430f2618
CONFIG_nrf = y
platform := nhb12b
endif

ifneq (,$(findstring $(board),nhb12))
mcu ?= msp430f2618
CONFIG_nrf = y
platform := nhb12
endif

ifneq (,$(findstring $(board),goodfet50 goodfet51))
mcu ?= msp430f5510
platform := goodfet
endif

ifeq ($(board),telosb)
mcu ?= msp430f1611
platform := telosb
config := monitor spi ccspi
CFLAGS += -Duseuart1
endif

ifeq ($(board),telosbbt)
mcu ?=msp430f1612
platform := telosb
config := monitor spi ccspi
endif




##################################
## These are experimental boards.
##################################

ifneq (,$(findstring $(board),donbfet))
GCC := avr-gcc
CC := avr-gcc
mcu ?= atmega644p
platform = donbfet
CFLAGS=$(DEBUG) -Iinclude -mmcu=$(mcu) -W -Os -mcall-prologues -Wall -Wextra -Wuninitialized -fpack-struct -fshort-enums -funsigned-bitfields
config := monitor avr spi jscan
endif

ifneq (,$(findstring $(board),zigduino))
GCC := avr-gcc
CC := avr-gcc
mcu ?= atmega128rfa1
platform = zigduino
CFLAGS=$(DEBUG) -Iinclude -mmcu=$(mcu) -W -Os -mcall-prologues -Wall -Wextra -Wuninitialized -fpack-struct -fshort-enums -funsigned-bitfields
config := monitor atmel_radio #avr spi
AVR_PLATFORM := m128rfa1
endif


ifneq (,$(findstring $(board),arduino))
GCC := avr-gcc
mcu ?= atmega168
#BSL := avrdude -V -F -c stk500v1 -p m328p -b 57600 -P /dev/tty.usbserial-* -U flash:w:blink.hex
LDFLAGS := 
config := monitor
endif

ifneq (,$(findstring $(board),tilaunchpad))
mcu ?=msp430f1612
CFLAGS := -DDEBUG_LEVEL=3 -DDEBUG_START=1 -DINBAND_DEBUG
CFLAGS+= -Wall
config := monitor chipcon i2c
endif



mcu ?= undef
ifeq ($(mcu),undef)
$(error Please define board, as explained in the README)
endif
#platform := $(board)

AVAILABLE_APPS = monitor spi jtag sbw jtag430 jtag430x2 i2c jtagarm7 ejtag jtagxscale openocd chipcon avr pic adc nrf ccspi glitch smartcard ps2 slc2  maxusb atmel_radio cc2500

# defaults
CONFIG_monitor    ?= y
CONFIG_spi        ?= y
CONFIG_maxusb     ?= y
CONFIG_jtag       ?= n
CONFIG_sbw        ?= n
CONFIG_jtag430    ?= y
CONFIG_jtag430x2  ?= y
CONFIG_i2c        ?= y
CONFIG_jtagarm7   ?= y
CONFIG_ejtag      ?= n
CONFIG_jtagxscale ?= n
CONFIG_openocd    ?= y
CONFIG_chipcon    ?= y
CONFIG_avr        ?= y
CONFIG_pic        ?= n
CONFIG_adc        ?= n
CONFIG_nrf        ?= n
CONFIG_ccspi      ?= n
CONFIG_cc2500     ?= y
CONFIG_glitch     ?= n
CONFIG_smartcard  ?= n
CONFIG_ps2        ?= n
CONFIG_slc2       ?= n
CONFIG_atmel_radio ?=n

#The CONFIG_foo vars are only interpreted if $(config) is "unset".
ifeq ($(config),undef)
config += $(foreach app,$(AVAILABLE_APPS),$(if $(findstring $(CONFIG_$(app)),y yes t true Y YES T TRUE),$(app)))
endif

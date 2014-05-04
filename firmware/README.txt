GoodFET Firmware
by Travis Goodspeed <travis at radiantmachines.com>
and some damned good neighbors.

Set $GOODFET to be the port of your GoodFET, such as
export GOODFET=/dev/cu.usbserial-*      #Darwin
export GOODFET=/dev/ttyUSB*             #Linux (Default)

The target board must be specified.  For example,
board=goodfet31 make clean install
board=goodfet41 make clean install
board=telosb make clean install

We require at least msp430-gcc-4.4.5, but older versions might work if
you're lucky.

For faster startup times, it helps to write a static clock
configuration into the firmware.  In the following example, the proper
DCO happens to be 0x8F8A.

pro% goodfet.monitor info
GoodFET with f26f MCU
Clocked at 0x8f8a
pro% board=goodfet41 CFLAGS='-DSTATICDCO=0x8f8a' make clean install

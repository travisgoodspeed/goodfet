#!/usr/bin/env python3
#
# facedancer-lcd.py

# This is an emulator for USBLCD devices supported by the usblcd.ko
# driver in Linux.  They enumerate as 10D2:0001 and seem to be the
# nearly the same protocol as the simple serial class used by the HP4X
# graphing calculators.  No ioctls are supported, but otherwise the
# /dev/LCD* device acts like any other character device.

from Facedancer import *
from MAXUSBApp import *
from USBSerial import *

sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBSerialDevice(u, verbose=4)

#Patch some settings to make an LCD device.
d.vendor_id=0x10D2;
d.product_id=0x0001;

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()


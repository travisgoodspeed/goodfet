#!/usr/bin/env python3
#
# facedancer-serial.py

from Facedancer import *
from MAXUSBApp import *
from USBSerial import *

sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBSerialDevice(u, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()

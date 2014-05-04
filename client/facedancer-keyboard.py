#!/usr/bin/env python3
#
# facedancer-keyboard.py

from Facedancer import *
from MAXUSBApp import *
from USBKeyboard import *

sp = GoodFETSerialPort()
fd = Facedancer(sp, verbose=1)
u = MAXUSBApp(fd, verbose=1)

d = USBKeyboardDevice(u, verbose=4)

d.connect()

try:
    d.run()
# SIGINT raises KeyboardInterrupt
except KeyboardInterrupt:
    d.disconnect()

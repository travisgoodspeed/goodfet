#!/usr/bin/env python3
#
# facedancer-monitor.py

from Facedancer import *

sp = GoodFETSerialPort(timeout=1)
fd = Facedancer(sp)

fd.monitor_app.print_info()
fd.monitor_app.list_apps()

res = fd.monitor_app.echo("I am the very model of a modern major general.")

if res == 0:
    print("echo failed")
else:
    print("echo succeeded")

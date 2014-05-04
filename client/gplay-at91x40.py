#!/usr/bin/env ipython
import sys, struct, binascii,time
from GoodFETAT91X40 import *
from intelhex import IntelHex


data = []

client=GoodFETAT91X40();
def init():
    #Initailize FET and set baud rate
    print >>sys.stderr,"Connecting to goodfet..."
    client.serInit()
    #
    #Connect to target
    print >>sys.stderr,"Setting up JTAG ARM on goodfet..."
    client.setup()
    print >>sys.stderr,"Starting JTAG ARM on goodfet...\n"
    client.start()
    print "STARTUP: %s\n"%repr(client.data)
    client.disableWatchDog()
    #

def print_registers():
    return [ hex(client.ARMget_register(x)) for x in range(15) ]


init()


def printResults():
    for y in range(len(results)):
            x=results[y]
            print "%.2x=%s"%(y,repr(["%x"%t for t in x]))


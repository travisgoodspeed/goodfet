#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, os;
import binascii;

from GoodFET import GoodFET;
from intelhex import IntelHex;


#grep CMD GoodFETConsole.py | grep def | sed s/\(sel.\*// | sed 's/def CMD//'

class GoodFETRadio():
    """An interactive goodfet driver."""
    
    def __init__(self, client):
        self.client=client;
    def start(self):
        client=self.client;
        client.serInit();
        client.setup();
        client.start();
        client.loadsymbols();
        
    def stop(self):
        self.client.stop();
    
    def test(self):
        print "Trying all functions.";
        self.setfreq(2.481*10**9);
        self.getfreq();
        
    def carrier(self):
        """Hold a carrier wave on the present frequency."""
        self.client.RF_carrier();
    def setfreq(self,freq):
        """Set the center frequency in Hz."""
        self.client.RF_setfreq(freq);
    def getfreq(self):
        """Get the center frequency in Hz."""
        return self.client.RF_getfreq();
    def getrssi(self):
        """Get the received signal strength as a float from 0 to 1."""
        return self.client.RF_getrssi();

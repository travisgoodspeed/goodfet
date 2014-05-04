#!/usr/bin/env python
# GoodFET Atmel 2-wire EEPROM client library
# 

import sys, time, string, cStringIO, struct, glob, serial, os;

from GoodFET import GoodFET;

class GoodFETtwe(GoodFET):
    
    JEDECsize=0;

    def setup(self):
        """Move the FET into the SPI application."""
        self.writecmd(0x05, 0x10, 0, []) # SETUP
    
    def peekblock(self, adr):
        """Grab a few block from an SPI Flash ROM.  Block size is unknown"""
        data = [adr&0xFF, (adr&0xFF00)>>8]
        
        self.writecmd(0x05, 0x02, 2, data) # PEEK
        return self.data
    


#!/usr/bin/env python
# GoodFET Atmel 2-wire EEPROM client library
# 

import sys, time, string, cStringIO, struct, glob, serial, os, binascii;

from GoodFET import GoodFET;

class GoodFETowe(GoodFET):
    
    def setup(self):
        """Move the FET into the 1-wire application."""
        self.writecmd(0x05, 0x10, 0, [])      # SETUP
        if self.verb != 0:
            print "Setup failed"
            sys.exit(-1);
    
    def reset(self):
        self.writecmd(0x05, 0x20, 0, [])      # Generate Reset Pulse
        if self.verb != 0:
            print "Device did not responde"
            sys.exit(-1);
    
    def read(self):
        self.writecmd(0x05, 0x00, 0, [])      # Read Byte
        if self.verb != 0:
            print "Read failed"
            sys.exit(-1);
        return self.data
    
    def write(self, value):
        self.writecmd(0x05, 0x01, 1, [value]) # Send Byte
        if self.verb != 0:
            print "Write failed"
            sys.exit(-1);
        return self.data
    
    def sendCommand(self, cmd):
        self.reset();
        self.write(cmd);

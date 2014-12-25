#!/usr/bin/env python
# GoodFET Atmel 2-wire EEPROM client library
# 

import sys, time, string, cStringIO, struct, glob, serial, os, binascii;

from GoodFET import GoodFET;

class GoodFETowe(GoodFET):
    
    def setup(self):
        """Move the FET into the 1-wire application."""
        self.writecmd(0x81, 0x01, 0, [])      # SETUP
        if self.verb != 0:
            print "Setup Failed"
            sys.exit(-1);
            
    def sendCommand(self, cmd):
        self.writecmd(0x81, 0x02, 0, [])      # Generate Reset Pulse 
        if self.verb != 0:
            print "Device did not Responde"
            sys.exit(-1);
            
        self.writecmd(0x81, 0x03, 1, [cmd])   # Send Command
        if self.verb != 0:
            print "Send Command Failed"
            sys.exit(-1);        
        
    def writeValue(self, cmd, value):
        self.sendCommand(cmd);
        self.writecmd(0x81, 0x03, 1, [value]) # Send Value
        if self.verb != 0:
            print "Send Command Failed"
            sys.exit(-1);
            
    def read(self):
        self.writecmd(0x81, 0x04, 0, [])      # Receive Response
        if self.verb != 0:
            print "Receive Response Failed"
            sys.exit(-1);    
        return self.data
            
    def readValue(self, cmd):
        self.sendCommand(cmd);
        self.read();
        return self.data

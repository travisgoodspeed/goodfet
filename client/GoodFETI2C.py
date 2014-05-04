#!/usr/bin/env python
# GoodFET I2C and I2Ceeprom Client Library
# 
# Pre-alpha.  You've been warned!

#import sys, time, string, cStringIO, struct, glob, serial, os

from GoodFET import GoodFET

APP_I2C = 0x02
CMD_READ = 0x00
CMD_WRITE = 0x01
CMD_PEEK = 0x02
CMD_SETUP = 0x10
CMD_START = 0x20
CMD_STOP = 0x21
CMD_SCAN = 0x80


class GoodFETI2C(GoodFET):
    def I2Csetup(self):
        """Move the FET into the I2C application."""
        self.writecmd(APP_I2C, CMD_SETUP)

    def I2Cstart(self):
        """Produce Start condition on I2C bus"""
        self.writecmd(APP_I2C, CMD_START)

    def I2Cstop(self):
        """Produce Stop condition on I2C bus"""
        self.writecmd(APP_I2C, CMD_STOP)

    def I2Cread(self, count=1):
        """Read data from I2C."""
        self.writecmd(APP_I2C, CMD_READ, 1, [count])

    def I2Cwritebytes(self, data):
        """Write multiple bytes to I2C."""
        self.writecmd(APP_I2C, CMD_WRITE, len(data), data)

    def I2Cwritebyte(self, val):
        """Write a single byte to I2C."""
        self.I2Cwritebytes([val])

    def I2Ctrans(self, readcount, data):
        """Use PEEK to do a multi-start transaction"""
        return self.writecmd(APP_I2C, CMD_PEEK, len(data) + 1, [readcount] + data)

    def I2Cscan(self):
        """Scan the I2C and returns all 7 bit addresses that can be talked to"""
        rv = []
        for addr in xrange(256):
            self.writecmd(APP_I2C, CMD_SCAN, 1, [addr])
            if len(self.data) > 0:
                rv.append(ord(self.data[0]))
        return rv

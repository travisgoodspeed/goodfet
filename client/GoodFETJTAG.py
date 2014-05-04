#!/usr/bin/env python
# GoodFET Basic JTAG Client

import sys, binascii, struct

# Standard verbs
READ  = 0x00
WRITE = 0x01
PEEK  = 0x02
POKE  = 0x03
SETUP = 0x10
START = 0x20
STOP  = 0x21
CALL  = 0x30
EXEC  = 0x31
NOK   = 0x7E
OK    = 0x7F

# JTAG commands
JTAG_RESET_TAP              = 0x82
JTAG_RESET_TARGET           = 0x83
JTAG_DETECT_IR_WIDTH        = 0x84
JTAG_DETECT_CHAIN_LENGTH    = 0x85
JTAG_GET_DEVICE_ID          = 0x86

from GoodFET import GoodFET
from intelhex import IntelHex

class GoodFETJTAG(GoodFET):

    """A GoodFET variant for basic JTAG'ing."""

    JTAGAPP=0x10;
    APP=JTAGAPP;
 
    def _check_return(self, verb, length=0):
        if (self.app == self.APP) and \
           (self.verb == verb) and \
           (len(self.data) == length):
            print "OK"
            return True
        print "Failed!"
        return False

    def setup(self):
        """Move the FET into the JTAG configuration."""
        sys.stdout.write("Initializing JTAG...")
        self.writecmd(self.APP, SETUP)
        self._check_return(SETUP)

    def reset_tap(self):
        sys.stdout.write("Resetting TAP...")
        self.writecmd(self.APP, JTAG_RESET_TAP)
        self._check_return(JTAG_RESET_TAP)

    def reset_target(self):
        sys.stdout.write("Resseting target device...")
        self.writecmd(self.APP, JTAG_RESET_TARGET)
        self._check_return(JTAG_RESET_TARGET)

    def detect_ir_width(self):
        sys.stdout.write("Detecting IR width...")
        self.writecmd(self.APP, JTAG_DETECT_IR_WIDTH)
        self._check_return(JTAG_DETECT_IR_WIDTH, 2)
        width = struct.unpack("!H", self.data)[0]
        return width

    def detect_chain_length(self):
        sys.stdout.write("Detecting chain length...")
        self.writecmd(self.APP, JTAG_DETECT_CHAIN_LENGTH)
        self._check_return(JTAG_DETECT_CHAIN_LENGTH, 2)
        length = struct.unpack("!H", self.data)[0]
        return length

    def get_device_id(self, chip):
        sys.stdout.write("Getting ID for device %d..." % chip)
        self.writecmd(self.APP, JTAG_GET_DEVICE_ID, 2, struct.pack("!H", chip))
        self._check_return(JTAG_GET_DEVICE_ID, 4)
        id = struct.unpack("!L", self.data)[0]
        return id



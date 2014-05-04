#!/usr/bin/env python
# GoodFET XScale JTAG Client

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

# XSCALE JTAG verbs
# verbs start at 0xF0

from GoodFETJTAG import GoodFETJTAG
from intelhex import IntelHex

class GoodFETXSCALE(GoodFETJTAG):

    """A GoodFET variant for use with XScale processors."""

    XSCALEAPP=0x15;
    APP=XSCALEAPP;

    def setup(self):
        """Move the FET into the JTAG ARM application."""
        sys.stdout.write("Initializing XScale...")
        self.writecmd(self.APP, SETUP)
        self._check_return(SETUP)

    def start(self):
        """Start debugging."""
        sys.stdout.write("Staring session...")
        self.writecmd(self.APP, START)
        self._check_return(START)

    def stop(self):
        """Stop debugging."""
        sys.stdout.write("Stopping session...")
        self.writecmd(self.APP, STOP)
        self._check_return(STOP)



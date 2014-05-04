#!/usr/bin/env python
# GoodFET ARM9 Client Library
# 
# Contributions and bug reports welcome.
#
# todo:
#  * full cycle debugging.. halt to resume
#  * ensure correct PC handling
#  * flash manipulation (probably need to get the specific chip for this one)
#  * set security (chip-specific)

import sys, binascii, struct, time
import atlasutils.smartprint as asp
from GoodFET import GoodFET
from GoodFETARM7 import *
from intelhex import IntelHex






















class GoodFETARM9(GoodFETARM7):
    def start(self):
        GoodFETARM7.start(self)
        self.ARMsetSCANsize(5)

    def ARMreadMem(self, adr, wordcount=0):
        """ Only works in ARM mode currently
        WARNING: Addresses must be word-aligned!
        """
        regs = self.ARMget_registers()
        self.ARMset_registers([0xdeadbeef for x in xrange(14)], 0xe)
        output = []
        count = wordcount
        while (wordcount > 0):
            count = (wordcount, 0xe)[wordcount>0xd]
            bitmask = LDM_BITMASKS[count]
            self.ARMset_register(14,adr)
            self.ARMdebuginstr(ARM_INSTR_LDMIA_R14_r0_rx | bitmask ,0)
            self.ARM_nop(1)
            #FIXME: do we need the extra nop here?
            self.ARMrestart()
            self.ARMwaitDBG()
            output.extend([self.ARMget_register(x) for x in xrange(count)])
            wordcount -= count
            adr += count*4
            #print hex(adr)
        # FIXME: handle the rest of the wordcount here.
        self.ARMset_registers(regs,0xe)
        return output

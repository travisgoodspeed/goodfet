"""
http://www.tonews.com/thread/1644423/comp/sys/arm/getting_chip_selects_working_after_remap_on_the_at91r40008.html

This sets the base to 0x00000000 (illegal).
If you would like to have it at 0x00400000, change the register to
0x0040203E.

The base address contains the real top bits of the base address, no offset
from the range base.

I'd start addressing from e.g. 0x01000000, so all sizes will fit in. There
are plenty of free addresses with the AT91: you can fill only 64 Mbytes of
the 4 Gbytes of address space.
"""

class M29W640G:
    """def __init__(self, addrE, pinE, addrG, pinG, addrW, pinW, chipnum, chip_base_addr=0x1000000):
        self.addrE = addrE
        self.pinE = pinE
        self.addrG = addrG
        self.pinG = pinG
        self.addrW = addrW
        self.pinW pinW
        self.chipnum = chipnum
        self.base_addr = chip_base_addr
        """
    def __init__(self, gfclient, chipnum, chip_base_addr=0x10000000):
        self.gfclient = gfclient
        self.chipnum = chipnum
        self.base_addr = chip_base_addr

    def ChipErase(self, rusure=False):
        if rusure:
            self.gfclient.writeMemByte(self.base_addr + 0x555, [0xaa])
            self.gfclient.writeMemByte(self.base_addr + 0x2aa, [0x55])
            self.gfclient.writeMemByte(self.base_addr + 0x555, [0x80])
            self.gfclient.writeMemByte(self.base_addr + 0x555, [0xaa])
            self.gfclient.writeMemByte(self.base_addr + 0x2aa, [0x55])
            self.gfclient.writeMemByte(self.base_addr + 0x555, [0x10])

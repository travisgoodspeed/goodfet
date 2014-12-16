#!/usr/bin/env python
# GoodFET SPI and SPIFlash Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, os;

from GoodFET import GoodFET;

class GoodFETSPI(GoodFET):
    APP=0x01;
    def SPIsetup(self):
        """Move the FET into the SPI application."""
        self.writecmd(0x01,0x10,0,self.data); #SPI/SETUP
        
    def SPItrans8(self,byte):
        """Read and write 8 bits by SPI."""
        data=self.SPItrans([byte]);
        return ord(data[0]);
    
    def SPItrans(self,data):
        """Exchange data by SPI."""
        self.data=data;
        self.writecmd(0x01,0x00,len(data),data);
        return self.data;

class GoodFETSPI25C(GoodFETSPI):
    #opcodes
    WREN=0x06;
    WRDI=0x04;
    RDSR=0x05;
    WRSR=0x01;
    READ=0x03;
    WRITE=0x02;
    
    def peek8(self,adr,memory="vn"):
        """Read a byte from the given address."""
        data=self.SPItrans([self.READ,(adr>>8)&0xFF,adr&0xFF,0x00]);
        return ord(data[3]);


class GoodFETZensys(GoodFETSPI):
    PROG_ENABLE = 0x83
    WRITE3_READ1 = 0x84
    WRITE2_READ2 = 0x85

    def programming_enable(self):
        self._wrt_defined = False
        for i in range(32):  # Doc says that sync may take up to 32 times (sic)
            self.writecmd(self.APP, self.PROG_ENABLE, 4, [0xac, 0x53, 0x00, 0x00])
            # print "Got %s - Expecting 0x53" % (" ".join(["%02x" % ord(x) for x in self.data[:4]]))
            if ord(self.data[2]) == 0x53:
                return i  # sync successful
        return -1

    def chip_erase(self):
        """Clear all pages including the information block"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        self.SPItrans([0xac, 0x80, 0x00, 0x00])
        time.sleep(0.5)  # gives enough time to erase memory
        return True

    def program_memory_erase(self):
        """Clear all pages exluding the information block"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        self.SPItrans([0xac, 0xa0, 0x00, 0x00])
        time.sleep(0.5)  # gives enough time to erase memory
        return True

    def page_erase(self, page_number):
        """Erase program memory at given address"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        self.SPItrans([0xac, 0xc0, page_number & 0x7f, 0x00])
        time.sleep(0.05)  # gives enough time to erase memory
        return True

    def read_program_memory(self, address):
        """Read byte at given address"""
        #print "\tRead 0x%06x [%s]" % (address, ",".join(["%02X" % x for x in [0x20 | (address & 1) << 3, (address >> 8) & 0x7f, address & 0xfe, 0x00]]))
        self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x20 | (address & 1) << 3,
                                                       (address >> 8) & 0x7f,
                                                       address & 0xfe, 0x42])
        return ord(self.data[0])

    def load_program_memory(self, offset, val):
        """Write val to SRAM page buffer at offset. val and offset are 8bit values"""
        self.SPItrans([0x40 | (offset & 1) << 3, 0x00, offset & 0xff, val & 0xff])

    def write_program_memory(self, page_number):
        """Write the SRAM page buffet into flash at the given page"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        self.SPItrans([0x4c, page_number & 0x7f, 0x00, 0x00])
        time.sleep(0.02)  # gives enough time to write memory
        return True

    def read_lock_bits(self):
        """Read lock bits. '1' = unprogrammed. '0' = programmed"""
        self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x54, 0x00, 0x00, 0x00])
        return [(ord(self.data[0]) >> x) & 1 for x in range(5)]

    def write_lock_bits(self, bit0=1, bit1=1, bit2=1, bit3=1, bit4=1):
        """Write lock bits. Set bits 0-4 to '0' to set lock on flash"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        lock_byte = 0
        for b in (bit4, bit3, bit2, bit1, bit0):
            lock_byte += b & 1
            lock_byte <<= 1
        self.SPItrans([0xac, 0xe0, 0x00, lock_byte])
        return True

    def protect_flash_memory(self):
        """Flash memory will not be readable anymore after this command"""
        return self.write_lock_bits(bit0=0)

    def set_bootsector_size(self, size=0):
        """Defines a read-only portion for bootsector."""
        _lookup = {
            0: 0b111,
            512: 0b110,
            1024: 0b101,
            2048: 0b100,
            4096: 0b011,
            8192: 0b010,
            16384: 0b001,
            32768: 0b000
        }
        if size not in _lookup:
            print "Invalid size. Must be %s" % " or ".join(["%d" % x for x in _lookup.keys()])
            return False
        self.write_lock_bits(bit1=_lookup[size] & 1, bit2=(_lookup[size] & 2) >> 1, bit3=(_lookup[size] & 4) >> 2)
        return True

    def protect_page0(self):
        """Sets the first page as a read-only memory zone"""
        return self.write_lock_bits(bit4=0)

    def set_write_cycle_time(self, osc_freq=32000000):
        """Set number of clock cycles for flash programming according to XTAL freq"""
        self.SPItrans([0xac, 0x5d, 0x00, int((0.000025 * osc_freq) / 64)])
        self._wrt_defined = True

    def read_signature(self):
        """Returns all the 7 bytes of signature"""
        sig = []
        for i in range(7):
            self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x30, 0x00, i, 0x00])
            sig.append(ord(self.data[0]))
        return sig

    def SPIjedec(self):
        """Reads the JEDEC ID"""
        jedec = []
        for i in range(5):
            self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x30, 0x00, i, 0x00])
            jedec.append(ord(self.data[0]))
        return jedec

    def read_chip_type(self):
        self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x30, 0x00, 0b101, 0x00])
        return ord(self.data[0])

    def read_chip_revision(self):
        self.writecmd(self.APP, self.WRITE3_READ1, 4, [0x30, 0x00, 0b110, 0x00])
        return ord(self.data[0])

    def read_chip_info(self):
        """Returns the tuple (chip type, chip revision)"""
        return [self.read_chip_type(), self.read_chip_revision()]

    def write_infodata(self, data):
        """Write the 4 byte infodata memory"""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        if len(data) != 4:
            print "Infodata block is 4 byte"
            return False
        self.SPItrans([0xac, 0x00, data[0], data[1]])
        self.SPItrans([0xac, 0x10, data[2], data[3]])
        return True

    def read_infodata(self):
        """Reads the 4 bytes infodata memory"""
        infodata = []
        self.writecmd(self.APP, self.WRITE2_READ2, 4, [0xac, 0x20, 0x00, 0x00])
        infodata += [ord(self.data[0]), ord(self.data[1])]
        self.writecmd(self.APP, self.WRITE2_READ2, 4, [0xac, 0x30, 0x00, 0x00])
        infodata += [ord(self.data[0]), ord(self.data[1])]
        return infodata

    def read_page(self, page_number):
        """Reads a whole page"""
        page = []
        for i in range(256):
            page.append(self.read_program_memory(256 * page_number + i))
        return page

    def write_page(self, page_number, data):
        """Write a whole page. Page is NOT erased first with this command."""
        if not self._wrt_defined:
            print "Please, call set_write_cycle_time() first"
            return False
        if len(data) > 256:
            print "data must fit in one page (256 bytes max)"
            return False
        for i in range(len(data)):
            self.load_program_memory(256 * page_number + i, data[i])
        self.write_program_memory(page_number)
        return True


class GoodFETSPIFlash(GoodFETSPI):
    JEDECmanufacturers={0xFF: "MISSING",
                        0xEF: "Winbond",
                        0xC2: "MXIC",
                        0x20: "Numonyx/ST",
                        0x1F: "Atmel",
                        0x1C: "eON",
                        0x01: "AMD/Spansion"
                        };

    JEDECdevices={0xFFFFFF: "MISSING",
                  0xEF3015: "W25X16L",
                  0xEF3014: "W25X80L",
                  0xEF3013: "W25X40L",
                  0xEF3012: "W25X20L",
                  0xEF3011: "W25X10L",
                  0xC22017: "MX25L6405D",
                  0xC22016: "MX25L3205D",
                  0xC22015: "MX25L1605D",
                  0xC22014: "MX25L8005",
                  0xC22013: "MX25L4005",
                  0x204011: "M45PE10",
                  0x202014: "M25P80",
                  0x1f4501: "AT24DF081",
                  0x1C3114: "EN25F80",
                  };
    
    JEDECsizes={0x17: 0x800000,
                0x16: 0x400000,
                0x15: 0x200000,
                0x14: 0x100000,
                0x13: 0x080000,
                0x12: 0x040000,
                0x11: 0x020000
                };
    
    JEDECsize=0;

    def SPIjedec(self):
        """Grab an SPI Flash ROM's JEDEC bytes.  Some chips don't implement
        this, such as Numonyx M25P* except in the 110nm processed."""
        data=[0x9f, 0, 0, 0];
        data=self.SPItrans(data);
        jedec=0;
        self.JEDECmanufacturer=ord(data[1]);
        if self.JEDECmanufacturer==0xFF:
            self.JEDECtype=0x20;
            self.JEDECcapacity=0x14;
            jedec=0x202014;
        else:
            self.JEDECtype=ord(data[2]);
            self.JEDECcapacity=ord(data[3]);
            jedec=(ord(data[1])<<16)+(ord(data[2])<<8)+ord(data[3]);
        self.JEDECsize=self.JEDECsizes.get(self.JEDECcapacity);
        if self.JEDECsize==None:
            self.JEDECsize=0;
        
        if jedec==0x1F4501:
            self.JEDECsize=1024**2;
        self.JEDECdevice=jedec;
        return data;
    def SPIpeek(self,adr):
        """Grab a byte from an SPI Flash ROM."""
        data=[0x03,
              (adr&0xFF0000)>>16,
              (adr&0xFF00)>>8,
              adr&0xFF,
              0];
        self.SPItrans(data);
        return ord(self.data[4]);
    def SPIpeekblock(self,adr):
        """Grab a few block from an SPI Flash ROM.  Block size is unknown"""
        data=[(adr&0xFF0000)>>16,
              (adr&0xFF00)>>8,
              adr&0xFF];
        
        self.writecmd(0x01,0x02,3,data);
        return self.data;
    
    def SPIpokebyte(self,adr,val):
        self.SPIpokebytes(adr,[val]);
    def SPIpokebytes(self,adr,data):
        #Used to be 24 bits, BE, not 32 bits, LE.
        adranddata=[adr&0xFF,
                    (adr&0xFF00)>>8,
                    (adr&0xFF0000)>>16,
                    0, #MSB
                    ]+data;
        #print "%06x: poking %i bytes" % (adr,len(data));
        self.writecmd(0x01,0x03,
                      len(adranddata),adranddata);
        
    def SPIerasesector(self,adr):
        #24 bits, BE, not 32 bits, LE.
        adranddata=[adr&0xFF,
                    (adr&0xFF00)>>8,
                    (adr&0xFF0000)>>16,
                    0, #MSB
                    ];
        self.writecmd(0x01,0x86,
                      len(adranddata),adranddata);

    def SPIchiperase(self):
        """Mass erase an SPI Flash ROM."""
        self.writecmd(0x01,0x81);
    def SPIwriteenable(self):
        """SPI Flash Write Enable"""
        data=[0x06];
        self.SPItrans(data);
        
    def SPIjedecmanstr(self):
        """Grab the JEDEC manufacturer string.  Call after SPIjedec()."""
        man=self.JEDECmanufacturers.get(self.JEDECmanufacturer)
        if man==0:
            man="UNKNOWN";
        return man;
    
    def SPIjedecstr(self):
        """Grab the JEDEC manufacturer string.  Call after SPIjedec()."""
        man=self.JEDECmanufacturers.get(self.JEDECmanufacturer);
        if man==0:
            man="UNKNOWN";
        device=self.JEDECdevices.get(self.JEDECdevice);
        if device==0:
            device="???"
        return "%s %s" % (man,device);

    def SPIreadstatusregister(self):
        """Read the status register."""
        data=[0x05,
            0];
        self.SPItrans(data);
        return ord(self.data[1]);

    def SPIwritestatusregister(self, val):
        """Write the status register."""
        data=[0x01,
            val];
        self.SPIwriteenable();
        self.SPItrans(data);

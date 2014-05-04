#!/usr/bin/env python
# GoodFET Chipcon RF Radio Client for CC2500
#
# (C) 2013 Jean-Michel Picod <jean-michel.picod at cassidian.com>
#

import time
import math

from GoodFET import GoodFET

class GoodFETCC2500(GoodFET):
    APP       = 0x52
    READ      = 0x00
    WRITE     = 0x01
    PEEK      = 0x02
    POKE      = 0x03
    SETUP     = 0x10
    TX        = 0x81
    RX        = 0x80
    REPEAT_RX = 0x91

    _chips = {
        0x8003: "CC2500",
        0x800f: "CC2500",
        0x0204: "CC1150"
    }
    _regnames = [
        "IOCFG2", "IOCFG1", "IOCFG0", "FIFOTHR", "SYNC1", "SYNC0",
        "PKTLEN", "PKTCTRL1", "PKTCTRL0", "ADDR", "CHANNR",
        "FSCTRL1", "FSCTRL0", "FREQ2", "FREQ1", "FREQ0",
        "MDMCFG4", "MDMCFG3", "MDMCFG2", "MDMCFG1", "MDMCFG0", "DEVIATN",
        "MCSM2", "MCSM1", "MCSM0", "FOCCFG", "BSCFG", "AGCCTRL2",
        "AGCCTRL1", "AGCCTRL0", "WOREVT1", "WOREVT0", "WORCTRL",
        "FREND1", "FREND0", "FSCAL3", "FSCAL2", "FSCAL1", "FSCAL0",
        "RCCTRL1", "RCCTRL0", "FSTEST", "PTEST", "AGCTEST", "TEST2",
        "TEST1", "TEST0", "?",
        ## Strobes
        "SRES", "SFSTXON", "SXOFF", "SCAL", "SRX", "STX", "SIDLE",
        "?", "SWOR", "SPWD", "SFRX", "SFTX", "SWORRST", "SNOP",
        "PATABLE", "TXFIFO",
        "IOCFG2", "IOCFG1", "IOCFG0", "FIFOTHR", "SYNC1", "SYNC0",
        "PKTLEN", "PKTCTRL1", "PKTCTRL0", "ADDR", "CHANNR",
        "FSCTRL1", "FSCTRL0", "FREQ2", "FREQ1", "FREQ0",
        "MDMCFG4", "MDMCFG3", "MDMCFG2", "MDMCFG1", "MDMCFG0", "DEVIATN",
        "MCSM2", "MCSM1", "MCSM0", "FOCCFG", "BSCFG", "AGCCTRL2",
        "AGCCTRL1", "AGCCTRL0", "WOREVT1", "WOREVT0", "WORCTRL",
        "FREND1", "FREND0", "FSCAL3", "FSCAL2", "FSCAL1", "FSCAL0",
        "RCCTRL1", "RCCTRL0", "FSTEST", "PTEST", "AGCTEST", "TEST2",
        "TEST1", "TEST0", "?",
        "?", "?", "?", "?", "?", "?", "?",
        "?", "?", "?", "?", "?", "?", "?",
        "PATABLE", "TXFIFO",
        "IOCFG2", "IOCFG1", "IOCFG0", "FIFOTHR", "SYNC1", "SYNC0",
        "PKTLEN", "PKTCTRL1", "PKTCTRL0", "ADDR", "CHANNR",
        "FSCTRL1", "FSCTRL0", "FREQ2", "FREQ1", "FREQ0",
        "MDMCFG4", "MDMCFG3", "MDMCFG2", "MDMCFG1", "MDMCFG0", "DEVIATN",
        "MCSM2", "MCSM1", "MCSM0", "FOCCFG", "BSCFG", "AGCCTRL2",
        "AGCCTRL1", "AGCCTRL0", "WOREVT1", "WOREVT0", "WORCTRL",
        "FREND1", "FREND0", "FSCAL3", "FSCAL2", "FSCAL1", "FSCAL0",
        "RCCTRL1", "RCCTRL0", "FSTEST", "PTEST", "AGCTEST", "TEST2",
        "TEST1", "TEST0", "?",
        ## Strobes
        "SRES", "SFSTXON", "SXOFF", "SCAL", "SRX", "STX", "SIDLE",
        "?", "SWOR", "SPWD", "SFRX", "SFTX", "SWORRST", "SNOP",
        "PATABLE", "RXFIFO",
        "IOCFG2", "IOCFG1", "IOCFG0", "FIFOTHR", "SYNC1", "SYNC0",
        "PKTLEN", "PKTCTRL1", "PKTCTRL0", "ADDR", "CHANNR",
        "FSCTRL1", "FSCTRL0", "FREQ2", "FREQ1", "FREQ0",
        "MDMCFG4", "MDMCFG3", "MDMCFG2", "MDMCFG1", "MDMCFG0", "DEVIATN",
        "MCSM2", "MCSM1", "MCSM0", "FOCCFG", "BSCFG", "AGCCTRL2",
        "AGCCTRL1", "AGCCTRL0", "WOREVT1", "WOREVT0", "WORCTRL",
        "FREND1", "FREND0", "FSCAL3", "FSCAL2", "FSCAL1", "FSCAL0",
        "RCCTRL1", "RCCTRL0", "FSTEST", "PTEST", "AGCTEST", "TEST2",
        "TEST1", "TEST0", "?",
        "PARTNUM", "VERSION", "FREQEST", "LQI", "RSSI", "MARCSTATE",
        "WORTIME1", "WORTIME0", "PKTSTATUS", "VCO_VC_DAC", "TXBYTES",
        "RXBYTES", "RCCTRL1_STATUS", "RCCTRL0_STATUS",
        "PATABLE", "RXFIFO"
    ]
    def CC_setup(self):
        """Move the FET into the CCSPI application."""
        self.writecmd(self.APP, self.SETUP, 0, self.data) #CCSPI/SETUP

    def CC_trans8(self, byte):
        """Read and write 8 bits by CCSPI."""
        data = self.CC_trans([byte])
        return ord(data[0])

    def CC_trans(self, data):
        """Exchange data by CCSPI."""
        self.data = data
        self.writecmd(self.APP, self.READ, len(data), data)
        return self.data
    def strobe(self, reg=0x00):
        """Strobes a strobe register, returning the status."""
        data = [reg]
        self.CC_trans(data)
        return ord(self.data[0])
    def CC_strobe_RES(self):
        """Reset the chip"""
        self.int_state = self.strobe(0x30)
    def CC_strobe_FSTXON(self):
        """Enable and calibrate the frequency synthesizer"""
        self.int_state = self.strobe(0x31)
    def CC_strobe_XOFF(self):
        """Turn off crystal oscillator"""
        self.int_state = self.strobe(0x32)
    def CC_strobe_CAL(self):
        """Calibrate frequency synthesizer and turn it off"""
        self.int_state = self.strobe(0x33)
    def CC_strobe_RX(self):
        """Enable RX"""
        self.int_state = self.strobe(0x34)
    def CC_strobe_TX(self):
        """Enable TX"""
        self.int_state = self.strobe(0x35)
    def CC_strobe_IDLE(self):
        """Exit RX/TX"""
        self.int_state = self.strobe(0x36)
    def CC_strobe_WOR(self):
        """Wake on Radio"""
        self.int_state = self.strobe(0x38)
    def CC_strobe_PWD(self):
        """Power Down mode"""
        self.int_state = self.strobe(0x39)
    def CC_strobe_FRX(self):
        """Flush RX FIFO buffer. Only issue in IDLE or RXFIFO_OVERFLOW state"""
        self.int_state = self.strobe(0x3A)
    def CC_strobe_FTX(self):
        """Flush TX FIFO buffer. Only issue in IDLE or TXFIFO_UNDERFLOW state"""
        self.int_state = self.strobe(0x3B)
    def CC_strobe_WORRST(self):
        """Reset realtime clock"""
        self.int_state = self.strobe(0x3C)
    def CC_strobe_NOP_READ(self):
        """No operation. May be used to get access to the chip status byte"""
        self.int_state = self.writecmd(self.APP, self.READ, 1, [0x3D])
    def CC_strobe_NOP_WRITE(self):
        """No operation. May be used to get access to the chip status byte"""
        self.int_state = self.strobe(0x3D)

    def peek_by_name(self, regname):
        return self.peek(self._regnames.index(regname), 1)[0]
    def poke_by_name(self, regname, val):
        return self.poke(self._regnames.index(regname), [val])
    def peek(self, reg, bytes=1):
        """Read one or more CCSPI Register."""
        #Reg is ORed with 0x80 by the GoodFET.
        if bytes < 1:
            bytes = 1
        data = [0 for i in xrange(bytes+1)]
        data[0] = reg
        self.writecmd(self.APP, self.PEEK, len(data), data)
        self.int_state = ord(self.data[0])
        return [ ord(i) for i in self.data[1:] ]

    def poke(self, reg, val):
        """Write one or more CCSPI Register."""
        if isinstance(val, int):
            val = [ val ]
        if not isinstance(val, list):
            raise TypeError("val must be a list of int or an int")
        data = [ reg ]
        for v in val:
            data.append(v & 0x0ff)
        self.writecmd(self.APP, self.POKE, len(data), data)
        res = self.peek(reg, len(val))
        for i in xrange(len(val)):
            if val[i] != res[i]:
                print "Warning, failed to set %s(%02x)=0x%02x, got 0x%02x." % (
                    self._regnames[reg + i], reg + i,
                    val[i],
                    res[i])
                return False
        return True

    def identify(self):
        (part, ver) = self.peek(0x30, bytes=2)
        return self._chips.get((part << 8) + ver, "Unsupported chip (0x%02x%02x)" % (part, ver))
    def status(self):
        _state = [ "RX_FIFO_LOW", "RX_FIFO_HIGH", "TX_FIFO_LOW", "TX_FIFO_HIGH", "RX_FIFO_OVERFLOW", "TX_FIFO_UNDERFLOW", "SYNC_WORD_SEEN",
            "PACKET_CRC_OK", "PREAMBLE_QUALITY_REACHED", "CLEAR_CHANNEL_ASSESSMENT", "PLL_LOCK", "SERIAL_CLOCK", "SERIAL_SYNCHRONOUS_DATA",
            "SERIAL_DATA_OUTPUT", "CARRIER_SENSE", "CRC_OK", "RESERVED (0x10)", "RESERVED (0x11)", "RESERVED (0x12)", "RESERVED (0x13)",
            "RESERVED (0x14)", "RESERVED (0x15)", "RX_HARD_DATA[1]", "RX_HARD_DATA[0]", "TEST (0x18)", "TEST (0x19)", "TEST (0x1A)", "PA_PD",
            "LNA_PD", "RX_SYMBOL_TICK", "RESERVED (0x1E)", "RESERVED (0x1F)", "RESERVED (0x20)", "RESERVED (0x21)", "RESERVED (0x22)",
            "RESERVED (0x23)", "WOR_EVNT0", "WOR_EVNT1", "TEST (0x26)", "CLK_32K", "TEST (0x28)", "CHIP_READY", "TEST (0x2A)", "XOSC_STABLE",
            "TEST (0x2C)", "GDO0_Z_EN_N", "HIGH_IMPEDANCE", "HW_0", "CLK_XOSC/1", "CLK_XOSC/1.5", "CLK_XOSC/2", "CLK_XOSC/3", "CLK_XOSC/4",
            "CLK_XOSC/6", "CLK_XOSC/8", "CLK_XOSC/12", "CLK_XOSC/16", "CLK_XOSC/24", "CLK_XOSC/32", "CLK_XOSC/48", "CLK_XOSC/64",
            "CLK_XOSC/96", "CLK_XOSC/128", "CLK_XOSC/192"
        ]
        # Read IOCFG2 register
        self.writecmd(self.APP, self.PEEK, 2, [ 0x00, 0x00 ])
        self.int_state = ord(self.data[0])
        return _state[ord(self.data[1]) & 0x3F]

    def internal_status(self):
        """Read the status byte."""
        _statestr = [ "IDLE", "RX", "TX", "FSTXON", "CALIBRATE", "SETTLING", "RXFIFO_OVERFLOW", "TXFIFO_UNDERFLOW" ]
        status = self.int_state
        fifo = status & 7
        state = (status >> 3) & 7
        ready = status >> 6
        return "State: %s - Ready: %s - FIFO available bytes: %d" % (_statestr[state], bool(ready == 0), fifo)

    def regs(self):
        rv = []
        vals = self.peek(0xC0, bytes=0x2F)
        for i in xrange(0x2f):
            rv.append((self._regnames[0xC0 + i], vals[i]))
        return rv

    #Radio stuff begins here.
    _bandwith = [ 812, 650, 541, 464, 406, 325, 270, 232, 203, 162, 135, 116, 102, 81, 68, 58 ]
    def RF_setbandwith(self, bw):
        """Sets the bandwith"""
        try:
            conf = self._bandwith.index(bw)
            conf <<= 4
            conf |= self.peek_by_name("MDMCFG4") & 0x0f
            self.poke_by_name("MDMCFG4", conf)
        except:
            print "ERROR: unsupported bandwith (%d KHz). Should be %s" % (bw, ", ".join(self._bandwith))
    def RF_getbandwith(self):
        reg = self.peek_by_name("MDMCFG4")
        bw_e = (reg >> 6) & 0x3
        bw_m = (reg >> 4) & 0x3
        conf = (bw_e << 2) + bw_m
        return self._bandwith[conf]

    def RF_get_frequency(self):
        vals = self.peek(0x0D, 3)
        freq = (vals[0] << 16) + (vals[1] << 8) + vals[2]
        return freq * 26000000.0 / 2**16

    def RF_set_frequency(self, freq):
        """freq is in Hz"""
        freq = int(round(freq*2**16/26000000))
        self.peek_by_name("FREQ2", freq >> 16)
        self.peek_by_name("FREQ1", (freq >> 8) & 0x0ff)
        self.peek_by_name("FREQ0", freq & 0x0ff)

    def RF_get_IF_freq(self):
        return (self.peek_by_name("FSCTRL1") & 15) * 26000000.0 / 2**10

    def RF_set_channel(self, n):
        self.poke_by_name("CHANNR", n % 256)
    def RF_get_channel(self):
        return self.peek_by_name("CHANNR")

    def RF_get_chan_spacing(self):
        space = (256 + self.peek_by_name("MDMCFG0")) * 2**((self.peek_by_name("MDMCFG1") & 3) - 2)
        return space * 26000000.0 / 2**16

    def RF_get_addr(self):
        return self.peek_by_name("ADDR")
    def RF_set_addr(self, addr):
        return self.poke_by_name("ADDR", addr % 256)
    def RF_enable_whitening(self):
        self.poke_by_name("PKTCTRL0", self.peek_by_name("PKTCTRL0") | 0x40)
        self.RF_disable_CC2400()
    def RF_disable_whitening(self):
        self.poke_by_name("PKTCTRL0", (self.peek_by_name("PKTCTRL0") & ~0x40) % 256)
    def RF_enable_CC2400(self):
        self.poke_by_name("PKTCTRL0", self.peek_by_name("PKTCTRL0") | 0x8)
        self.RF_disable_whitening()
        self.RF_disable_CRC_autoflush()
    def RF_disable_CC2400(self):
        self.poke_by_name("PKTCTRL0", (self.peek_by_name("PKTCTRL0") & ~0x8) % 256)
    def RF_enable_CRC(self):
        self.poke_by_name("PKTCTRL0", self.peek_by_name("PKTCTRL0") | 0x4)
    def RF_disable_CRC(self):
        self.poke_by_name("PKTCTRL0", (self.peek_by_name("PKTCTRL0") & ~0x4) % 256)
    def RF_get_pkt_len(self):
        """Returns packet length.
        Positive integer means fixed.
        Negative integer means a variable packet with at most N bytes.
        None means Infinite length."""
        conf = self.peek_by_name("PKTCTRL0") & 0x3
        if conf == 0:
            # Fixed
            return self.peek_by_name("PKTLEN")
        elif conf == 1:
            # Variable
            return -self.peek_by_name("PKTLEN")
        elif conf == 2:
            # infinite
            return None
        else:
            # Reserved
            print "ERROR: Reserved packet length"
    def RF_set_pkt_len(self, size):
        """Sets packet length.
        Positive integer means fixed.
        Negative integer means a variable packet with at most N bytes.
        None means Infinite length."""
        if size is None:
            self.poke_by_name((self.peek_by_name("PKTCTRL0") & 0x0fc) | 0x2)
        elif size >= 0:
            self.poke_by_name((self.peek_by_name("PKTCTRL0") & 0x0fc) | 0x0)
            self.poke_by_name("PKTLEN", abs(size))
        else:
            self.poke_by_name((self.peek_by_name("PKTCTRL0") & 0x0fc) | 0x1)
            self.poke_by_name("PKTLEN", abs(size))

    def RF_get_syncword(self):
        return (self.peek_by_name("SYNC1") << 8) + self.peek_by_name("SYNC0")
    def RF_set_syncword(self, sync):
        self.poke_by_name("SYNC1", (sync >> 8) & 0x0ff)
        self.poke_by_name("SYNC0", sync & 0x0ff)

    def RF_get_datarate(self):
        """return the configured value in bauds"""
        drate_m = self.peek_by_name("MDMCFG3")
        drate_e = self.peek_by_name("MDMCFG4") & 0x0f
        return 26000000 * ((256 + drate_m) * 2**drate_e)/2**28
    def RF_set_datarate(self, rate):
        """rate is expressed as a float in bauds"""
        drate_e = int(math.floor(math.log(rate * 2**20 / 26000000.0, 2)))
        drate_m = int(round(((rate * 2**28) / (26000000.0 * 2**drate_e)) - 256))
        if drate_m >= 256:
            drate_m -= 256
            drate_e += 1
        if drate_e < 0 or drate_e > 15:
            print "ERROR: can't set datarate (too high or too low)"
        else:
            self.poke_by_name("MDMCFG3", drate_m % 256)
            self.poke_by_name("MDMCFG4", (self.peek_by_name("MDMCFG4") & 0xf0) | drate_e)

    def RF_set_modulation(self, mod):
        """modulation can be 2-FSK, GFSK, OOK or MSK"""
        _vals = { "2-FSK": 0, "GFSK": 1, "OOK": 3, "MSK": 7}
        if mod not in _vals:
            print "ERROR: invalid modulation. Must be: %s" % ", ".join(_vals.keys())
        else:
            self.poke_by_name("MDMCFG2", (self.peek_by_name("MDMCFG2") & 0x8f) | _vals[mod])
    def RF_get_modulation(self):
        _vals = [ "2-FSK", "GFSK", "? (2)", "OOK", "? (4)", "? (5)", "? (6)", "MSK" ]
        return _vals[(self.peek_by_name("MDMCFG2") & 0x70) >> 4]

    def RF_enable_manchester(self):
        self.poke_by_name("MDMCFG2", self.peek_by_name("MDMCFG2") | 0x8)
    def RF_disable_manchester(self):
        self.poke_by_name("MDMCFG2", (self.peek_by_name("MDMCFG2") & ~0x8) % 256)

    def RF_set_preamble_len(self, length):
        _valid = [2, 3, 4, 6, 8, 12, 16, 24]
        if length not in _valid:
            print "ERROR: preamble len should be %s" % ", ".join(_valid)
        else:
            self.poke_by_name("MDMCFG1", (self.peek_by_name("MDMCFG1") & 0x8f) + (length<<4))
    def RF_get_preamble_len(self):
        _vals = [2, 3, 4, 6, 8, 12, 16, 24]
        return _vals[(self.peek_by_name("MDMCFG1") >> 4) & 0x7]

    def RF_set_rxoff_mode(self, mode):
        _valid = { "IDLE": 0, "FSTXON": 1, "TX": 2, "RX": 3}
        if mode not in _valid:
            print "ERROR: mode should be " % ", ".join(_valid)
        else:
            self.poke_by_name("MCSM1", (self.peek_by_name("MCSM1") & 0xf3) + (_valid[mode] << 2))
    def RF_get_rxoff_mode(self):
        _vals = ["IDLE", "FSTXON", "TX", "RX"]
        return _vals[(self.peek_by_name("MCSM1") & 0x0c) >> 2]

    def RF_set_txoff_mode(self, mode):
        _valid = { "IDLE": 0, "FSTXON": 1, "TX": 2, "RX": 3}
        if mode not in _valid:
            print "ERROR: mode should be " % ", ".join(_valid)
        else:
            self.poke_by_name("MCSM1", (self.peek_by_name("MCSM1") & 0xfc) + _valid[mode])
    def RF_get_txoff_mode(self):
        _vals = ["IDLE", "FSTXON", "TX", "RX"]
        return _vals[self.peek_by_name("MCSM1") & 0x03]

    def RF_get_RSSI(self):
        rssi = self.peek_by_name("RSSI")
        if rssi >= 128:
            rssi = (rssi - 256) / 2.0
        else:
            rssi /= 2.0
        rssi -= 71.0 ## mean rssi offset. Not accurate

    def RF_carrier(self):
        print "ERROR: RF Carrier is not implemented"

    def RF_rxpacket(self, bytes=None):
        """Get a packet from the radio.  Returns None if none is
        waiting."""
        data = "\0"
        self.data = data
        self.writecmd(self.APP, self.RX, len(data), data)
        if len(self.data) == 0:
            return None
        return self.data

    def RF_txpacket(self,packet):
        """Send a packet through the radio."""
        if isinstance(packet, str):
            packet = [ ord(x) for x in packet ]
        self.writecmd(self.APP, self.TX, len(packet), packet)
        return

    def RF_rxpacketrepeat(self):
        self.writecmd(self.APP, self.REPEAT_RX, 0, None)


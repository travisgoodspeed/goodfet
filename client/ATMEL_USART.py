
"""
This library helps interface with USARTs on Atmel microcontrollers.  The library has been modeled after the AT91X40 series (1354D-ATARM-08/02).  AT91SAM7 has also been thrown in a little.
"""

USART0_BASE = 0xfffd0000
USART1_BASE = 0xfffcc000

US_CR_OFF =     0x00    # wO
US_MR_OFF =     0x04    # R/w
US_IER_OFF =    0x08    # wO
US_IDR_OFF =    0x0c    # wO

US_IMR_OFF =    0x10    # RO
US_CSR_OFF =    0x14    # RO
US_RHR_OFF =    0x18    # RO
US_THR_OFF =    0x1c    # wO

US_BRGR_OFF =   0x20    # R/w
US_RTOR_OFF =   0x24    # R/w
US_TTGR_OFF =   0x28    # R/w

US_RPR_OFF =    0x30    # R/w   - AT91X40
US_RCR_OFF =    0x34    # R/w   - AT91X40
US_TPR_OFF =    0x38    # R/w   - AT91X40
US_TCR_OFF =    0x3c    # R/w   - AT91X40

US_FIDI_OFF =   0x40    # R/w   - AT91SAM7
US_NER_OFF =    0x44    # RO    - AT91SAM7
US_IF_OFF =     0x4c    # R/w   - AT91SAM7

CR_RSTRX =      1<<2
CR_RSTTX =      1<<3
CR_RXEN =       1<<4
CR_RXDIS =      1<<5
CR_TXEN =       1<<6
CR_TXDIS =      1<<7
CR_RSTSTA =     1<<8
CR_STTBRK =     1<<9
CR_STPBRK =     1<<10
CR_STTTO =      1<<11
CR_SENDA =      1<<12
CR_RSTIT =      1<<13
CR_RSTNACK =    1<<14
CR_RETTO =      1<<15
CR_DTREN =      1<<16
CR_DTRDIS =     1<<17
CR_RTSEN =      1<<18
CR_RTSDIS =     1<<19

CSR_RXRDY =     1
CSR_TXRDY =     1<<1
CSR_RXBRK =     1<<2
CSR_ENDRX =     1<<3
CSR_ENDTX =     1<<4
CSR_OVRE =      1<<5
CSR_FRAME =     1<<6
CSR_PARE =      1<<7
CSR_TIMEOUT =   1<<8
CSR_TXEMPTY =   1<<9

INTERRUPTS = {
        CSR_RXRDY:"RXRDY",
        CSR_TXRDY:"TXRDY", 
        CSR_RXBRK:"RXBRK", 
        CSR_ENDRX:"ENDRX", 
        CSR_ENDTX:"ENDTX", 
        CSR_OVRE:"OVRE", 
        CSR_FRAME:"FRAME", 
        CSR_PARE:"PARE", 
        CSR_TIMEOUT:"TIMEOUT", 
        CSR_TXEMPTY:"TXEMPTY", 
        }

MR_USCLKS =     1<<4
MR_CHRL =       1<<6
MR_SYNC =       1<<8
MR_PAR =        1<<9
MR_NBSTOP =     1<<12
MR_CHMOD =      1<<14
MR_MODE9 =      1<<17
MR_CLKO =       1<<18

MR_USCLK_INTERP = {
        0:"MCK",
        1:"MCK/8",
        2:"External (SCK)",
        3:"External (SCK)",
        }

class USART:
    def __init__(self, arm7_gf_client, base_addr=USART0_BASE):
        self.client = arm7_gf_client
        self.base_addr = base_addr
    
    def setControlReg(self, cr):
        """ only integers, please """
        self.client.writeMem(self.base + US_CR_OFF, [cr])
    def getModeReg(self):
        return self.client.readMem(self.base + US_MR_OFF, 1)
    def setModeReg(self, mr):
        return self.client.writeMem(self.base + US_MR_OFF, [mr])
    def interruptEnable(self, mask=0):
        self.client.writeMem(self.base + US_IER_OFF, [mask])
    def interruptDisable(self, mask=0):
        self.client.writeMem(self.base + US_IDR_OFF, [mask])

    def getInterruptMask(self):
        return self.client.readMem(self.base + US_IMR_OFF,1)
    def getChannelStatus(self):
        return self.client.readMem(self.base + US_CSR_OFF,1)
    def getRecvHoldReg(self):
        return self.client.readMem(self.base + US_RHR_OFF,1)
    def setXmitHoldReg(self, char):
        num, = struct.unpack("B",char)
        self.client.writeMem(self.base + US_THR_OFF,[num])

    def getBaudRateGenReg(self):
        return self.client.readMem(self.base + US_BRGR_OFF,1)
    def setBaudRateGenReg(self, brgr):
        self.client.writeMem(self.base + US_BRGR_OFF,[brgr])
    def getRecvTOReg(self):
        return self.client.readMem(self.base + US_RTOR_OFF,1)
    def setRecvTOReg(self, rtor):
        self.client.writeMem(self.base + US_RTOR_OFF,[rtor])
    def getXmitTOReg(self):
        return self.client.readMem(self.base + US_TTOR_OFF,1)
    def setXmitTOReg(self, ttor):
        self.client.writeMem(self.base + US_TTOR_OFF,[ttor])

    def getRecvPtrReg(self):
        return self.client.readMem(self.base + US_RPR_OFF,1)
    def setRecvPtrReg(self, rpr):
        self.client.writeMem(self.base + US_RPR_OFF,[rpr])
    def getRecvCtrReg(self):
        return self.client.readMem(self.base + US_RCR_OFF,1)
    def setRecvCtrReg(self, cpr):
        self.client.writeMem(self.base + US_RCR_OFF,[rcr])
    def getXmitPtrReg(self):
        return self.client.readMem(self.base + US_TPR_OFF,1)
    def setXmitPtrReg(self, tpr):
        self.client.writeMem(self.base + US_TPR_OFF,[tpr])
    def getXmitCtrReg(self):
        return self.client.readMem(self.base + US_TCR_OFF,1)
    def setXmitCtrReg(self, cpr):
        self.client.writeMem(self.base + US_TCR_OFF,[tcr])

    def crResetRecv(self):
        self.setControlReg(CR_RSTRX)
    def crResetXmit(self):
        self.setControlReg(CR_RSTTX)
    def crEnableRecv(self):
        self.setControlReg(CR_RXEN)
    def crDisableRecv(self):
        self.setControlReg(CR_RXDIS)
    def crEnableXmit(self):
        self.setControlReg(CR_TXEN)
    def crDisableXmit(self):
        self.setControlReg(CR_TXDIS)
    def crResetStatus(self):
        self.setControlReg(CR_RSTSTA)
    def crStartBreak(self):
        self.setControlReg(CR_STTBRK)
    def crStopBreak(self):
        self.setControlReg(CR_STPBRK)
    def crStartTimeout(self):
        self.setControlReg(CR_STTTO)
    def crSendAddress(self):
        self.setControlReg(CR_SENDA)
    def crSendBreak(self):
        timeout = 0x100
        while (timeout > 0 and self.getChannelStatus() & CSR_TXRDY):
            time.sleep(.1)
        self.crStartBreak()
        timeout = 0x100
        while (timeout > 0 and self.getChannelStatus() & CSR_TXRDY):
            time.sleep(.1)
        self.crStopBreak()

    def mrGetModeParts(self):
        mode = self.getMode()
        usart_mode = mode & 0xf
        usclks =    ((mode>>4) & 3)
        chrl =      ((mode>>6) & 3) + 5
        sync =      ((mode>>8) & 1)
        par =       ((mode>>9) & 7)
        nbstop =    ((mode>>12)& 3)
        chmode =    ((mode>>14)& 3)
        mode9 =     ((mode>>17)& 1)
        cklo =      ((mode>>18)& 1)
        return (usclks,chrl,sync,par,nbstop,chmode,mode9,cklo)
    def mrReprUsartMode(self):
        return ("normal","rs485","hwhandshake","modem","iso7816/t=0",
                "reserved","iso7816/t=1","reserved","irda","reserved",
                "reserved","reserved","reserved","reserved","reserved",
                "reserved","reserved",)[self.mrGetModeParts()[0]]
    def mrReprSelectedClock(self):
        return MR_USCLKS_INTERP[self.mrGetModeParts()[1]]
    def mrReprParity(self):
        return ("even","odd","forced-0","forced-1","None","None","Multidrop")[self.mrGetModeParts()[4]]
    def mrReprStopBits(self):
        return ("1","1.5","2","reserved")[self.mrGetModeParts()[5]]
    def mrReprChannelMode(self):
        return ("normal","auto-echo","local-loopback","remote-loopback")[self.mrGetModeParts()[5]]

    def csrReprStatus(self):
        csr = self.getControlStatus()
        output = []
        for bit in xrange(10):
            b = 1<<bit
            if csr & b:
                output.append(INTERRUPTS[b])
        return "\n".join(output)




#!/usr/bin/env python
# GoodFET ARM Debugging Interface v5 (ADIv5) Client Library.
# the ideal interface to pwning ARM Cortex
# 
# Contributions and bug reports welcome.
#
# 

import sys, binascii, struct, time
import atlasutils.smartprint as asp
from GoodFET import GoodFET
from intelhex import IntelHex


#Global Commands
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

# ARM7TDMI JTAG commands
IR_SHIFT =              0x80
DR_SHIFT =              0x81
RESETTAP =              0x82
RESETTARGET =           0x83
GET_REGISTER =          0x87
SET_REGISTER =          0x88
DEBUG_INSTR =           0x89
# Really ARM specific stuff
WAIT_DBG =              0x91
CHAIN0 =                0x93
SCANCHAIN1 =            0x94
EICE_READ =             0x95
EICE_WRITE =            0x96

#4-bit ARM JTAG INSTRUCTIONS - STANDARD
IR_ABORT =              0x8
IR_RESERVED1 =          0x9
IR_DPACC =              0xA
IR_APACC =              0xB
IR_RESERVED2 =          0xC
IR_RESERVED3 =          0xD
IR_IDCODE =             0xE
IR_BYPASS =             0xF
#4-bit ARM JTAG INSTRUCTIONS - IMPLEMENTATION-DEFINED
IR_EXTEST =             0x0
IR_SAMPLE =             0x1
IR_PRELOAD =            0x2
IR_RESERVED =           0x3
IR_INTEST =             0x4
IR_CLAMP =              0x5
IR_HIGHZ =              0x6
IR_CLAMPZ =             0x7

DP_CTRLSTAT_OFF =       0x4
DP_SELECT_OFF =         0x8
DP_RDBUFF_OFF =         0xC

MAX_AP_COUNT = 16

PM_usr = 0b10000
PM_fiq = 0b10001
PM_irq = 0b10010
PM_svc = 0b10011
PM_abt = 0b10111
PM_und = 0b11011
PM_sys = 0b11111
proc_modes = {
    0:      ("UNKNOWN, MESSED UP PROCESSOR MODE","fsck", "This should Never happen.  MCU is in funky state!"),
    PM_usr: ("User Processor Mode", "usr", "Normal program execution mode"),
    PM_fiq: ("FIQ Processor Mode", "fiq", "Supports a high-speed data transfer or channel process"),
    PM_irq: ("IRQ Processor Mode", "irq", "Used for general-purpose interrupt handling"),
    PM_svc: ("Supervisor Processor Mode", "svc", "A protected mode for the operating system"),
    PM_abt: ("Abort Processor Mode", "abt", "Implements virtual memory and/or memory protection"),
    PM_und: ("Undefined Processor Mode", "und", "Supports software emulation of hardware coprocessor"),
    PM_sys: ("System Processor Mode", "sys", "Runs privileged operating system tasks (ARMv4 and above)"),
}

PSR_bits = [ 
    None, None, None, None, None, "Thumb", "nFIQ_int", "nIRQ_int", 
    "nImprDataAbort_int", "BIGendian", None, None, None, None, None, None, 
    "GE_0", "GE_1", "GE_2", "GE_3", None, None, None, None, 
    "Jazelle", None, None, "Q (DSP-overflow)", "oVerflow", "Carry", "Zero", "Neg",
    ]

ARM_INSTR_NOP =             0xe1a00000L
ARM_INSTR_BX_R0 =           0xe12fff10L
ARM_INSTR_STR_Rx_r14 =      0xe58f0000L # from atmel docs
ARM_READ_REG =              ARM_INSTR_STR_Rx_r14
ARM_INSTR_LDR_Rx_r14 =      0xe59f0000L # from atmel docs
ARM_WRITE_REG =             ARM_INSTR_LDR_Rx_r14
ARM_INSTR_LDR_R1_r0_4 =     0xe4901004L
ARM_READ_MEM =              ARM_INSTR_LDR_R1_r0_4
ARM_INSTR_STR_R1_r0_4 =     0xe4801004L
ARM_WRITE_MEM =             ARM_INSTR_STR_R1_r0_4
ARM_INSTR_MRS_R0_CPSR =     0xe10f0000L
ARM_INSTR_MSR_cpsr_cxsf_R0 =0xe12ff000L
ARM_INSTR_STMIA_R14_r0_rx = 0xE88e0000L      # add up to 65k to indicate which registers...
ARM_INSTR_LDMIA_R14_r0_rx = 0xE89e0000L      # add up to 65k to indicate which registers...
ARM_STORE_MULTIPLE =        ARM_INSTR_STMIA_R14_r0_rx
ARM_INSTR_SKANKREGS =       0xE88F7fffL
ARM_INSTR_CLOBBEREGS =      0xE89F7fffL

ARM_INSTR_B_IMM =           0xea000000L
ARM_INSTR_B_PC =            0xea000000L
ARM_INSTR_BX_PC =           0xe1200010L      # need to set r0 to the desired address
THUMB_INSTR_LDR_R0_r0 =     0x68006800L
THUMB_WRITE_REG =           THUMB_INSTR_LDR_R0_r0
THUMB_INSTR_STR_R0_r0 =     0x60006000L
THUMB_READ_REG =            THUMB_INSTR_STR_R0_r0
THUMB_INSTR_MOV_R0_PC =     0x46b846b8L
THUMB_INSTR_MOV_PC_R0 =     0x46474647L
THUMB_INSTR_BX_PC =         0x47784778L
THUMB_INSTR_NOP =           0x1c001c00L
THUMB_INSTR_B_IMM =         0xe000e000L
ARM_REG_PC =                15


LDM_BITMASKS = [(1<<x)-1 for x in xrange(16)]

CSYSPWRUPACK =              1<<31
CSYSPWRUPACK_BIT =          31
CSYSPWRUPREQ =              1<<30
CSYSPWRUPREQ_BIT =          30
CDBGPWRUPACK =              1<<29
CDBGPWRUPACK_BIT =          29
CDBGPWRUPREQ =              1<<28
CDBGPWRUPREQ_BIT =          28
CSYSRSTACK =                1<<27
CSYSRSTACK_BIT =            27
CSYSRSTREQ =                1<<26
CSYSRSTREQ_BIT =            26
TRNCNT =                    0x3ff<<12
TRNCNT_BIT =                12
MASKLANE =                  0xf<<8
MASKLANE_BIT =              8
WDATAERR =                  1<<7
WDATAERR =                  1<<7
READOK =                    1<<6
READOK =                    1<<6
STICKYERR =                 1<<5
STICKYERR =                 1<<5
STICKYCMP =                 1<<4
STICKYCMP =                 1<<4
TRNMODE =                   3<<2
TRNMODE =                   3<<2
STICKYORUN =                1<<1
STICKYORUN =                1<<1
ORUNDETECT =                1<<0
ORUNDETECT =                1<<0


def debugstr(strng):
    print >>sys.stderr,(strng)
def PSRdecode(psrval):
    output = [ "(%s mode)"%proc_modes[psrval&0x1f][1] ]
    for x in xrange(5,32):
        if psrval & (1<<x):
            output.append(PSR_bits[x])
    return " ".join(output)
   
fmt = ["B", "B", "<H", "<L", "<L", "<Q", "<Q", "<Q", "<Q"]
def chop(val,byts):
    s = struct.pack(fmt[byts], val)
    return [ord(b) for b in s ][:byts]
        
class GoodFETADIv5(GoodFET):
    """A GoodFET variant for use with ARM7TDMI microprocessor."""
    def __init__(self):
        GoodFET.__init__(self)
        self.storedPC =         0xffffffff
        self.current_dbgstate = 0xffffffff
        self.flags =            0xffffffff
        self.nothing =          0xffffffff
        self.ir_status =        None
        self.ap_selected =      None
        self.ap_bank =          0
        self.aps =              None

    def __del__(self):
        pass

    def setup(self):
        """Move the FET into the JTAG ARM application."""
        #print "Initializing ARM."
        self.writecmd(0x14,SETUP,0,self.data)

    def getpc(self):
        return self.ADIgetPC()

    def flash(self,file):
        """Flash an intel hex file to code memory."""
        print "Flash not implemented.";

    def dump(self,file,start=0,stop=0xffff):
        """Dump an intel hex file from code memory."""
        print "Dump not implemented.";

    def ADIident(self):
        """Get an ARM's ID."""
        raise Exception("Not Implemented.  Abstract base class method called.")
    def ADIidentstr(self):
        ident=self.ADIident()
        ver     = (ident >> 28)
        partno  = (ident >> 12) & 0xffff
        mfgid   = (ident >> 1)  & 0x7ff
        return "Chip IDCODE: 0x%x\n\tver: %x\n\tpartno: %x\n\tmfgid: %x\n" % (ident, ver, partno, mfgid); 

    def ADIget_register(self, reg):
        """Get an ARM's Register"""
        self.writecmd(0x14,GET_REGISTER,1,[reg&0xf])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ADIset_register(self, reg, val):
        """Get an ARM's Register"""
        self.writecmd(0x14,SET_REGISTER,8,[val&0xff, (val>>8)&0xff, (val>>16)&0xff, val>>24, reg,0,0,0])
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval
    def ADIget_registers(self):
        """Get ARM Registers"""
        regs = [ self.ADIget_register(x) for x in range(15) ]
        regs.append(self.ADIgetPC())            # make sure we snag the "static" version of PC
        return regs
    def ADIset_registers(self, regs, mask):
        """Set ARM Registers"""
        for x in xrange(15):
          if (1<<x) & mask:
            self.ADIset_register(x,regs.pop(0))
        if (1<<15) & mask:                      # make sure we set the "static" version of PC or changes will be lost
          self.ADIsetPC(regs.pop(0))

    def ADIrestart(self):
        raise Exception("Not Implemented.  Abstract base class method called.")

    ####### Common DP features #######
    def ADIgetAPACC(self, addr, flags):         # candidate for firmware.  not sure the intelligence wants to be there, but performance may want it.
        raise Exception("Not Implemented.  Abstract base class method called.")
    def ADIsetAPACC(self, addr, val):
        raise Exception("Not Implemented.  Abstract base class method called.")
    def ADIgetDPACC(self, addr, flags):         # candidate for firmware.  not sure the intelligence wants to be there, but performance may want it.
        raise Exception("Not Implemented.  Abstract base class method called.")
    def ADIsetDPACC(self, addr, val):
        raise Exception("Not Implemented.  Abstract base class method called.")
    def ADIsetABORT(self):
        """ ONLY use if the debugger has received WAIT responses over an extended period"""
        raise Exception("Not Implemented.  Abstract base class method called.")

    def ADIsetSELECT(self, num):
        return self.ADIsetDPACC(0x8, num)
    def ADIgetSELECT(self):
        return self.ADIgetDPACC(0x8)
    def ADIgetSELECTrepr(self):
        raw = self.ADIgetSELECT()
        swdp_ctrlsel = raw&1
        apbanksel = (raw>>4) & 0xf
        apsel = raw>>24
        return "SWDP_CTRLSEL = %d\nAPBANKSEL = %d\nAPSEL = %d\n"

    def ADIgetAccessPorts(self):
        if self.aps == None:
            self.aps = [createAP(self, x) for x in xrange(MAX_AP_COUNT)]
        return self.aps

    def ADIgetWCR(self):        # SWDP only
        raise Exception("IMPLEMENT ME: ADIgetWCR")

    def ADIgetRESEND(self):     # SWDP only
        raise Exception("IMPLEMENT ME: ADIgetRESEND")

class GoodFETADIjtag(GoodFETADIv5):
    """A GoodFET variant for use with ARM7TDMI microprocessor."""
    def ADIshift_IR(self, IR, noretidle=0):
        if (self.ir_status != IR):
            self.writecmd(0x14,IR_SHIFT,2, [IR, LSB|noretidle])
            self.ir_status = IR
        return self.data
    def ADIshift_DR(self, bignum, bits, flags=0):
        data = [bits&0xff, flags&0xff,0,0]
        data.extend(chop(data, bits/4))
        self.writecmd(0x14,DR_SHIFT, len(data), data)
        return self.data
    def ADIident(self):
        """Get an ARM's ID."""
        self.ADIshift_IR(IR_IDCODE,0)
        self.ADIshift_DR(0,32,LSB)
        retval = struct.unpack("<L", "".join(self.data[0:4]))[0]
        return retval

    def ADIdebuginstr(self,instr,bkpt):
        """if type (instr) == int or type(instr) == long:
            instr = struct.pack("<L", instr)
        instr = [int("0x%x"%ord(x),16) for x in instr]
        instr.extend([bkpt])
        self.writecmd(0x14,DEBUG_INSTR,len(instr),instr)
        return (self.data)"""
        pass
    def ADI_nop(self, bkpt=0):
        """if self.status() & DBG_TBIT:
            return self.ADIdebuginstr(THUMB_INSTR_NOP, bkpt)
        return self.ADIdebuginstr(ARM_INSTR_NOP, bkpt)"""
        pass

    def ADIrestart(self):
        self.ADIshift_IR(IR_RESTART)

    ####### Common DP features #######
    def ADIgetAPACC(self, addr):                # candidate for firmware.  not sure the intelligence wants to be there, but performance may want it.
        self.ADIshift_IR(IR_APACC)
        data = 1 | (addr>>1)                    # addr[3:2] goes in bits [2:1].  this *must* be a multiple of 4.
        return self.ADIshift_DR(data, 35, LSB)
    def ADIsetAPACC(self, addr, val):
        """
        0 < val < 0xffffffff
        addr == 4*n   (ie.  multiple of four, returns the word at that register)
        """
        self.ADIshift_IR(IR_APACC)
        data = (val<<3) | (addr>>1)             # addr[3:2] goes in bits [2:1].  this *must* be a multiple of 4.
        self.ADIshift_DR(data, 35, LSB)
    def ADIgetDPACC(self, addr, flags):         # candidate for firmware.  not sure the intelligence wants to be there, but performance may want it.
        self.ADIshift_IR(IR_DPACC)
        data = 1 | (addr>>1)                    # addr[3:2] goes in bits [2:1].  this *must* be a multiple of 4.
        return self.ADIshift_DR(data, 35, LSB)
    def ADIsetDPACC(self, addr, val):
        """
        0 < val < 0xffffffff
        addr == 4*n   (ie.  multiple of four, returns the word at that register)
        """
        self.ADIshift_IR(IR_DPACC)
        data = (val<<3) | (addr>>1)             # addr[3:2] goes in bits [2:1].  this *must* be a multiple of 4.
        self.ADIshift_DR(data, 35, LSB)

    def ADIsetABORT(self):
        """ ONLY use if the debugger has received WAIT responses over an extended period"""
        self.ADIshift_IR(self, IR_ABORT)
        self.ADIshift_DR(self, 1, 35)

    def ADIsetSELECT(self, apnum, apbank, flags="ignored for jtag"):
        if (apnum != self.ap_selected or apbank != self.ap_bank):
            select = (apnum<<24) | (apbank<<4)
            self.ADIsetDPACC(0x8, select)
            self.ap_selected = apnum
            self.ap_bank = apbank
    def ADIgetSELECT(self, noncached=False):
        if (noncached):
            return self.ADIgetDPACC(0x8)
        return self.ap_selected

def createAP(dp, apnum):
    idr = 0xfc
    bank = idr/16
    self.dp.ADIsetSELECT(self.apnum, bank)
    ident = self.dp.ADIgetAPACC(idr&0xf)
    if ((ident>>16)&1):
        return ADI_MEM_AP(dp, apnum)
    return ADI_JTAG_AP(dp, apnum)

class ADI_AccessPort:           # define common AP calls
    def __init__(self, DP, apnum):
        self.dp = DP            # link to parent.  all calls should use this to access the underlying debug port.
        self.apnum = apnum      # which AP am i to this DP?

    def getRegister(self, bank, off):
        self.dp.ADIsetSELECT(self.apnum, bank)
        return self.dp.ADIgetAPACC(off)

    def getRegisterByAddr(self, addr):
        bank = addr/16
        self.dp.ADIsetSELECT(self.apnum, bank)
        return self.dp.ADIgetAPACC(addr&0xf)

    def getIdentRegister(self):
        ident = self.getRegisterByAddr(0xfc)
        return ident

    def getIdentRegisterrepr(self):
        raw = self.getIdentRegister()
        ap_rev = raw>>28
        jep_cont = (raw>>24) & 0xf
        jep_ident = (raw>>17) & 0x7f
        ap_class = (raw>>16) & 1
        ap_ident = raw & 0xff
        return "AP Revision: 0x%x\nJEP-106 Continuation Code: 0x%x\nJEP-106 Identity Code: 0x%x\nAP Class: 0x%x\nAP Identification: %x (%s)\n"%(ap_rev,jep_cont,jep_ident,ap_class,ap_ident,AP_IDENT_TYPES[ap_ident&0xf])
    #def 

class ADI_MEM_AP(ADI_AccessPort):
    MEMAP_CSW_REG =             0x0
    MEMAP_TAR_REG =             0x4
    MEMAP_DRW_REG =             0xC
    MEMAP_BD0 =                 0x10
    MEMAP_BD1 =                 0x14
    MEMAP_BD2 =                 0x18
    MEMAP_BD3 =                 0x1C
    MEMAP_CFG_REG =             0xF4
    MEMAP_BASE_REG =            0xF8
    MEMAP_IDR_REG =             0xFC

    def __init__(self, DP, apnum):
        ADI_AccessPort.__init__(self, DP, apnum)
        self.cfg = self.getCFG()                    # necessary to cache endianness information
        # FIXME: how do i determine if this adi supports multibyte access or just word?  or packed transfers?
        self.setMemAccessSize(4)

    def getCSW(self):
        """ Control/Status Word reg  """
        return self.getRegister(self.MEMAP_CSW_REG)
    def setCSW(self, csw):
        """ Control/Status Word reg.  Some bits are RO """
        return self.setRegister(self.MEMAP_CSW_REG, csw)
    def reprCSW(self):
        csw = self.getCSW()
        

    def getTAR(self):
        """ Transfer Address Register.  Used for both DRW and BDx accesses.  Autoinc (see CSW) only works for DRW accesses, not Banked Regs"""
        return self.getRegister(self.MEMAP_TAR_REG)
    def setTAR(self, tar):
        """ Transfer Address Register.  Used for both DRW and BDx accesses.  Autoinc (see CSW) only works for DRW accesses, not Banked Regs"""
        return self.setRegister(self.MEMAP_TAR_REG, tar)

    def getDRW(self):
        """ Data Read/Write reg. """
        return self.getRegister(self.MEMAP_DRW_REG)
    def setDRW(self, drw):
        """ Data Read/Write reg. """
        return self.setRegister(self.MEMAP_DRW_REG, drw)

    #FIXME: use one set of accessors... either keep the indexed version or the individuals.
    def getBDReg(self, index):
        return self.getRegister(self.MEMAP_BD0_REG + (index*4))
    def setBDReg(self, index, bd):
        return self.setRegister(self.MEMAP_BD0_REG + (index*4), bd0)

    def getBD0(self):
        return self.getRegister(self.MEMAP_BD0_REG)
    def setBD0(self, bd0):
        return self.setRegister(self.MEMAP_BD0_REG, bd0)

    def getBD1(self):
        return self.getRegister(self.MEMAP_BD1_REG)
    def setBD1(self, bd1):
        return self.setRegister(self.MEMAP_BD1_REG, bd1)

    def getBD2(self):
        return self.getRegister(self.MEMAP_BD2_REG)
    def setBD2(self, bd2):
        return self.setRegister(self.MEMAP_BD2_REG, bd2)

    def getBD3(self):
        return self.getRegister(self.MEMAP_BD3_REG)
    def setBD3(self, bd3):
        return self.setRegister(self.MEMAP_BD3_REG, bd3)

    def getCFG(self):
        return self.getRegister(self.MEMAP_CFG_REG)
    def setCFG(self, cfg):
        return self.setRegister(self.MEMAP_CFG_REG, cfg)

    def getBASE(self):
        """ BASE debug address.  RO """
        return self.getRegister(self.MEMAP_BASE_REG)
    def setBASE(self, base):
        """ BASE debug address.  RO """
        return self.setRegister(self.MEMAP_BASE_REG, base)

    def getIDR(self):
        return self.getRegister(self.MEMAP_IDR_REG)

    # CFG accessors
    CFG_DBGSWENABLE_BITS =      31
    CFG_DBGSWENABLE =           1<<31
    CFG_PROT_BITS =             24
    CFG_PROT =               0x3f<<24
    CFG_SPIDEN_BITS =           23
    CFG_SPIDEN =                1<<23
    CFG_MODE_BITS =             8
    CFG_MODE =                0xf<<8
    CFG_TRINPROG_BITS =         7
    CFG_TRINPROG =              1<<7
    CFG_DEVICEEN_BITS =         6
    CFG_DEVICEEN =              1<<6
    CFG_ADDRINC_BITS =          4
    CFG_ADDRINC =               3<<4
    CFG_SIZE_BITS =             0
    CFG_SIZE =                  7
    CFG_ADDRINC_off =           0b00
    CFG_ADDRINC_single =        0b01
    CFG_ADDRINC_packed =        0b10
    CFG_MEM_8bits =             0b000
    CFG_MEM_16bits =            0b001
    CFG_MEM_32bits =            0b010
    def CSWsetDbgSwEnable(self, bit):
        cfg = self.getCFG() & self.CFG_DBGSWENABLE
        cfg |= (bit<<self.CFG_DBGSWENABLE_BITS)
    def CSWgetDbgSwEnable(self):
        cfg = (self.getCFG() & self.CFG_DBGSWENABLE) >> self.CFG_DBGSWENABLE_BITS
        return cfg

    def CSWsetAddrInc(self, bits=CFG_ADDRINC_single):
        cfg = (self.getCFG() & self.CFG_ADDRINC) >> self.CFG_ADDRINC_BITS
        cfg |= (bit<<self.CFG_DBGSWENABLE_BITS)
    def CSWsetMemAccessSize(self, bytecount=self.CSW_MEM_32bits):        # 0b010 == 32bit words, necessary if the implementation allows for variable sizes
        csw = self.getCSW()
        csw &= 0xfffffff8
        csw |= (bytecount>>1)
        self.setCSW(csw)




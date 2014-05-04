from GoodFETARM7 import *
import ATMEL_USART as usart
"""
This is the ARM7 series of microcontrollers from Atmel, including:
* AT91M40800
* AT91R40807
* AT91M40807
* AT91R40008

"""
##### FLASH UPLOADER CODE
EBI_BASE =       0xFFE00000
EBI_OFF_CSR0 =   0x0
EBI_OFF_CSR1 =   0x4
EBI_OFF_CSR2 =   0x8
EBI_OFF_CSR3 =   0xc
EBI_OFF_CSR4 =   0x10
EBI_OFF_CSR5 =   0x14
EBI_OFF_CSR6 =   0x18
EBI_OFF_CSR7 =   0x1c
EBI_CSR0_MASK =  0xFFFF0000
EBI_OFF_RCR =    0x20
EBI_OFF_MCR =    0x24

EBI_CSR0 =      EBI_BASE + EBI_OFF_CSR0
EBI_CSR1 =      EBI_BASE + EBI_OFF_CSR1
EBI_CSR2 =      EBI_BASE + EBI_OFF_CSR2
EBI_CSR3 =      EBI_BASE + EBI_OFF_CSR3
EBI_CSR4 =      EBI_BASE + EBI_OFF_CSR4
EBI_CSR5 =      EBI_BASE + EBI_OFF_CSR5
EBI_CSR6 =      EBI_BASE + EBI_OFF_CSR6
EBI_CSR7 =      EBI_BASE + EBI_OFF_CSR7
EBI_MCR =       EBI_BASE + EBI_OFF_MCR

REMAP_CMD =      0x00000001
MEM_CTRL_VAL =   0x00000006


SF_CHIP_ID =     0xFFF00000         # AT91R40 series, not sure on others
SF_CIDR_MASK =   0x0FFFFF00

PS_BASE =        0xFFFF4000
PS_CR =          PS_BASE
PS_PCER =        PS_BASE + 0x4
PS_PCDR =        PS_BASE + 0x8
PS_PCSR =        PS_BASE + 0xC
PS_US0 =         1<<2
PS_US1 =         1<<3
PS_TC0 =         1<<4
PS_TC1 =         1<<5
PS_TC2 =         1<<6
PS_PIO =         1<<8

AIC_INT_SOURCES = (
        ("FIQ","Fast Interrupt"),
        ("SWIRQ","Software Interrupt"),
        ("US0IRQ","USART Channel 0 Interrupt"),
        ("US1IRQ","USART Channel 1 Interrupt"),
        ("TC0IRQ","Timer Channel 0 Interrupt"),
        ("TC1IRQ","Timer Channel 1 Interrupt"),
        ("TC2IRQ","Timer Channel 2 Interrupt"),
        ("WDIRQ", "Watchdog Interrupt"),
        ("PIOIRQ","Parallel I/O Controller Interrupt"),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        ("IRQ0","External Interrupt 0"),
        ("IRQ1","External Interrupt 0"),
        ("IRQ0","External Interrupt 0"),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        (None,None),
        )

def aic_smr_decode(smr):
    output = ["Interrupt Priority: %s"%(smr&7),
            "Interrupt Source Type: %s"%("Low Level Sensitive","Negative Edge Triggered","High Level Sensitive","Positive Edge Triggered")[(smr>>5)],
            ]
    return "\n".join(output)

AIC_BASE = 0xFFFFF000
AIC_SMR = [(AIC_BASE+(x*4), "Source Mode Register %d"%x)  for x in xrange(32)]
AIC_SVR = [(AIC_BASE+0x80+(x*4), "Source Vector Register %d"%x)  for x in xrange(32)]
AIC_IVR = AIC_BASE + 0x100
AIC_FVR = AIC_BASE + 0x104
AIC_ISR = AIC_BASE + 0x108
AIC_IPR = AIC_BASE + 0x10c
AIC_IMR = AIC_BASE + 0x110
AIC_CISR = AIC_BASE + 0x114
AIC_IECR = AIC_BASE + 0x120
AIC_IDCR = AIC_BASE + 0x124
AIC_ICCR = AIC_BASE + 0x128
AIC_ISCR = AIC_BASE + 0x12c
AIC_EOICR = AIC_BASE + 0x130
AIC_SPU = AIC_BASE + 0x134


PIO_BASE = 0xFFFF0000
PIO_PER =   PIO_BASE + 0x0
PIO_PDR =   PIO_BASE + 0x4
PIO_PSR =   PIO_BASE + 0x8
PIO_OER =   PIO_BASE + 0x10
PIO_ODR =   PIO_BASE + 0x14
PIO_OSR =   PIO_BASE + 0x18
PIO_SODR =  PIO_BASE + 0x30
PIO_CODR =  PIO_BASE + 0x34
PIO_ODSR =  PIO_BASE + 0x38
PIO_CDSR =  PIO_BASE + 0x3c
PIO_IER =   PIO_BASE + 0x40
PIO_IDR =   PIO_BASE + 0x44
PIO_IMR =   PIO_BASE + 0x48
PIO_ISR =   PIO_BASE + 0x4c

WD_BASE = 0xFFFF8000
WD_OMR  =   WD_BASE + 0x0
WD_CMR  =   WD_BASE + 0x4
WD_CR   =   WD_BASE + 0x8
WD_SR   =   WD_BASE + 0xc

SF_BASE = 0xFFF00000
SF_CIDR =   SF_BASE + 0x0
SF_EXID =   SF_BASE + 0x4
SF_RSR =    SF_BASE + 0x8
SF_MMR =    SF_BASE + 0xC
SF_PMR =    SF_BASE + 0x18

#* Flash
FLASH_BASE_ADDR =    0x1000000
WAIT =               300000
FLASH_CODE_MASK =    0x000000FF

#*Flash AT49 codes
ATMEL_MANUFACTURED =         0x001F
FLASH_AT49BV_UNKNOW =        0xFFFF
FLASH_AT49BV8011 =           0x00CB
FLASH_AT49BV8011T =          0x004A
FLASH_AT49BV16x4 =           0x00C0
FLASH_AT49BV16x4T =          0x00C2

#*Flash AT29 codes
FLASH_AT29LV1024 =               0X26
FLASH_AT29C020 =                 0XDA

#* Flash Program information
FLASH_PRG_SIZE =     0x800   #* 2Kbytes
FLASH_PRG_DEST =     0x20    #* Address on the target
START_PRG =          0x20

#* Parameter for Flash_XV_Send_Data functions
ERASE =  1
PROGRAM =0

MIRROR =     1
NO_MIRROR =  0

ERASE_DATA = 0

#* Load program parameters
NB_REG =     13
SIZE_DATA =  4

#* Flash LV Send Data parameters
SIZE_256_BYTES = 0x100
PACKET_SIZE =64

NB_PRG =     3

#* Periph
EBI =    0
PLL =    1

#* Targets
EB40 =   0x04080700
EB40A =  0x04000800
EB42 =   0x04280000
EB55 =   0x05580000
EB63 =   0x06320000
EBMASK = 0x0fffff00

NB_TARGET_SUPPORTED =    6

#* Flash type
FLASH_LV =   0
FLASH_BV =   1

#* Flash Program Address 
FLASH_LV_PRG =   0x01018000
FLASH_BV_PRG =   0x0101A000

EBI_READ    = 4
EBI_WRITE   = 2

ebi_memory_map_items = {
        EBI_OFF_CSR0:("Chip Select Register 0", "EBI_CSR0", EBI_READ|EBI_WRITE,0x0000203e),
        EBI_OFF_CSR1:("Chip Select Register 1", "EBI_CSR1", EBI_READ|EBI_WRITE,0x10000000),
        EBI_OFF_CSR2:("Chip Select Register 2", "EBI_CSR2", EBI_READ|EBI_WRITE,0x20000000),
        EBI_OFF_CSR3:("Chip Select Register 3", "EBI_CSR3", EBI_READ|EBI_WRITE,0x30000000),
        EBI_OFF_CSR4:("Chip Select Register 4", "EBI_CSR4", EBI_READ|EBI_WRITE,0x40000000),
        EBI_OFF_CSR5:("Chip Select Register 5", "EBI_CSR5", EBI_READ|EBI_WRITE,0x50000000),
        EBI_OFF_CSR6:("Chip Select Register 6", "EBI_CSR6", EBI_READ|EBI_WRITE,0x60000000),
        EBI_OFF_CSR7:("Chip Select Register 7", "EBI_CSR7", EBI_READ|EBI_WRITE,0x70000000),
        EBI_OFF_MCR: ("Memory Control Register","EBI_MCR",  EBI_READ|EBI_WRITE,0),
        }

def ebi_csr_decode(reg):
    addr = reg>>20
    csen = (reg>>13)&1
    bat =  (reg>>12)&1
    tdf =  (reg>>9)&7
    pages =(reg>>7)&3
    wse =  (reg>>5)&1
    nws =  (reg>>2)&7
    dbw =  (reg&3)
    return [ addr, csen, bat, tdf, pages, wse, nws, dbw]

def ebi_csr_decode_str(reg):
    (addr,
    csen,
    bat,
    tdf,
    pages,
    wse,
    nws,
    dbw) = ebi_csr_decode(reg)
    output = ["(register: %x)"%reg,
            "Base Address: %s"%hex(addr<<20),
            "Chip Select: %s"%("False","True")[csen],
            "Byte Access Type: %s"%("Byte-Write","Byte-Access")[bat],
            "Data Float Output Time: %d cycles added"%tdf,
            "Page Size: %d MB"%(1,4,16,64)[pages],
            "Wait State: %s"%("disabled","enabled")[wse],
            "Wait States: %d"%nws,
            "Data Bus Size: %d bits"%(0,16,8,0)[dbw],
            ]
    return "\n".join(output)

mcr_ale = {
        0: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        1: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        2: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        3: ("A20,A21,A22,A23", 16, "None", "EBI_ALE_16M"),
        4: ("A20,A21,A22", 8, "CS4", "EBI_ALE_8M"),
        5: ("A20,A21", 4, "CS4,CS5", "EBI_ALE_4M"),
        6: ("A20", 2, "CS4,CS5,CS6", "EBI_ALE_2M"),
        7: ("None", 1, "CS4,CS5,CS6,CS7", "EBI_ALE_1M"),
        }

def mcr_decode(mcr):
    validAddrBits,maxAddrSpace,validCS,codeLabel = mcr_ale[mcr&7]
    drp = mcr>>4
    #print hex(drp)
    if drp and drp != 1:
        drp = 2
    return (validAddrBits, maxAddrSpace, validCS, codeLabel, drp)

def mcr_decode_str(mcr):
    ( validAddrBits, maxAddrSpace, validCS, codeLabel, drp) = mcr_decode(mcr)
    output = [ 
            "(register: %x)"%mcr,
            "Valid Address Bits: %s"%validAddrBits,
            "Maximum Address Space: 0x%x MB"%maxAddrSpace,
            "Valid Chip Select: %s"%validCS,
            "Code Label:  %s"%codeLabel,
            ("Standard Read Protocol for all external memory devices enabled (EBI_DRP_STANDARD)","Early Read Protocol for all external memory devices enabled (EBI_DRP_EARLY)","Invalid mcr")[drp]
            ]
    return "\n".join(output)

def wd_omr_decode(omr):
	return (omr>>4, (omr>>3)&1, (omr>>2)&1, (omr>>1)&1, omr&1)

def wd_omr_decode_str(omr):
    ( okey, esig, int, rst, wdog ) = wd_omr_decode(omr)
    return "\n".join([
            "Overflow Access Key (OKEY): %x"%(okey),
            "External Signal (EXTEN): %s"%("disabled","enabled")[esig],
            "Interrupt (IRQEN): %s"%("disabled","enabled")[int],
            "Reset (RSTEN): %s"%("disabled","enabled")[rst],
            "Watch Dog (WDEN): %s"%("disabled","enabled")[wdog],
            ])

def wd_cmr_decode(cmr):
    return "MCK/%d"%(8,32,128,1024)[(cmr>>2)&0xf]





class GoodFETAT91X40(GoodFETARM7):
    def __init__(self):
        GoodFETARM7.__init__(self)
        self.usart0 = usart.USART(usart.USART0_BASE)
        self.usart1 = usart.USART(usart.USART1_BASE)

    def halt(self, disableWD=True):
        GoodFETARM7.halt(self)
        if not disableWD: return

        #Disable Watch Dog
        self.disableWatchDog()

    def resume(self, enableWD=False):
        GoodFETARM7.resume(self)
        if not enableWD: return

        self.enableWatchDog()

    def getChipSelectReg(self, chipnum):
        addr = EBI_BASE + (chipnum*4)
        reg, = self.ARMreadChunk(addr,1)
        return reg
    def getChipSelectRegstr(self, chipnum):
        return ebi_csr_decode_str(self.getChipSelectReg(chipnum))
    def getChipSelectReglist(self, chipnum):
        return ebi_csr_decode(self.getChipSelectReg(chipnum))
    def setChipSelectReg(self, chipnum, value):
        addr = EBI_BASE + (chipnum*4)
        self.ARMwriteChunk(addr,[value])

    def getEBIMemoryMapstr(self):
        keys = ebi_memory_map_items.keys()
        keys.sort()
        output = [ "===EBI Memory Map==="]
        for x in xrange(8):
            desc,name,rw,default = ebi_memory_map_items[x*4]
            output.append("\nMAP: %s (%s) - default: %x\n%s"%(name,desc,default,self.getChipSelectRegstr(x)))
        return "\n".join(output)
    def setRemap(self):
        self.ARMwriteChunk(EBI_BASE + EBI_OFF_RCR,[REMAP_CMD])
    def getMemoryControlRegister(self):
        mcr, = self.ARMreadMem(EBI_MCR)
        return mcr
    def getMemoryControlRegisterstr(self):
        return mcr_decode_str(self.getMemoryControlRegister())
    def getEBIMCRstr(self):
        return  "EBI Memory Control Register\n" + self.getMemoryControlRegisterstr()

    def getInterruptSourceModeReg(self, regnum):
        regval = self.ARMreadMem(AIC_SMR[regnum][0])
        return retval
    def getInterruptSourceModeRegstr(self, regnum):
        return aic_smr_decode(self.getInterruptSourceModeReg(regnum))
    def setInterruptSourceModeReg(self, regnum, val):
        self.ARMwriteMem(AIC_SMR[regnum][0], val)

    def getInterruptSourceVectorReg(self, regnum):
        regval = self.ARMreadMem(AIC_SVR[regnum][0])
        return retval
    def setInterruptSourceModeReg(self, regnum, val):
        self.ARMwriteMem(AIC_SVR[regnum][0], val)

    def getIRQVectorReg(self):
        return self.ARMreadMem(AIC_IVR)
    def getFIQVectorReg(self):
        return self.ARMreadMem(AIC_FVR)

    def getInterruptStatusReg(self):
        return self.ARMreadMem(AIC_ISR)
    def getInterruptPendingReg(self):
        return self.ARMreadMem(AIC_FSR)
    def getInterruptMaskReg(self):
        return self.ARMreadMem(AIC_IMR)
    def getCoreInterruptStatusReg(self):
        return self.ARMreadMem(AIC_CISR)
    def enableInterrupt(self, interrupt):
        self.ARMwriteMem(AIC_IECR, 1<<interrupt)
    def disableInterrupt(self, interrupt):
        self.ARMwriteMem(AIC_IDCR, 1<<interrupt)
    def setInterruptCommandReg(self, interrupt):
        self.ARMwriteMem(AIC_ISCR, 1<<interrupt)
    def clearInterruptCommandReg(self, interrupt):
        self.ARMwriteMem(AIC_ICCR, 1<<interrupt)
    def clearCurrentInterrupt(self):
        self.ARMwriteMem(AIC_EOICR, 1<<interrupt)
    def getSpuriousVectorReg(self):
        return self.ARMreadMem(AIC_SPU)
    def setSpuriousVectorReg(self, val):
        return self.ARMreadMem(AIC_SPU)

    def enablePIOpin(self, mask):
        self.ARMwriteMem(PIO_PER, mask)
    def disablePIOpin(self, mask):
        self.ARMwriteMem(PIO_PDR, mask)
    def getPIOstatus(self):
        return self.ARMreadMem(PIO_PSR)
    def enablePIOoutput(self,mask):
        self.ARMwriteMem(PIO_OER, mask)
    def disablePIOoutput(self,mask):
        self.ARMwriteMem(PIO_ODR, mask)
    def getPIOoutputStatus(self):
        return self.ARMreadMem(PIO_OSR)

    def setOutputPin(self,mask):
        self.ARMwriteMem(PIO_SODR, mask)
    def clearOutputPin(self,mask):
        self.ARMwriteMem(PIO_CODR, mask)
    def getOutputDataStatusReg(self):
        return self.ARMreadMem(PIO_ODSR)
    def getPinDataStatusReg(self):
        return self.ARMreadMem(PIO_PDSR)
    def enablePIOinterrupt(self, mask):
        self.ARMwriteMem(PIO_IER, mask)
    def disablePIOinterrupt(self, mask):
        self.ARMwriteMem(PIO_IDR, mask)
    def getPIOinterruptMaskReg(self):
        return self.ARMreadMem(PIO_IMR)
    def getPIOinteruptStatusReg(self):
        return self.ARMreadMem(PIO_ODSR)


    def getWatchDogOverflowModeReg(self):
        return self.ARMreadMem(WD_OMR)
    def getWatchDogOverflowModeStr(self):
        return wd_omr_decode_str(self.getWatchDogOverflowModeReg()[0])
    def setWatchDogOverflowModeReg(self, mode=0x00002340):
        self.ARMwriteMem(WD_OMR, [mode])
    def getWatchDogClockModeReg(self):
        return self.ARMreadMem(WD_CMR)[0]
    def setWatchDogClockModeReg(self, mode=0x06e):
        self.ARMwriteMem(WD_CMR, [mode])
    def setWatchDogControlReg(self, mode=0xC071):
        self.ARMwriteMem(WD_CR, [mode])
    def getWatchDogStatusReg(self):
        return self.ARMreadMem(WD_SR)[0]
    def disableWatchDog(self):
        # 0x234 in OKEY enables writing and 0 in lowest nibble disables
        self.setWatchDogOverflowModeReg()
    def enableWatchDog(self):
        # Initialize the WD Clock Mode Register
        self.setWatchDogClockModeReg(mode=0x0000373c)
        # Restart the timer
        self.setWatchDogControlReg(mode=0x0000c071)
        # Enable the watchdog
        self.setWatchDogOverflowModeReg(mode=0x00002340)
    def statWatchDog(self):
        print "Status Watch Dog:"
        print "Register Value: 0b%s" % '{0:032b}'.format(self.getWatchDogOverflowModeReg()[0])
        print self.getWatchDogOverflowModeStr()
        print "Clock Mode Reg: %x" % self.getWatchDogClockModeReg()
        print "Status Reg: %x" % self.getWatchDogStatusReg()
    def checkWatchDog(self):
        return self.getWatchDogOverflowModeStr()
        

    def getChipID(self):
        chipid = self.ARMreadMem(SF_CIDR,1)
        return chipid[0]
    def getResetStatusReg(self):
        return self.ARMreadMem(SF_RSR)
    def getMemoryModeReg(self):
        return self.ARMreadMem(SF_MMR)
    def setMemoryModeReg(self, val=0):
        self.ARMwriteMem(SF_MMR, val)
    def getProtectModeReg(self):
        return self.ARMreadMem(SF_PMR)
    def setProtectModeReg(self, val=0x27a80000):
        self.ARMwriteMem(SF_PMR, val)







    def ARMwriteFirmware(self, firmware):
        self.halt()
        chipid = self.ARMgetChipID()
        # FIXME: initialize PLL or EBI
        self.ARMmassErase(chipid)
        self.ARMset_regCPSR(PM_svc)   # set supervisor mode
        # FIXME: download the "flash identifier" program into target RAM
        self.ARMsetPC(PROGGYBASE)
        self.release()
        # get manufacturer crap through DCC (really??  screw this...)
        self.halt()
        if (self.ARMget_regCPSR() & PM_svc != PM_svc):
            raise Exception("No longer in Supervisor mode after firmware upload")
        # FIXME: download the downloader program into target RAM
        self.ARMsetPC(PROGGYBASE)
        self.release()
        # FIXME: use DCC to upload the new firmware

    def clearFlash(self):
        pass

    def readPages(self, addr, pagecount, pagesz=(1024*1024)):
        global pages;
        pages = []
        for page in xrange(pagecount):
            pages.append(self.ARMreadChunk(addr+(pagesz*page), pagesz))
        return pages


######### command line stuff #########

from GoodFETARM7 import *

def at91x40_main():
    ''' this function should be called from command line app '''
    #Initialize FET and set baud rate
    client=GoodFETAT91X40()
    client.serInit()

    client.setup()
    client.start()

    at91x40_cli_handler(client, sys.argv)



BLOCK_DWORDS = 48
BLOCK_SIZE   = 4 * BLOCK_DWORDS
def at91x40_cli_handler(client, argv):

    if(argv[1]=="chipRegStr"):
        client.halt()
        print "#####"
        print client.getChipSelectRegstr(int(argv[2]))
        print "#####"
        client.resume()

    if(argv[1]=="chipRegList"):
        client.halt()
        print "#####"
        print client.getChipSelectReglist(int(argv[2]))
        print "#####"
        client.resume()

    if(argv[1]=="chipRegValue"):
        client.halt()
        print "#####"
        print "Chip Register Value:",hex(client.getChipSelectReg(int(argv[2])))
        print "#####"

    if(argv[1]=="ecdump"):
        f = argv[2]
        start=0x00000000
        stop=0xFFFFFFFF
        if(len(argv)>3):
            start=int(argv[3],16)
        if(len(argv)>4):
            stop=int(argv[4],16)

        ##############################3
        # Error checking requires a special register
        # Should an error occur while reading from the chip's memory
        # These values will help to test if the chip is working and 
        # the memory is mapped properly before continuing
        # Use the chipRegStr verb to determine the value of the 
        # Special Register when the chip is operating normally
        # Example: ./goodfet.at91x40 chipRegValue 1
        ##############################3
        # user$ ./goodfet.at91x40 chipRegValue 1
        # Identifying Target:
        # # DEBUG 0x120
        # Chip IDCODE: 0x1f0f0f0f
        #     ver: 1
        #     partno: f0f0
        #     mfgid: 787
        #
        # Debug Status:   Interrupts Enabled (or not?) 
        #
        # #####
        # Chip Register Value: 0x10000000
        # #####
        ##############################
        special_reg_num=1
        special_addr=0x010000000
        if(len(argv)>5):
            # Yes, this requires that you set the start and stop addresses
            special_reg_num=int(argv[5])
            special_addr=int(argv[6],16)
        err_list = []
        
        print "Dumping from %04x to %04x as %s." % (start,stop,f)
        # FIXME: get mcu state and return it to that state
        client.halt()

        h = IntelHex(None)
        base = start
        err_cnt = 0
        reset_cnt = 0
        while base<=stop:
            confirmed = False
            while not confirmed: 
                i = base
                try:
                    data=client.ARMreadChunk(i, BLOCK_DWORDS, verbose=0)
                    print "Dumped %06x."%i
                    for dword in data:
                        if i<=stop:# and dword != 0xdeadbeef:
                            h.puts( i, struct.pack("<I", dword) )
                            err_cnt = 0
                        i += 4

                    confirmed=True

                # FIXME: get mcu state and return it to that state
                except:
                    # Handle exceptions by counting errors after pausing to let ARM settle
                    err_cnt = 1
                    fail = 0
                    while err_cnt:
                        time.sleep(.25)
                        if err_cnt == 100:
                            print "Unknown error occurred at least 100 times. Resync did not work. Writing incomplete data to file."
                            fail = 1
                            break
                        else:
                            try:
                                print "Unknown error during read. Resync and retry."
                                err_list.append("0x%06x"%i)

                                # If we error out several times then reset the chip and restart
                                # This uses a special register value from a Chip Select Register
                                # to test that the chip is in the operation state we expect
                                if not ((err_cnt+1) % 2):
                                    while True:
                                        print "    Reset:",reset_cnt
                                        check_addr = client.getChipSelectReg(special_reg_num)
                                        print "    Special Addr:",hex(special_addr)
                                        print "    Check Addr:",hex(check_addr)
                                        if (special_addr == check_addr):
                                            break
                                        if reset_cnt == 10:
                                            reset_cnt = 0
                                            print "    Resetting Target"
                                            client.ARMresettarget(1000)
                                            client.halt()
                                        reset_cnt += 1
                                        time.sleep(.25)
                                else:
                                    #Resync ARM and Watch Dog
                                    client.resume()
                                    client.halt()

                                err_cnt = 0
                            except:
                                err_cnt += 1
                                pass
                    if fail:
                        break

            # we've confirmed the write on this block... move on.
            base += BLOCK_SIZE

        h.write_hex_file(f)
        print "Addresses that required resync:"
        if err_list:
            for e in err_list:
                print "   ",e
        else:
            print "   None"

        try:
            client.resume()
        except:
            print "error resuming...  resetting"
            try:
                client.ARMresettarget()
            except:
                print "error resetting!  just exiting"



    if(argv[1]=="memorymap"):
        client.halt()
        print "=============================================="
        print client.getEBIMCRstr()
        print ""
        print client.getEBIMemoryMapstr()
        client.resume()

    if(argv[1]=="memorycontrolreg"):
        client.halt()
        print client.getEBIMCRstr()
        client.resume()



    if(argv[1]=="stat_watchdog"):
        client.halt()
        print "Watch Dog Status:"
        print "--"
        client.statWatchDog()
        client.resume()

    if(argv[1]=="test_disable_watchdog"):
        client.halt()
        print "Status Watch Dog:"
        client.statWatchDog()
        print "--"
        print "Disabling Watchdog Timer:"
        client.disableWatchDog()
        time.sleep(2) # pause to settle
        print "\nChecking:"
        client.statWatchDog()
        print "--"
        print "Done. Resume may re-enable Watch Dog."
        client.resume()

    # anything we didn't provide from arm7:        
    arm7_cli_handler(client, argv)

    #client.ARMreleasecpu()
    #client.ARMstop()


if __name__ == "__main__":
    if(len(sys.argv)==1):
        at91x40_syntax()

    else: 
        at91x40_main()



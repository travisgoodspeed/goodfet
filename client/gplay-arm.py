#!/usr/bin/env ipython
import sys, struct, binascii,time
from GoodFETARM7 import *
from intelhex import IntelHex


data = []

client=GoodFETARM7();
def init():
    #Initailize FET and set baud rate
    print >>sys.stderr,"Connecting to goodfet..."
    client.serInit()
    #
    #Connect to target
    print >>sys.stderr,"Setting up JTAG ARM on goodfet..."
    client.setup()
    print >>sys.stderr,"Starting JTAG ARM on goodfet...\n\n"
    client.start()
    print "STARTUP: %s\n"%repr(client.data)
    #

def print_registers():
    return [ hex(client.ARMget_register(x)) for x in range(15) ]

def regwratchet(num,hi=13,lo=0):
    for x in xrange(lo,hi+1):
        client.ARMset_register(x,num)

def test():
    print "ARM JTAG Test Unit"
    print " Chip ID", hex(client.ARMident())
    print client.ARMidentstr()
    print " Debug State: ",hex(client.ARMget_dbgstate())
    print " Debug CTRL:  ",hex(client.ARMget_dbgctrl())
    print
    print "Testing Register Read/Writes"
    print " Storing old values"
    originalregs = [client.ARMget_register(x) for x in xrange(16)]

    print "Simple test"
    test = [None for x in xrange(15)]
    control = [x for x in xrange(15)]
    for x in xrange(15):
        client.ARMset_register(x,control[x])
        test[x] = client.ARMget_register(x)
    if control != test:
        print "FAIL"
        print "Control:",control
        print "Test:   ",test

    print "A little harder..."
    test = [None for x in xrange(15)]
    control = [4*x for x in xrange(15)]
    for x in xrange(15):
        client.ARMset_register(x,control[x])
        test[x] = client.ARMget_register(x)
    if control != test:
        print "FAIL"
        print "Control:",control
        print "Test:   ",test

    print "Complex testing 1"
    for y in xrange(0,0xffffffff,0x10101010):
            test = [None for x in xrange(15)]
            control = [y for x in xrange(15)]
            print " Test parms: ",control
            for x in xrange(15):
                client.ARMset_register(x,control[x])
                test[x] = client.ARMget_register(x)
            if control != test:
                print "FAIL"
                print "Control:",control
                print "Test:   ",test

    print "Complex testing 2"
    for y in xrange(0,0xffffffff,101010101):
            test = [None for x in xrange(15)]
            control = [y for x in xrange(15)]
            print " Test parms: ",control
            for x in xrange(15):
                client.ARMset_register(x,control[x])
                test[x] = client.ARMget_register(x)
            if control != test:
                print "FAIL"
                print "Control:",control
                print "Test:   ",test

    test = [None for x in xrange(15)]
    control = [0x100*x for x in xrange(15)]
    for x in xrange(15):
        client.ARMset_register(x,control[x])
        test[x] = client.ARMget_register(x)
    if control != test:
        print "FAIL"
        print "Control:",control
        print "Test:   ",test

    print "Resetting original register values..."
    for x in xrange(16):
        client.ARMset_register(x,originalregs[x])
    regs = [client.ARMget_register(x) for x in xrange(16)]
    print "Original:           \t",originalregs
    print "Now (r15 may differ:\t",regs

    print "Testing setting and movement of PC between instructions"
    #client.ARMsetPC(0x0)
    print "PC:",client.ARMgetPC()
    print "PC:",client.ARMgetPC()
    print "PC:",client.ARMgetPC()
    print "PC:",client.ARMgetPC()
    print "Testing readChunk/writeChunk"
    mem=client.ARMreadChunk(0x200000,32)
    client.ARMwriteChunk(0x200000,mem)
    mem2=client.ARMreadChunk(0x200000,32)
    if (mem != mem2):
        print "Failed: \n%s\n%s"%(repr([hex(x) for x in mem]), repr([hex(x) for x in mem2]))
    else:
        print "Passed."


def test1():
    global data
    print "\n\nTesting JTAG for ARM\n"
    client.writecmd(0x33,0xd0,4,[0x40,0x40,0x40,0x40]); print "loopback:   \t %s"%repr(client.data)                  # loopback
    data.append(client.data)
    client.writecmd(0x33,0xd1,2,[1,0]); print "scanchain1:\t %s"%repr(client.data)               # set scan chain
    data.append(client.data)
    client.writecmd(0x33,0xd2,0,[]); print "debug state:\t %s"%repr(client.data)                  # get dbg state
    data.append(client.data)
    client.writecmd(0x33,0xd3,0,[0,0,0xa0,0xe1]); print "exec_nop: \t %s"%repr(client.data)     # execute instruction
    data.append(client.data)
    client.writecmd(0x33,0xd3,0,[0,0,0x8e,0xe5]); print "exec_stuff: \t %s"%repr(client.data)     # execute instruction
    data.append(client.data)
    client.writecmd(0x33,0xd3,0,[0,0,0xa0,0xe1]); print "exec_nop: \t %s"%repr(client.data)     # execute instruction
    data.append(client.data)
    client.writecmd(0x33,0xd3,0,[0,0,0xa0,0xe1]); print "exec_nop: \t %s"%repr(client.data)     # execute instruction
    data.append(client.data)
    client.writecmd(0x33,0xd3,0,[0,0,0xa0,0xe1]); print "exec_nop: \t %s"%repr(client.data)     # execute instruction
    data.append(client.data)
    client.writecmd(0x33,0xd6,0,[]); print "shift_dr_32: \t %s"%repr(client.data)                  # dr_shift32
    data.append(client.data)
    client.writecmd(0x33,0xd5,8,[3, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40]); print "set_register:\t %s"%repr(client.data)                  # set register
    data.append(client.data)
    client.writecmd(0x33,0xd4,1,[3]); print "get_register:\t %s"%repr(client.data)                  # get register
    data.append(client.data)
    client.writecmd(0x33,0xd7,0,[]); print "chain1:      \t %s"%repr(client.data)                  # chain1
    data.append(client.data)
    client.writecmd(0x33,0xd8,0,[]); print "read_chain2: \t %s"%repr(client.data)                  # read chain2
    data.append(client.data)
    client.writecmd(0x33,0xd9,0,[]); print "idcode:      \t %s"%repr(client.data)                  # read idcode
    data.append(client.data)
    client.writecmd(0x33,0xf0,2,[4,4,1,1]); print "f0:       \t %s"%repr(client.data)   # read idcode
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x0,4,4,4,4,4,4,4]); print "verb(0):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x2,4,4,4,4,4,4,4]); print "verb(2):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x3,4,4,4,4,4,4,4]); print "verb(3):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x4,4,4,4,4,4,4,4]); print "verb(4):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x5,4,4,4,4,4,4,4]); print "verb(5):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x7,4,4,4,4,4,4,4]); print "verb(7):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0x9,4,4,4,4,4,4,4]); print "verb(9):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0xc,4,4,4,4,4,4,4]); print "verb(c):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0xe,0,0,0,0,0,0xa0,0xe1]); print "verb(e):     \t %s"%repr(client.data)
    data.append(client.data)
    client.writecmd(0x33,0xdb,8,[0xf,4,4,4,4,4,4,4]); print "verb(f):     \t %s"%repr(client.data)
    data.append(client.data)

def test2():
    global data
    print "\n\nTesting JTAG for ARM\n"
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "Debug CTRL:  %x"%client.ARMget_dbgctrl()
    client.writecmd(0x33,0xda,0,[])
    print "TEST CHAIN0: %s"%repr(client.data)
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    client.writecmd(0x33,0xd0,4,[0xf7,0xf7,0xf7,0xf7])
    print "Loopback:   \t %s"%repr(client.data)                  # loopback
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "IDCODE:      %x"%client.ARMident()
    print "GetPC: %x"%client.ARMgetPC()
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "IDCODE:      %x"%client.ARMident()
    print "set_register(3,0x41414141):  %x"%client.ARMset_register(3,0x41414141)
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "IDCODE:      %x"%client.ARMident()
    print "get_register(3):             %x"%client.ARMget_register(3)
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    print "IDCODE:      %x"%client.ARMident()

def test3():
    print "IDCODE:      %x"%client.ARMident()
    print "Debug State: %x"%client.ARMget_dbgstate ()
    client.writecmd(0x33,0xd0,4,[0xf7,0xf7,0xf7,0xf7])
    print "Loopback:   \t %s"%repr(client.data)                  # loopback
    client.writecmd(0x33,0xd5,8,[0,0,0,0,0xf7,0xf7,0xf7,0xf7])
    print "test_set_reg:   \t %s"%repr(client.data)            
    client.writecmd(0x33,0xd4,1,[0])
    print "test_get_reg:   \t %s"%repr(client.data)           
    print "set_register(3,0x41414141):  %x"%client.ARMset_register(3,0x41414141)
    print "get_register(3):             %x"%client.ARMget_register(3)
    client.writecmd(0x33,0xd4,1,[0])
    print "test_get_reg:   \t %s"%repr(client.data)           

def test4():
        print "IDCODE:      %x"%client.ARMident()
        print "Debug State: %x"%client.ARMget_dbgstate ()
        print "set_register(0,0x4141):  %x"%client.ARMset_register(0,0x4141)
        print "get_register(0):             %x"%client.ARMget_register(0)
        print "set_register(1,0x4141):  %x"%client.ARMset_register(1,0x4142)
        print "get_register(1):             %x"%client.ARMget_register(1)
        print "set_register(2,0x4141):  %x"%client.ARMset_register(2,0x4143)
        print "get_register(2):             %x"%client.ARMget_register(2)
        print "set_register(3,0x4141):  %x"%client.ARMset_register(3,0x4144)
        print "get_register(3):             %x"%client.ARMget_register(3)
        print "set_register(4,0x4141):  %x"%client.ARMset_register(4,0x4145)
        print "get_register(4):             %x"%client.ARMget_register(4)
        print "set_register(5,0x4141):  %x"%client.ARMset_register(5,0x4146)
        print "get_register(5):             %x"%client.ARMget_register(5)
        print "set_register(6,0x4141):  %x"%client.ARMset_register(6,0x4147)
        print "get_register(6):             %x"%client.ARMget_register(6)
        print "set_register(7,0x4141):  %x"%client.ARMset_register(7,0x4148)
        print "get_register(7):             %x"%client.ARMget_register(7)
        print "set_register(8,0x4141):  %x"%client.ARMset_register(8,0x4149)
        print "get_register(8):             %x"%client.ARMget_register(8)
        print "set_register(9,0x4141):  %x"%client.ARMset_register(9,0x4140)
        print "get_register(9):             %x"%client.ARMget_register(9)
        print "set_register(10,0x4141):  %x"%client.ARMset_register(10,0x4151)
        print "get_register(10):             %x"%client.ARMget_register(10)
        print "set_register(11,0x4141):  %x"%client.ARMset_register(11,0x4152)
        print "get_register(11):             %x"%client.ARMget_register(11)
        print "set_register(12,0x4141):  %x"%client.ARMset_register(12,0x4153)
        print "get_register(12):             %x"%client.ARMget_register(12)
        print "set_register(13,0x4141):  %x"%client.ARMset_register(13,0x4154)
        print "get_register(13):             %x"%client.ARMget_register(13)
        print "set_register(14,0x4141):  %x"%client.ARMset_register(14,0x4155)
        print "get_register(14):             %x"%client.ARMget_register(14)
        #print "set_register(15,0x4141):  %x"%client.ARMset_register(15,0x41414156)
        #print "get_register(15):             %x"%client.ARMget_register(15)


seed = 0
def test5(start=0,end=15):
    global results,seed
    results = [[] for x in range(end)]
    while True:
        #print "IDCODE:      %x"%client.ARMident()
        #print "Debug State: %x"%client.ARMget_dbgstate ()
        for x in range(start,end):
            num = client.ARMset_register(x,seed)
            print "set_register(%d,0x%x):  %x"%(x,seed,num)
            num = client.ARMget_register(x)
            print "get_register(%d):             %x"%(x,num)
            results[x].append(num)
            if (num != seed):
                for y in range(13):
                    num = client.ARMset_register(x,seed)
                    print "set_register(%d,0x%x):  %x"%(x,seed,num)
                    num = client.ARMget_register(x)
                    print "get_register(%d):             %x"%(x,num)
                    results[x].append(num)
            seed += 1
            client.ARMident()
            client.ARMident()
            print "Debug State: %x"%client.ARMget_dbgstate ()

def test6(start=0,end=15):
    global results,seed
    results = [[] for x in range(end)]
    while True:
        #print "IDCODE:      %x"%client.ARMident()
        #print "Debug State: %x"%client.ARMget_dbgstate ()
        for x in range(start,end):
            num = client.ARMset_register(x,seed+x)
            print "set_register(%d,0x%x):  %x"%(x,seed+x,num)
            client.ARMident()
            client.ARMident()
        for x in range(start,end):
            num = client.ARMget_register(x)
            print "get_register(%d):             %x"%(x,num)
            results[x].append(num)
            if (num != seed+x):
                for y in range(13):
                    num = client.ARMset_register(x,seed+x)
                    print "set_register(%d,0x%x):  %x"%(x,seed+x,num)
                    num = client.ARMget_register(x)
                    print "get_register(%d):             %x"%(x,num)
                    results[x].append(num)
            client.ARMident()
            client.ARMident()
            print "Debug State: %x"%client.ARMget_dbgstate ()
        seed += 1

def test7(start=0,end=14):
    global results,seed
    results = [[] for x in range(end)]
    while True:
        #print "IDCODE:      %x"%client.ARMident()
        #print "Debug State: %x"%client.ARMget_dbgstate ()
        for x in range(end,start-1, -1):
            num = client.ARMset_register(x,seed+x)
            time.sleep(1)
            print "set_register(%d,0x%x):  %x"%(x,seed+x,num)
        for y in range(10):
          for x in range(start,endi+1):
            num = client.ARMget_register(x)
            time.sleep(1)
            print "get_register(%d):             %x"%(x,num)
            results[x].append(num)
        seed += 1

def readtest(start=0,end=14):
    global results,seed
    results = [[] for x in range(end)]
    while True:
        #print "IDCODE:      %x"%client.ARMident()
        #print "Debug State: %x"%client.ARMget_dbgstate ()
        for x in range(end,start, -1):
            num = client.ARMget_register(x)
            time.sleep(1)
            print "get_register(%d):  %x"%(x,num)
        for y in range(10):
          for x in range(start,end,2):
            num = client.ARMget_register(x)
            time.sleep(1)
            print "get_register(%d):             %x"%(x,num)
            results[x].append(num)
        seed += 1

init()


def printResults():
    for y in range(len(results)):
            x=results[y]
            print "%.2x=%s"%(y,repr(["%x"%t for t in x]))

def ARMreadMem(self, adr, wrdcount):
    retval = [] 
    r0 = self.ARMget_register(5);        # store R0 and R1
    r1 = self.ARMget_register(9);
    #print >>sys.stderr,("CPSR:\t%x"%self.ARMget_regCPSR())
    for word in range(adr, adr+(wrdcount*4), 4):
        #sys.stdin.readline()
        self.ARMset_register(5, word);        # write address into R0
        self.ARMset_register(9, 0xdeadbeef)
        self.ARM_nop(0)
        self.ARM_nop(1)
        self.ARMdebuginstr(0xe4959004L, 0); # push LDR R1, [R0], #4 into instruction pipeline  (autoincrements for consecutive reads)
        self.ARM_nop(0)
        self.ARMrestart()
        self.ARMwaitDBG()
        time.sleep(.4)
        self.ARMdebuginstr(0x47146,0)
        self.ARMdebuginstr(0x47147,0)
        print hex(self.ARMget_register(9))
        # FIXME: this may end up changing te current debug-state.  should we compare to current_dbgstate?
        #print repr(self.data[4])
        if (len(self.data)>4 and self.data[4] == '\x00'):
          print >>sys.stderr,("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
          raise Exception("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE")
          #return -1
        else:
          retval.append( self.ARMget_register(9) )  # read memory value from R1 register
          #print >>sys.stderr,("CPSR: %x\t\tR0: %x\t\tR1: %x"%(self.ARMget_regCPSR(),self.ARMget_register(0),self.ARMget_register(1)))
    self.ARMset_register(9, r1);       # restore R0 and R1 
    self.ARMset_register(5, r0);
    return retval

"""
  case 0xD0: // loopback test
    cmddatalong[0] = 0x12345678;
  case 0xD1: // Set Scan Chain
    cmddatalong[0] = jtagarm7tdmi_scan_n(cmddataword[0]);
  case 0xD2: //
    cmddatalong[0] = jtagarm7tdmi_get_dbgstate();
  case 0xD3:
    cmddatalong[0] = jtagarm7tdmi_exec(cmddatalong[0]);
  case 0xD4:
    cmddatalong[0] = jtagarm7tdmi_get_register(cmddata[0]);
  case 0xD5:
    cmddatalong[0] = jtagarm7tdmi_set_register(cmddata[0], cmddatalong[1]);
  case 0xD6:
    cmddatalong[0] = jtagarm7tdmi_dr_shift32(cmddatalong[0]);
  case 0xD7:
    cmddatalong[0] = jtagarm7tdmi_chain1(cmddatalong[0], 0);
  case 0xD8:
    cmddatalong[0] = jtagarm7tdmi_chain2_read(cmddata[0], 32);
"""

"""
if(sys.argv[1]=="test"):
    client.CCtest();
if(sys.argv[1]=="deadtest"):
    for i in range(1,10):
        print "IDENT as %s" % client.CCidentstr();
if(sys.argv[1]=="dumpcode"):
    f = sys.argv[2];
    start=0x0000;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    print "Dumping code from %04x to %04x as %s." % (start,stop,f);
    h = IntelHex(None);
    i=start;
    while i<=stop:
        h[i]=client.CCpeekcodebyte(i);
        if(i%0x100==0):
            print "Dumped %04x."%i;
        i+=1;
    h.write_hex_file(f);
if(sys.argv[1]=="dumpdata"):
    f = sys.argv[2];
    start=0xE000;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    print "Dumping data from %04x to %04x as %s." % (start,stop,f);
    h = IntelHex(None);
    i=start;
    while i<=stop:
        h[i]=client.CCpeekdatabyte(i);
        if(i%0x100==0):
            print "Dumped %04x."%i;
        i+=1;
    h.write_hex_file(f);
if(sys.argv[1]=="status"):
    print "Status: %s" %client.CCstatusstr();
if(sys.argv[1]=="erase"):
    print "Status: %s" % client.CCstatusstr();
    client.CCchiperase();
    print "Status: %s" %client.CCstatusstr();

if(sys.argv[1]=="peekinfo"):
    print "Select info flash."
    client.CCwr_config(1);
    print "Config is %02x" % client.CCrd_config();
    
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekcodebyte(start));
        start=start+1;
if(sys.argv[1]=="poke"):
    client.CCpokeirambyte(int(sys.argv[2],16),
                          int(sys.argv[3],16));
if(sys.argv[1]=="randtest"):
    #Seed RNG
    client.CCpokeirambyte(0xBD,0x01); #RNDH=0x01
    client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
    client.CCpokeirambyte(0xBD,0x01); #RNDH=0x01
    client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
    
    #Dump values
    for foo in range(1,10):
        print "%02x" % client.CCpeekirambyte(0xBD); #RNDH
        client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
        client.CCreleasecpu();
        client.CChaltcpu();
    print "%02x" % client.CCpeekdatabyte(0xDF61); #CHIP ID
if(sys.argv[1]=="adctest"):
    # ADCTest 0xDF3A 0xDF3B
    print "ADC TEST %02x%02x" % (
        client.CCpeekdatabyte(0xDF3A),
        client.CCpeekdatabyte(0xDF3B));
if(sys.argv[1]=="config"):
    print "Config is %02x" % client.CCrd_config();

if(sys.argv[1]=="flash"):
     f=sys.argv[2];
     start=0;
     stop=0xFFFF;
     if(len(sys.argv)>3):
         start=int(sys.argv[3],16);
     if(len(sys.argv)>4):
         stop=int(sys.argv[4],16);
   
     h = IntelHex(f);
     page = 0x0000;
     pagelen = 2048; #2kB pages in 32-bit words
     bcount = 0;
     
     print "Wiping Flash."
     #Wipe all of flash.
     #client.CCchiperase();
     #Wipe the RAM buffer for the next flash page.
     #client.CCeraseflashbuffer();
     for i in h._buf.keys():
         while(i>page+pagelen):
             if bcount>0:
                 client.CCflashpage(page);
                 #client.CCeraseflashbuffer();
                 bcount=0;
                 print "Flashed page at %06x" % page
             page+=pagelen;
             
         #Place byte into buffer.
         client.CCpokedatabyte(0xF000+i-page,
                               h[i]);
         bcount+=1;
         if(i%0x100==0):
                print "Buffering %04x toward %06x" % (i,page);
     #last page
     client.CCflashpage(page);
     print "Flashed final page at %06x" % page;
     
if(sys.argv[1]=="lock"):
    print "Status: %s" %client.CCstatusstr();
    client.CClockchip();
    print "Status: %s" %client.CCstatusstr();
if(sys.argv[1]=="flashpage"):
    target=0;
    if(len(sys.argv)>2):
        target=int(sys.argv[2],16);
    print "Writing a page of flash from 0xF000 in XDATA"
    client.CCflashpage(target);
if(sys.argv[1]=="erasebuffer"):
    print "Erasing flash buffer.";
    client.CCeraseflashbuffer();

if(sys.argv[1]=="writedata"):
    f=sys.argv[2];
    start=0;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    h = IntelHex(f);
    
    for i in h._buf.keys():
        if(i>=start and i<=stop):
            client.CCpokedatabyte(i,h[i]);
            if(i%0x100==0):
                print "%04x" % i;
#if(sys.argv[1]=="flashtest"):
#    client.CCflashtest();
if(sys.argv[1]=="peekdata"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekdatabyte(start));
        start=start+1;
if(sys.argv[1]=="peek"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekirambyte(start));
        start=start+1;

if(sys.argv[1]=="peekcode"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekcodebyte(start));
        start=start+1;
if(sys.argv[1]=="pokedata"):
    start=0x0000;
    val=0x00;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    if(len(sys.argv)>3):
        val=int(sys.argv[3],16);
    print "Poking %04x to become %02x." % (start,val);
    client.CCpokedatabyte(start,val);

client.stop();
"""

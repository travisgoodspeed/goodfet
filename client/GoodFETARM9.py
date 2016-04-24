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
#import atlasutils.smartprint as asp
from GoodFET import GoodFET
from GoodFETARM7 import *
from intelhex import IntelHex


from intelhex import IntelHex16bit, IntelHex

def arm9_syntax():
    print "Usage: %s verb [objects]\n" % sys.argv[0]
    print "%s info" % sys.argv[0]
    print "%s dump $foo.hex [0x$start 0x$stop]" % sys.argv[0]
    print "%s erase" % sys.argv[0]
    print "%s eraseinfo" % sys.argv[0]
    print "%s flash $foo.hex [0x$start 0x$stop]" % sys.argv[0]
    print "%s verify $foo.hex [0x$start 0x$stop]" % sys.argv[0]
    print "%s poke 0x$adr 0x$val" % sys.argv[0]
    print "%s peek 0x$start [0x$stop]" % sys.argv[0]
    print "%s reset" % sys.argv[0]
    sys.exit()

def arm9_main():
    ''' this function should be called from command line app '''

    #Initialize FET and set baud rate
    client=GoodFETARM9()
    client.serInit()

    client.setup()
    client.start()

    arm9_cli_handler(client, sys.argv)


def arm9_cli_handler(client, argv):
    if(argv[1]=="info"):
        client.halt()
        print >>sys.stderr, client.ARMidentstr()
        print >>sys.stderr,"Debug Status:\t%s" % client.statusstr()
        print >>sys.stderr,"CPSR: (%s) %s\n"%(client.ARMget_regCPSRstr())
        client.resume()


    if(argv[1]=="dump"):
        f = sys.argv[2]
        start=0x00000000
        stop=0xFFFFFFFF
        if(len(sys.argv)>3):
            start=int(sys.argv[3],16)
        if(len(sys.argv)>4):
            stop=int(sys.argv[4],16)
        
        print "Dumping from %04x to %04x as %s." % (start,stop,f)
        #h = IntelHex16bit(None)
        # FIXME: get mcu state and return it to that state
        client.halt()

        try:
            h = IntelHex(None)
            i=start
            while i<=stop:
                #data=client.ARMreadMem(i, 48)
                data=client.ARMreadChunk(i, 48, verbose=0)
                print "Dumped %06x."%i
                for dword in data:
                    if i<=stop and dword != 0xdeadbeef:
                        h.puts( i, struct.pack("<I", dword) )
                    i+=4
            # FIXME: get mcu state and return it to that state
        except:
            print "Unknown error during read. Writing results to output file."
            print "Rename file with last address dumped %06x."%i
            pass

        client.resume()
        h.write_hex_file(f)

    '''
    if(sys.argv[1]=="erase"):
        print "Erasing main flash memory."
        client.ARMmasserase()

    if(sys.argv[1]=="eraseinfo"):
        print "Erasing info memory."
        client.ARMinfoerase()

        
    '''
    if(sys.argv[1]=="ivt"):
        client.halt()
        client.ARMprintChunk(0x0,0x20)
        client.resume()

    if(sys.argv[1]=="regs"):
        client.halt()
        for i in range(0,16):
            print "r%i=%04x" % (i,client.ARMget_register(i))
        client.resume()

    if(sys.argv[1]=="flash"):
        f=sys.argv[2]
        start=0
        stop=0x10000
        if(len(sys.argv)>3):
            start=int(sys.argv[3],16)
        if(len(sys.argv)>4):
            stop=int(sys.argv[4],16)
        
        client.halt()
        h = IntelHex16bit(f)
        
        #Should this be default?
        #Makes flashing multiple images inconvenient.
        #client.ARMmasserase()
        
        count=0; #Bytes in commit.
        first=0
        vals=[]
        last=0;  #Last address committed.
        for i in h._buf.keys():
            if((count>0x40 or last+2!=i) and count>0 and i&1==0):
                #print "%i, %x, %x" % (len(vals), last, i)
                client.ARMpokeflashblock(first,vals)
                count=0
                first=0
                last=0
                vals=[]
            if(i>=start and i<stop  and i&1==0):
                val=h[i>>1]
                if(count==0):
                    first=i
                last=i
                count+=2
                vals+=[val&0xff,(val&0xff00)>>8]
                if(i%0x100==0):
                    print "%04x" % i
        if count>0: #last commit, ivt
            client.ARMpokeflashblock(first,vals)
        client.resume()

    if(sys.argv[1]=="verify"):
        f=sys.argv[2]
        start=0
        stop=0xFFFF
        if(len(sys.argv)>3):
            start=int(sys.argv[3],16)
        if(len(sys.argv)>4):
            stop=int(sys.argv[4],16)
        
        client.halt()
        h = IntelHex16bit(f)
        for i in h._buf.keys():
            if(i>=start and i<stop and i&1==0):
                peek=client.peek(i)
                if(h[i>>1]!=peek):
                    print "ERROR at %04x, found %04x not %04x"%(i,peek,h[i>>1])
                if(i%0x100==0):
                    print "%04x" % i
        client.resume()


    if(sys.argv[1]=="peek"):
        start = 0x0000
        if(len(sys.argv)>2):
            start=int(sys.argv[2],16)

        stop = start+4
        if(len(sys.argv)>3):
            stop=int(sys.argv[3],16)

        print "Peeking from %04x to %04x." % (start,stop)
        client.halt()
        for dword in client.ARMreadChunk(start, (stop-start)/4, verbose=0):
            print "%.4x: %.8x" % (start, dword)
            start += 4
        client.resume()

    if(sys.argv[1]=="poke"):
        start=0x0000
        val=0x00
        if(len(sys.argv)>2):
            start=int(sys.argv[2],16)
        if(len(sys.argv)>3):
            val=int(sys.argv[3],16)
        
        print "Poking %06x to become %04x." % (start,val)
        client.halt()
        #???while client.ARMreadMem(start)[0]&(~val)>0:
        client.ARMwriteChunk(start, [val])
        print "Poked to %.8x" % client.ARMreadMem(start)[0]
        client.resume()


    if(sys.argv[1]=="reset"):
        #Set PC to RESET vector's value.
        
        #client.ARMsetPC(0x00000000)
        #client.ARMset_regCPSR(0)
        #client.ARMreleasecpu()
        client.ARMresettarget(1000)

    #client.ARMreleasecpu()
    #client.ARMstop()



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

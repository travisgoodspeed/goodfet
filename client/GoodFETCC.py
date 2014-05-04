#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys;
import binascii;

from GoodFET import GoodFET;
from intelhex import IntelHex;

import xml.dom.minidom, time, os;

class GoodFETCC(GoodFET):
    """A GoodFET variant for use with Chipcon 8051 Zigbee SoC."""
    APP=0x30;
    
    smartrfpath=None;
    def __init__(self,filename=None):
        """GoodFETCC constructor.
        Mostly concerned with finding SmartRF7."""
        if self.smartrfpath==None:
            self.smartrfpath=os.environ.get("SMARTRF");
        if self.smartrfpath==None and os.name=='nt':
            pf=os.environ['PROGRAMFILES'];
            self.smartrfpath="%s\\\\Texas Instruments\\\\SmartRF Tools\\\\SmartRF Studio 7" % pf;
            
        if self.smartrfpath==None:
            self.smartrfpath="/opt/smartrf7";
        
    haveloadedsymbols=False;
    def loadsymbols(self):
        if self.haveloadedsymbols:
            return;
        try:
            self.SRF_loadsymbols();
            self.haveloadedsymbols=True;
        except:
            ident=self.CCident();
            if ident==0x0000 or ident==0xFFFF:
                print "Chip ID is 0x%04x, implying a wiring problem." % ident;
            else:
                print "SmartRF not found for chip 0x%04x." % ident;
    def SRF_chipdom(self,chip="cc1110", doc="register_definition.xml"):
    #def SRF_chipdom(self,chip="cc1110", doc="workingconfig.xml"):
        """Loads the chip XML definitions from SmartRF7."""
        fn="%s/config/xml/%s/%s" % (self.smartrfpath,chip,doc);
        #print "Opening %s" % fn;
        return xml.dom.minidom.parse(fn)
        
    def CMDrs(self,args=[]):
        """Chip command to grab the radio state."""
        #try:
        self.SRF_radiostate();
        #except:
        #    print "Error printing radio state.";
        #    print "SmartRF not found at %s." % self.smartrfpath;
    def SRF_bitfieldstr(self,bf):
        name="unused";
        start=0;
        stop=0;
        access="";
        reset="0x00";
        description="";
        for e in bf.childNodes:
            if e.localName=="Name" and e.childNodes: name= e.childNodes[0].nodeValue;
            elif e.localName=="Start": start=e.childNodes[0].nodeValue;
            elif e.localName=="Stop": stop=e.childNodes[0].nodeValue;
        return "   [%s:%s] %30s " % (start,stop,name);

    def SRF_radiostate(self):
        ident=self.CCident();
        chip=self.CCversions.get(ident&0xFF00);
        dom=self.SRF_chipdom(chip,"register_definition.xml");
        for e in dom.getElementsByTagName("registerdefinition"):
            for f in e.childNodes:
                if f.localName=="DeviceName":
                    print "// %s RadioState" % (f.childNodes[0].nodeValue);
                elif f.localName=="Register":
                    name="unknownreg";
                    address="0xdead";
                    description="";
                    bitfields="";
                    for g in f.childNodes:
                        if g.localName=="Name":
                            name=g.childNodes[0].nodeValue;
                        elif g.localName=="Address":
                            address=g.childNodes[0].nodeValue;
                        elif g.localName=="Description":
                            if g.childNodes:
                                description=g.childNodes[0].nodeValue;
                        elif g.localName=="Bitfield":
                            bitfields+="%17s/* %-50s */\n" % ("",self.SRF_bitfieldstr(g));
                    #print "SFRX(%10s, %s); /* %50s */" % (name,address, description);
                    print "%-10s=0x%02x; /* %-50s */" % (
                        name,self.CCpeekdatabyte(eval(address)), description);
                    if bitfields!="": print bitfields.rstrip();

    def SRF_radiostate_select(self,args=[]):
        lreg = []
        ident=self.CCident();
        chip=self.CCversions.get(ident&0xFF00);
        dom=self.SRF_chipdom(chip,"register_definition.xml");
        for reg in args:
            if reg.lower() == "help":
                lreg = "help"
                break
            lreg.append(reg.lower())
        for e in dom.getElementsByTagName("registerdefinition"):
            for f in e.childNodes:
                if f.localName=="DeviceName":
                    print "// %s RadioState" % (f.childNodes[0].nodeValue);
                elif f.localName=="Register":
                    name="unknownreg";
                    address="0xdead";
                    description="";
                    bitfields="";
                    for g in f.childNodes:
                        if g.localName=="Name":
                            name=g.childNodes[0].nodeValue;
                        elif g.localName=="Address":
                            address=g.childNodes[0].nodeValue;
                        elif g.localName=="Description":
                            if g.childNodes:
                                description=g.childNodes[0].nodeValue;
                        elif g.localName=="Bitfield":
                            bitfields+="%17s/* %-50s */\n" % ("",self.SRF_bitfieldstr(g));
                    #print "SFRX(%10s, %s); /* %50s */" % (name,address, description);
                    if lreg == "help":
                        print "%-10s /* %-50s */" % (name, description);
                    elif name.lower() in lreg:
                        print "%-10s=0x%02x; /* %-50s */" % (
                            name,self.CCpeekdatabyte(eval(address)), description);
                        if bitfields!="": print bitfields.rstrip();

    def RF_setfreq(self,frequency):
        """Set the frequency in Hz."""
        #FIXME CC1110 specific
        #Some frequencies fail, probably and FSCAL thing.
        
        hz=frequency;
        freq=int(hz/396.728515625);
        
        freq0=freq&0xFF;
        freq1=(freq&0xFF00)>>8;
        freq2=(freq&0xFF0000)>>16;
        
        self.pokebysym("FREQ2",freq2);
        self.pokebysym("FREQ1",freq1);
        self.pokebysym("FREQ0",freq0);
        
        self.pokebysym("TEST1",0x31);
        self.pokebysym("TEST0",0x09);
        
        
        #self.pokebysym("FSCAL2" ,   0x2A);  #above mid
        self.pokebysym("FSCAL2" ,   0x0A);  #beneath mid
        
        #self.CC_RFST_CAL(); #SCAL
        #time.sleep(1);
    
        
    def RF_getfreq(self):
        """Get the frequency in Hz."""
        #FIXME CC1110 specific
        
        #return (2400+self.peek(0x05))*10**6
        #self.poke(0x05,chan);
        
        #freq2=self.CCpeekdatabyte(0xdf09);
        #freq1=self.CCpeekdatabyte(0xdf0a);
        #freq0=self.CCpeekdatabyte(0xdf0b);
        freq=0;
        try:
            freq2=self.peekbysym("FREQ2");
            freq1=self.peekbysym("FREQ1");
            freq0=self.peekbysym("FREQ0");
            freq=(freq2<<16)+(freq1<<8)+freq0;
        except:
            freq=0;
            
        hz=freq*396.728515625;
        
        return hz;
    
    def RF_getchannel(self):
        """Get the hex channel."""
        #FIXME CC1110 specific
        freq=0;
        try:
            freq2=self.peekbysym("FREQ2");
            freq1=self.peekbysym("FREQ1");
            freq0=self.peekbysym("FREQ0");
            freq=(freq2<<16)+(freq1<<8)+freq0;
        except:
            freq=0;
            
        return freq;
    
    
    lastshellcode="none";
    def shellcodefile(self,filename,wait=1, alwaysreload=0):
        """Run a fragment of shellcode by name."""
        #FIXME: should identify chip model number, use shellcode for that chip.
        
        if self.lastshellcode!=filename or alwaysreload>0:
            self.lastshellcode=filename;
            file=__file__;
            file=file.replace("GoodFETCC.pyc","GoodFETCC.py");
            #TODO make this generic
            path=file.replace("GoodFETCC.py","shellcode/chipcon/cc1110/");
            filename=path+filename;
        
            #Load the shellcode.
            h=IntelHex(filename);
            for i in h._buf.keys():
                self.CCpokedatabyte(i,h[i]);
        #Execute it.
        self.CCdebuginstr([0x02, 0xf0, 0x00]); #ljmp 0xF000
        self.resume();
        while wait>0 and (0==self.CCstatus()&0x20):
            a=1;
            #print "Waiting for shell code to return.";
        return;
    def ishalted(self):
        return self.CCstatus()&0x20;
    def shellcode(self,code,wait=1):
        """Copy a block of code into RAM and execute it."""
        i=0;
        ram=0xF000;
        for byte in code:
            self.pokebyte(0xF000+i,byte);
            i=i+1;
        #print "Code loaded, executing."
        self.CCdebuginstr([0x02, 0xf0, 0x00]); #ljmp 0xF000
        self.resume();
        while wait>0 and (0==self.CCstatus()&0x20):
            a=1;
            #time.sleep(0.1);
            #print "Waiting for shell code to return.";
        return;
    def CC1110_crystal(self):
        """Start the main crystal of the CC1110 oscillating, needed for radio use."""
        code=[0x53, 0xBE, 0xFB, #anl SLEEP, #0xFB
              #one:
              0xE5, 0xBE,       #mov a,SLEEP
              0x30, 0xE6, 0xFB, #jnb acc.6, back
              0x53, 0xc6, 0xB8, #anl CLKCON, #0xB8
              #two
              0xE5, 0xC6,       #mov a,CLKCON
              0x20, 0xE6, 0xFB, #jb acc.6, two
              0x43, 0xBE, 0x04, #orl SLEEP, #0x04
              0xA5,             #HALT
              ];
        self.shellcode(code);
        
        #Slower to load, but produced from C.
        #self.shellcodefile("crystal.ihx");
        return;
    def RF_idle(self):
        """Move the radio to its idle state."""
        self.CC_RFST_IDLE();
        return;
    
    #Chipcon RF strobes.  CC1110 specific
    RFST_IDLE=0x04;
    RFST_RX=0x02;
    RFST_TX=0x03;
    RFST_CAL=0x01;
    def CC_RFST_IDLE(self):
        """Switch the radio to idle mode, clearing overflows and errors."""
        self.CC_RFST(self.RFST_IDLE);
    def CC_RFST_TX(self):
        """Switch the radio to TX mode."""
        self.CC_RFST(self.RFST_TX);
    def CC_RFST_RX(self):
        """Switch the radio to RX mode."""
        self.CC_RFST(self.RFST_RX);
    def CC_RFST_CAL(self):
        """Calibrate strobe the radio."""
        self.CC_RFST(self.RFST_CAL);
    def CC_RFST(self,state=RFST_IDLE):
        RFST=0xDFE1
        self.pokebyte(RFST,state); #Return to idle state.
        return;
    def config_dash7(self,band="lf"):
        #These settings came from the OpenTag project's GIT repo on 18 Dec, 2010.
        #Waiting for official confirmation of the accuracy.

        self.pokebysym("FSCTRL1"  , 0x08)   # Frequency synthesizer control.
        self.pokebysym("FSCTRL0"  , 0x00)   # Frequency synthesizer control.
        
        #Don't change these while the radio is active.
        self.pokebysym("FSCAL3"   , 0xEA)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL2"   , 0x2A)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL1"   , 0x00)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL0"   , 0x1F)   # Frequency synthesizer calibration.
        
        if band=="ismeu" or band=="eu":
            print "There is no official eu band for dash7."
            self.pokebysym("FREQ2"    , 0x21)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0x71)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x7a)   # Frequency control word, low byte.
        elif band=="ismus" or band=="us":
            print "There is no official us band for dash7."
            self.pokebysym("FREQ2"    , 0x22)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xB1)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x3B)   # Frequency control word, low byte.
        elif band=="ismlf" or band=="lf":
            # 433.9198 MHz, same as Simpliciti.
            self.pokebysym("FREQ2"    , 0x10)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xB0)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x71)   # Frequency control word, low byte.
        elif band=="none":
            pass;
        else:
            #Got a frequency, not a band.
            self.RF_setfreq(eval(band));
        self.pokebysym("MDMCFG4"  , 0x8B)   # 62.5 kbps w/ 200 kHz filter
        self.pokebysym("MDMCFG3"  , 0x3B)
        self.pokebysym("MDMCFG2"  , 0x11)
        self.pokebysym("MDMCFG1"  , 0x02)
        self.pokebysym("MDMCFG0"  , 0x53)
        self.pokebysym("CHANNR"   , 0x00)   # Channel zero.
        self.pokebysym("DEVIATN"  , 0x50)   # 50 kHz deviation
        
        self.pokebysym("FREND1"   , 0xB6)   # Front end RX configuration.
        self.pokebysym("FREND0"   , 0x10)   # Front end RX configuration.
        self.pokebysym("MCSM2"    , 0x1E)
        self.pokebysym("MCSM1"    , 0x3F)
        self.pokebysym("MCSM0"    , 0x30)
        self.pokebysym("FOCCFG"   , 0x1D)   # Frequency Offset Compensation Configuration.
        self.pokebysym("BSCFG"    , 0x1E)   # 6.25% data error rate
        
        self.pokebysym("AGCCTRL2" , 0xC7)   # AGC control.
        self.pokebysym("AGCCTRL1" , 0x00)   # AGC control.
        self.pokebysym("AGCCTRL0" , 0xB2)   # AGC control.
        
        self.pokebysym("TEST2"    , 0x81)   # Various test settings.
        self.pokebysym("TEST1"    , 0x35)   # Various test settings.
        self.pokebysym("TEST0"    , 0x09)   # Various test settings.
        self.pokebysym("PA_TABLE0", 0xc0)   # Max output power.
        self.pokebysym("PKTCTRL1" , 0x04)   # Packet automation control, w/ lqi
        #self.pokebysym("PKTCTRL1" , 0x00)   # Packet automation control. w/o lqi
        self.pokebysym("PKTCTRL0" , 0x05)   # Packet automation control, w/ checksum.
        #self.pokebysym("PKTCTRL0" , 0x00)   # Packet automation control, w/o checksum, fixed length
        self.pokebysym("ADDR"     , 0x01)   # Device address.
        self.pokebysym("PKTLEN"   , 0xFF)   # Packet length.
        
        #Sync word hack
        self.pokebysym("SYNC1",0x83);
        self.pokebysym("SYNC0",0xFE);
        return;
    def config_iclicker(self,band="lf"):
        #Mike Ossmann figured most of this out, with help from neighbors.
        
        self.pokebysym("FSCTRL1"  , 0x06)   # Frequency synthesizer control.
        self.pokebysym("FSCTRL0"  , 0x00)   # Frequency synthesizer control.
        
        #Don't change these while the radio is active.
        self.pokebysym("FSCAL3"   , 0xE9)
        self.pokebysym("FSCAL2"   , 0x2A)
        self.pokebysym("FSCAL1"   , 0x00)
        self.pokebysym("FSCAL0"   , 0x1F)
        
        if band=="ismeu" or band=="eu":
            print "The EU band is unknown.";
        elif band=="ismus" or band=="us":
            #905.5MHz
            self.pokebysym("FREQ2"    , 0x22)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xD3)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0xAC)   # Frequency control word, low byte.
        elif band=="ismlf" or band=="lf":
            print "There is no LF version of the iclicker."
        elif band=="none":
            pass;
        else:
            #Got a frequency, not a band.
            self.RF_setfreq(eval(band));
        # 812.5kHz bandwidth, 152.34 kbaud
        self.pokebysym("MDMCFG4"  , 0x1C)   
        self.pokebysym("MDMCFG3"  , 0x80)
        # no FEC, 2 byte preamble, 250kHz chan spacing
        
        #15/16 sync
        #self.pokebysym("MDMCFG2"  , 0x01)
        #16/16 sync
        self.pokebysym("MDMCFG2"  , 0x02)
        
        self.pokebysym("MDMCFG1"  , 0x03)
        self.pokebysym("MDMCFG0"  , 0x3b)
        
        self.pokebysym("CHANNR"   , 0x2e)   # Channel zero.
        
        #self.pokebysym("DEVIATN"  , 0x71)  # 118.5
        self.pokebysym("DEVIATN"  , 0x72)   # 253.9 kHz deviation
        
        self.pokebysym("FREND1"   , 0x56)   # Front end RX configuration.
        self.pokebysym("FREND0"   , 0x10)   # Front end RX configuration.
        self.pokebysym("MCSM2"    , 0x07)
        self.pokebysym("MCSM1"    , 0x30)   #Auto freq. cal.
        self.pokebysym("MCSM0"    , 0x14)
        
        self.pokebysym("TEST2"    , 0x88)   # 
        self.pokebysym("TEST1"    , 0x31)   # 
        self.pokebysym("TEST0"    , 0x09)   # High VCO (Upper band.)
        self.pokebysym("PA_TABLE0", 0xC0)   # Max output power.
        self.pokebysym("PKTCTRL1" , 0x45)   # Preamble qualidy 2*4=6, adr check, status
        self.pokebysym("PKTCTRL0" , 0x00)   # No whitening, CR, fixed len.
        
        self.pokebysym("PKTLEN"   , 0x09)   # Packet length.
        
        self.pokebysym("SYNC1",0xB0);
        self.pokebysym("SYNC0",0xB0);
        self.pokebysym("ADDR", 0xB0);
        return;

    def config_ademco(self, band="lf"):
        pass
        # FIXME Temporary placeholder for me to write the Ademco protocol into the GoodFET Chipcon Application
        # TODO  Also, write a class that takes in the XML registration files and sets values (not just addresses)

	def config_ook(self,band="none"):
		self.pokebysym("FSCTRL1"  , 0x0C) #08   # Frequency synthesizer control.
		self.pokebysym("FSCTRL0"  , 0x00)   # Frequency synthesizer control.
        
        #Don't change these while the radio is active.
        self.pokebysym("FSCAL3"   , 0xEA)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL2"   , 0x2A)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL1"   , 0x00)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL0"   , 0x1F)   # Frequency synthesizer calibration.
        
        if band=="ismeu" or band=="eu":
            self.pokebysym("FREQ2"    , 0x21)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0x71)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x7a)   # Frequency control word, low byte.
        elif band=="ismus" or band=="us":
            self.pokebysym("FREQ2"    , 0x22)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xB1)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x3B)   # Frequency control word, low byte.
        elif band=="ismlf" or band=="lf":
            self.pokebysym("FREQ2"    , 0x0C)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0x1D)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x89)   # Frequency control word, low byte.
        elif band=="none":
            pass;
        else:
            #Got a frequency, not a band.
            self.RF_setfreq(eval(band));
        
        #data rate
        #~1
        #self.pokebysym("MDMCFG4"  , 0x85)
        #self.pokebysym("MDMCFG3"  , 0x83)
        #0.5
        #self.pokebysym("MDMCFG4"  , 0xf4)
        #self.pokebysym("MDMCFG3"  , 0x43)
        #2.4
        #self.pokebysym("MDMCFG4"  , 0xf6)
        #self.pokebysym("MDMCFG3"  , 0x83)
        
        #4.8 kbaud
        #print "Warning: Default to 4.8kbaud.";
        #self.pokebysym("MDMCFG4"  , 0xf7)
        #self.pokebysym("MDMCFG3"  , 0x83)
        #9.6 kbaud
        #print "Warning: Default to 9.6kbaud.";
        #
        
        self.pokebysym("MDMCFG4"  , 0xf8)
        self.pokebysym("MDMCFG3"  , 0x83)
        self.pokebysym("MDMCFG2"  , 0x34)   # OOK, carrier-sense, no-manchester
        
        #Kind aright for keeloq
        print "Warning: Guessing baud rate.";
        #self.pokebysym("MDMCFG4"  , 0xf6)
        #self.pokebysym("MDMCFG3"  , 0x93)
        #self.pokebysym("MDMCFG2"  , 0x3C)   # OOK, carrier-sense, manchester
        
        self.pokebysym("MDMCFG1"  , 0x00)   # Modem configuration.
        self.pokebysym("MDMCFG0"  , 0xF8)   # Modem configuration.
        self.pokebysym("CHANNR"   , 0x00)   # Channel number.
        
        self.pokebysym("FREND1"   , 0x56)   # Front end RX configuration.
        self.pokebysym("FREND0"   , 0x11)   # Front end RX configuration.
        self.pokebysym("MCSM0"    , 0x18)   # Main Radio Control State Machine configuration.
        #self.pokebysym("FOCCFG"   , 0x1D)   # Frequency Offset Compensation Configuration.
        #self.pokebysym("BSCFG"    , 0x1C)   # Bit synchronization Configuration.
        
        #self.pokebysym("AGCCTRL2" , 0xC7)   # AGC control.
        #self.pokebysym("AGCCTRL1" , 0x00)   # AGC control.
        #self.pokebysym("AGCCTRL0" , 0xB2)   # AGC control.
        
        self.pokebysym("TEST2"    , 0x81)   # Various test settings.
        self.pokebysym("TEST1"    , 0x35)   # Various test settings.
        self.pokebysym("TEST0"    , 0x0B)   # Various test settings.
        self.pokebysym("PA_TABLE0", 0xc2)   # Max output power.
        self.pokebysym("PKTCTRL1" , 0x04)   # Packet automation control, w/ lqi
        #self.pokebysym("PKTCTRL1" , 0x00)   # Packet automation control. w/o lqi
        #self.pokebysym("PKTCTRL0" , 0x05)   # Packet automation control, w/ checksum.
        self.pokebysym("PKTCTRL0" , 0x00)   # Packet automation control, w/o checksum, fixed length
        self.pokebysym("ADDR"     , 0x01)   # Device address.
        self.pokebysym("PKTLEN"   , 0xFF)   # Packet length.
        
        self.pokebysym("SYNC1",0xD3);
        self.pokebysym("SYNC0",0x91);
        
    def config_simpliciti(self,band="none"):
        self.pokebysym("FSCTRL1"  , 0x0C) #08   # Frequency synthesizer control.
        self.pokebysym("FSCTRL0"  , 0x00)   # Frequency synthesizer control.
        
        #Don't change these while the radio is active.
        self.pokebysym("FSCAL3"   , 0xEA)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL2"   , 0x2A)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL1"   , 0x00)   # Frequency synthesizer calibration.
        self.pokebysym("FSCAL0"   , 0x1F)   # Frequency synthesizer calibration.
        
        if band=="ismeu" or band=="eu":
            self.pokebysym("FREQ2"    , 0x21)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0x71)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x7a)   # Frequency control word, low byte.
        elif band=="ismus" or band=="us":
            self.pokebysym("FREQ2"    , 0x22)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xB1)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x3B)   # Frequency control word, low byte.
        elif band=="ismlf" or band=="lf":
            self.pokebysym("FREQ2"    , 0x10)   # Frequency control word, high byte.
            self.pokebysym("FREQ1"    , 0xB0)   # Frequency control word, middle byte.
            self.pokebysym("FREQ0"    , 0x71)   # Frequency control word, low byte.
        elif band=="none":
            band="none";
        else:
            #Got a frequency, not a band.
            self.RF_setfreq(eval(band));
        self.pokebysym("MDMCFG4"  , 0x7B)   # Modem configuration.
        self.pokebysym("MDMCFG3"  , 0x83)   # Modem configuration.
        self.pokebysym("MDMCFG2"  , 0x13)   # Modem configuration.
        self.pokebysym("MDMCFG1"  , 0x22)   # Modem configuration.
        self.pokebysym("MDMCFG0"  , 0xF8)   # Modem configuration.
        if band=="ismus" or band=="us":
            self.pokebysym("CHANNR"   , 20)   # Channel number.
        else:
            self.pokebysym("CHANNR"   , 0x00)   # Channel number.
        self.pokebysym("DEVIATN"  , 0x42)   # Modem deviation setting (when FSK modulation is enabled).
        
        self.pokebysym("FREND1"   , 0xB6)   # Front end RX configuration.
        self.pokebysym("FREND0"   , 0x10)   # Front end RX configuration.
        self.pokebysym("MCSM0"    , 0x18)   # Main Radio Control State Machine configuration.
        self.pokebysym("FOCCFG"   , 0x1D)   # Frequency Offset Compensation Configuration.
        self.pokebysym("BSCFG"    , 0x1C)   # Bit synchronization Configuration.
        
        self.pokebysym("AGCCTRL2" , 0xC7)   # AGC control.
        self.pokebysym("AGCCTRL1" , 0x00)   # AGC control.
        self.pokebysym("AGCCTRL0" , 0xB2)   # AGC control.
        
        self.pokebysym("TEST2"    , 0x81)   # Various test settings.
        self.pokebysym("TEST1"    , 0x35)   # Various test settings.
        self.pokebysym("TEST0"    , 0x09)   # Various test settings.
        self.pokebysym("PA_TABLE0", 0xc0)   # Max output power.
        self.pokebysym("PKTCTRL1" , 0x04)   # Packet automation control, w/ lqi
        #self.pokebysym("PKTCTRL1" , 0x00)   # Packet automation control. w/o lqi
        self.pokebysym("PKTCTRL0" , 0x05)   # Packet automation control, w/ checksum.
        #self.pokebysym("PKTCTRL0" , 0x00)   # Packet automation control, w/o checksum, fixed length
        self.pokebysym("ADDR"     , 0x01)   # Device address.
        self.pokebysym("PKTLEN"   , 0xFF)   # Packet length.
        
        self.pokebysym("SYNC1",0xD3);
        self.pokebysym("SYNC0",0x91);
        
    def RF_carrier(self):
        """Hold a carrier wave on the present frequency."""
        
        self.CC1110_crystal(); #FIXME, '1110 specific.
        self.RF_idle();
        
        
        RFST=0xDFE1;
        
        self.config_simpliciti();
        
        #Don't change these while the radio is active.
        #self.pokebysym("FSCAL3"   , 0xA9)   # Frequency synthesizer calibration.
        #self.pokebysym("FSCAL2"   , 0x0A)   # Frequency synthesizer calibration.
        #self.pokebysym("FSCAL1"   , 0x00)   # Frequency synthesizer calibration.
        #self.pokebysym("FSCAL0"   , 0x11)   # Frequency synthesizer calibration.
        
        #Ramp up the power.
        #self.pokebysym("PA_TABLE0", 0xFF)   # PA output power setting.
        
        #This is what drops to OOK.
        #Comment to keep GFSK, might be better at jamming.
        self.pokebysym("MDMCFG4"  , 0x86)   # Modem configuration.
        self.pokebysym("MDMCFG3"  , 0x83)   # Modem configuration.
        self.pokebysym("MDMCFG2"  , 0x30)   # Modem configuration.
        self.pokebysym("MDMCFG1"  , 0x22)   # Modem configuration.
        self.pokebysym("MDMCFG0"  , 0xF8)   # Modem configuration.
        
        self.pokebysym("SYNC1",0xAA);
        self.pokebysym("SYNC0",0xAA);
        
        #while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_TX); 
        state=0;
        
        while((state!=0x13)):
            self.pokebyte(RFST,0x03); #RFST=RFST_STX
            time.sleep(0.1);
            state=self.peekbysym("MARCSTATE")&0x1F;
            #print "state=%02x" % state;
        print "Holding a carrier on %f MHz." % (self.RF_getfreq()/10**6);
        
        return;
            
    def RF_getsmac(self):
        """Return the source MAC address."""
        
        #Register 0A is RX_ADDR_P0, five bytes.
        mac=self.peekbysym("ADDR");
        return mac;
    def RF_setsmac(self,mac):
        """Set the source MAC address."""
        self.pokebysym("ADDR",mac);
        return 0;
    def RF_gettmac(self):
        """Return the target MAC address."""
        return 0;
    def RF_settmac(self,mac):
        """Set the target MAC address."""
        return 0;
    def RF_rxpacket(self):
        """Get a packet from the radio.  Returns None if none is waiting."""
        self.shellcodefile("rxpacket.ihx");
        len=self.peek8(0xFE00,"xdata");
        return self.peekblock(0xFE00,len+3,"data");
    def RF_txpacket(self,packet):
        """Transmit a packet.  Untested."""
        
        self.pokeblock(0xFE00,packet,"data");
        self.shellcodefile("txpacket.ihx");
        return;
    def RF_txrxpacket(self,packet):
        """Transmit a packet.  Untested."""
        
        self.pokeblock(0xFE00,packet,"data");
        self.shellcodefile("txrxpacket.ihx");
        len=self.peek8(0xFE00,"xdata");
        return self.peekblock(0xFE00,len+3,"data");

    def RF_getrssi(self):
        """Returns the received signal strenght, with a weird offset."""
        try:
            rssireg=self.symbols.get("RSSI");
            return self.CCpeekdatabyte(rssireg)^0x80;
        except:
            if self.verbose>0: print "RSSI reg doesn't exist.";
        try:
            #RSSI doesn't exist on some 2.4GHz devices.  Maybe RSSIL and RSSIH?
            rssilreg=self.symbols.get("RSSIL");
            rssil=self.CCpeekdatabyte(rssilreg);
            rssihreg=self.symbols.get("RSSIL");
            rssih=self.CCpeekdatabyte(rssihreg);
            return (rssih<<8)|rssil;
        except:
            if self.verbose>0: print "RSSIL/RSSIH regs don't exist.";
        
        return 0;
    
    def SRF_loadsymbols(self):
        ident=self.CCident();
        chip=self.CCversions.get(ident&0xFF00);
        dom=self.SRF_chipdom(chip,"register_definition.xml");
        for e in dom.getElementsByTagName("registerdefinition"):
            for f in e.childNodes:
                if f.localName=="Register":
                    name="unknownreg";
                    address="0xdead";
                    description="";
                    bitfields="";
                    for g in f.childNodes:
                        if g.localName=="Name":
                            name=g.childNodes[0].nodeValue;
                        elif g.localName=="Address":
                            address=g.childNodes[0].nodeValue;
                        elif g.localName=="Description":
                            if g.childNodes:
                                description=g.childNodes[0].nodeValue;
                        elif g.localName=="Bitfield":
                            bitfields+="%17s/* %-50s */\n" % ("",self.SRF_bitfieldstr(g));
                    #print "SFRX(%10s, %s); /* %50s */" % (name,address, description);
                    self.symbols.define(eval(address),name,description,"data");
    def halt(self):
        """Halt the CPU."""
        self.CChaltcpu();
    def CChaltcpu(self):
        """Halt the CPU."""
        self.writecmd(self.APP,0x86,0,self.data);
    def resume(self):
        self.CCreleasecpu();
    def CCreleasecpu(self):
        """Resume the CPU."""
        self.writecmd(self.APP,0x87,0,self.data);
    def test(self):
        self.CCreleasecpu();
        self.CChaltcpu();
        #print "Status: %s" % self.CCstatusstr();
        
        #Grab ident three times, should be equal.
        ident1=self.CCident();
        ident2=self.CCident();
        ident3=self.CCident();
        if(ident1!=ident2 or ident2!=ident3):
            print "Error, repeated ident attempts unequal."
            print "%04x, %04x, %04x" % (ident1, ident2, ident3);

        #Single step, printing PC.
        print "Tracing execution at startup."
        for i in range(1,15):
            pc=self.CCgetPC();
            byte=self.CCpeekcodebyte(i);
            #print "PC=%04x, %02x" % (pc, byte);
            self.CCstep_instr();
        
        print "Verifying that debugging a NOP doesn't affect the PC."
        for i in range(1,15):
            pc=self.CCgetPC();
            self.CCdebuginstr([0x00]);
            if(pc!=self.CCgetPC()):
                print "ERROR: PC changed during CCdebuginstr([NOP])!";
        
        print "Checking pokes to XRAM."
        for i in range(self.execbuf,self.execbuf+0x20):
            self.CCpokedatabyte(i,0xde);
            if(self.CCpeekdatabyte(i)!=0xde):
                print "Error in XDATA at 0x%04x" % i;
        
        #print "Status: %s." % self.CCstatusstr();
        #Exit debugger
        self.stop();
        print "Done.";

    def setup(self):
        """Move the FET into the Chipcon 8051 application."""
        #print "Initializing Chipcon.";
        self.writecmd(self.APP,0x10,0,self.data);
    def CCrd_config(self):
        """Read the config register of a Chipcon."""
        self.writecmd(self.APP,0x82,0,self.data);
        return ord(self.data[0]);
    def CCwr_config(self,config):
        """Write the config register of a Chipcon."""
        self.writecmd(self.APP,0x81,1,[config&0xFF]);
    def CClockchip(self):
        """Set the flash lock bit in info mem."""
        self.writecmd(self.APP, 0x9A, 0, None);
    def lock(self):
        """Set the flash lock bit in info mem."""
        self.CClockchip();
    

    CCversions={0x0100:"cc1110",
                0x1100:"cc1111",
                0x8500:"cc2430",
                0x8900:"cc2431",
                0x8100:"cc2510",
                0x9100:"cc2511",
                0xA500:"cc2530", #page 57 of SWRU191B
                0xB500:"cc2531",
                0x9500:"cc2533",
                0x8D00:"cc2540",
                0xFF00:"CCmissing"};
    execbuf=None;
    CCexecbuf= {0x0100:0xF000,
                0x1100:0xF000,
                0x8500:0xF000,
                0x8900:0xF000,
                0x8100:0xF000,
                0x9100:0xF000,
                0xA500:0x0000, #CC2530
                0xB500:0x8000,
                0x9500:0x8000,
                0x8D00:0x8000,
                0xFF00:None} #missing
    CCpagesizes={0x01: 1024, #"CC1110",
                 0x11: 1024, #"CC1111",
                 0x85: 2048, #"CC2430",
                 0x89: 2048, #"CC2431",
                 0x81: 1024, #"CC2510",
                 0x91: 1024, #"CC2511",
                 0xA5: 2048, #"CC2530", #page 57 of SWRU191B
                 0xB5: 2048, #"CC2531",
                 0x95: 2048, #"CC2533",
                 0x8D: 2048, #"CC2540",
                 0xFF: None}
    def infostring(self):
        return self.CCidentstr();
    def CCidentstr(self):
        ident=self.CCident();
        chip=self.CCversions.get(ident&0xFF00);
        execbuf=self.CCexecbuf.get(ident&0xFF00);
        pagesize=self.CCpagesizes.get(ident>0xFF);
        self.execbuf=execbuf;
        
        try:
            return "%s/r%0.4x/ps0x%0.4x" % (chip, ident, pagesize); 
        except:
            return "%04x" % ident;
    def CCident(self):
        """Get a chipcon's ID."""
        self.writecmd(self.APP,0x8B,0,None);
        chip=ord(self.data[0]);
        rev=ord(self.data[1]);
        return (chip<<8)+rev;
    def CCpagesize(self):
        """Get a chipcon's ID."""
        self.writecmd(self.APP,0x8B,0,None);
        chip=ord(self.data[0]);
        size=self.CCpagesizes.get(chip);
        if(size<10):
            print "ERROR: Pagesize undefined.";
            print "chip=%0.4x" %chip;
            sys.exit(1);
            #return 2048;
        return size;
    def getpc(self):
        return self.CCgetPC();
    def CCgetPC(self):
        """Get a chipcon's PC."""
        self.writecmd(self.APP,0x83,0,None);
        hi=ord(self.data[0]);
        lo=ord(self.data[1]);
        return (hi<<8)+lo;
    def CCcmd(self,phrase):
        self.writecmd(self.APP,0x00,len(phrase),phrase);
        val=ord(self.data[0]);
        print "Got %02x" % val;
        return val;
    def CCdebuginstr(self,instr):
        self.writecmd(self.APP,0x88,len(instr),instr);
        return ord(self.data[0]);
    #def peekblock(self,adr,length,memory="vn"):
    #    """Return a block of data, broken"""
    #    data=[adr&0xff, (adr&0xff00)>>8,
    #          length&0xFF,(length&0xFF00)>>8];
    #    self.writecmd(self.APP,0x91,4,data);
    #    return [ord(x) for x in self.data]
    def peek8(self,address, memory="code"):
        if(memory=="code" or memory=="flash" or memory=="vn"):
            return self.CCpeekcodebyte(address);
        elif(memory=="data" or memory=="xdata" or memory=="ram"):
            return self.CCpeekdatabyte(address);
        elif(memory=="idata" or memory=="iram"):
            return self.CCpeekirambyte(address);
        print "%s is an unknown memory." % memory;
        return 0xdead;
    def CCpeekcodebyte(self,adr):
        """Read the contents of code memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8];
        self.writecmd(self.APP,0x90,2,self.data);
        return ord(self.data[0]);
    def CCpeekdatabyte(self,adr):
        """Read the contents of data memory at an address."""
        self.data=[adr&0xff, (adr&0xff00)>>8];
        self.writecmd(self.APP,0x91, 2, self.data);
        return ord(self.data[0]);
    def CCpeekirambyte(self,adr):
        """Read the contents of IRAM at an address."""
        self.data=[adr&0xff];
        self.writecmd(self.APP,0x02, 1, self.data);
        return ord(self.data[0]);
    def CCpeekiramword(self,adr):
        """Read the little-endian contents of IRAM at an address."""
        return self.CCpeekirambyte(adr)+(
            self.CCpeekirambyte(adr+1)<<8);
    def CCpokeiramword(self,adr,val):
        self.CCpokeirambyte(adr,val&0xff);
        self.CCpokeirambyte(adr+1,(val>>8)&0xff);
    def CCpokeirambyte(self,adr,val):
        """Write the contents of IRAM at an address."""
        self.data=[adr&0xff, val&0xff];
        self.writecmd(self.APP,0x02, 2, self.data);
        return ord(self.data[0]);
    def pokebyte(self,adr,val,mem="xdata"):
        self.CCpokedatabyte(adr,val);
    def CCpokedatabyte(self,adr,val):
        """Write a byte to data memory."""
        self.data=[adr&0xff, (adr&0xff00)>>8, val];
        self.writecmd(self.APP, 0x92, 3, self.data);
        return ord(self.data[0]);
    def CCchiperase(self):
        """Erase all of the target's memory."""
        self.writecmd(self.APP,0x80,0,None);
    def erase(self):
        """Erase all of the target's memory."""
        self.CCchiperase();
        self.start();
    
    def CCstatus(self):
        """Check the status."""
        self.writecmd(self.APP,0x84,0,None);
        return ord(self.data[0])
    #Same as CC2530
    CCstatusbits={0x80 : "erase_busy",
                  0x40 : "pcon_idle",
                  0x20 : "cpu_halted",
                  0x10 : "pm0",
                  0x08 : "halt_status",
                  0x04 : "locked",
                  0x02 : "oscstable",
                  0x01 : "overflow"
                  };
    CCconfigbits={0x20 : "soft_power_mode",   #new for CC2530
                  0x08 : "timers_off",
                  0x04 : "dma_pause",
                  0x02 : "timer_suspend",
                  0x01 : "sel_flash_info_page" #stricken from CC2530
                  };
                  
    def status(self):
        """Check the status as a string."""
        status=self.CCstatus();
        str="";
        i=1;
        while i<0x100:
            if(status&i):
                str="%s %s" %(self.CCstatusbits[i],str);
            i*=2;
        return str;
    def start(self):
        """Start debugging."""
        ident=0x0000;
        #while ident==0xFFFF or ident==0x0000:
        self.setup();
        self.writecmd(self.APP,0x20,0,self.data);
        identa=self.CCident();
        self.CCidentstr();
        
        ident=self.CCident();
        #Get SmartRF Studio regs if they exist.
        self.loadsymbols(); 
        #print "Status: %s" % self.status();
    def stop(self):
        """Stop debugging."""
        self.writecmd(self.APP,0x21,0,self.data);
    def CCstep_instr(self):
        """Step one instruction."""
        self.writecmd(self.APP,0x89,0,self.data);
    def CCeraseflashbuffer(self):
        """Erase the 2kB flash buffer"""
        self.writecmd(self.APP,0x99);
    def CCflashpage(self,adr):
        """Flash 2kB a page of flash from 0xF000 in XDATA"""
        data=[adr&0xFF,
              (adr>>8)&0xFF,
              (adr>>16)&0xFF,
              (adr>>24)&0xFF];
        print "Flashing buffer to 0x%06x" % adr;
        self.writecmd(self.APP,0x95,4,data);
    
    def setsecret(self,value):
        """Set a secret word for later retreival.  Used by glitcher."""
        page = 0x0000;
        pagelen = self.CCpagesize(); #Varies by chip.
        print "page=%04x, pagelen=%04x" % (page,pagelen);
        
        self.CCeraseflashbuffer();
        print "Setting secret to %x" % value;
        self.CCpokedatabyte(0xF000,value);
        self.CCpokedatabyte(0xF800,value);
        print "Setting secret to %x==%x" % (value,
                                            self.CCpeekdatabyte(0xf000));
        self.CCflashpage(0);
        print "code[0]=%x" % self.CCpeekcodebyte(0);
    def getsecret(self):
        """Get a secret word.  Used by glitcher."""
        secret=self.CCpeekcodebyte(0);
        #print "Got secret %02x" % secret;
        return secret;
    
    #FIXME: This is CC1110-specific and duplicates functionality of 
    #       SmartRF7 integration.
    CCspecfuncregs={
        'P0':0x80,
        'SP':0x81,
        'DPL0':0x82,
        'DPH0':0x83,
        'DPL1':0x84,
        'DPH1':0x85,
        'U0CSR':0x86,
        'PCON':0x87,
        'TCON':0x88,
        'P0IFG':0x89,
        'P1IFG':0x8A,
        'P2IFG':0x8B,
        'PICTL':0x8C,
        'P1IEN':0x8D,
        'P0INP':0x8F,
        'P1':0x90,
        'RFIM':0x91,
        'DPS':0x92,
        'MPAGE':0x93,
        'ENDIAN':0x95,
        'S0CON':0x98,
        'IEN2':0x9A,
        'S1CON':0x9B,
        'T2CT':0x9C,
        'T2PR':0x9D,
        'T2CTL':0x9E,
        'P2':0xA0,
        'WORIRQ':0xA1,
        'WORCTRL':0xA2,
        'WOREVT0':0xA3,
        'WOREVT1':0xA4,
        'WORTIME0':0xA5,
        'WORTIME1':0xA6,
        'IEN0':0xA8,
        'IP0':0xA9,
        'FWT':0xAB,
        'FADDRL':0xAC,
        'FADDRH':0xAD,
        'FCTL':0xAE,
        'FWDATA':0xAF,
        'ENCDI':0xB1,
        'ENCDO':0xB2,
        'ENCCS':0xB3,
        'ADCCON1':0xB4,
        'ADCCON2':0xB5,
        'ADCCON3':0xB6,
        'IEN1':0xB8,
        'IP1':0xB9,
        'ADCL':0xBA,
        'ADCH':0xBB,
        'RNDL':0xBC,
        'RNDH':0xBD,
        'SLEEP':0xBE,
        'IRCON':0xC0,
        'U0DBUF':0xC1,
        'U0BAUD':0xC2,
        'U0UCR':0xC4,
        'U0GCR':0xC5,
        'CLKCON':0xC6,
        'MEMCTR':0xC7,
        'WDCTL':0xC9,
        'T3CNT':0xCA,
        'T3CTL':0xCB,
        'T3CCTL0':0xCC,
        'T3CC0':0xCD,
        'T3CCTL1':0xCE,
        'T3CC1':0xCF,
        'PSW':0xD0,
        'DMAIRQ':0xD1,
        'DMA1CFGL':0xD2,
        'DMA1CFGH':0xD3,
        'DMA0CFGL':0xD4,
        'DMA0CFGH':0xD5,
        'DMAARM':0xD6,
        'DMAREQ':0xD7,
        'TIMIF':0xD8,
        'RFD':0xD9,
        'T1CC0L':0xDA,
        'T1CC0H':0xDB,
        'T1CC1L':0xDC,
        'T1CC1H':0xDD,
        'T1CC2L':0xDE,
        'T1CC2H':0xDF,
        'ACC':0xE0,
        'RFST':0xE1,
        'T1CNTL':0xE2,
        'T1CNTH':0xE3,
        'T1CTL':0xE4,
        'T1CCTL0':0xE5,
        'T1CCTL1':0xE6,
        'T1CCTL2':0xE7,
        'IRCON2':0xE8,
        'RFIF':0xE9,
        'T4CNT':0xEA,
        'T4CTL':0xEB,
        'T4CCTL0':0xEC,
        'T4CC0':0xED,
        'T4CCTL1':0xEE,
        'T4CC1':0xEF,
        'B':0xF0,
        'PERCFG':0xF1,
        'ADCCFG':0xF2,
        'P0SEL':0xF3,
        'P1SEL':0xF4,
        'P2SEL':0xF5,
        'P1INP':0xF6,
        'P2INP':0xF7,
        'U1CSR':0xF8,
        'U1DBUF':0xF9,
        'U1BAUD':0xFA,
        'U1UCR':0xFB,
        'U1GCR':0xFC,
        'P0DIR':0xFD,
        'P1DIR':0xFE,
        'P2DIR':0xFF
    }
    def getSPR(self,args=[]):
        """Get special function registers."""
        print "Special Function Registers:"
        if len(args):
            for e in args:
                print "    %-8s : 0x%0.2x"%(e,self.CCpeekcodebyte(self.CCspecfuncregs[e]))
        else:
            for e in self.CCspecfuncregs.keys():
                print "    %-8s : 0x%0.2x"%(e,self.CCpeekcodebyte(self.CCspecfuncregs[e]))
    
    def dump(self,file,start=0,stop=0xffff):
        """Dump an intel hex file from code memory."""
        print "Dumping code from %04x to %04x as %s." % (start,stop,file);
        h = IntelHex(None);
        i=start;
        while i<=stop:
            h[i]=self.CCpeekcodebyte(i);
            if(i%0x100==0):
                print "Dumped %04x."%i;
                h.write_hex_file(file); #buffer to disk.
            i+=1;
        h.write_hex_file(file);

    def flash(self,file):
        """Flash an intel hex file to code memory."""
        print "Flashing %s" % file;
        
        h = IntelHex(file);
        page = 0x0000;
        pagelen = self.CCpagesize(); #Varies by chip.
        
        #print "page=%04x, pagelen=%04x" % (page,pagelen);
        
        bcount = 0;
        
        #Wipe the RAM buffer for the next flash page.
        self.CCeraseflashbuffer();
        for i in h._buf.keys():
            while(i>=page+pagelen):
                if bcount>0:
                    self.CCflashpage(page);
                    #client.CCeraseflashbuffer();
                    bcount=0;
                    print "Flashed page at %06x" % page
                page+=pagelen;
                    
            #Place byte into buffer.
            self.CCpokedatabyte(0xF000+i-page,
                                h[i]);
            bcount+=1;
            if(i%0x100==0):
                print "Buffering %04x toward %06x" % (i,page);
        #last page
        self.CCflashpage(page);
        print "Flashed final page at %06x" % page;


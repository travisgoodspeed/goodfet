#!/usr/bin/env python
# GoodFET Client Library for Maxim USB Chips.
# 
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!


import sys, time, string, cStringIO, struct, glob, os;
import warnings

from GoodFET import GoodFET;

warnings.warn(
"""This library will soon be deprecated in favor of the USB*.py libraries."""
)

#Handy registers.
rEP0FIFO=0
rEP1OUTFIFO=1
rEP2INFIFO=2
rEP3INFIFO=3
rSUDFIFO=4
rEP0BC=5
rEP1OUTBC=6
rEP2INBC=7
rEP3INBC=8
rEPSTALLS=9
rCLRTOGS=10
rEPIRQ=11
rEPIEN=12
rUSBIRQ=13
rUSBIEN=14
rUSBCTL=15
rCPUCTL=16
rPINCTL=17
rREVISION=18
rFNADDR=19
rIOPINS=20
rIOPINS1=20  #Same as rIOPINS
rIOPINS2=21
rHIRQ=25
rHIEN=26
rMODE=27
rPERADDR=28
rHCTL=29
rHXFR=30
rHRSL=31

#Host mode registers.
rRCVFIFO =1
rSNDFIFO =2
rRCVBC   =6
rSNDBC   =7
rHIRQ    =25


# R11 EPIRQ register bits
bmSUDAVIRQ =0x20
bmIN3BAVIRQ =0x10
bmIN2BAVIRQ =0x08
bmOUT1DAVIRQ= 0x04
bmOUT0DAVIRQ= 0x02
bmIN0BAVIRQ =0x01

# R12 EPIEN register bits
bmSUDAVIE   =0x20
bmIN3BAVIE  =0x10
bmIN2BAVIE  =0x08
bmOUT1DAVIE =0x04
bmOUT0DAVIE =0x02
bmIN0BAVIE  =0x01




# ************************
# Standard USB Requests
SR_GET_STATUS		=0x00	# Get Status
SR_CLEAR_FEATURE	=0x01	# Clear Feature
SR_RESERVED		=0x02	# Reserved
SR_SET_FEATURE		=0x03	# Set Feature
SR_SET_ADDRESS		=0x05	# Set Address
SR_GET_DESCRIPTOR	=0x06	# Get Descriptor
SR_SET_DESCRIPTOR	=0x07	# Set Descriptor
SR_GET_CONFIGURATION	=0x08	# Get Configuration
SR_SET_CONFIGURATION	=0x09	# Set Configuration
SR_GET_INTERFACE	=0x0a	# Get Interface
SR_SET_INTERFACE	=0x0b	# Set Interface

# Get Descriptor codes	
GD_DEVICE		=0x01	# Get device descriptor: Device
GD_CONFIGURATION	=0x02	# Get device descriptor: Configuration
GD_STRING		=0x03	# Get device descriptor: String
GD_HID	            	=0x21	# Get descriptor: HID
GD_REPORT	        =0x22	# Get descriptor: Report

# SETUP packet header offsets
bmRequestType           =0
bRequest       	        =1
wValueL			=2
wValueH			=3
wIndexL			=4
wIndexH			=5
wLengthL		=6
wLengthH		=7

# HID bRequest values
GET_REPORT		=1
GET_IDLE		=2
GET_PROTOCOL            =3
SET_REPORT		=9
SET_IDLE		=0x0A
SET_PROTOCOL            =0x0B
INPUT_REPORT            =1

# PINCTL bits
bmEP3INAK   =0x80
bmEP2INAK   =0x40
bmEP1INAK   =0x20
bmFDUPSPI   =0x10
bmINTLEVEL  =0x08
bmPOSINT    =0x04
bmGPXB      =0x02
bmGPXA      =0x01

# rUSBCTL bits
bmHOSCSTEN  =0x80
bmVBGATE    =0x40
bmCHIPRES   =0x20
bmPWRDOWN   =0x10
bmCONNECT   =0x08
bmSIGRWU    =0x04

# USBIRQ bits
bmURESDNIRQ =0x80
bmVBUSIRQ   =0x40
bmNOVBUSIRQ =0x20
bmSUSPIRQ   =0x10
bmURESIRQ   =0x08
bmBUSACTIRQ =0x04
bmRWUDNIRQ  =0x02
bmOSCOKIRQ  =0x01

# MODE bits
bmHOST          =0x01
bmLOWSPEED      =0x02
bmHUBPRE        =0x04
bmSOFKAENAB     =0x08
bmSEPIRQ        =0x10
bmDELAYISO      =0x20
bmDMPULLDN      =0x40
bmDPPULLDN      =0x80

# PERADDR/HCTL bits
bmBUSRST        =0x01
bmFRMRST        =0x02
bmSAMPLEBUS     =0x04
bmSIGRSM        =0x08
bmRCVTOG0       =0x10
bmRCVTOG1       =0x20
bmSNDTOG0       =0x40
bmSNDTOG1       =0x80

# rHXFR bits
# Host XFR token values for writing the HXFR register (R30).
# OR this bit field with the endpoint number in bits 3:0
tokSETUP  =0x10  # HS=0, ISO=0, OUTNIN=0, SETUP=1
tokIN     =0x00  # HS=0, ISO=0, OUTNIN=0, SETUP=0
tokOUT    =0x20  # HS=0, ISO=0, OUTNIN=1, SETUP=0
tokINHS   =0x80  # HS=1, ISO=0, OUTNIN=0, SETUP=0
tokOUTHS  =0xA0  # HS=1, ISO=0, OUTNIN=1, SETUP=0 
tokISOIN  =0x40  # HS=0, ISO=1, OUTNIN=0, SETUP=0
tokISOOUT =0x60  # HS=0, ISO=1, OUTNIN=1, SETUP=0

# rRSL bits
bmRCVTOGRD   =0x10
bmSNDTOGRD   =0x20
bmKSTATUS    =0x40
bmJSTATUS    =0x80
# Host error result codes, the 4 LSB's in the HRSL register.
hrSUCCESS   =0x00
hrBUSY      =0x01
hrBADREQ    =0x02
hrUNDEF     =0x03
hrNAK       =0x04
hrSTALL     =0x05
hrTOGERR    =0x06
hrWRONGPID  =0x07
hrBADBC     =0x08
hrPIDERR    =0x09
hrPKTERR    =0x0A
hrCRCERR    =0x0B
hrKERR      =0x0C
hrJERR      =0x0D
hrTIMEOUT   =0x0E
hrBABBLE    =0x0F

# HIRQ bits
bmBUSEVENTIRQ   =0x01   # indicates BUS Reset Done or BUS Resume     
bmRWUIRQ        =0x02
bmRCVDAVIRQ     =0x04
bmSNDBAVIRQ     =0x08
bmSUSDNIRQ      =0x10
bmCONDETIRQ     =0x20
bmFRAMEIRQ      =0x40
bmHXFRDNIRQ     =0x80

class GoodFETMAXUSB(GoodFET):
    MAXUSBAPP=0x40;
    usbverbose=False;
    
    def service_irqs(self):
        """Handle USB interrupt events."""
        epirq=self.rreg(rEPIRQ);
        usbirq=self.rreg(rUSBIRQ);
        
        
        #Are we being asked for setup data?
        if(epirq&bmSUDAVIRQ): #Setup Data Requested
            self.wreg(rEPIRQ,bmSUDAVIRQ); #Clear the bit
            self.do_SETUP();
        if(epirq&bmOUT1DAVIRQ): #OUT1-OUT packet
            self.do_OUT1();
            self.wreg(rEPIRQ,bmOUT1DAVIRQ); #Clear the bit *AFTER* servicing.
        if(epirq&bmIN3BAVIRQ): #IN3-IN packet
            self.do_IN3();
            #self.wreg(rEPIRQ,bmIN3BAVIRQ); #Clear the bit
        if(epirq&bmIN2BAVIRQ): #IN2 packet
            self.do_IN2();
            #self.wreg(rEPIRQ,bmIN2BAVIRQ); #Clear the bit
        #else:
        #    print "No idea how to service this IRQ: %02x" % epirq;
    def do_IN2(self):
        """Overload this."""
    def do_IN3(self):
        """Overload this."""
    def do_OUT1(self):
        """Overload this."""
        if self.usbverbose: print "Ignoring an OUT1 interrupt.";
    def setup2str(self,SUD):
        """Converts the header of a setup packet to a string."""
        return "bmRequestType=0x%02x, bRequest=0x%02x, wValue=0x%04x, wIndex=0x%04x, wLength=0x%04x" % (
                ord(SUD[0]), ord(SUD[1]),
                ord(SUD[2])+(ord(SUD[3])<<8),
                ord(SUD[4])+(ord(SUD[5])<<8),
                ord(SUD[6])+(ord(SUD[7])<<8)
                );
    
    def MAXUSBsetup(self):
        """Move the FET into the MAXUSB application."""
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        print "Connected to MAX342x Rev. %x" % (self.rreg(rREVISION));
        self.wreg(rPINCTL,0x18); #Set duplex and negative INT level.
        
    def MAXUSBtrans8(self,byte):
        """Read and write 8 bits by MAXUSB."""
        data=self.MAXUSBtrans([byte]);
        return ord(data[0]);
    
    def MAXUSBtrans(self,data):
        """Exchange data by MAXUSB."""
        self.data=data;
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return self.data;

    def rreg(self,reg):
        """Peek 8 bits from a register."""
        data=[reg<<3,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def rregAS(self,reg):
        """Peek 8 bits from a register, setting AS."""
        data=[(reg<<3)|1,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def wreg(self,reg,value):
        """Poke 8 bits into a register."""
        data=[(reg<<3)|2,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def wregAS(self,reg,value):
        """Poke 8 bits into a register, setting AS."""
        data=[(reg<<3)|3,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def readbytes(self,reg,length):
        """Peek some bytes from a register."""
        data=[(reg<<3)]+range(0,length);
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        toret=self.data[1:len(self.data)];
        ashex="";
        for foo in toret:
            ashex=ashex+(" %02x"%ord(foo));
        if self.usbverbose: print "GET   %02x==%s" % (reg,ashex);
        return toret;
    def readbytesAS(self,reg,length):
        """Peek some bytes from a register, acking prior transfer."""
        data=[(reg<<3)|1]+range(0,length);
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        toret=self.data[1:len(self.data)];
        ashex="";
        for foo in toret:
            ashex=ashex+(" %02x"%ord(foo));
        if self.usbverbose: print "GETAS %02x==%s" % (reg,ashex);
        return toret;
    def fifo_ep3in_tx(self,data):
        """Sends the data out of EP3 in 64-byte chunks."""
        #Wait for the buffer to be free before starting.
        while not(self.rreg(rEPIRQ)&bmIN3BAVIRQ): pass;
        
        count=len(data);
        pos=0;
        while count>0:
            #Send 64-byte chunks or the remainder.
            c=min(count,64);
            self.writebytes(rEP3INFIFO,
                            data[pos:pos+c]);
            self.wregAS(rEP3INBC,c);
            count=count-c;
            pos=pos+c;
            
            #Wait for the buffer to be free before continuing.
            while not(self.rreg(rEPIRQ)&bmIN3BAVIRQ): pass;
            
        return;
        
    def ctl_write_nd(self,request):
        """Control Write with no data stage.  Assumes PERADDR is set
        and the SUDFIFO contains the 8 setup bytes.  Returns with
        result code = HRSLT[3:0] (HRSL register).  If there is an
        error, the 4MSBits of the returned value indicate the stage 1
        or 2."""
        
        # 1. Send the SETUP token and 8 setup bytes. 
        # Should ACK immediately.
        self.writebytes(rSUDFIFO,request);
        resultcode=self.send_packet(tokSETUP,0); #SETUP packet to EP0.
        if resultcode: return resultcode;
        
        # 2. No data stage, so the last operation is to send an IN
        # token to the peripheral as the STATUS (handhsake) stage of
        # this control transfer.  We should get NAK or the DATA1 PID.
        # When we get back to the DATA1 PID the 3421 automatically
        # sends the closing NAK.
        resultcode=self.send_packet(tokINHS,0); #Function takes care of retries.
        if resultcode: return resultcode;
        
        return 0;
        
        
    def ctl_read(self,request):
        """Control read transfer, used in Host mode."""
        resultcode=0;
        bytes_to_read=request[6]+256*request[7];
        
        ##SETUP packet
        self.writebytes(rSUDFIFO,request);     #Load the FIFO
        resultcode=self.send_packet(tokSETUP,0); #SETUP packet to EP0
        if resultcode:
            print "Failed to get ACK on SETUP request in ctl_read()."
            return resultcode;
        
        self.wreg(rHCTL,bmRCVTOG1);              #FIRST data packet in CTL transfer uses DATA1 toggle.
        resultcode=self.IN_Transfer(0,bytes_to_read);
        if resultcode:
            print "Failed on IN Transfer in ctl_read()";
            return resultcode;
        
        self.IN_nak_count=self.nak_count;
        
        #The OUT status stage.
        resultcode=self.send_packet(tokOUTHS,0);
        if resultcode:
            print "Failed on OUT Status stage in ctl_read()";
            return resultcode;
        
        return 0; #Success
    
    xfrdata=[]; #Ugly variable used only by a few functions.  FIXME
    def IN_Transfer(self,endpoint,INbytes):
        """Does an IN transfer to an endpoint, used for Host mode."""
        xfrsize=INbytes;
        xfrlen=0;
        self.xfrdata=[];
        
        while 1:
            resultcode=self.send_packet(tokIN,endpoint); #IN packet to EP. NAKS taken care of.
            if resultcode: return resultcode;
            
            pktsize=self.rreg(rRCVBC); #Numer of RXed bytes.
            
            #Very innefficient, move this to C if performance is needed.
            for j in range(0,pktsize):
                self.xfrdata=self.xfrdata+[self.rreg(rRCVFIFO)];
            xfrsize=self.xfrdata[0];
            self.wreg(rHIRQ,bmRCVDAVIRQ); #Clear IRQ
            xfrlen=xfrlen+pktsize; #Add byte count to total transfer length.
            
            #print "%i / %i" % (xfrlen,xfrsize)
            
            #Packet is complete if:
            # 1. The device sent a short packet, <maxPacketSize
            # 2. INbytes have been transfered.
            if (pktsize<self.maxPacketSize) or (xfrlen>=xfrsize):
                self.last_transfer_size=xfrlen;
                ashex="";
                for foo in self.xfrdata:
                    ashex=ashex+(" %02x"%foo);
                #print "INPACKET EP%i==%s (0x%02x bytes remain)" % (endpoint,ashex,xfrsize);
                return resultcode;

    RETRY_LIMIT=3;
    NAK_LIMIT=300;
    def send_packet(self,token,endpoint):
        """Send a packet to an endpoint as the Host, taking care of NAKs.
        Don't use this for device code."""
        self.retry_count=0;
        self.nak_count=0;
        
        #Repeat until NAK_LIMIT or RETRY_LIMIT is reached.
        while self.nak_count<self.NAK_LIMIT and self.retry_count<self.RETRY_LIMIT:
            self.wreg(rHXFR,(token|endpoint)); #launch the transfer
            while not (self.rreg(rHIRQ) & bmHXFRDNIRQ):
                # wait for the completion IRQ
                pass;
            self.wreg(rHIRQ,bmHXFRDNIRQ);           #Clear IRQ
            resultcode = (self.rreg(rHRSL) & 0x0F); # get the result
            if (resultcode==hrNAK):
                self.nak_count=self.nak_count+1;
            elif (resultcode==hrTIMEOUT):
                self.retry_count=self.retry_count+1;
            else:
                #Success!
                return resultcode;
        return resultcode;
            
    def writebytes(self,reg,tosend):
        """Poke some bytes into a register."""
        data="";
        if type(tosend)==str:
            data=chr((reg<<3)|3)+tosend;
            if self.usbverbose: print "PUT %02x:=%s (0x%02x bytes)" % (reg,tosend,len(data))
        else:
            data=[(reg<<3)|3]+tosend;
            ashex="";
            for foo in tosend:
                ashex=ashex+(" %02x"%foo);
            if self.usbverbose: print "PUT %02x:=%s (0x%02x bytes)" % (reg,ashex,len(data))
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
    def usb_connect(self):
        """Connect the USB port."""
        
        #disconnect D+ pullup if host turns off VBUS
        self.wreg(rUSBCTL,bmVBGATE|bmCONNECT);
    def usb_disconnect(self):
        """Disconnect the USB port."""
        self.wreg(rUSBCTL,bmVBGATE);
    def STALL_EP0(self,SUD=None):
        """Stall for an unknown SETUP event."""
        if SUD==None:
            print "Stalling EP0.";
        else:
            print "Stalling EPO for %s" % self.setup2str(SUD);
        self.wreg(rEPSTALLS,0x23); #All three stall bits.
    def SETBIT(self,reg,val):
        """Set a bit in a register."""
        self.wreg(reg,self.rreg(reg)|val);
    def vbus_on(self):
        """Turn on the target device."""
        self.wreg(rIOPINS2,(self.rreg(rIOPINS2)|0x08));
    def vbus_off(self):
        """Turn off the target device's power."""
        self.wreg(rIOPINS2,0x00);
    def reset_host(self):
        """Resets the chip into host mode."""
        self.wreg(rUSBCTL,bmCHIPRES); #Stop the oscillator.
        self.wreg(rUSBCTL,0x00);      #restart it.
        
        #FIXME: Why does the OSC line never settle?
        #Code works without it.
        
        #print "Waiting for PLL to sabilize.";
        #while self.rreg(rUSBIRQ)&bmOSCOKIRQ:
        #    #Hang until the PLL stabilizes.
        #    pass;
        #print "Stable.";

class GoodFETMAXUSBHost(GoodFETMAXUSB):
    """This is a class for implemented a minimal USB host.
    It's intended for fuzzing, rather than for daily use."""
    def hostinit(self):
        """Initialize the MAX3421 as a USB Host."""
        self.usb_connect();
        print "Enabling host mode.";
        self.wreg(rPINCTL,(bmFDUPSPI|bmPOSINT));
        print "Resetting host.";
        self.reset_host();
        self.vbus_off();
        time.sleep(0.2);
        print "Powering host.";
        self.vbus_on();
        
        #self.hostrun();
    def hostrun(self):
        """Run as a minimal host and dump the config tables."""
        while 1:
            self.detect_device();
            time.sleep(0.2);
            self.enumerate_device();
            self.wait_for_disconnect();
    def detect_device(self):
        """Waits for a device to be inserted and then returns."""
        busstate=0;
        
        #Activate host mode and turn on 15K pulldown resistors on D+ and D-.
        self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST));
        #Clear connection detect IRQ.
        self.wreg(rHIRQ,bmCONDETIRQ);
        
        print "Waiting for a device connection.";
        while busstate==0:
            self.wreg(rHCTL,bmSAMPLEBUS); #Update JSTATUS and KSTATUS bits.
            busstate=self.rreg(rHRSL) & (bmJSTATUS|bmKSTATUS);
            
        if busstate==bmJSTATUS:
            print "Detected Full-Speed Device.";
            self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST|bmSOFKAENAB));
        elif busstate==bmKSTATUS:
            print "Detected Low-Speed Device.";
            self.wreg(rMODE,(bmDPPULLDN|bmDMPULLDN|bmHOST|bmLOWSPEED|bmSOFKAENAB));
        else:
            print "Not sure whether this is Full-Speed or Low-Speed.  Please investigate.";
    def wait_for_disconnect(self):
        """Wait for a device to be disconnected."""
        print "Waiting for a device disconnect.";
        
        self.wreg(rHIRQ,bmCONDETIRQ); #Clear disconnect IRQ
        while not (self.rreg(rHIRQ) & bmCONDETIRQ):
            #Wait for IRQ to change.
            pass;
        
        #Turn off markers.
        self.wreg(rMODE,bmDPPULLDN|bmDMPULLDN|bmHOST);
        print "Device disconnected.";
        self.wreg(rIOPINS2,(self.rreg(rIOPINS2) & ~0x04)); #HL1_OFF
        self.wreg(rIOPINS1,(self.rreg(rIOPINS1) & ~0x02)); #HL4_OFF

    def enumerate_device(self):
        """Enumerates a device on the present port."""
        
        Set_Address_to_7 = [0x00,0x05,0x07,0x00,0x00,0x00,0x00,0x00];
        Get_Descriptor_Device = [0x80,0x06,0x00,0x01,0x00,0x00,0x00,0x00]; #len filled in
        Get_Descriptor_Config = [0x80,0x06,0x00,0x02,0x00,0x00,0x00,0x00];
        
        
        print "Issuing USB bus reset.";
        self.wreg(rHCTL,bmBUSRST);
        while self.rreg(rHCTL) & bmBUSRST:
            #Wait for reset to complete.
            pass;
        
        time.sleep(0.2);
        
        #Get the device descriptor.
        self.wreg(rPERADDR,0); #First request to address 0.
        self.maxPacketSize=8; #Only safe value for first check.
        Get_Descriptor_Device[6]=8; # wLengthL
        Get_Descriptor_Device[7]=0; # wLengthH
        
        print "Fetching 8 bytes of Device Descriptor.";
        self.ctl_read(Get_Descriptor_Device); # Get device descriptor into self.xfrdata;
        self.maxPacketSize=self.xfrdata[7];
        print "EP0 maxPacketSize is %02i bytes." % self.maxPacketSize;
        
        # Issue another USB bus reset
        print "Resetting the bus again."
        self.wreg(rHCTL,bmBUSRST);
        while self.rreg(rHCTL) & bmBUSRST:
            #Wait for reset to complete.
            pass;
        time.sleep(0.2);
        
        # Set_Address to 7 (Note: this request goes to address 0, already set in PERADDR register).
        print "Setting address to 0x07";
        HR = self.ctl_write_nd(Set_Address_to_7);   # CTL-Write, no data stage
        #if(print_error(HR)) return;
        
        time.sleep(0.002);           # Device gets 2 msec recovery time
        self.wreg(rPERADDR,7);       # now all transfers go to addr 7
        
        
        #Get the device descriptor at the assigned address.
        Get_Descriptor_Device[6]=0x12; #Fill in real descriptor length.
        print "Fetching Device Descriptor."
        self.ctl_read(Get_Descriptor_Device); #Result in self.xfrdata;
        
        self.descriptor=self.xfrdata;
        self.VID 	= self.xfrdata[8] + 256*self.xfrdata[9];
        self.PID 	= self.xfrdata[10]+ 256*self.xfrdata[11];
        iMFG 	= self.xfrdata[14];
        iPROD 	= self.xfrdata[15];
        iSERIAL	= self.xfrdata[16];
        
        self.manufacturer=self.getDescriptorString(iMFG);
        self.product=self.getDescriptorString(iPROD);
        self.serial=self.getDescriptorString(iSERIAL);
        
        self.printstrings();
        
    def printstrings(self):
        print "Vendor  ID is %04x." % self.VID;
        print "Product ID is %04x." % self.PID;
        print "Manufacturer: %s" % self.manufacturer;
        print "Product:      %s" % self.product;
        print "Serial:       %s" % self.serial;
        
    def getDescriptorString(self, index):
        """Grabs a string from the descriptor string table."""
        # Get_Descriptor-String template. Code fills in idx at str[2].
        Get_Descriptor_String = [0x80,0x06,index,0x03,0x00,0x00,0x40,0x00];
        
        if index==0: return "MISSING STRING";
        
        status=self.ctl_read(Get_Descriptor_String);
        if status: return None;
        
        #Since we've got a string
        toret="";
        for c in self.xfrdata[2:len(self.xfrdata)]:
            if c>0: toret=toret+chr(c);
        return toret;
class GoodFETMAXUSBDevice(GoodFETMAXUSB):
    
    def send_descriptor(self,SUD):
        """Send the USB descriptors based upon the setup data."""
        desclen=0;
        reqlen=ord(SUD[wLengthL])+256*ord(SUD[wLengthH]); #16-bit length
        desctype=ord(SUD[wValueH]);
        
        if desctype==GD_DEVICE:
            desclen=self.DD[0];
            ddata=self.DD;
        elif desctype==GD_CONFIGURATION:
            desclen=self.CD[2];
            ddata=self.CD;
        elif desctype==GD_STRING:
            desclen=ord(self.strDesc[ord(SUD[wValueL])][0]);
            ddata=self.strDesc[ord(SUD[wValueL])];
        elif desctype==GD_HID:
            #Don't know how to do this yet.
            pass;
        elif desctype==GD_REPORT:
            desclen=self.CD[25];
            ddata=self.RepD;
        #TODO Configuration, String, Hid, and Report
        
        if desclen>0:
            #Reduce desclen if asked for fewer bytes.
            desclen=min(reqlen,desclen);
            #Send those bytes.
            self.writebytes(rEP0FIFO,ddata[0:desclen]);
            self.wregAS(rEP0BC,desclen);
        else:
            print "Stalling in send_descriptor() for lack of handler for %02x." % desctype;
            self.STALL_EP0(SUD);
    def set_configuration(self,SUD):
        """Set the configuration."""
        bmSUSPIE=0x10;
        configval=ord(SUD[wValueL]);
        if(configval>0):
            self.SETBIT(rUSBIEN,bmSUSPIE);
        self.rregAS(rFNADDR);
class GoodFETMAXUSBHID(GoodFETMAXUSBDevice):
    """This is an example HID keyboard driver, loosely based on the
    MAX3420 examples."""
    def hidinit(self):
        """Initialize a USB HID device."""
        self.usb_disconnect();
        self.usb_connect();
        
        self.hidrun();
        
    def hidrun(self):
        """Main loop of the USB HID emulator."""
        print "Starting a HID device.  This won't return.";
        while 1:
            self.service_irqs();
    def do_SETUP(self):
        """Handle USB Enumeration"""
        
        #Grab the SETUP packet from the buffer.
        SUD=self.readbytes(rSUDFIFO,8);
        
        #Parse the SETUP packet
        print "Handling a setup packet of %s" % self.setup2str(SUD);
        
	self.OsLastConfigType=ord(SUD[bmRequestType]);
	self.typepos=0;
        setuptype=(ord(SUD[bmRequestType])&0x60);
        if setuptype==0x00:
            self.std_request(SUD);
        elif setuptype==0x20:
            self.class_request(SUD);
        elif setuptype==0x40:
            self.vendor_request(SUD);
        else:
            print "Unknown request type 0x%02x." % ord(SUD[bmRequestType])
            self.STALL_EP0(SUD);
    def class_request(self,SUD):
        """Handle a class request."""
        print "Stalling a class request.";
        self.STALL_EP0(SUD);
    def vendor_request(self,SUD):
        print "Stalling a vendor request.";
        self.STALL_EP0(SUD);
    def std_request(self,SUD):
        """Handles a standard setup request."""
        setuptype=ord(SUD[bRequest]);
        if setuptype==SR_GET_DESCRIPTOR: self.send_descriptor(SUD);
        #elif setuptype==SR_SET_FEATURE:
        #    self.rregAS(rFNADDR);
        #    # self.feature(1);
        elif setuptype==SR_SET_CONFIGURATION: self.set_configuration(SUD);
        elif setuptype==SR_GET_STATUS: self.get_status(SUD);
        elif setuptype==SR_SET_ADDRESS: self.rregAS(rFNADDR);
        elif setuptype==SR_GET_INTERFACE: self.get_interface(SUD);
        else:
            print "Stalling Unknown standard setup request type %02x" % setuptype;
            self.STALL_EP0(SUD);
    
    def get_interface(self,SUD):
        """Handles a setup request for SR_GET_INTERFACE."""
        if ord(SUD[wIndexL]==0):
            self.wreg(rEP0FIFO,0);
            self.wregAS(rEP0BC,1);
        else:
            self.STALL_EP0(SUD);
    
    OsLastConfigType=-1;
#Device Descriptor
    DD=[0x12,	       		# bLength = 18d
        0x01,			# bDescriptorType = Device (1)
        0x00,0x01,		# bcdUSB(L/H) USB spec rev (BCD)
	0x00,0x00,0x00, 	# bDeviceClass, bDeviceSubClass, bDeviceProtocol
	0x40,			# bMaxPacketSize0 EP0 is 64 bytes
	0x6A,0x0B,		# idVendor(L/H)--Maxim is 0B6A
	0x46,0x53,		# idProduct(L/H)--5346
	0x34,0x12,		# bcdDevice--1234
	1,2,3,			# iManufacturer, iProduct, iSerialNumber
	1];
#Configuration Descriptor
    CD=[0x09,			# bLength
	0x02,			# bDescriptorType = Config
	0x22,0x00,		# wTotalLength(L/H) = 34 bytes
	0x01,			# bNumInterfaces
	0x01,			# bConfigValue
	0x00,			# iConfiguration
	0xE0,			# bmAttributes. b7=1 b6=self-powered b5=RWU supported
	0x01,			# MaxPower is 2 ma
# INTERFACE Descriptor
	0x09,			# length = 9
	0x04,			# type = IF
	0x00,			# IF #0
	0x00,			# bAlternate Setting
	0x01,			# bNum Endpoints
	0x03,			# bInterfaceClass = HID
	0x00,0x00,		# bInterfaceSubClass, bInterfaceProtocol
	0x00,			# iInterface
# HID Descriptor--It's at CD[18]
	0x09,			# bLength
	0x21,			# bDescriptorType = HID
	0x10,0x01,		# bcdHID(L/H) Rev 1.1
	0x00,			# bCountryCode (none)
	0x01,			# bNumDescriptors (one report descriptor)
	0x22,			# bDescriptorType	(report)
	43,0,                   # CD[25]: wDescriptorLength(L/H) (report descriptor size is 43 bytes)
# Endpoint Descriptor
	0x07,			# bLength
	0x05,			# bDescriptorType (Endpoint)
	0x83,			# bEndpointAddress (EP3-IN)		
	0x03,			# bmAttributes	(interrupt)
	64,0,                   # wMaxPacketSize (64)
	10];
    strDesc=[
# STRING descriptor 0--Language string
"\x04\x03\x09\x04",
# [
#         0x04,			# bLength
# 	0x03,			# bDescriptorType = string
# 	0x09,0x04		# wLANGID(L/H) = English-United Sates
# ],
# STRING descriptor 1--Manufacturer ID
"\x0c\x03M\x00a\x00x\x00i\x00m\x00",
# [
#         12,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'a',0,'x',0,'i',0,'m',0 # text in Unicode
# ], 
# STRING descriptor 2 - Product ID
"\x18\x03M\x00A\x00X\x003\x004\x002\x000\x00E\x00 \x00E\x00n\x00u\x00m\x00 \x00C\x00o\x00d\x00e\x00",
# [	24,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'A',0,'X',0,'3',0,'4',0,'2',0,'0',0,'E',0,' ',0,
#         'E',0,'n',0,'u',0,'m',0,' ',0,'C',0,'o',0,'d',0,'e',0
# ],


# STRING descriptor 3 - Serial Number ID
"\x14\x03S\x00/\x00N\x00 \x003\x004\x002\x000\x00E\x00"
# [       20,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'S',0,				
# 	'/',0,
# 	'N',0,
# 	' ',0,
# 	'3',0,
# 	'4',0,
# 	'2',0,
# 	'0',0,
#         'E',0,
# ]
];
    RepD=[
        0x05,0x01,		# Usage Page (generic desktop)
	0x09,0x06,		# Usage (keyboard)
	0xA1,0x01,		# Collection
	0x05,0x07,		#   Usage Page 7 (keyboard/keypad)
	0x19,0xE0,		#   Usage Minimum = 224
	0x29,0xE7,		#   Usage Maximum = 231
	0x15,0x00,		#   Logical Minimum = 0
	0x25,0x01,		#   Logical Maximum = 1
	0x75,0x01,		#   Report Size = 1
	0x95,0x08,		#   Report Count = 8
	0x81,0x02,		#  Input(Data,Variable,Absolute)
	0x95,0x01,		#   Report Count = 1
	0x75,0x08,		#   Report Size = 8
	0x81,0x01,		#  Input(Constant)
	0x19,0x00,		#   Usage Minimum = 0
	0x29,0x65,		#   Usage Maximum = 101
	0x15,0x00,		#   Logical Minimum = 0,
	0x25,0x65,		#   Logical Maximum = 101
	0x75,0x08,		#   Report Size = 8
	0x95,0x01,		#   Report Count = 1
	0x81,0x00,		#  Input(Data,Variable,Array)
	0xC0]

    def get_status(self,SUD):
        """Get the USB Setup Status."""
        testbyte=ord(SUD[bmRequestType])
        
        #Toward Device
        if testbyte==0x80:
            self.wreg(rEP0FIFO,0x03); #Enable RWU and self-powered
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);    #Load byte count, arm transfer, and ack CTL.
        #Toward Interface
        elif testbyte==0x81:
            self.wreg(rEP0FIFO,0x00);
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);
        #Toward Endpoint
        elif testbyte==0x82:
            if(ord(SUD[wIndexL])==0x83):
                self.wreg(rEP0FIFO,0x01); #Stall EP3
                self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
                self.wregAS(rEP0BC,2);
            else:
                self.STALL_EP0(SUD);
        else:
            self.STALL_EP0(SUD);

    typepos=0;
    typestrings={
	-1   : "Python does USB HID!\n",		# Unidentified OS.  This is the default typestring.
	0x00 : "OSX Hosts don't recognize Maxim keyboards.\n",	# We have to identify as an Apple keyboard to get arround the unknown keyboard error.
	0xA1 : "Python does USB HID on Linux!\n",
	0x81 : "                                                                                             Python does USB HID on Windows!\n",	# Windows requires a bit of a delay.  Maybe we can watch for a keyboard reset command?
    }
    def typestring(self):
	if self.typestrings.has_key(self.OsLastConfigType):
	    return self.typestrings[self.OsLastConfigType];
	else:
	    return self.typestrings[-1];
    # http://www.win.tue.nl/~aeb/linux/kbd/scancodes-14.html
    # Escape=0x29 Backsp=0x2A Space=0x2C CapsLock=0x39 Menu=0x65
    keymaps={
	'en_US'  :[ '    abcdefghijklmnopqrstuvwxyz1234567890\n\t -=[]\\\\;\'`,./',
		    '''        ''',	 # LeftCtrl
		    '    ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()     {}?+||:"~<>?', # LeftShift
		    '', # LeftCtrl & LeftShift
		    '    abc'], # LeftAlt
	'Dvorak' :[ '    axje.uidchtnmbrl\'poygk,qf;1234567890\n\t []/=\\\\s-`wvz',
		    '''                                   ''',	 # LeftCtrl
		    '    AXJE UIDCHTNMBRL"POYGK<QF:!@#$%^&*()     {}?+||S_~WVZ', # LeftShift
		    '', # LeftCtrl & LeftShift
		    '    axj'], # LeftAlt
    }
    layout='en_US';
    def keymap(self):
	return self.keymaps[self.layout];
    modifiers={
	'None':		0b00000000,
	'LeftCtrl':	0b00000001,
	'LeftShift':	0b00000010,
	'LeftAlt':	0b00000100,
	'LeftGUI':	0b00001000,
	'RightCtrl':	0b00010000,
	'RightShift':	0b00100000,
	'RightAlt':	0b01000000,
	'RightGUI':	0b10000000
    }

    def asc2hid(self,ascii):
        """Translate ASCII to an USB keycode."""
	if type(ascii)!=str:
	    return (0,0);		# Send NoEvent if not passed a character
        if ascii==' ':
            return (0,0x2C);		# space
	for modset in self.keymap():
	    keycode=modset.find(ascii);
	    if keycode != -1:
		modifier = self.keymap().index(modset)
		return (modifier, keycode);
	return (0,0);
    def type_IN3(self):
	"""Type next letter in buffer."""
	string=self.typestring();
	if self.typepos>=len(string):
	    self.typeletter(0);		# Send NoEvent to indicate key-up
	    exit(0);
	    self.typepos=0;		# Repeat typestring forever!
	    # This would be a great place to enable a typethrough mode so the host operator can control the target
	else:
	    if self.usbverbose:
		sys.stdout.write(string[self.typepos]);
		sys.stdout.flush();
	    self.typeletter(string[self.typepos]);
	    self.typepos+=1;
	return;
    def typeletter(self,key):
        """Type a letter on IN3.  Zero for keyup."""
	mod=0;
	if type(key)==str:
	    (mod, key) = self.asc2hid(key);
	self.wreg(rEP3INFIFO,mod);
        self.wreg(rEP3INFIFO,0);
        self.wreg(rEP3INFIFO,key);
        self.wreg(rEP3INBC,3);
    def do_IN3(self):
        """Handle IN3 event."""
        #Don't bother clearing interrupt flag, that's done by sending the reply.
	if self.OsLastConfigType != -1:	# Wait for some configuration before stuffing keycodes down the pipe
	    self.type_IN3();
        

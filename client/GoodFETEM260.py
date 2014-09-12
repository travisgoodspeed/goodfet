#!/usr/bin/env python
# GoodFET EM260 Radio Client
# 
# (C) 2010 Travis Goodspeed <travis at radiantmachines.com>
# EM260 testing and updates by Don C. Weber (@cutaway), InGuardians, Inc.
#
# This code is being rewritten and refactored.  You've been warned!

# The EM260 is almost textbook SPI, except that the response cannot be
# read until after the nHOST_INT pin of the EM260 drops low and a dummy
# byte is read.  That is, the sequence will look like the following:

# Transmit Host->Slave Data
# while(nHOST_INT); //Sleep until ready.
# Recv Dummy Byte
# Recv Slave->Host Data

# The delay is mandatory.

import sys, time, string, cStringIO, struct, glob, os;

from GoodFETSPI import GoodFETSPI;

class GoodFETEM260(GoodFETSPI):
    EM260APP=0x01;
    seq=0;
    def EM260trans(self,data,retry=1):
        """Exchange data by EM260 SPI. (Slightly nonstandard.)"""
        
        if retry==0:
            #Retries exceeded.  Send a trivial command to clear error.
            data=[0x0A,0xA7];
        self.writecmd(0x01,0x82,len(data),data);
        
        
        try:
            reply=ord(self.data[0]);
            if(reply==0x00):
                #print "Warning: EM260 rebooted.";
                return self.EM260trans(data,retry-1);
            if(reply==0x02):
                #print "Error: Aborted Transaction.";
                return self.EM260trans(data,retry-1);
            if(reply==0x03):
                print "Error: Missing Frame Terminator.";
                return self.data;
            if(reply==0x04):
                print "Error: Reserved Error.  (Access denied?)";
                return self.data;
        except:
            print "Error in EM260trans.";
        return self.data;
    
    def EZSPtrans(self,frame):
        """Send an EZSP frame."""
        data=self.EM260trans([0xFE,len(frame)+2,
                              self.seq&0xFF,0x00,
                              ]+frame+[
                              0xA7]);
        s="EZSP< ";
        for foo in data:
            s=s+"%02x " % ord(foo);
        print s;
        
        if ord(data[0])!=0xFE:
            print "EZSP error: 0x%02x" % ord(data[0]);
        if ord(data[4])==0x58:
            print "EZSP Invalid Command because 0x%02x" % ord(data[5]);
            return data;
        if frame[0]!=ord(data[4]):
            print "EZSP warning: Command 0x%02x returned type 0x%02x." % (
                frame[0],ord(data[4]));
        self.seq=self.seq+1;
        return data;
    
# TODO: Get SIF Debugging interface working
# TODO: DUMP, PEEK, and POKE are broken because it needs to be done using the SIF debugging interface
'''        
    def peek8(self,adr):
        """Read a byte from the given address.  Untested."""
        
        data=self.EZSPtrans([0x47,adr&0xFF,10]);
        
        return ord(data[6]);
    def poke8(self,adr,val):
        """Poke a value into RAM.  Untested"""
        self.EZSPtrans([0x46,adr&0xFF,1,val&0xFF]);
        return val;
'''                
        
    def rand16(self):
        """Read a random 16-bit word."""
        
        data=self.EZSPtrans([0x49]);
        if data==None:
            print "Insufficient random data.";
            return 0;
        return ord(data[6])+(ord(data[7])<<8);

    def info(self):
        """Read the info bytes."""
        print "Ember EM26 Z-Stack SPI Module.";
        version=self.EM260spiversion();
        status=self.EM260spistatus();
        print "Version: %i" % (version); 
        print "Status:  %s" % (["dead","alive"][status]);
        print ""
        self.setVersion();
        print "Node ID: %04x" % (self.getNodeID());
        print "Connected to %2i neighbors." % self.neighborCount();
    def EM260spiversion(self):
        """Read the SPI version number from EM260."""
        data=self.EM260trans([0x0A,0xA7]);        
        version=ord(data[0]);
        
        if version==0x00:
            return self.EM260spiversion();
        if version==0x02:
            return self.EM260spiversion();
        if not version&0x80:
            print "Version misread.";
            return 0;
        return version&0x7F;
    
    def EM260spistatus(self):
        """Read the status bit."""
        data=self.EM260trans([0x0B,0xA7]);
        status=ord(data[0]);
        
        if status==0x00:
            return self.EM260spistatus();
        if status==0x02:
            return self.EM260spistatus();
        if not status&0x80 and status&0x40:
            print "Status misread.";
            return 0;
        return status&1;
    
    def echoData(self,edata='',ldata=None):
        """Read the EZSP node id."""
        tdata = [ord(e) for e in edata]
        if ldata:
            tdata += [ldata]
        else:
            tdata += [len(edata)]
        
        data=self.EZSPtrans([0x81]+tdata);
        rdata = data[5:-2]
        rlen  = data[-2]
        print "Returned length:",rlen
        print "Returned data:",rdata
        print "Returned data list:",rdata.encode('hex')
        return data
    
    #Everything after here is ZigBee.
    def getToken(self,token):
        data=self.EZSPtrans([0x0a]+[token]);
        return data[5:-1]

    def getMfgToken(self,token):
        data=self.EZSPtrans([0x0b]+[token]);
        return data[5:-1]

    def getKey(self,key):
        data=self.EZSPtrans([0x6a]+[key]);
        return data[5:-1]

    def getKeyTableEntry(self,key):
        data=self.EZSPtrans([0x6a]+[key]);
        return data[5:-1]

    def getCert(self):
        data=self.EZSPtrans([0xec]);
        return data[5:-1]

    def getCert283k1(self):
        data=self.EZSPtrans([0x6a]);
        return data[5:-1]
    
    def getNodeID(self):
        """Read the EZSP node id."""
        
        data=self.EZSPtrans([0x27]);
        return ord(data[5])+(ord(data[6])<<8);
    def neighborCount(self):
        """Read the count of neighbors, used for iterating the neighbor table."""
        
        data=self.EZSPtrans([0x7A]);
        return ord(data[5]);
    def setRadioChannel(self,channel):
        """Set the radio channel."""
        
        data=self.EZSPtrans([0x9A, channel&xFF]);
        return ord(data[5]);
    def setVersion(self,version=2):
        """Set the requested EZSP protocol version."""
        
        data=self.EZSPtrans([0x00, version]);
        newversion=ord(data[5]);
        if version==newversion:
            print "Version set."
            print "Protocol %i, stack type %i, Stack Version 0x%02x%02x." % (
                newversion,
                ord(data[6]),
                ord(data[8]),
                ord(data[7]));
        else:
            self.setVersion(newversion);

#!/usr/bin/env python
# GoodFET SPI Flash Client
#
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
#  Edited By: Chris Hoder    2013
#             Ted Summers    2013
#             Grayson Zulauf 2013
#


import sys;
import binascii;
import array;
import csv, time, argparse;
import datetime
import os
from random import randrange
from GoodFETMCPCAN import GoodFETMCPCAN;
from intelhex import IntelHex;
import Queue
from scapy.all import *


class CAN(Packet):
    name = "CANPacket"
    fields_desc=[	#IntEnumField("MessageType" , 0 ,
                	#{ 0: "unknown", 1: "Data" , 2: "RTR", 3: "Error" } ),
    				XShortField("SID", None),
                 	X3BytesField("EID", None),
                 	FieldLenField("DLC", None, count_of="Data", fmt="B"),
                 	FieldListField("Data", None, XByteField("DB", None), count_from=lambda pkt:pkt.DLC)
                 	]

class GoodFETMCPCANCommunication:
    
    def __init__(self, dataLocation = "../../contrib/ThayerData/"):
       self.client=GoodFETMCPCAN();
       """ Communication with the bus"""
       self.client.serInit()
       self.client.MCPsetup();
       #self.DATA_LOCATION = "../../contrib/ThayerData/"
       self.DATA_LOCATION = dataLocation; 
       """ Stores file data location. This is the root folder where basic sniffs will be stored"""
       self.INJECT_DATA_LOCATION  = self.DATA_LOCATION+"InjectedData/" 
       """ stores the sub folder path where injected data will be stored"""
       

    
    def printInfo(self):
        """ 
        This method will print information about the board to the terminal. 
        It is good for diagnostics.
        """
        
        self.client.MCPreqstatConfiguration();
        
        print "MCP2515 Info:\n\n";
        
        print "Mode: %s" % self.client.MCPcanstatstr();
        print "Read Status: %02x" % self.client.MCPreadstatus();
        print "Rx Status:   %02x" % self.client.MCPrxstatus();
        print "Error Flags:  %02x" % self.client.peek8(0x2D);
        print "Tx Errors:  %3d" % self.client.peek8(0x1c);
        print "Rx Errors:  %3d\n" % self.client.peek8(0x1d);
        
        print "Timing Info:";
        print "CNF1: %02x" %self.client.peek8(0x2a);
        print "CNF2: %02x" %self.client.peek8(0x29);
        print "CNF3: %02x\n" %self.client.peek8(0x28);
        print "RXB0 CTRL: %02x" %self.client.peek8(0x60);
        print "RXB1 CTRL: %02x" %self.client.peek8(0x70);
        
        print "RX Info:";
        print "RXB0: %02x" %self.client.peek8(0x60);
        print "RXB1: %02x" %self.client.peek8(0x70);
        print "RXB0 masks: %02x, %02x, %02x, %02x" %(self.client.peek8(0x20), self.client.peek8(0x21), self.client.peek8(0x22), self.client.peek8(0x23));
        print "RXB1 masks: %02x, %02x, %02x, %02x" %(self.client.peek8(0x24), self.client.peek8(0x25), self.client.peek8(0x26), self.client.peek8(0x27));

        
        print "RX Buffers:"
        packet0=self.client.readrxbuffer(0);
        packet1=self.client.readrxbuffer(1);
        for foo in [packet0, packet1]:
           print self.client.packet2str(foo);
           
    def reset(self):
        """ 
        Reset the chip
        """
        self.client.MCPsetup();
    
    
    ##########################
    #   SNIFF
    ##########################
         
    def sniff(self,freq,duration,description, verbose=True, comment=None, filename=None, standardid=None, debug=False, faster=False, parsed=True, data = None,writeToFile=True, db0 = None, db1 = None):
        """
        
        """
        #reset eveything on the chip
        self.client.serInit() 
        self.reset()
        
        # filtering for specific packets
        if(db0 != None and db1 != None and standardid != None):
            self.filterForPacket(standardid[0], db0, db1, verbose)
            if(comment == None):
                comment = ""
            comment += ("f%d[%d][%d]" %(standardid[0], db0, db1))
        # filtering for standard ID
        elif(standardid != None):
            self.addFilter(standardid, verbose)
            if(comment == None):
                comment = ""
                for ID in standardid:
                    comment += ("f%d" %(ID))

                
        self.client.MCPsetrate(freq);
        
        # This will handle the files so that we do not loose them. each day we will create a new csv file
        if( filename==None and writeToFile == True):
            #get folder information (based on today's date)
            now = datetime.datetime.now()
            datestr = now.strftime("%Y%m%d")
            path = self.DATA_LOCATION+datestr+".csv"
            filename = path
            
        if( writeToFile == True):
            outfile = open(filename,'a');
            dataWriter = csv.writer(outfile,delimiter=',');
            dataWriter.writerow(['# Time     Error        Bytes 1-13']);
            dataWriter.writerow(['#' + description])
            
        self.client.MCPreqstatNormal();
        print "Listening...";
        packetcount = 0;
        starttime = time.time();
        
        while((time.time()-starttime < duration)):
            
            if(faster):
                packet=self.client.fastrxpacket();
            else:
                packet=self.client.rxpacket();
                
            #add the data to list if the pointer was included
            if(data != None and packet != None):
                #data.append(self.client.packet2parsedstr(packet))
                packetParsed = self.client.packet2parsed(packet)
                packetParsed["time"] =time.time()
                data.put(packetParsed)
            if(debug == True):
                #check packet status
                MCPstatusReg = self.client.MCPrxstatus();
                messagestat=MCPstatusReg&0xC0;
                messagetype=MCPstatusReg&0x18;
                if(messagestat == 0xC0):
                    print "Message in both buffers; message type is %02x (0x00 is standard data, 0x08 is standard remote)." %messagetype
                elif(messagestat == 0x80):
                    print "Message in RXB1; message type is %02x (0x00 is standard data, 0x08 is standard remote)." %messagetype
                elif(messagestat == 0x40):
                    print "Message in RXB0; message type is %02x (0x00 is standard data, 0x08 is standard remote)." %messagetype
                elif(messagestat == 0x00):
                    print "No messages in buffers."
            #check to see if there was a packet
            if( packet != None):
                packetcount+=1;
            if (packet!=None and writeToFile == True):
                
                row = [];
                row.append("%f"%time.time());
                
                if( verbose==True):
                    #if we want to print a parsed message
                    if( parsed == True):
                        packetParsed = self.client.packet2parsed(packet)
                        sId = packetParsed.get('sID')
                        msg = "sID: %04d" %sId
                        if( packetParsed.get('eID')):
                            msg += " eID: %d" %packetParsed.get('eID')
                        msg += " rtr: %d"%packetParsed['rtr']
                        length = packetParsed['length']
                        msg += " length: %d"%length
                        msg += " data:"
                        for i in range(0,length):
                            dbidx = 'db%d'%i
                            msg +=" %03d"% packetParsed[dbidx]
                        #msg = self.client.packet2parsedstr(packet)
                        print msg
                    # if we want to print just the message as it is read off the chip
                    else:
                        print self.client.packet2str(packet)
                
                if(debug == True):
                    
                    #check overflow
                    MCPeflgReg=self.client.peek8(0x2D);
                    print"EFLG register equals: %x" %MCPeflgReg;
                    if((MCPeflgReg & 0xC0)==0xC0):
                        print "WARNING: BOTH overflow flags set. Missed a packet. Clearing and proceeding."
                    elif(MCPeflgReg & 0x80):
                        print "WARNING: RXB1 overflow flag set. A packet has been missed. Clearing and proceeding."
                    elif(MCPeflgReg & 0x40):
                        print "WARNING: RXB0 overflow flag set. A packet has been missed. Clearing and proceeding."
                    self.client.MCPbitmodify(0x2D,0xC0,0x00);
                    print"EFLG register set to: %x" % self.client.peek(0x2D);
                
                    #check for errors
                    if (self.client.peek8(0x2C) & 0x80):
                        self.client.MCPbitmodify(0x2C,0x80,0x00);
                        print "ERROR: Malformed packet recieved: " + self.client.packet2str(packet);
                        row.append(1);
                    else:
                        row.append(0);
                else:
                    row.append(0);  #since we don't check for errors if we're not in debug mode...
                            
                row.append(comment)
                #how long the sniff was for
                row.append(duration)
                #boolean that tells us if there was filtering. 0 == no filters, 1 == filters
                if(standardid != None):
                    row.append(1)
                else:
                    row.append(0)
                #write packet to file
                for byte in packet:
                    row.append("%02x"%ord(byte));
                dataWriter.writerow(row);
        if(writeToFile == True):
            outfile.close()
        print "Listened for %d seconds, captured %d packets." %(duration,packetcount);
        return packetcount
        
        
#    def filterStdSweep(self, freq, low, high, time = 5):
#        msgIDs = []
#        self.client.serInit()
#        self.client.MCPsetup()
#        for i in range(low, high+1, 6):
#            print "sniffing id: %d, %d, %d, %d, %d, %d" % (i,i+1,i+2,i+3,i+4,i+5)
#            comment= "sweepFilter: "
#            #comment = "sweepFilter_%d_%d_%d_%d_%d_%d" % (i,i+1,i+2,i+3,i+4,i+5)
#            description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d, %d, %d, %d, %d, %d" % (i,i+1,i+2,i+3,i+4,i+5)
#            count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [i, i+1, i+2, i+3, i+4, i+5])
#            if( count != 0):
#                for j in range(i,i+5):
#                    comment = "sweepFilter: "
#                    #comment = "sweepFilter: %d" % (j)
#                    description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d " % j
#                    count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [j, j, j, j])
#                    if( count != 0):
#                        msgIDs.append(j)
#        return msgIDs
    
#    def sweepRandom(self, freq, number = 5, time = 200):
#        msgIDs = []
#        ids = []
#        self.client.serInit()
#        self.client.MCPsetup()
#        for i in range(0,number+1,6):
#            idsTemp = []
#            comment = "sweepFilter: "
#            for j in range(0,6,1):
#                id = randrange(2047)
#                #comment += "_%d" % id
#                idsTemp.append(id)
#                ids.append(id)
#            print comment
#            description = "Running a sweep filer for all the possible standard IDs. This runs the following : " + comment
#            count = self.sniff(freq=freq, duration=time, description=description, comment = comment, standardid = idsTemp)
#            if( count != 0):
#                for element in idsTemp:
#                    #comment = "sweepFilter: %d" % (element)
#                    comment="sweepFilter: "
#                    description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d " % element
#                    count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [element, element, element])
#                    if( count != 0):
#                        msgIDs.append(j)
#        return msgIDs, ids
    
    def sniffTest(self, freq):
        """
        This method will preform a test to see if we can sniff corretly formed packets from the CAN bus.
        
        @type freq: number
        @param freq: frequency of the CAN bus
        """
        rate = freq;
        
        print "Calling MCPsetrate for %i." %rate;
        self.client.MCPsetrate(rate);
        self.client.MCPreqstatNormal();
        
        print "Mode: %s" % self.client.MCPcanstatstr();
        print "CNF1: %02x" %self.client.peek8(0x2a);
        print "CNF2: %02x" %self.client.peek8(0x29);
        print "CNF3: %02x\n" %self.client.peek8(0x28);
        
        while(1):
            packet=self.client.rxpacket();
            
            if packet!=None:                
                if (self.client.peek8(0x2C) & 0x80):
                    self.client.MCPbitmodify(0x2C,0x80,0x00);
                    print "malformed packet recieved: "+ self.client.packet2str(packet);
                else:
                    print "properly formatted packet recieved" + self.client.packet2str(packet);
   
    
    def freqtest(self,freq):
        """
        This method will test the frequency provided to see if it is the correct frequency for this CAN bus.
        
        @type freq: Number
        @param freq: The frequency to listen to the CAN bus.
        
        """
        self.client.MCPsetup();

        self.client.MCPsetrate(freq);
        self.client.MCPreqstatListenOnly();
    
        print "CAN Freq Test: %3d kHz" %freq;
    
        x = 0;
        errors = 0;
    
        starttime = time.time();
        while((time.time()-starttime < args.time)):
            packet=self.client.rxpacket();
            if packet!=None:
                x+=1;
                
                if (self.client.peek8(0x2C) & 0x80):
                    print "malformed packet recieved"
                    errors+=1;
                    self.client.MCPbitmodify(0x2C,0x80,0x00);
                else:         
                    print self.client.packet2str(packet);
    
        print "Results for %3.1d kHz: recieved %3d packets, registered %3d RX errors." %(freq, x, errors);
    

    def isniff(self,freq):
        """ An intelligent sniffer, decodes message format """
        """ More features to be added soon """
        
        self.client.MCPsetrate(freq);
        self.client.MCPreqstatListenOnly();
        while 1:
            packet=self.client.rxpacket();
            if packet!=None:
                plist=[];
                for byte in packet:
                    plist.append(byte);
                arbid=plist[0:2];
                eid=plist[2:4];
                dlc=plist[4:5];
                data=plist[5:13];         
                print "\nArbID: " + self.client.packet2str(arbid);
                print "EID: " + self.client.packet2str(eid);
                print "DLC: " + self.client.packet2str(dlc);
                print "Data: " + self.client.packet2str(data);

    def test(self):
        """ This will perform a test on the GOODTHOPTER10. Diagnostic messages will be printed
        out to the terminal
        """
        comm.reset();
        print "Just reset..."
        print "EFLG register:  %02x" % self.client.peek8(0x2d);
        print "Tx Errors:  %3d" % self.client.peek8(0x1c);
        print "Rx Errors:  %3d" % self.client.peek8(0x1d);
        print "CANINTF: %02x"  %self.client.peek8(0x2C);
        self.client.MCPreqstatConfiguration();
        self.client.poke8(0x60,0x66);
        self.client.MCPsetrate(500);
        self.client.MCPreqstatNormal();
        print "In normal mode now"
        print "EFLG register:  %02x" % self.client.peek8(0x2d);
        print "Tx Errors:  %3d" % self.client.peek8(0x1c);
        print "Rx Errors:  %3d" % self.client.peek8(0x1d);
        print "CANINTF: %02x"  %self.client.peek8(0x2C);
        print "Waiting on packets.";
        checkcount = 0;
        packet=None;
        while(1):
            packet=self.client.rxpacket();
            if packet!=None:
                print "Message recieved: %s" % self.client.packet2str(packet);
            else:
                checkcount=checkcount+1;
                if (checkcount%30==0):
                    print "EFLG register:  %02x" % self.client.peek8(0x2d);
                    print "Tx Errors:  %3d" % self.client.peek8(0x1c);
                    print "Rx Errors:  %3d" % self.client.peek8(0x1d);
                    print "CANINTF: %02x"  %self.client.peek8(0x2C);

    
    
    
    def addFilter(self,standardid, verbose= True):
        """ This method will configure filters on the board. Filters are positive filters meaning that they will only 
        store messages that match the ids provided in the list of standardid. Since there are 2 buffers and due to the configuration
        of how the filtering works (see MCP2515 documentation), at least 3 filters must be set to guarentee you do not get any
        unwanted messages. However even with only 1 filter set you should get all messages from that ID but the other buffer will store 
        any additional messages.
        @type standardid: list of integers
        @param standardid: List of standard ids that need to be set. There can be at most 6 filters set.
        @type verbose: Boolean
        @param verbose: If true it will print out messages and diagnostics to terminal.
        
        @rtype: None
        @return: This method does not return anything
        @todo: rename setFilters
        """
       
        ### ON-CHIP FILTERING
        if(standardid != None):
            self.client.MCPreqstatConfiguration();  
            self.client.poke8(0x60,0x26); # set RXB0 CTRL register to ONLY accept STANDARD messages with filter match (RXM1=0, RMX0=1, BUKT=1)
            self.client.poke8(0x20,0xFF); #set buffer 0 mask 1 (SID 10:3) to FF
            self.client.poke8(0x21,0xE0); #set buffer 0 mask 2 bits 7:5 (SID 2:0) to 1s
            if(len(standardid)>2):
               self.client.poke8(0x70,0x20); # set RXB1 CTRL register to ONLY accept STANDARD messages with filter match (RXM1=0, RMX0=1)
               self.client.poke8(0x24,0xFF); #set buffer 1 mask 1 (SID 10:3) to FF
               self.client.poke8(0x25,0xE0); #set buffer 1 mask 2 bits 7:5 (SID 2:0) to 1s 
            
            for filter,ID in enumerate(standardid):
        
               if (filter==0):
                RXFSIDH = 0x00;
                RXFSIDL = 0x01;
               elif (filter==1):
                RXFSIDH = 0x04;
                RXFSIDL = 0x05;
               elif (filter==2):
                RXFSIDH = 0x08;
                RXFSIDL = 0x09;
               elif (filter==3):
                RXFSIDH = 0x10;
                RXFSIDL = 0x11;
               elif (filter==4):
                RXFSIDH = 0x14;
                RXFSIDL = 0x15;
               else:
                RXFSIDH = 0x18;
                RXFSIDL = 0x19;
        
               #### split SID into different regs
               SIDlow = (ID & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
               SIDhigh = (ID >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
               
               #write SID to regs 
               self.client.poke8(RXFSIDH,SIDhigh);
               self.client.poke8(RXFSIDL, SIDlow);
                       
               if (verbose == True):
                   print "Filtering for SID %d (0x%02xh) with filter #%d"%(ID, ID, filter);
               
        self.client.MCPreqstatNormal();
    
    def filterForPacket(self, standardid, DB0, DB1, verbose= True):
        """ 
        This method will configure filters on the board to listen for a specific packet originating 
        from standardid with data bytes 0 and 1. It will configure all six filters, so you will not receive any other packets.
        
        @type standardid: integer
        @param standardid: standardID to listen for
        @type DB0: integer
        @param standardid: DB0 contents to filter for
        @type DB1: integer
        @param standardid: DB1 contents to filter for
        @type verbose: Boolean
        @param verbose: If true it will print out messages and diagnostics to terminal.
        
        @rtype: None
        @return: This method does not return anything
        """
        
        ### ON-CHIP FILTERING
       
        self.client.MCPreqstatConfiguration();  
        
        # SID filtering: set CTRL registers to only accept standard messages
        self.client.poke8(0x60,0x06); # set RXB0 CTRL register to ONLY accept STANDARD messages with filter match (RXM1=0, RXM=1, BUKT=1)
        self.client.poke8(0x70,0x00); # set RXB1 CTRL register to ONLY accept STANDARD messages with filter match (RXM1=0, RXM0=1)

        # Mask buffer 0 to match SID, DB0, DB1
        self.client.poke8(0x20,0xFF); #set buffer 0 mask 1 (SID 10:3) to FF
        self.client.poke8(0x21,0xE0); #set buffer 0 mask 2 bits 7:5 (SID 2:0) to 1s
        self.client.poke8(0x22,0xFF); #set buffer 0 mask 3 (DB0) to FF 
        self.client.poke8(0x23,0xFF); #set buffer 0 mask 4 (DB0) to FF

        # Mask buffer 1 to match SID, DB0, DB1
        self.client.poke8(0x24,0xFF); #set buffer 1 mask 1 (SID 10:3) to FF
        self.client.poke8(0x25,0xE0); #set buffer 1 mask 2 bits 7:5 (SID 2:0) to 1s
        self.client.poke8(0x26,0xFF); #set buffer 1 mask 3 (DB0) to FF
        self.client.poke8(0x27,0xFF); #set buffer 1 mask 4 (DB1) to FF
        
        # Split SID into high and low bytes
        SIDlow = (standardid & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (standardid >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0

            
        for filter in range(0,5):
            if (filter==0):
                RXFSIDH = 0x00;
                RXFSIDL = 0x01;
                RXFDB0 = 0x02;
                RXFDB1 = 0x03;
            elif (filter==1):
                RXFSIDH = 0x04;
                RXFSIDL = 0x05;
                RXFDB0 = 0x06;
                RXFDB1 = 0x07;
            elif (filter==2):
                RXFSIDH = 0x08;
                RXFSIDL = 0x09;
                RXFDB0 = 0x0A;
                RXFDB1 = 0x0B;
            elif (filter==3):
                RXFSIDH = 0x10;
                RXFSIDL = 0x11;
                RXFDB0 = 0x12;
                RXFDB1 = 0x13;
            elif (filter==4):
                RXFSIDH = 0x14;
                RXFSIDL = 0x15;
                RXFDB0 = 0x16;
                RXFDB1 = 0x17;
            else:
                RXFSIDH = 0x18;
                RXFSIDL = 0x19;
                RXFDB0 = 0x1A;
                RXFDB1 = 0x1B;

            self.client.poke8(RXFSIDH, SIDhigh);
            self.client.poke8(RXFSIDL, SIDlow);
            self.client.poke8(RXFDB0, DB0);
            self.client.poke8(RXFDB1, DB1);
                
            if (verbose == True):
                print "Filtering for SID %d DB0 %d DB1 %d with filter #%d"%(standardid, DB0, DB1, filter);
        
        self.client.MCPreqstatNormal();   
    
    def multiPacketTest(self):
        
        self.reset();
        self.client.MCPsetrate(500);
        self.client.MCPreqstatNormal();
        
        packet0 = [0x00, 0x00, 0x00,0x00, # pad out EID regs
                   0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                   # lower nibble is DLC                   
                   0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        
        packet1 = [0x00, 0x20, 0x00,0x00, # pad out EID regs
                   0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                   # lower nibble is DLC                   
                   0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
        packet2 = [0x00, 0x40, 0x00,0x00, # pad out EID regs
                   0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                   # lower nibble is DLC                   
                   0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
            
        comm.multiPacketSpit(packet0=packet0, packet1=packet1, packet2=packet2)
        
        comm.multiPacketSpit(packet0rts=True, packet1rts=True, packet2rts=True)
        comm.multiPacketSpit(packet2rts=True)
        comm.multiPacketSpit(packet1rts=True)
        comm.multiPacketSpit(packet0rts=True)
        


    def multiPacketSpit(self, packet0 = None, packet1 = None, packet2 = None, packet0rts = False, packet1rts = False, packet2rts = False):
        """ 
            This method writes packets to the chip's TX buffers and/or sends the contents of the buffers onto the bus.
            
            @type packet0: list of integer
            @param packet0: A list of 13 integers of the format [SIDhigh SIDlow 0 0 DLC DB0-7] to be loaded into TXBF0
            
            @type packet1: list of integer
            @param packet1: A list of 13 integers of the format [SIDhigh SIDlow 0 0 DLC DB0-7] to be loaded into TXBF1
            
            @type packet2: list of integer
            @param packet2: A list of 13 integers of the format [SIDhigh SIDlow 0 0 DLC DB0-7] to be loaded into TXBF2
            
            @type packet0rts: Boolean
            @param packet0rts: If true the message in TX buffer 0 will be sent
            
            @type packet2rts: Boolean
            @param packet0rts: If true the message in TX buffer 1 will be sent
            
            @type packet2rts: Boolean
            @param packet0rts: If true the message in TX buffer 2 will be sent
            
        """
        
        if(packet0 != None):
            self.client.writetxbuffer(packet0,0)
        #   print("trying to write TX buffer 0");
        #  for db in packet0:
        #      print" %d" %db
        if (packet1 != None):
            self.client.writetxbuffer(packet1,1)
            # print("trying to write TX buffer 1");
                # for db in packet0:
                    #     print" %d" %db
        if (packet2 != None):
            self.client.writetxbuffer(packet2,2)
            # print("trying to write TX buffer 2");
                #  for db in packet0:
                    #   print" %d" %db
            
        #  if(packet0rts):
            #    print("trying to send TX buffer 0")
        #if(packet1rts):
            #    print("trying to send TX buffer 1")
        #if(packet2rts):
            #    print("trying to send TX buffer 2")

        self.client.MCPrts(TXB0=packet0rts, TXB1=packet1rts, TXB2=packet2rts)
 
        
    def spitSetup(self,freq):
        """ 
        This method sets up the chip for transmitting messages, but does not transmit anything itself.
        """
        self.reset();
        self.client.MCPsetrate(freq);
        self.client.MCPreqstatNormal();
        
    
    def spitSingle(self,freq, standardid, repeat,writes, period = None, debug = False, packet = None):
        """ 
        This method will spit a single message onto the bus. If there is no packet information provided then the 
        message will be sent as a remote transmission request (RTR). The packet length is assumed to be 8 bytes The message can be repeated given number of times with
        a gap of period (milliseconds) between each message. This will continue for the the number of times specified in the writes input.
        This method will setup the bus and call the spit method, L{spit}. This method includes a bus reset and initialization.
        
        @type freq: number
        @param freq: The frequency of the bus
        
        @type standardid: list of integer
        @param standardid: This is a single length list with one integer elment that corresponds to the standard id you wish to write to
        
        @type repeat: Boolean
        @param repeat: If true the message will be repeatedly injected. if not the message will only be injected 1 time
        
        @type writes: Integer
        @param writes: Number of writes of the packet
        
        @type period: Integer
        @param period: Time delay between injections of the packet in Milliseconds
        
        @type debug: Boolean
        @param debug: When true debug status messages will be printed to the terminal
        
        @type packet: List
        @param packet: Contains the data bytes for the packet which is assumed to be of length 8. Each byte is stored as
                       an integer and can range from 0 to 255 (8 bits). If packet == None then an RTR will be sent on the given
                       standard id.
        
        """
        self.spitSetup(freq);
        spit(self,freq, standardid, repeat,writes,  period, debug , packet)

    def spit(self,freq, standardid, repeat,writes, period = None, debug = False, packet = None):
        """ 
        This method will spit a single message onto the bus. If there is no packet information provided then the 
        message will be sent as a remote transmission request (RTR). The packet length is assumed to be 8 bytes The message can be repeated a given number of times with
        a gap of period (milliseconds) between each message. This will continue for the the number of times specified in the writes input.
        This method does not include bus setup, it must be done before the method call.
        
        
        @type freq: number
        @param freq: The frequency of the bus
        
        @type standardid: list of integer
        @param standardid: This is a single length list with one integer elment that corresponds to the standard id you wish to write to
        
        @type repeat: Boolean
        @param repeat: If true the message will be repeatedly injected. if not the message will only be injected 1 time
        
        @type writes: Integer
        @param writes: Number of writes of the packet
        
        @type period: Integer
        @param period: Time delay between injections of the packet in Milliseconds
        
        @type debug: Boolean
        @param debug: When true debug status messages will be printed to the terminal
        
        @type packet: List
        @param packet: Contains the data bytes for the packet which is assumed to be of length 8. Each byte is stored as
                       an integer and can range from 0 to 255 (8 bits). If packet == None then an RTR will be sent on the given
                       standard id.
        
        """

        #### split SID into different regs
        SIDlow = (standardid[0] & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (standardid[0] >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        
        if(packet == None):
            
            # if no packet, RTR for inputted arbID
            # so packet to transmit is SID + padding out EID registers + RTR request (set bit 6, clear lower nibble of DLC register)
            packet = [SIDhigh, SIDlow, 0x00,0x00,0x40] 
        
        
        else:

            # if we do have a packet, packet is SID + padding out EID registers + DLC of 8 + packet
            #
            """@todo: allow for variable-length packets"""
            #    TODO: allow for variable-length packets
            #
            packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
            
        
        if(debug):
            if self.client.MCPcanstat()>>5!=0:
                print "Warning: currently in %s mode. NOT in normal mode! May not transmit.\n" %self.client.MCPcanstatstr();
            print "\nInitial state:"
            print "Tx Errors:  %3d" % self.client.peek8(0x1c);
            print "Rx Errors:  %3d" % self.client.peek8(0x1d);
            print "Error Flags:  %02x\n" % self.client.peek8(0x2d);
            print "TXB0CTRL: %02x" %self.client.peek8(0x30);
            print "CANINTF: %02x\n"  %self.client.peek8(0x2C);
            print "\n\nATTEMPTING TRANSMISSION!!!"
                
        print "Transmitting packet: "
        #print self.client.packet2str(packet)
                
        self.client.txpacket(packet);
            
        if repeat:
            """@todo: the repeat variable is no longer needed and can be removed """
            print "\nNow looping on transmit. "
            if period != None:
                for i in range(0,writes):
                    self.client.MCPrts(TXB0=True);
                    #tic = time.time()
                    time.sleep(period/1000) # pause for period ms before sending again
                    #print time.time()-tic
                #starttime = time.time();
                #while((time.time()-starttime < duration)):
                #    self.client.MCPrts(TXB0=True);
                #    print "MSG printed"
            else:
                for i in range(0,writes): 
                    self.client.MCPrts(TXB0=True);
        print "messages injected"
        
        # MORE DEBUGGING        
        if(debug): 
            checkcount = 0;
            TXB0CTRL = self.client.peek8(0x30);
        
            print "Tx Errors:  %3d" % self.client.peek8(0x1c);
            print "Rx Errors:  %3d" % self.client.peek8(0x1d);
            print "EFLG register:  %02x" % self.client.peek8(0x2d);
            print "TXB0CTRL: %02x" %TXB0CTRL;
            print "CANINTF: %02x\n"  %self.client.peek8(0x2C);
        
            while(TXB0CTRL | 0x00 != 0x00):
                checkcount+=1;
                TXB0CTRL = self.client.peek8(0x30);
                if (checkcount %30 ==0):
                    print "Tx Errors:  %3d" % self.client.peek8(0x1c);
                    print "Rx Errors:  %3d" % self.client.peek8(0x1d);
                    print "EFLG register:  %02x" % self.client.peek8(0x2d);
                    print "TXB0CTRL: %02x" %TXB0CTRL;
                    print "CANINTF: %02x\n"  %self.client.peek8(0x2C);


    def setRate(self,freq):
        """ 
        This method will reset the frequency that the MCP2515 expects the CAN bus to be on.
        
        @type freq: Number
        @param freq: Frequency of the CAN bus
        """
        self.client.MCPsetrate(freq);

        

    # This will write the data provided in the packets which is expected to be a list of lists
    # of the following form:
    # for a given row = packets[i]
    # row[0] time delay relative to the last packet. if 0 or empty there will be no delay
    # row[1] = Standard ID (integer)
    # row[2] = Data Length (0-8) (if it is zero we assume an Remote Transmit Request)
    # row[3] = Data Byte 0
    # row[4] = Data Byte 1
    #    .... up to Data Byte 8 ( THIS ASSUMES A PACKET OF LENGTH 8!!!
    def writeData(self,packets,freq):
        """
        This method will write a list of packets to the bus at the given frequency. This method assumes a packet 
        length of 8 for all packets as well as a standard id.
        
        @type packets: List of Lists
        @param packets: The list of packets to be injected into the bus. Each element of packets is a list that is 
        a packet to be injected onto the bus. These packets are assumed to be in the following format::
                 row[0] time delay relative to the last packet. if 0 or empty there will be no delay
                 row[1] = Standard ID (integer)
                 row[2] = Data Length (0-8) (if it is zero we assume an Remote Transmit Request)
                 row[3] = Data Byte 0
                 row[4] = Data Byte 1
                 ...
                 row[10] = Data Byte 7
        
        @type freq: number
        @param freq: Frequency of the CAN bus
        
        """
        self.client.serInit()
        self.spitSetup(freq)
        for row in packets:
            if( row[0] != 0 and row[0] != ""):
                time.sleep(row[0])
            sID = row[1]
            #### split SID into different regs
            SIDlow = (sID & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
            SIDhigh = (sID >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
            packet = [SIDhigh,SIDlow,0x00,0x00,0x08]
            #dlc = row[2]
            dlc = 8
            for i in range(3,dlc+3):
                packet.append(row[i])
            print packet
            self.client.txpacket(packet)


                
        
        
        

if __name__ == "__main__":  

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''\
    
        Run commands on the MCP2515. Valid commands are:
        
            info 
            test
            peek 0x(start) [0x(stop)]
            reset
            
            sniff 
            freqtest
            snifftest
            spit
        ''')
        
    
    parser.add_argument('verb', choices=['info', 'test','peek', 'reset', 'sniff', 'freqtest','snifftest', 'spit', 'packet', 'multipacket']);
    parser.add_argument('-f', '--freq', type=int, default=500, help='The desired frequency (kHz)', choices=[100, 125, 250, 500, 1000]);
    parser.add_argument('-t','--time', type=int, default=15, help='The duration to run the command (s)');
    parser.add_argument('-o', '--output', default=None,help='Output file');
    parser.add_argument("-d", "--description", help='Description of experiment (included in the output file)', default="");
    parser.add_argument('-v',"--verbose",action='store_false',help='-v will stop packet output to terminal', default=True);
    parser.add_argument('-c','--comment', help='Comment attached to ech packet uploaded',default=None);
    parser.add_argument('-b', '--debug', action='store_true', help='-b will turn on debug mode, printing packet status', default=False);
    parser.add_argument('-a', '--standardid', type=int, action='append', help='Standard ID to accept with filter 0 [1, 2, 3, 4, 5]', default=None);
    parser.add_argument('-x', '--faster', action='store_true', help='-x will use "fast packet recieve," which may duplicate packets and/or cause other weird behavior.', default=False);
    parser.add_argument('-r', '--repeat', action='store_true', help='-r with "spit" will continuously send the inputted packet. This will put the GoodTHOPTHER into an infinite loop.', default=False);
    parser.add_argument('-db0', '--databyte0', type=int, default = None, help='-db0 to filter for a specfic data byte');
    parser.add_argument('-db1', '--databyte1', type=int, default = None, help='-db0 to filter for a specfic data byte');

    
    
    args = parser.parse_args();
    freq = args.freq
    duration = args.time
    filename = args.output
    description = args.description
    verbose = args.verbose
    comments = args.comment
    debug = args.debug
    standardid = args.standardid
    faster=args.faster
    repeat = args.repeat
    db0 = args.databyte0
    db1 = args.databyte1

    comm = GoodFETMCPCANCommunication("./");
    
    if(args.verb=="packet"):
        comm.filterForPacket(standardid=standardid[0], DB0=db0, DB1=db1, verbose= True)
    if(args.verb=="multipacket"):
        comm.multiPacketTest();
    
    ##########################
    #   INFO
    ##########################
    #
    # Prints MCP state info
    #
    if(args.verb=="info"):
        comm.printInfo()
        
           
    ##########################
    #   RESET
    ##########################
    #
    #
            
    if(args.verb=="reset"):
        comm.reset()
        
    ##########################
    #   SNIFF
    ##########################
    #
    #   runs in ListenOnly mode
    #   utility function to pull info off the car's CAN bus
    #
    
    if(args.verb=="sniff"):
        comm.sniff(freq=freq,duration=duration,description=description,verbose=verbose,comment=comments,filename=filename, standardid=standardid, debug=debug, faster=faster, db0=db0, db1=db1)    
                    
    ##########################
    #   SNIFF TEST
    ##########################
    #
    #   runs in NORMAL mode
    #   intended for NETWORKED MCP chips to verify proper operation
    #
       
    if(args.verb=="snifftest"):
        comm.sniffTest(freq=freq)
        
        
    ##########################
    #   FREQ TEST
    ##########################
    #
    #   runs in LISTEN ONLY mode
    #   tests bus for desired frequency --> sniffs bus for specified length of time and reports
    #   if packets were properly formatted
    #
    #
    
    if(args.verb=="freqtest"):
        comm.freqtest(freq=freq)



    ##########################
    #   iSniff
    ##########################
    #
    #    """ An intelligent sniffer, decodes message format """
    #    """ More features to be added soon """
    if(args.verb=="isniff"):
        comm.isniff(freq=freq)
                
                
    ##########################
    #   MCP TEST
    ##########################
    #
    #   Runs in LOOPBACK mode
    #   self-check diagnostic
    #   wasn't working before due to improperly formatted packet
    #
    #   ...add automatic packet check rather than making user verify successful packet
    if(args.verb=="test"):
        comm.test()
        
    if(args.verb=="peek"):
        start=0x0000;
        if(len(sys.argv)>2):
            start=int(sys.argv[2],16);
        stop=start;
        if(len(sys.argv)>3):
            stop=int(sys.argv[3],16);
        print "Peeking from %04x to %04x." % (start,stop);
        while start<=stop:
            print "%04x: %02x" % (start,client.peek8(start));
            start=start+1;
            
    ##########################
    #   SPIT
    ##########################
    #
    #   Basic packet transmission
    #   runs in NORMAL MODE!
    # 
    #   checking TX error flags--> currently throwing error flags on every
    #   transmission (travis thinks this is because we're sniffing in listen-only
    #   and thus not generating an ack bit on the recieving board)
    if(args.verb=="spit"):
        comm.spitSingle(freq=freq, standardid=standardid,duration=duration, repeat=repeat, debug=debug)


    
    
    
    
        
        
    
    
    
    

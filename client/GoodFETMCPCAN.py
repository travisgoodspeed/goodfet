#!/usr/bin/env python
# GoodFET MCP2515 CAN Bus Client
# 
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
# WORKING COPY
# Currently being updated by Siege Technology's ENGS89 team
# Primary contact: Theodore Sumers <ted.sumers at gmail.com>
# ADDED FUNCTIONALITY:
#   10.4/41.6/83.3 kHz sniffing
#   setbitrate
#   debugs on TX and RX packet
#   int-based state change reqs for preserving state
#

# The MCP2515 is a CAN Bus to SPI adapter from Microchip Technology,
# as used in the Goodthopter series of boards.  It requires a separate
# chip for voltage level conversion, such as the MCP2551.

import sys, time, string, cStringIO, struct, glob, os;

from GoodFETSPI import GoodFETSPI;

class GoodFETMCPCAN(GoodFETSPI):
    """This class uses the regular SPI app to implement a CAN Bus
    adapter on the Goodthopter10 hardware."""
    MCPMODES=["Normal","Sleep","Loopback","Listen-only","Configuration",
              "UNKNOWN","UNKNOWN","PowerUp"];
    
    def MCPsetup(self):
        """Sets up the ports."""
        self.SPIsetup();
        self.MCPreset(); #Reset the chip.
        # We're going to set some registers, so we must be in config
        # mode.
        self.MCPreqstatConfiguration();
        
        # If we don't enable promiscous mode, we'll miss a lot of
        # packets.  It can be manually disabled later.
        #self.poke8(0x60,0xFF); #TODO Does this have any unpleasant side effects?
        self.poke8(0x60,0x66); #Wanted FF, but some bits are reserved.

    #Array of supported rates.
    MCPrates=[10.4, 41.6, 83.3, 100, 125, 250, 500, 1000];
    
    def MCPreset(self):
        """Reset the MCP2515 chip."""
        self.SPItrans([0xC0]);
    
      
    ################    SETTING BAUD RATE   ################
    
    
    def MCPsetrate(self,rate=125):
        """Sets the data rate in kHz."""
        # Now we need to set the timing registers.  See chapter 5 of
        # the MCP2515 datasheet to get some clue as to how this
        # arithmetic of this works.

        
        #STORE the prior status
        oldstatus=self.MCPcanstatint();
        print "Setting rate of %i kHz." % rate;
        #print "Current state is %s." % self.MCPcanstatstr();
        self.MCPreqstatConfiguration();
        # print "Switched to %s state." % self.MCPcanstatstr();
        
        
        if rate>41 and rate<42:
            # NOT CHECKED: based on kvaser website.
            # Sets baud rate for 41.6 kbps
            CNF1=0x8e;
            CNF2=0xa3;
            CNF3=0x05;
        elif rate>10 and rate<11:
            # NOT CHECKED: based on kvaser website.
            # Sets baud rate for 10.4 kbps
            CNF1=0xbb;
            CNF2=0xa3;
            CNF3=0x05;  
        elif rate==125:
            #125 kHz, 16 TQ, not quite as worked out above.
            CNF1=0x04;
            CNF2=0xB8;
            CNF3=0x05;
        elif rate==100:
            #100 kHz, 20 TQ
            CNF1=0x04;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate>83 and rate<83.5:
            #83+1/3 kHz, 8 TQ
            # 0.04% error from 83.30
            CNF1=0x0E;
            CNF2=0x90;
            CNF3=0x02;
        elif rate==250:
            #256 kHz, 20 TQ
            CNF1=0x01;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate==500:
            #500 kHz, 20 TQ
            CNF1=0x00;
            CNF2=0xBA;
            CNF3=0x07;
        elif rate==1000:
            #1,000 kHz, 10 TQ
            CNF1=0x00;
            CNF2=0xA0;
            CNF3=0x02;
            print "WARNING: Because of chip errata, this probably won't work."
        else:
            print "Given unsupported rate of %i kHz." % rate;
            print "Defaulting to 125kHz.";
            CNF1=0x04;
            CNF2=0xB8;
            CNF3=0x05;
        self.poke8(0x2a,CNF1);
        self.poke8(0x29,CNF2);
        self.poke8(0x28,CNF3);

        # and now return to whatever state we were in before
        self.MCPreqstat(oldstatus);
        #print "Reverted to %s." % self.MCPcanstatstr();

    
    #################   STATE MANAGEMENT   ##################

    def MCPcanstat(self):
        """Get the CAN Status."""
        return self.peek8(0x0E);
    def MCPcanstatstr(self):
        """Read the present status as a string."""
        opmod=self.MCPcanstatint();
        return self.MCPMODES[opmod];
    def MCPcanstatint(self):
        """Read present status as an int."""
        return self.MCPcanstat()>>5;

            
    def MCPreqstat(self, state):
        """Set the CAN state."""
        if state==0:
            self.MCPreqstatNormal();
        elif state==1:
            self.MCPreqstatSleep();
        elif state==2:
            self.MCPreqstatLoopback();
        elif state==3:
            self.MCPreqstatListenOnly();
        elif state==4:
            self.MCPreqstatConfiguration();
        else:
            print "Invalid state entered; defaulting to Listen-Only"
            self.MCPreqstatListenOnly();
    def MCPreqstatNormal(self):
        """Set the CAN state."""
        state=0x0;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatSleep(self):
        """Set the CAN state."""
        state=0x1;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatLoopback(self):
        """Set the CAN state."""
        state=0x2;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatListenOnly(self):
        """Set the CAN state."""
        state=0x3;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    def MCPreqstatConfiguration(self):
        """Set the CAN state."""
        state=0x4;
        self.MCPbitmodify(0x0F,0xE0,(state<<5));
    
    ####################     RX MANAGEMENT     #####################
    
    def MCPrxstatus(self):
        """Reads the RX Status by the SPI verb of the same name."""
        data=self.SPItrans([0xB0,0x00]);
        return ord(data[1]);

    def MCPreadstatus(self):
        """Reads the Read Status by the SPI verb of the same name."""
        #See page 69 of the datasheet for the flag names.
        data=self.SPItrans([0xA0,0x00]);
        return ord(data[1]);
            
    def readrxbuffer(self,packbuf=0):
        """Reads the RX buffer.  Might have old data."""
        data=self.SPItrans([0x90|(packbuf<<2),
                            0x00,0x00, #SID
                            0x00,0x00, #EID
                            0x00,      #DLC
                            0x00, 0x00, 0x00, 0x00,
                            0x00, 0x00, 0x00, 0x00
                            ]);
        
        return data[1:len(data)];
    
    def fastrxpacket(self):
        return self.readrxbuffer(0);
    
    def rxpacket(self):
        """Reads the next incoming packet from either buffer.
            Returns None immediately if no packet is waiting."""
        status=self.MCPrxstatus()&0xC0;
        if status&0x40:
            #Buffer 0 has higher priority.
            return self.readrxbuffer(0);
        elif status&0x80:
            #Buffer 1 has lower priority.
            return self.readrxbuffer(1);
        else:
            return None;

    #################      TX MANAGEMENT    ##################
            
    def MCPrts(self,TXB0=False,TXB1=False,TXB2=False):
        """Requests to send one of the transmit buffers."""
        flags=0;
        if TXB0: flags=flags|1;
        if TXB1: flags=flags|2;
        if TXB2: flags=flags|4;
        
        if flags==0:
            print "Warning: Requesting to send no buffer.";
        self.SPItrans([0x80|flags]);
    
    def writetxbuffer(self,packet,packbuf=0):
        """Writes the transmit buffer."""
        
        self.SPItrans([0x40|(packbuf<<1)]+packet);

   
    def txpacket(self,packet):
        """Transmits a packet through one of the outbound buffers.
        As usual, the packet should begin with SIDH.
        For now, only TXB0 is supported."""

        self.writetxbuffer(packet,0);
        self.MCPrts(TXB0=True);

                
    ###############   UTILITY FUNCTIONS  #################
     
    def simpleParse(self,packet):
        """ 
        This will print a simple parsing of the data with the standard Id and the extended id parsed.
        """
        dataPt = ord(packet[0]);
        dataPt2 = ord(packet[1]);
        # check if we have a standard frame, the msb of the second
        # nibble will be 1. otherwise it is an extended rame
        stdCheck = dataPt2 & 0x0f
        if( stdCheck == 16 ):
            #arb id is first byte + 3 msb of the 2nd byte
            dataPt = dataPt<<3 | dataPt2>>5
            print "Standard Packet \n Arb ID: "+("%d"%dataPt)
        else:
            #arb id is first byte + 3 msb + 2 lsb of 2nd byte +
            # 3rd byte + 4th byte
            dataPt = dataPt<<3 | dataPt2>>5
            dataPt = dataPt<<2 | (dataPt2 & 0x03)
            dataPt = dataPt<<8 | ord(packet[2])
            dataPt = dataPt<<8 | ord(packet[3])
            print "Extended Data Frame \n Arb ID: "+("%d"%dataPt)
        
        #find the dataLength
        dataPt5 = packet[4]
        dataLength = dataPt5 & 0x0e
        #print "Data Length: "+("%d"%dataLength)
        # Print the data packet
        #print "Data:"
        # Temporary, until correct packets are read
        if( dataLength > 8 ):
            dataLength = 8
        toprint = self.pcket2str(packet[5:12])
        print toprint
        # For reading correct packets
       # if (dataLength > 8 ):
        #    print "Acceptable Length Exceeded"
            # Data length value should never exceed 8
       # else:
       # toprint =  self.pcket2str(packet[5:(5+dataLength)])
       # print toprint

            
    def packet2str(self,packet):
        """Converts a packet from the internal format to a string."""
        toprint="";
        for bar in packet:
            toprint=toprint+("%02x "%ord(bar))
        return toprint;
    
    
    
    def packet2parsed(self,data):
        """
        This method will parse the packet that was received via L{rxpacket}.
        
        @type data: List
        @param data: data packet read off of the MCP2515 from the CAN bus. format will be
                     14 bytes where each element is a character whose unicode integer value corresponds
                     to the hex value of the byte (use the ord() method).
        
        @rtype: Dictionary
        @return: Dictionary of the packet parsed into various components. The key values will be as follows
                     
                     1. ide : 1 if the message is an extended frame. 0 otherwise
                     2. eID : extended ID. Not included if not an extended frame
                     3. rtr : 1 if the message is a remote transmission request (RTR)
                     4. sID : Standard ID. 
                     5. length: packet length (between 0 and 8)
                     6. db0 : Data byte 0 (not included if RTR message)
                         
                         ---
                     7. db7 : Data byte 7 (not included if RTR message)
        """
        dp1 = ord(data[0])
        dp2 = ord(data[1])
        dp5 = ord(data[4])
        
        packet = {}
        #get the ide bit. allows us to check to see if we have an extended
        #frame
        packet['ide'] = (dp2 & 0x0f)>>3
        #we have an extended frame
        if( packet['ide'] != 0):
            #get lower nibble, last 2 bits
            eId = dp2 & 0x03
            eId = eId<<8 | ord(data[2])
            eId = eId<<8 | ord(data[3])
            rtr = dp5>>6 & 0x01
            packet['eID'] = " eID: %06d" %(eId)
            packet['rtr'] = " rtr: %d" % (rtr)
    
        else:
            packet['rtr'] = dp2>>4 & 0x01
            
        
        # Create the standard ID. from the message
        packet['sID'] = dp1<<3 | dp2>>5
        packet['length'] = dp5 & 0x0f
        
        #generate the data section
        for i in range(0,packet['length']):
            idx = 5 + i
            dbidx = 'db%d'%i
            packet[dbidx] = ord(data[idx])
        return packet
    
    def packet2parsedstr(self,data):
        """
        This will return a string that is the parsed CAN message. The bytes will be parsed
        for the standard ID, extended ID (if one is present), rtr, length and databytes (if present).
        The message will be placed into a string as decimal integers not hex values. This method 
        calls L{packet2parsed} to do the packet parsing.
        
        @type data: List
        @param data: Data packet as returned by the L{rxpacket}
        @rtype: String
        @return: String that shows the data message in decimal format, parsed.
        """
        packet = self.packet2parsed(data)
        msg = "sID: %04d" %packet['sId']
        if( packetParsed.get('eID')):
            msg += " eID: %d" %packetParsed.get('eID')
        msg += " rtr: %d"%packetParsed['rtr']
        length = packetParsed['length']
        msg += " length: %d"%length
        msg += " data:"
        for i in range(0,length):
            dbidx = 'db%d'%i
            msg +=" %03d"% ord(packetParsed[dbidx])  # could change this to HEX
        #msg = self.client.packet2parsedstr(packet)
        return msg
        
        
    def peek8(self,adr):
        """Read a byte from the given address.  Untested."""
        data=self.SPItrans([0x03,adr&0xFF,00]);
        return ord(data[2]);
    def poke8(self,adr,val):
        """Poke a value into RAM.  Untested"""
        self.SPItrans([0x02,adr&0xFF,val&0xFF]);
        newval=self.peek8(adr);
        if newval!=val:
            print "Failed to poke %02x to %02x.  Got %02x." % (adr,val,newval);
            print "Are you not in idle mode?";
        return val;
    def MCPbitmodify(self,adr,mask,data):
        """Writes a byte with a mask.  Doesn't work for many registers."""
        data=self.SPItrans([0x05,adr&0xFF,mask&0xFF,data&0xFF]);
        return ord(data[2]);

############### DEBUG UTILITIES: STATUS MESSAGES ##############

#    def MCPrxstatusmessage(self):
#        """Returns string indicating status of RX buffers"""
#        status = self.MCPrxstatus();
#
#        if status < 64:
#            print "No RX message";
#        elif status < 128:
#            print "Message in RXB0";
#        elif status < 192:
#            print "Message in RXB1";
#        else:
#            print "Messages in both buffers";



# TXB0TRL = 0x30
# RXB0CTRL = 0x60
# CNF3/2/1 = 0x28, 29, 2a
# CANINTE = 0x2b
# CANINTF = 0x2c
# TXRTSCTRL = x0D


    

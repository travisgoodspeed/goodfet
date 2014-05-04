#!/usr/bin/env python
# GoodFET SPI Flash Client
#
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
#
# Ted's working copy
#   1) getting hot reads on frequency
#   2) allow sniffing in "normal" mode to get ack bits
#       --check if that's whats causing error flags in board-to-board transmission
#
#

import sys;
import binascii;
import array;
import csv, time, argparse;

from GoodFETMCPCAN import GoodFETMCPCAN;
from intelhex import IntelHex;

class GoodFETMCPCANommunication:
    
    def __init__(self):
       self.client=GoodFETMCPCAN();
       self.client.serInit()
       self.client.MCPsetup();
       
    
    ##########################
    #   INFO
    ##########################
    #
    # Prints MCP state info
    #
    def printInfo(self):
        print "MCP2515 Info:\n\n";
        
        print "Mode: %s" % self.client.MCPcanstatstr();
        print "Read Status: %02x" % self.client.MCPreadstatus();
        print "Rx Status:   %02x" % self.client.MCPrxstatus();
        print "Tx Errors:  %3d" % self.client.peek8(0x1c);
        print "Rx Errors:  %3d\n" % self.client.peek8(0x1d);
        
        print "Timing Info:";
        print "CNF1: %02x" %self.client.peek8(0x2a);
        print "CNF2: %02x" %self.client.peek8(0x29);
        print "CNF3: %02x\n" %self.client.peek8(0x28);
        print "RXB0 CTRL: %02x" %self.client.peek8(0x60);
        print "RXB1 CTRL: %02x" %self.client.peek8(0x70);
        print "RX Buffers:"
        packet0=self.client.readrxbuffer(0);
        packet1=self.client.readrxbuffer(1);
        for foo in [packet0, packet1]:
           print self.client.packet2str(foo);
           
    def reset(self):
        self.client.MCPsetup();
         
    def sniff(self,freq,duration,filename,description, verbose=True):
        self.client.MCPsetrate(freq);
        outfile = open(filename,'a');
        dataWriter = csv.writer(outfile,delimiter=',');
        dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        dataWriter.writerow(['#' + description])
            
        client.MCPreqstatListenOnly();
        print "Listening...";
        packetcount = 0;
        starttime = time.time();
    
        while((time.time()-starttime < duration)):
            packet=self.client.rxpacket();
            if packet!=None:
                if( verbose==True):
                    print self.client.packet2str(packet)   
                packetcount+=1;
                row = [];
                row.append("%f"%time.time());
                if (self.client.peek8(0x2C) & 0x80):
                    self.client.MCPbitmodify(0x2C,0x80,0x00);
                    print "ERROR: Malformed packet recieved: " + self.client.packet2str(packet);
                    row.append(1);
                else:
                    row.append(0);
                for byte in packet:
                    row.append("%02x"%ord(byte));
                dataWriter.writerow(row);
        
        outfile.close()
        print "Listened for %x seconds, captured %x packets." %(duration,packetcount);
        
        
        
    def sniffTest(self, freq):
        self.client.MCPsetup();
    
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
        print "\nMCP2515 Self Test:";
        
        #Switch to config mode and try to rewrite TEC.
        self.client.MCPreqstatConfiguration();
        self.client.poke8(0x00,0xde);
        if self.client.peek8(0x00)!=0xde:
            print "ERROR: Poke to TEC failed.";
        else:
            print "SUCCESS: Register read/write.";
        
        #Switch to Loopback mode and try to catch our own packet.
        self.client.MCPreqstatLoopback();
    
        packet1 = [0x00, 
                   0x08, # LOWER nibble must be 8 or greater to set EXTENDED ID 
                   0x00, 0x00,
                   0x08, # UPPER nibble must be 0 to set RTR bit for DATA FRAME
                         # LOWER nibble is DLC
                   0x01,0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0xFF]
        self.client.txpacket(packet1);
        self.client.txpacket(packet1);
        print "Waiting on loopback packets.";
        packet=None;
        while(1):
            packet=self.client.rxpacket();
            if packet!=None:
                print "Message recieved: %s" % self.client.packet2str(packet);
                break;
    
        
    def spit(self,freq):
        self.client.MCPsetrate(freq);
        self.client.MCPreqstatNormal();
        
        print "Tx Errors:  %3d" % self.client.peek8(0x1c);
        print "Rx Errors:  %3d" % self.client.peek8(0x1d);
        print "Error Flags:  %02x\n" % self.client.peek8(0x2d);
        print "TXB0CTRL: %02x" %self.client.peek8(0x30);
        print "CANINTF: %02x"  %self.client.peek8(0x2C);
    
        
        packet = [0x00, 
                   0x08, # LOWER nibble must be 8 or greater to set EXTENDED ID 
                   0x00, 0x00,
                   0x08, # UPPER nibble must be 0 to set RTR bit for DATA FRAME
                      # LOWER nibble is DLC
                   0x01,0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0xFF]    
        
        self.client.txpacket(packet);
    
        if(self.client.peek8(0x2C)&0x80)==0x80:
            print "Error flag raised on transmission. Clearing this flag and proceeding.\n"
            print "INT Flags:  %02x" % self.client.peek8(0x2c);
            self.client.MCPbitmodify(0x2C,0x80,0x00);
            print "INT Flags modified to:  %02x\n" % self.client.peek8(0x2c);
            print "TXB0CTRL: %02x" %self.client.peek8(0x30);
            self.client.MCPbitmodify(0x30,0x08,0x00);
            print "TXB0CTRL modified to: %02x\n" %self.client.peek8(0x30);
    
        print "message sending attempted.";
        print "Tx Errors:  %02x" % self.client.peek8(0x1c);
        print "Rx Errors:  %02x" % self.client.peek8(0x1d);
        print "Error Flags:  %02x" % self.client.peek8(0x2d);        
        


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
        
    
    parser.add_argument('verb', choices=['info', 'test','peek', 'reset', 'sniff', 'freqtest','snifftest', 'spit']);
    parser.add_argument('-f', '--freq', type=int, default=500, help='The desired frequency (kHz)', choices=[100, 125, 250, 500, 1000]);
    parser.add_argument('-t','--time', type=int, default=15, help='The duration to run the command (s)');
    parser.add_argument('-o', '--output', default="../../contrib/ted/sniff_out.csv",help='Output file');
    parser.add_argument("-d", "--description", help='Description of experiment (included in the output file)');
    parser.add_argumetn('-v',"--verbose",action='store_false',default=True)
    
    args = parser.parse_args();
    freq = args.freq
    duration = args.time
    filename = args.output
    description = args.description
    verbose = args.verbose

    comm = GoodFETMCPCANommunication();
    
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
        comm.sniff(freq=freq,duration=duration,filename=filename,description=description,verbose=verbose)
        
    
                    
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
        comm.spit(freq=freq)
    
    
    
    
        
        
    
    
    
    

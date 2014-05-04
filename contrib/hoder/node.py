# Chris Hoder
# 11/3/2012

import sys, time, string, cStringIO, struct, glob, os;
import csv

# This is a node for a single linked list. this will store the data packet 
# read off of the GOODTHOPTER10
# the data will then be parsed and printed to the terminal. 
# The data can also be saved to csv files or pcap file using
# the appropriate methods below
class node:
    
    def __init__(self, packet, buffer, nextNode):
        #set buffer flag
        self.buffer = buffer
        #points to next node
        self.nextNode = nextNode
        self.packet = packet
        # this is a timestamp of the time since the 12am jan1, 1970
        self.timestamp = time.time()
        dataPt = ord(packet[0])
        dataPt2 = ord(packet[1])
        # check if we have a standard frame, the msb of the second
        # nibble will be 1. otherwise it is an extended rame
        stdCheck = dataPt2 & 0x0f
        if stdCheck == 16:
            self.isStandard = True
            #arb id is first byte + 3 msb of the 2nd byte
            dataPt = dataPt<<3 | dataPt2>>5 
           # print "Standard Packet \n Arb ID: "+("%d"%dataPt)
        else:
            #arb id is first byte + 3 msb + 2 lsb of 2nd byte +
            # 3rd byte + 4th byte
            self.isStandard = False
            dataPt = dataPt<<3 | dataPt2>>5
            dataPt = dataPt<<2 | (dataPt2 & 0x03)
            dataPt = dataPt<<8 | ord(packet[2])
            dataPt = dataPt<<8 | ord(packet[3])
            #print "Extended Data Frame \n Arb ID: "+("%d"%dataPt)
        self.arbID = dataPt
        #find the dataLength
        dataPt5 = ord(packet[4])
        self.dataLength = dataPt5 & 0x0f
        #print "Data Length: "+("%d"%self.dataLength)
        # Print the data packet
        #print "Data:"
        # Temporary, until correct packets are read
        if self.dataLength > 8 :
            self.data = packet[5:12]
            #self.dataLength = 8
        else:
            self.data = packet[5:(5+self.dataLength)]
        self.printData()
        return
        
    # This method will print the data out to the standard output
    def printData(self):
        print "Time stamp: ", self.timestamp 
        print "Buffer: ", self.buffer 
        if self.isStandard:
            # we have a standard length data packet, print standard ID
            print "Standard Packet \nArb ID: "+("%d"%self.arbID)
        else:
            # we have an extended length data packet, print extended ID
            print "Extended Data Frame \nArb ID: "+("%d"%self.arbID)
        #print the data length
        print "Data Length: "+("%d"%self.dataLength)  
        #print the data
        if( self.dataLength > 8):
            print "Acceptable Length Exceeded"
          
        toprint = self.packet2str(self.data)
        print toprint
        print "\n\n\n\n"
    
    #this converts the packet to string with spaces
    def packet2str(self,packet):
        """Converts a packet from the internal format to a string."""
        toprint=""
        for bar in packet:
            toprint=toprint+("%02x "%ord(bar))
        return toprint;
    
    # this method will print out the packet as is, unparsed 
    # with the time stamp (added via python
    # time.time(). NOTE: this is not a very accurate method of 
    # recording timestamps and could lead to inconsistencies
    def writeToFile(self,filename):
        writeFile = open(filename,'a')
        dataWriter = csv.writer(writeFile,delimiter=',')
        #write out the row
        row = []
        row.append(self.timestamp)
        for i in range(1,9):
            row.append(self.packet2str(self.packet[i-1]))
        #write row to file
        dataWriter.writerow(row)    
        writeFile.close()
        return
    
    # This method will write out a parsed packet to the end of a csv
    # file included as filename2.
    # the format will be [timestamp , arbID, data length, data ] 
    def writeParsed(self,filename2):
        writeFile = open(filename2,'a')
        dataWriter = csv.writer(writeFile,delimiter=',')
        row = []
        row.append(self.timestamp)
        row.append(self.arbID)
        row.append(self.dataLength)
        row.append(self.packet2str(self.data))
        dataWriter.writerow(row)
        writeFile.close()
        return
    
    
    # This method will write out the packet into a pcap file which 
    # is wireshark compatible
    def writePcap(self,filehandle):
        #f = open(filename,'ab')
        ph = ''
        # this time may be inaccurate, using python time.time() and 
        # some systems
        # may not record precision greater than 1s despite 
        # floating output of the method
        t = self.timestamp
        #get microseconds
        us = int(t*(10**6))-int(t)*(10**6);
        #us = 0x00
        # faking the pcap header. -- 
        # see wiki.wireshark.org/Development/LibpcapFileFormat
        # for more information on the header format
        ph += struct.pack("<L",int(t))
        #ph += struct.pack("<L", us)
        ph += struct.pack("<L",us)
        ph += struct.pack("<L", 13)
        ph += struct.pack("<L", 13)
        filehandle.write(ph)
        filehandle.write(self.packet2strNoSpace())
       
        
    # This method returns a string of hex with no spaces
    def packet2strNoSpace(self):
        packetstr = ""
        for bar in self.packet:
            #packetstr += ("\x%02x"%ord(bar))
            packetstr += chr(ord(bar))
        #print packetstr
        return packetstr

        
    # this method sets the next pointer in the node for the single linked list    
    def setNext(self,node):
        self.nextNode = node
    
    def getNext(self):
        return self.nextNode
        
    def getPacket(self):
        return self.packet
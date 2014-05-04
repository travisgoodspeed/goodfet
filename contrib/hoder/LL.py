
# Chris Hoder
# 11/3/2012

import time
import sys
import struct
import os
#this is a simple linked list
class LL:
    #constructor
    def __init__(self,filenames,fileBooleans):
        #save filenames and booleans to know if we are writing that file
        self.filenames = filenames
        self.fileBooleans = fileBooleans
       
        #create/overwrite file only if we are 
        #saving that type of file
        for i in range(len(fileBooleans)):
            if( fileBooleans[i].get() == 1):
            	if(filenames[i] == None):
            		continue
            #check to see if the file exists, if so delete
                try:
                    with open(filenames[i]) as f:
                        f.close()
                        os.remove(self.filenames[i])
                except:
                    pass
                writeFile = open(filenames[i],'wb')
                # 3rd file is the pcap file
                if(i == 3):
                    writeFile.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00"+
                                    "\x00\x00\x00\x00\x00\x00\x00\x00\x90"+
                                    "\x01\x00\xe3\x00\x00\x00")
                writeFile.close()
        self.first = None
        self.last = None
        
    def addNode(self,node):
        for i in range(len(self.fileBooleans)):
            if( self.fileBooleans[i].get() == 1):
            	if( self.filenames[i] == None):
            		continue
                if( i == 0):
                    node.writeToFile(self.filenames[i])
                elif( i == 1):
                    node.writeParsed(self.filenames[i])
                #elif( i == 2):
                   #node.writePcap(self.filenames[i])

        #add the node to the linked list
        #check the initial condition edge case
        if( self.first == None):
            self.first = node
            self.last = node
        else:
            self.last.setNext(node)
            self.last = node
            
    def writeToPcap(self):
        print "saving to filename", self.filenames[2]
        os.remove(self.filenames[2])
        f = open(self.filenames[2],"wb")
        f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\
                 x00\x90\x01\x00\xe3\x00\x00\x00")
        nextNode = self.first
        while(nextNode != None):
#            ph = ''
#            t = int(time.time())
#            
#            ph += struct.pack("<L", t)
#            ph += struct.pack("<L", 0x00)
#            ph += struct.pack("<L", 13)
#            ph += struct.pack("<L", 13)
#            f.write(ph)
#            f.write(nextNode.packet2strNoSpace())
            nextNode.writePcap(f)
            nextNode = nextNode.getNext()
        f.close()

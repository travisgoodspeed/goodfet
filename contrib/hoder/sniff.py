# Chris Hoder
# 11/3/2012
import threading

from node import *
from LL import *
import sys
import binascii
import array

sys.path.append('~/svn/goodfet/trunk/client/')
from GoodFETMCPCAN import GoodFETMCPCAN;
from intelhex import IntelHex;

# This method will be run as a separate thread from the mainDisplay. 
# It will sniff the GOODTHOPTER10
# for CAN traffic and add all the data to the provided 
# linked list (LList). client is the MCP controller
# the thread will terminate when the 
#Threading.Event() stop_cond is set. 
class sniff(threading.Thread):
    
    def __init__(self, stop_cond,LList,client):
        threading.Thread.__init__(self)
        self.stop_cond = stop_cond
        self.LList = LList
        self.client = client
        
     #sniff the bus for traffic and save it to the LList   
    def run(self):
        while(not self.stop_cond.is_set()):
            packet = self.client.rxpacket()
            if packet != None:
                node1 = node(packet,0,None)
                self.LList.addNode(node1)
            else:
            	print "no packet"
        
        print "Sniffing Terminated"
        return
        
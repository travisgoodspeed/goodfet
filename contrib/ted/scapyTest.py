"""
Ted's early foray into Scapy.
"""


#! /usr/bin/env python

import sys
from scapy.all import *

"""      	
86 40 ff fd 08 80 00 fa 00 1f ff ff 3f 
72 20 d9 7f 08 00 00 00 00 00 89 1e 00 
"""

                 	
class standardID(XShortField):
	
	def i2m(self, pkt, x):
		if x != None:
			SIDlow = (x & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
			SIDhigh = (x >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
			return "%02x%02x" %(SIDhigh, SIDlow)
		return "%02x%02x" %(0, 0)
    
	def m2i(self, pkt, x):
		return(int(x))
		
	def addfield(self, pkt, s, val):
		return s+self.i2m(pkt, val)
	
	def i2h(self, pkt, x):
		return(int(x & 0x07FF))

class fordEnginePacket(Packet):

	name = "Ford Engine Data"
    fields_desc = [ ByteField("engineRPM", 0),
                    ByteField("db1",0),
                    ByteField("db2",0),
                    ByteField("db3",0),
                    ByteField("db4",0),
                    ByteField("db5",0),
                    ByteField("db6",0),
                    ByteField("db7",0)
                    ]

"""	
class extendedID(X3BytesField):
	
	def
"""

class CAN(Packet):
    name = "CANPacket"
    fields_desc=[	#IntEnumField("MessageType" , 0 ,
                	#{ 0: "unknown", 1: "Data" , 2: "RTR", 3: "Error" } ),
                	standardID("SID", None),
    				#XShortField("SID", None),
                 	X3BytesField("EID", None),
                 	FieldLenField("DLC", None, count_of="Data", fmt="B"),
                 	#FieldListField("Data", None, XByteField("DB", None), count_from=lambda pkt:pkt.DLC)
                 	]
                 	
bind_layers(CAN, fordEnginePacket, {'SID':1057} )

    	
#packet = [0x00, 0x40, 0x00,0x00, # pad out EID regs
#                   0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
#                   # lower nibble is DLC                   
#                   0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
            

#d = CAN(packet)
#ls(d)
#d.show2()
                      
d=CAN(SID=1,Data = [0x01, 0x02])

d.show2()

print "\n" + str(d) +"\n\n"

#ls(d)

#print "\nprinting raw string\n\n"

#hexdump(str(d))

#d.Data = [0x01, 0x02]
#d.SID = 5

#hexdump(d)

#print "\n\n\n"

#CAN(str(d))
#d.show2()
#ls(d)
#CAN(str(d))
#d.show2()
#print str(d)
#d.show()
#CAN()
#d.show2()


"""
write: 	1) dissector
		2) builder
		3) *2* fields...


"""
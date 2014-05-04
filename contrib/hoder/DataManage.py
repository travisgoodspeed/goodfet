# 
# 1/11/2012

import MySQLdb
import sys
import csv
import argparse;
import time
import struct
import glob
import os
import datetime
import json
#data parsing assumes an standard ID!!

sys.path.insert(0,'../../trunk/client/')
from GoodFETMCPCANCommunication import *
from GoodFETMCPCAN import GoodFETMCPCAN;
from experiments import experiments

class DataManage:
    """
    This class will do the data Management for the CAN analysis. This includes loading data up to the 
    MYSQL database, downloading data from the MYSQL database, converting data to pcap, loading in packets.
    
    @todo: change the way to upload data to run bulk inserts and not item by item as it is now
    """
    
    def __init__(self, host, db, username, password, table, dataLocation):
        """
        Constructor method.
        
        @type table: string
        @param table: SQL table to add data to
        @type host: string
        @param host: Host for MYSQL table
        @type username: string
        @param username: MYSQL username
        @type password: string
        @param password: MYSQL username password
        @type db: String
        @type db: database we want to use
        
        @type dataLocation: String
        @param dataLocation: path to the folder where data will be saved and loaded from

        """
        # Save MYSQL information for later use
        self.host = host
        self.db = db
        self.username = username
        self.password = password
        self.table = table
        #self.DATALOCATION = "../ThayerData/"
        self.DATALOCATION = dataLocation
        """ Location of main data folder """
        self.SQLDDATALOCATION = self.DATALOCATION+"SQLData/"
        """ Location where MYSQL data will be stored"""
        self.INJECTDATALOCATION  = self.DATALOCATION+"InjectedData/"
        """ Location where injection data will be stored """
        self.MIN_TIME_DELAY = 0.01
        """ This is the minimum time between 2 packets that we will consider there to be a delay between injection of the packets. """
        self.MAX_TIME_DELAY = 1.1
        """ This is the maximum time between 2 packets that we will consider as a time delay between the two packets """
        
    def getSQLLocation(self):
        """
        This method returns the path to folder where all sql queries will be saved
        
        @rtype: string
        @return: path to the folder where sql data is stored. this will be a sub folder of the data location
                 path that was passed into the constructor, L{__init__}.
        """
        return self.SQLDDATALOCATION
    
    def getDataLocation(self):
        """
        This method returns the path to the main folder where all data will be stored and read from.
        @rtype: String
        @return: path to the main folder where data will be saved and loaded from
        """
        return self.DATALOCATION
    
    def getInjectedLocation(self):
        """
        This method returns the path to the sub folder where data that was injected will be read from.
        
        @rtype: String
        @return: Path, relative to dataLocation, give in the constructor L{__init__}, where the injection data will be stored
        """
        return self.INJECTDATALOCATION
    
    #Creates a new MySQL table in the database with the given table name
    def createTable(self, table):
        """
        This method will create a new table in the MYSQL database. There is no error checking so be 
        careful when adding in a new table
        @type table: String
        @param table: Name of the new table in the database. The database information was set in the constructor, L{__init__}
        """ 
        self.table = table
        cmd =" CREATE TABLE `%s` ( \
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT, \
  `time` double(20,5) unsigned NOT NULL, \
  `stdID` int(5) unsigned NOT NULL, \
  `exID` int(5) unsigned DEFAULT NULL, \
  `length` int(1) unsigned NOT NULL, \
  `error` bit(1) NOT NULL, \
  `remoteframe` bit(1) NOT NULL DEFAULT b'0', \
  `db0` int(3) unsigned DEFAULT NULL, \
  `db1` int(3) unsigned DEFAULT NULL, \
  `db2` int(3) unsigned DEFAULT NULL, \
  `db3` int(3) unsigned DEFAULT NULL, \
  `db4` int(3) unsigned DEFAULT NULL, \
  `db5` int(3) unsigned DEFAULT NULL, \
  `db6` int(3) unsigned DEFAULT NULL, \
  `db7` int(3) unsigned DEFAULT NULL, \
  `msg` varchar(30) NOT NULL, \
  `comment` varchar(500) DEFAULT NULL, \
  `filter` bit(1) NOT NULL DEFAULT b'0', \
  `readTime` int(11) unsigned NOT NULL DEFAULT '0', \
  PRIMARY KEY (`id`) \
) ENGINE=MyISAM AUTO_INCREMENT=310634 DEFAULT CHARSET=utf8;"% (table)
        self.addData(cmd)
        self.table = table
        
    def changeTable(self,table):
        """
        Changes the dtable that we are going to be reading from and uploading to in the MYSQL database
        @type table: String
        @param table: String that is the name of the table we want to communicate with in the MYSQL database
        """
        self.table = table
    
    def getTable(self):
        """
        Returns the name of the table that we are set to upload to.
        @rtype: String
        @return: The table we are set to communicate with
        """
        return self.table
    
    def addData(self,cmd):
        """
        This method will insert data into the MYSQL database based on the given command and the MYSQL information provided 
        in the constructor, L{__init__}. This method is designed for the insertion of data and not for retrieving data.
        Use the method L{getData} to retrieve data from the MYSQL database.
        @type cmd: String
        @param cmd: MYSQL command that we want executed. This is designed for the insertion of data.
        """
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        try:
            #execute the SQL command
            cursor.execute(cmd)
            #commit the changes the to database
            db_conn.commit()
        except:
            #Rollback in case there is any error
            db_conn.rollback()
            
            #unable to add, raise an exception
            raise Exception, "Error inserting into db, %s with the command %s" % self.db,cmd
        
        db_conn.close()


    def getData(self,cmd):
        """
        This method is designed to grab data from the MYSQL database and return it to the user. It is not designed for insertions. See L{getData} for 
        a method to insert data to the database. 
        
        @param cmd: MYSQL command requesting data
        @type cmd:  String
        
        @rtype: List of Lists
        @return: SQL data that you requested. The format will be a list of all the rows of data. Each row will be a list
                 of the columns you requested.
        
        """
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        try:
            #Execute the SQL command
            cursor.execute(cmd)
            #Fetch all the rows in a list of lists.
            results = cursor.fetchall()
        except:
            error = "Error fetching data from db, %s with the command, %s" % (self.db, cmd)
            raise Exception( error )
        
        db_conn.close()
        return results
    
    # This method will take in a data packet, the time stamp, an error boolean and will add the information
    # to the MySQL table. 
    # INPUT:
    # data: list of the CAN message received. each 
    def addDataPacket(self,data,time,error):
        """
        This method will take in a data packet (such as one read from our sniff file) and then upload it to the MYSQL database that is
        set for the class.
        
        @type data: List
        @param data: This is a list that is one packet as it read off by GooDFETMCPCAN rxpacket method. It is 14 elements long and each byte is stored to an element as an ASCII character .
        @type time: float
        @param time: The time stamp of the packet
        @type error: Boolean 
        @param error: An additional boolean to set if there was an error detected with this packet during its parsing.
        """
        parse = self.parseMessage(data)
        cmd = self.getCmd(parse, time, error)
        self.addData(cmd)
       
    
    #Creates a SQl command to upload data packet to the database
    def getCmd(self,packet,time,error,duration,filter, comment=None):
        """
        This method will create a sql insertion command based on the given data and the MYSQL information stored in the class. This is 
        designed for inserting 1 packet.
        
        @type packet: Dictionary
        @param packet: This is a dictionary that contains the information for an entire data packet sniffed off of the CAN bus it has already
                      been parsed from the format that it is saved as in the sniff method from GoodFETMCPCANCommuniation, L{GoodFETMCPCANCommunication.sniff}. See L{parseMessageInt} to 
                      parse the message and for information on the packet Dictionary. The keys expected to be contained in this dictionary are as follows
                      sID, length,rtr,error, ide, eID (optional), db0 (optional), ... , db7 (optional). See the parsing method for information on all components
        
        @type time: float
        @param time: Time stamp of the packet
        
        @type error: Boolean
        @param error: 1 if there is an error in the packet, 0 otherwise. This is a field in the MYSQL database
        
        @type duration: Float
        @param duration: The length of the observation time during which this packet was sniffed off of the CAN bus.
        
        @type filter: Boolean
        @param filter: 1 if there was filtering applied during this experiment, 0 otherwise
        
        @type comment: string
        @param comment: Comment tag that can be assigned to the field in the MYSQL database
        
        @rtype: String
        @return: SQL command for insertion of the packet to the MYSQL database table set in the class
        """
        length = packet['length']
        
        cmd = "INSERT INTO %s ( time, stdID" % self.table
        
        #if there is an extended id, include it
        if(packet.get('eID')):
            cmd += ", exID"
            
        cmd +=", length,"
        
        #if there was an error detected in parsing, note it
        if( packet.get('error') != None):
            print "ERROR CHANGED"
            error = 1
        #add in only data bytes written to
        for i in range(0,length):
            cmd +=" db" + str(i) + ","
        cmd += ' error, remoteFrame'

        if( comment != None): # optional comment
            cmd += ", comment"

        cmd+= ', msg, filter, readTime) VALUES (%f, %d' % (time, packet['sID'])
        
        #if there is an extended id include it
        if(packet.get('eID')):
            cmd += ", %d" % packet['eID']
        
        cmd += ", %d" % length
        
        #add data
        for i in range(0,length):
            cmd += ", %d" % (packet['db'+str(i)])
        
        cmd += ', %d, %d' %(error,packet['rtr'])

        if(comment != None): # if there was a comment
            cmd += ',"%s"' %comment

        cmd += ', "%s", %d, %f)' %(packet['msg'], filter, duration)
         
        return cmd
    
    def writeDataCsv(self,data, filename):
        """
        This method will write the given data to the given filename as a csv file. This is designed to write packet data to files
        
        @type data: List of Lists
        @param data: A list of the data we wish to write to the csv file. The format is that each element in the list is a considered a row. and then each
                     element in the row is a column in the csv file. This can handle both string and numeric elements in the lists. This is 
                     the format that is returned by L{opencsv}.
        """
        outputfile = open(filename,'a')
        dataWriter = csv.writer(outputfile,delimiter=',')
        #dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        for row in data:
            rowTemp = []
            for col in row:
                if( isinstance(col,str)): #if the element is a string, write a string
                    rowTemp.append(col)
                elif(isinstance(col,float)): # if the element is a number, turn it into a string
                    rowTemp.append("%f" % col)
                else:
                    rowTemp.append(col)
            dataWriter.writerow(rowTemp)
        outputfile.close()
            
    
    def writePcapUpload(self,filenameUp,filenameWriteTo):
        """
        This method will create a pcap file of the data contained in a given csv file. The csv file is assumed to be of the format
        saved by the sniff method in the GoodFETMCPCANCommunication class, L{GoodFETMCPCANCommunication.sniff}. 
        
        @type filenameUp: String
        @param filenameUp: path/filename for the csv file that will be read and used for making a pcap file. This assumes that the .csv is included in the input.
        
        @type filenameWriteTo: String
        @param filenameWriteTo: path/filename for the pcap to be saved to. This assumes that there is the .pcap ending included in the input.
        """
        #load the data from the csv file
        try:
            fileObj = open(filenameUp,'rU')
            data = self.opencsv(fileObj)
        except:
            print "Unable to open file!"
            return
        self.writeToPcap(filenameWriteTo, data)
        return
        
    def writeToPcap(self,filenameWriteTo, data):
        """
        This method will create a pcap formatted file from the data that was supplied.
        
        @type filenameWriteTo: String
        @param filenameWriteTo: path/filename for the pcap to be saved to. This assumes that there is the .pcap ending included in the input.

        @type data: List of Lists
        @param data: A list of the data we wish to write to the csv file. The format is that each element in the list is a considered a row. and then each
                     element in the row is a column in the csv file. This can handle both string and numeric elements in the lists. This is 
                     the format that is returned by L{opencsv}.
        """
        f = open(filenameWriteTo,"wb")
        # write global header to file
        # d4c3 b2a1 0200 0400 0000 0000 0000 0000 0090 0100 be00 0000
        f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xe3\x00\x00\x00")
        
        # write to pcap file
        for line in data:
            # packet header creation
            ph = ''
            t = line[0]
            #get microseconds
            us = int(t*(10**6))-int(t)*(10**6);
            ph += struct.pack("<L", int(t))
            ph += struct.pack("<L", us)
            ph += struct.pack("<L", 16)
            ph += struct.pack("<L", 16)
            
            
            # write packet header
            f.write(ph)
            # create a message of characters from the integers created above
            # first 5 bytes
            msg = '%s%s%s%s%s' % (chr(line[3]), chr(line[4]), chr(line[5]), chr(line[6]), chr(line[7]))
            # 3 bytes to provide stuffing for Wireshark
            msg += '%s%s%s' % (chr(int('00', 16)), chr(int('00', 16)), chr(int('00', 16)))
            # 8 data bytes
            msg += '%s%s%s%s%s%s%s%s' % (chr(line[8]), chr(line[9]), chr(line[10]), chr(line[11]), chr(line[12]), chr(line[13]), chr(line[14]), chr(line[15]))
            # write message
            f.write(msg)
        f.close()
        
    def testSQLPCAP(self):
        """ 
        This is an internal test method
        """
        cmd = 'Select time,msg from ford_2004 where comment="bgtest"'
        data = self.getData(cmd)
        self.writetoPcapfromSQL("test.pcap",data)
        return

    def writetoPcapfromSQL(self, filenameWriteto, results): # pass in results from SQL query
        """
        This method will create a pcap formatted file from the data that was supplied.
        
        @type filenameWriteto: String
        @param filenameWriteto: path/filename for the pcap to be saved to. This assumes that there is the .pcap ending included in the input.

        @type results: List of Lists
        @param results: A list of the data we wish to write to the csv file. The format is that each element in the list is a considered a row. and then each
                     element in the row is a column in the csv file. This can handle both string and numeric elements in the lists. This is 
                     the format that is returned by a MYSQL query.
        """
        f = open(filenameWriteto, "wb")
        # write global header to file
        # d4c3 b2a1 0200 0400 0000 0000 0000 0000 0090 0100 be00 0000
        f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xe3\x00\x00\x00")
            
        # run through all lines in results
        for line in results:
            
            # create packet header for Wireshark
            ph = ''
            t = line[0]
            us = int(t*(10**6))-int(t)*(10**6) #create microseconds
            ph += struct.pack("<L", int(t)) # use time integer from results
            ph += struct.pack("<L", us) # microseconds
            ph += struct.pack("<L", 16) # number of packet octets saved in file
            ph += struct.pack("<L", 16) # packet length
            
            # write the packet header to the file
            f.write(ph)

            # create a message of characters from 'message' in SQL database
            # pad with 0s to ensure Wireshark accepts it correctly

            # separate out bytes
            bytes = [line[1][i:i+2]for i in range(0,len(line[1]),2)];
         #   print chr(int(bytes[0],16))
         #   print int(bytes[0],16)
            # first 5 bytes
            msg = '%s%s%s%s%s' % (chr(int(bytes[0], 16)), chr(int(bytes[1], 16)), chr(int(bytes[2], 16)), chr(int(bytes[3], 16)), chr(int(bytes[4], 16)))
            # 3 bytes of zero to provide stuffing for Wireshark
            msg += '%s%s%s' % (chr(int('00', 16)), chr(int('00', 16)), chr(int('00', 16)))
            # 8 data bytes
            msg += '%s%s%s%s%s%s%s%s' % (chr(int(bytes[5], 16)), chr(int(bytes[6], 16)), chr(int(bytes[7], 16)), chr(int(bytes[8], 16)), chr(int(bytes[9], 16)), chr(int(bytes[10], 16)), chr(int(bytes[11], 16)), chr(int(bytes[12], 16)))

            # write message
            f.write(msg)

        # close file
        f.close()

    
    # This method converts the data to integers and then passes it into parseMessageInt.
    # see that method for more documentation.
    def parseMessage(self,data):
        """
        This method will parse a row of the data packets that is of the form of the packet as returned by the GoodFETMCPCAN rxpacket method will simply convert
        each databyte to integers and then call L{parseMessageInt}. See this method for more information. 
        
        @type data: List
        @param data: This is a list that is one packet as returned by GoodFETMCPCAN rxpacket method. It is 13 bytes long and ASCII value.
        
        @rtype: Dictionary
        @return: This is a dictionary that contains the information for an entire data packet sniffed off of the CAN bus it has already
                 been parsed from the format that it is saved as in the sniff method from GoodFETMCPCANCommuniation. See L{parseMessageInt} to 
                 parse the message and for information on the packet Dictionary. The keys expected to be contained in this dictionary are as follows
                 sID, length,rtr,error, ide, eID (optional), db0 (optional), ... , db7 (optional). 
                 
                     1. sID: standard ID of the packet
                     2. length: length of the data packet (number of data bytes). This will be 0 for an Remote Transmission Request frame
                     3. rtr: boolean that is 1 if the message is a Remote Transmission Request, 0 otherwise
                     4. ide: Boolean that is 1 if the message has an extended id. 0 otherwise
                     5. eID: Extended ID. Only included if one exists
                     6. db0: Databyte 0. Only included if one exists
                        
                        ---
                     7. db7: Databyte 7. Only included if one exists
            
        """
        numData =[]
        for element in data:
            numData.append(ord(element))
        
        return self.parseMessageInt(numData)
    
    # This method will parse the CAN message input into the various components as integers.
    # The method will return the parsed information stored in a dictionary. Basic packet formation
    # error checking will be performed. Certain bits are always expected to be 0 as well as 
    # DLC must be 8 or less
    #
    # INPUT: CAN message as an array of integers corresponding to the hex read in
    #
    # OUTPUT: Dictionary containing the parsed information as follows
    # packet
    #    key:value
    #    msg: original full CAN message as a string
    #    sID: standard ID as integer
    #    ide: extended id identifier (1 means extended id)
    #    eID: extended ID as integer
    #    rb0: rb0 bit
    #    rb1: rb1 bit
    #    rtr: rtr bit
    #    length: DLC of packet
    #    db0: first data packet byte as integer
    #    db1: 2nd data packet byte as integer
    #     ...
    #    db8: nth data packet byte as integer
    #   
    #    NOTE: db1-8 are only assigned if the data byte contains info (see length int)
    def parseMessageInt(self,data):
        """
        @type data: List
        @param data: This is a list that is one packet as it read off by L{opencsv} method. The Elements will have been convereted to integers.
        
        @rtype: Dictionary
        @return: This is a dictionary that contains the information for an entire data packet sniffed off of the CAN bus it has already
                 been parsed from the format that it is saved as in the sniff method from GoodFETMCPCANCommuniation. See L{parseMessageInt} to 
                 parse the message and for information on the packet Dictionary. The keys expected to be contained in this dictionary are as follows
                 sID, length,rtr,error, ide, eID (optional), db0 (optional), ... , db7 (optional). 
                 
                     1. sID: standard ID of the packet
                     2. length: length of the data packet (number of data bytes). This will be 0 for an Remote Transmission Request frame
                     3. rtr: boolean that is 1 if the message is a Remote Transmission Request, 0 otherwise
                     4. ide: Boolean that is 1 if the message has an extended id. 0 otherwise
                     5. eID: Extended ID. Only included if one exists
                     6. db0: Databyte 0. Only included if one exists
                         
                        ---
                     7. db7: Databyte 7. Only included if one exists
        """
        dp1 = data[0]
        dp2 = data[1]
        dp5 = data[4]
        
        #converts the CAN message to a string
        msg="";
        for bar in data:
            msg=msg+("%02x"%bar)
        
        packet = {'msg':msg}
        
        #get the ide bit. allows us to check to see if we have an extended
        #frame
        packet['ide'] = (dp2 & 0x0f)>>3
        #we have an extended frame
        if( packet['ide'] != 0):
            #get lower nibble, last 2 bits
            eId = dp2 & 0x03
            eId = eId<<8 | data[2]
            packet['eID'] = eId<<8 | data[3]
            packet['rtr'] = dp5>>6 & 0x01
    
        else:
            packet['rtr'] = dp2>>4 & 0x01
        
        #error check, 2nd msb of the lower nibble of byte 2 should be 0
        if( (dp2 & 0x04) == 4 ):
            packet['error'] = 1
        #error check an always 0 bit
        if( (dp5 & 0xf0) == 240):
            packet['error'] = 1
        
        # Create the standard ID. from the message
        packet['sID'] = dp1<<3 | dp2>>5
        
 
        length = dp5 & 0x0f
        packet['length'] = length
        
        if( length > 8):
            packet['error'] = 1
        
        #generate the data section
        for i in range(0,length):
            idx = 5+i
            dbidx = 'db%d' % i
            packet[dbidx] = data[idx]   
        return packet
    
    #this converts the packet to string with no spaces
    def packet2str(self,packet):
        """
        Converts the packet, in the form of the datapacket provided by GoodFETMCPCAN rxpacket and each element is a string ASCII character corresponding to the Hex number
        of the databyte. This will convert the list to a string of the hex bytes.
        
        @type packet: List
        @param packet: This is a list that is one packet as it read off by the GoodFETMCPCANComunication class. It is 13 bytes long and string character is in each element.
        
        @rtype: String
        @return: String that is the data packet printed out where each byte has been converted to the hex characters.
        """
        toprint="";
        for bar in packet:
            toprint=toprint+("%02x"%ord(bar))
        return toprint;
    
    
    # This method will take a csv file as the file name and upload it to the MySQL 
    # database in the object. 
    def uploadData(self,filename):
        """
        This method will upload all the data contained in the given file path to the MYSQL database. 
        
        @type filename: String
        @param filename: This is the path to the file that the user wishes to upload. It is assumed to contain the .csv ending and
                         be a file in the format of the data that is saved by GoodFETMCPCANCommunication sniff method. 
        """
        
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        
        #load the data from the csv file
        try:
            
            fileObj = open(filename,'rU')
            data = self.opencsv(fileObj)
        except:
            print "Unable to open file!"
            return
        
        print "uploading data to SQL table, %s" % (self.table)
        #upload the data to the SQL database
        for packet in data:
            time = packet[0]
            error = packet[1]
            #could be None
            comment = packet[2]
            #get duration
            duration = packet[3]
            #get filterbit
            filter = packet[4]
            # parse the message
            parsedP = self.parseMessageInt(packet[5:])
            # generate the command
            cmd = self.getCmd(parsedP, time, error,duration,filter,comment)
            try:
                #execute the SQL command
                cursor.execute(cmd)
                #commit the changes to the database
                db_conn.commit()
            except:
                # Rollback in case  there is any error
                db_conn.rollback()
                
                #unable to add, raise an exception
                raise Exception, "Error inserting into db, %s with the command %s" % (self.db, cmd)
        print "data uplaod successful!"
        db_conn.close()
        
        
    # this file will open the csv file and parse out the information according to our standard
    # The returned value is a list of lists. Each row is a packet received and the columns are as defined
    # by our standard
    def opencsv(self,fileObj):
        """
        This method will load packet data from a csv file. The format of the data will be of the form of the data that was saved by the
        GoodFETMCPCANCommunication sniff method. See L{GoodFETMCPCANCommunication.sniff} for more information on the meaning of the databytes. The elements in each row of the csv file will be parsed as if they are the following types:
                     1. float
                     2. string
                     3. integer 
                     4 Hex value (i.e. 'ff' or 'af')
        This will ignore any lines in the csv document that begin with # in the first column. This allows for comments to be added.
        
        @type fileObj: Object of the file
        @param fileObj: This is the file object (i.e. what is returned by the open command) of the csv document that is to be read.
        
        @rtype: List of lists
        @return: The csv file parsed by rows and columns. The format will be that each element in the return list will be one row of the
                 csv file. All entries will be stored as a number except column 2 which will be stored as a string (see above).
        """
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    packet.append(float(col))
                #error flag
                elif(colnum == 1):
                    packet.append(int(col))
                elif(colnum ==2):
                    packet.append(col)
                elif(colnum == 3):
                    packet.append(int(col))
                #data packets
                else:
                    packet.append(int(col,16))
                colnum += 1
                #print packet
            data.append(packet)
            rownum += 1
        #print data
        fileObj.close()
        return data

    # This will be used to read a file for writing packets on to the bus
    # The format below will assume a standard id but there will be easy extensible to make generic.
    # The format of the data in this case is assumed to be in hex
    # row format: will ignore any rows that begin with #
    # col 0: delay time from previous row (if empty no delay)
    # col 1: sID
    # COULD ADD eID column here
    # col2: DLC
    # col3: db0
    #  ...
    # colDLC
    def readWriteFileHex(self, filename):
        """
        This method will be used for reading a file for of packets to be written to the the CAN bus. The format of the csv layout is
        expected to be as follows with each element stored as a hex except for the time delay:
            - col 0: delay time from previous row (0 if no delay)
            - col 1: Standard ID
            - col 2: Data Length (0-8) 
            - col 3: db 0
            ---
            - col 7: db7 (as needed, based on data length)
            
            @type filename: String
            @param filename: path/filenae to the csv file to be uploaded. This is expected to include the .csv ending. The format of the rows
                             is described above. 
                             
            @rtype: List of Lists
            @return: This will simply turn the csv file to a list of lists where the elements of the outer list are rows in the csv file. Each row is a list 
                     of all the columns.  The time delay will be converted to a float while all other columns are converted to an integer.
        """
        try:
            fileObj = open(filename,'rU')
        except:
            print "Unable to open file!"
            return
        
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0]=='' or row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    packet.append(float(col))
                else: # all other packets
                    packet.append(int(col,16))
                colnum += 1
                
            data.append(packet)
            rownum += 1
        
        fileObj.close()
        return data
    
    # same as the readWriteFileHex but format is assumed to be in Decimal format
    def readWriteFileDEC(self,filename):
        """
        This method will be used for reading a file for of packets to be written to the the CAN bus. The format of the csv layout is
        expected to be as follows with each element stored as an integer value except for the time delay which is expected as a float:
            - col 0: delay time from previous row (0 if no delay)
            - col 1: Standard ID
            - col 2: Data Length (0-8) 
            - col 3: db 0
            ---
            - col 7: db7 (as needed, based on data length)
            
        Additionally, this can now take in the packets that the sniff method writes out, L{GoodFETMCPCANCommunication.sniff}. It will detect
        either the header that is added to these files or that the length is longer than those written by the fuzz methods.
        
        @type filename: String
        @param filename: path/filenae to the csv file to be uploaded. This is expected to include the .csv ending. The format of the rows
                         is described above. 
                         
        @rtype: List of Lists
        @return: This will simply turn the csv file to a list of lists where the elements of the outer list are rows in the csv file. Each row is a list 
                 of all the columns.  The time delay will be converted to a float while all other columns are converted to an integer.
        """
        try:
            fileObj = open(filename,'rU')
        except:
            print "Unable to open file!"
            return
        
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        
        #it was a sniff file or sniff file format
        if( reader[0] == "# Time     Error        Bytes 1-13" or len(reader[1] == 18)):
            # for every row
            for row in reader:
                packet = []
                #check to see if the line begins with #
                # if it does it is a comment and should be ignored
                if( row[0][0] == '#'):
                    rownum += 1
                    continue
                colnum = 0;
                #go down each byte, the first one is the time
                for col in row:
                    #time stamp
                    if(colnum == 0):
                        packet.append(float(col))
                    #error flag
                    elif(colnum == 1 or column== 2 or column == 3 or column == 4):
                        continue
                    elif( colnum == 5 ):
                        dp1 = int(col,16)
                    elif( colnum == 6):
                        dp2 = int(col,16)
                        sID = dp1<<3 | dp2>>5 #get the standard ID
                    elif( colnum == 9):
                        length = int(col,16)&0x0f # get the length
                        packet.append(sID) #add in the standard id
                        packet.append(length) # add in the length
                    elif( colnum > 9 ):
                        packet.append(int(col,16))   
                    colnum += 1
                    #print packet
                data.append(packet)
                rownum += 1
            #print data
            fileObj.close()
            return data
        
        
        else:
            # for every row
            for row in reader:
                print row
                packet = []
                #check to see if the line begins with #
                # if it does it is a comment and should be ignored
                if( row[0] == '' or row[0][0] == '#'):
                    rownum += 1
                    continue
                colnum = 0;
                #go down each byte, the first one is the time
                for col in row:
                    #time stamp
                    if(colnum == 0):
                        packet.append(float(col))
                    else:
                        packet.append(int(col))
                    colnum += 1
                
                data.append(packet)
                rownum += 1
        
        fileObj.close()
        return data
    
    def readInjectedFileDEC(self,filename,startTime = None,endTime = None,id=None):
        """
        This method will read packets from a file that was saved from packets that were injected onto the bus. An example of a method that does this would be
        the experiments method L{experiments.generationFuzzer}. The file is assumed to be a csv file with the .csv included matching this format. Any lines that
        begin with a # in the first column will be ignored. The user can specify start and end times to only get a subset of the packet. If no startTime is provided 
        then it will return packets starting from the begining up until the endTime. If no endTime is provided then it will return all packets in the file after the 
        startTime. An id can be provided and it will return only the packets with the given id.  
        
        When parsing the data it will assume the data is of the following form where the first column is parsed as a float and all subsequent are parsed as a decimal ineteger:
        
            1. time of injection
            2. standard Id 
            3. 8 (data length) @todo: extend to varied length
            4. db0
            
               ---
            5. db7
        
        @type filename: String
        @param filename: path/filenae to the csv file to be uploaded. This is expected to include the .csv ending. The format of the rows
                         is described above.
        @type startTime: timestamp
        @param startTime: This is a timestamp of the start time for the earliest time for packets you want. The method will not return any packets that were injected
                          before this start time. This input is optional.
                         
        @type endTime: timestamp
        @param endTime: This is the timestamp of the latest inject time for packets you want. The method will return no packets with an endTime after this timestamp.
                        This input is optional.
                        
        @type id: Integer
        @param id: This is an optional parameter that allows you to positively filter for the id that you want of packets. Only packets with the given id will be returned.
        
        @rtype: List of Lists
        @return: This imports the data on the csv file. Each element in the list will correspond to a row. each element in the row will correspond to the column. The types of the 
                 column will be a float for the first columna and integer for all subsequent columns.
        """
        print startTime, "    ", endTime, "      ", id
        try:
            fileObj = open(filename,'rU')
        except:
            print "Unable to open file!"
            return
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        timePrev = 0;
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            #print row
            if( row[0][0] == '#'):
                rownum += 1
                continue
            # if the user specified an id to get and this doesn't match
            elif( id != None and int(row[1]) != id):
                print int(row[1])
                rownum +=1
                continue
            # if the user specified a start time to the packets that were fuzzed make sure it is after that.
            elif( startTime != None and float(row[0]) < startTime):
                print "startTime", row[0],"   ", startTime
                rownum += 1
                continue
            # if the user specified an end time to the packets that were fuzzed make sure it is before that.
            elif( endTime != None and float(row[0]) > endTime):
                print "endTime Issue", row[0], "     ",endTime

                break # We are assuming that the file is ordered by time in an ascending order so that as soon as we are
                      # after the end time we are not going to add any new packets
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    timeInject = float(col)
                    # if the difference between this packet's inject time is less than the minimum and not more than 
                    # the maximum delay. The reason for the maximum delay is to make sure that if you are combining
                    # different fuzzes you are not having an unwanted long pause
                    if( rownum != 0 and (timeInject-timePrev) > self.MIN_TIME_DELAY and (timeInject-timePrev) < self.MAX_TIME_DELAY):
                        packet.append(timeInject-timePrev)
                    else:
                        packet.append(0)
                    timePrev = timeInject
                    #packet.append(float(col))
                
                else:
                    packet.append(int(col))
                colnum += 1
                #print packet
            print packet
            data.append(packet)
            rownum += 1
        #print data
        fileObj.close()
        #print data
        return data
    
    
    # will upload all the csv files in the self.DATALOCATION to the MySQL database
    # the files uploaded will be moved to a folder named as today's date and a tag _Uploaded will
    # be appended to the end of the filename
    def uploadFiles(self):
        """
        This method will upload all data files from sniffing experiments that have been saved. The sniff would be called by L{GoodFETMCPCANCommunication.sniff}
        and it will be all .csv files saved in the self.DATALOCATION which is input by the user when the class is initiated. 
        
        This method will find all .csv files in the folder and attemp to upload them all. It will call the L{uploadData} method on all the filenames. Once a 
        file has been uploaded (or attempted to) the file will be moved to a subfolder that is named by todays date in the following format: YYYYMMDD. If the
        folder does not exist, it will be created. The filename will then be changed by adding  "_Uploaded" to the end of the csv. To ensure that no files are
        overwritten, the program will ensure that the file does not exist. if one does of the same filename it will append "_i" where i is the first integer that
        does not have a conflicting filename. This allows the user to upload multiple times during the same day without loosing the origional data files.
        """
        #get all files in the ThayerData folder
        files = glob.glob(self.DATALOCATION+"*.csv")
        if( len(files) == 0):
            print "No new files to upload"
            return
        print files
        for file in files:
            #upload the file to the db
            self.uploadData(filename=file)
            
            #see if there is a folder with today's date
            now = datetime.datetime.now()
            datestr = now.strftime("%Y%m%d")
            path = self.DATALOCATION + datestr
            if( not os.path.exists(path)):
                #folder does not exists, create it
                os.mkdir(self.DATALOCATION+datestr)
            baseName = os.path.basename(file)
            root = file[:-len(baseName)]
            filename = root+datestr+"/"+baseName[:-4]+"_Uploaded.csv"
            print root
            print filename
            i=1
            #make sure the name is unique
            while( os.path.exists(filename)):
                filename = root+datestr+"/"+baseName[:-4]+"_Uploaded_%d.csv" %i
                i+=1 
            #change the name so to register that it has been uploaded
            print "file ",file
            print "filename ", filename
            os.rename(file, filename)        
        
    def saveJson(self, filename, data):
        """ 
        This method will dump a json data structure to the filename given.
        
        @type filename: String
        @param filename: path to the .json file that the data will be saved to
        
        @type data: json data
        @param data: Data to be saved to a json file
        """
        
        with open(filename, 'wb') as fp:
            json.dump(data,fp)
        
    def loadJson(self, filename):
        """
        This method will load a json file into memory.
        
        @type filename: String
        @param filename: path to the .json file that is to be loaded into memory
        """
        json_data = open(filename).read()
        data = json.loads(json_data)
        #print data
        return data
        
# executes everything to run, inputs of the command lines
if __name__ == "__main__":
    """
    Script that allows this to be called from the command line
    
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''\
    
        Data Management Program. The following options are available:
        
        upload csv file to MYSQL table
        write csv file to .pcap format
        ''')
        
    parser.add_argument('verb', choices=['upload','pcap','getDataPcap', 'getDataCSV', 'autoUpload', 'test'])
    parser.add_argument('-f','--filename1', help="Filename to upload from")
    parser.add_argument('-s','--filename2', help='Filename to save to')
    parser.add_argument('-t','--table', help="table to upload to SQL")
    parser.add_argument('--sql',help="SQL command to execute")
    
    
    args = parser.parse_args();
    verb = args.verb;
   
    # upload data to SQL server from csv file provided
    if( verb == "test"):
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table="ford_2004")
        dm.testSQLPCAP()
        
    if( verb == "upload"):
        filename = args.filename1
        table = args.table
        if( filename == None or table  == None):
            print " Error: must supply filename(-f) and table to upload to(-t)!"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.uploadData(filename)
        
    # This will automatically upload all the csv files in the ../ThayerData/ folder. The uploaded files will be moved inot a
    # different folder so that they will not be uploaded more than once.
    if( verb == "autoUpload"):
        if( filename == None or table  == None):
            print " Error: must supply filename(-f) and table to upload to(-t)!"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.uploadFiles()
    
    # create a .pcap file from the csv file provided
    if( verb == "pcap"):
        filename1 = args.filename1
        filename2 = args.filename2
        table = "placeHolder"
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.writePcapUpload(filenameUp=filename1, filenameWriteTo=filename2)
    
    #input sql command and get data. saved as a pcap file
    if( verb == "getDataPcap"):
        sql = args.sql
        filename2 = args.filename2
        if( sql == None or filename2 == None):
            print "ERROR: Must enter SQL command as well as filename to save to"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=None)
        data = dm.getData(sql)
        print data
        dm.writeToPcap(filenameWriteTo=filename2, data=data)
    
    #input SQl command and get data.
    if( verb == "getDataCSV" ):
        sql = args.sql
        filename2 = args.filename2
        if( sql == None or filename2 == None):
            print "ERROR: Must enter SQL command as well as filename to save to"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=None)
        data = dm.getData(sql)
        dm.writeDataCsv(data=data, filename=filename2)
        

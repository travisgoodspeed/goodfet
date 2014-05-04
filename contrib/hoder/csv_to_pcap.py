# This program converts a file in our csv format (timestamp, error flag, 16 data bits) and converts it to a format that Wireshark will interpret (.pcap)

import sys
import time
import struct
import csv

    # Function Definitions #
    # This method will take a csv file as the file name and upload it to the MySQL 
    # database in the object. 
class csvReader:
    def uploadData(self,filename):
        
        #load the data from the csv file
        try:
            fileObj = open(filename,'rU')
            data = self.opencsv(fileObj)
            return data
        except:
            print "Unable to open file!"
            return data
    
    # this file will open the csv file and parse out the information according to our standard
    # The returned value is a list of lists. Each row is a packet received and the columns are as defined
    # by our standard
    def opencsv(self,fileObj):
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #this is the header row, we can ignore
            if rownum == 0:
                rownum += 1
                continue
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #timestamp
                if(colnum == 0):
                    packet.append(float(col))
                #error flag
                elif(colnum == 1):
                    packet.append(int(col))
                #datapackets
                else:
                    packet.append(int(col,16))
                colnum += 1
            #print packet
            data.append(packet)
            rownum += 1
        #print data
        return data

# Read in packet
filename = 'csv_test1234.csv'
read_class = csvReader()
data = read_class.uploadData(filename);

# Write to pcap format
# open pcap file to write to
f = open( "fake_gz.pcap", "wb" );
# write global header to file
# d4c3 b2a1 0200 0400 0000 0000 0000 0000 0090 0100 be00 0000
f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xe3\x00\x00\x00")


# write to pcap file
for line in data:
    # packet header creation
    ph = ''
    t = int(time.time())
    ph += struct.pack("<L", t)
    ph += struct.pack("<L", 0x00)
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
print "Data Converted!"

f.close()
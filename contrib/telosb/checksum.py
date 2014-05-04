#!/usr/bin/env python
# Basic Checksumming Utility for GoodFET 802.15.4 Packets
# 
# (C) 2011 Ryan Speers <ryan at rmspeers.com>
#
import re
import sys
import struct

# Takes packet in format such as:
# 0a 03 08 8b ff ff ff ff 07 bf 01 00
# First byte is length of pkt, and may have extra trailing bytes
def parse(data):
    bytes = re.findall(r'[0-9a-fA-F]{2}', data) #keep only hex bytes
    length = int(bytes[0], 16) #first byte is length of pkt
    framelen = len(bytes[1:])
    print "Provided packet indicates length %d and body is of length %d." % (length, framelen)
    if length > framelen:
        bytes = bytes + (["00"] * (length-framelen))
        print "Warning: Input was shorter than length byte specified, it has been padded with null bytes."
    bytes = bytes[1:length+1]
    origCRC = ''.join(bytes[-2:])
    body = [chr(int(x, 16)) for x in bytes[:-2]]
    newCRC = toHex(makeFCS(body))
    print "On packet %s, found original CRC as %s and calculated CRC as %s." % (''.join(bytes), origCRC, newCRC)
    print ''.join(bytes[:-2]) + newCRC

# Do a CRC-CCITT Kermit 16bit on the data given
# Returns a CRC that is the FCS for the frame
#  Implemented using pseudocode from: June 1986, Kermit Protocol Manual
#  See also: http://regregex.bbcmicro.net/crc-catalogue.htm#crc.cat.kermit
def makeFCS(data):
    crc = 0
    for i in range(0, len(data)):
        c = ord(data[i])
        q = (crc ^ c) & 15				#Do low-order 4 bits
        crc = (crc // 16) ^ (q * 4225)
        q = (crc ^ (c // 16)) & 15		#And high 4 bits
        crc = (crc // 16) ^ (q * 4225)
    return struct.pack('<H', crc) #return as bytes in little endian order

# Convert binary data into hex string
def toHex(bin):
	return ''.join(["%02x" % ord(x) for x in bin])

# Command line main
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s '0a 03 08 8b ff ff ff ff 07 bf 01 00'" % sys.argv[0]
    else:
        parse(sys.argv[1])


#!/usr/bin/env python
# GoodFET Chipcon Example
#
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, binascii;

f=sys.argv[1];
file=open(f,mode='rb');

bytes=file.read();

count=range(0,0x10000);

for b in range(0,0x10000):
    count[b]=0;

last=0;
i=0;
j=0;
byte=0;
bits=range(0,len(bytes));
for b in bytes:
    bit=(ord(b)&1);
    byte=((byte<<1)+bit)&0xFF;
    if(i % 8==7):
        sys.stdout.write(chr(byte));
        #print "%02x" % byte;
    i=i+1;

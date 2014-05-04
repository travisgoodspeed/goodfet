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
print "# Histogram from %i bytes." % len(bytes);

count=range(0,0x10000);

for b in range(0,0x10000):
    count[b]=0;

last=0;
for b in bytes:
    count[last+ord(b)]+=1;
    last=(ord(b)<<8);

for b in range(0,0x10000):
    x=b&0xFF;
    y=(b&0xFF00)>>8;
    if count[b]>0:
        print "%i %i %i" % (x, y, count[b]);
        


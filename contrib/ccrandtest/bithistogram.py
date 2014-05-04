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

bits=[1, 2, 4, 8, 16, 32, 64, 128];

count={};

for b in bits:
    count[b]=0;
for b in bytes:
    for bit in bits:
        if ord(b)&bit:
            count[bit]+=1;
i=0;
for b in bits:
    print "%i %f" % (b,(count[b]*1.0/len(bytes)));
    i+=1;


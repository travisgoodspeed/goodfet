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

count={};

for b in range(0,256):
    count[b]=0;
for b in bytes:
    count[ord(b)]+=1;
for b in range(0,256):
    print "%i %f" % (b,(count[b]*1.0/len(bytes)));


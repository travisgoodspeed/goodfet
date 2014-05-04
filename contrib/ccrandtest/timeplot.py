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
print "# Plotting %i bytes." % len(bytes);

count=0;

for b in bytes:
    count+=1;
    print "%i %i" % (count,ord(b));

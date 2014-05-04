#!/usr/bin/env python
# GoodFET Chipcon Example
#
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code dumps the spectrum analyzer data from Mike Ossmann's
# spectrum analyzer firmware.
#
#
#

import sys;

sys.path.append('/Users/travis/svn/goodfet/trunk/client/')

from GoodFETCC import GoodFETCC;
from intelhex import IntelHex16bit, IntelHex;
import time;

client=GoodFETCC();
client.serInit();

client.setup();
client.start();
client.CChaltcpu();
client.CCreleasecpu();

time.sleep(1);

bytestart=0xf000;
bytescount=8*132
maxchan=132;
round=0;

print "time freq rssi rssimax";

while 1:
    time.sleep(0.1);
    client.halt();
    
    round=round+1;
    
    print "# Requesting %i bytes." % bytescount;
    data=client.peekblock(bytestart,bytescount,"xdata");
    client.CCreleasecpu();
    print "# Got %i bytes." % len(data);
    dump="";
    for entry in range(0,maxchan):
        adr=entry*8;
        freq=((data[adr+0]<<16)+
              (data[adr+1]<<8)+
              (data[adr+2]<<0));
        hz=freq*396.728515625;
        mhz=hz/1000000.0
        rssi=data[adr+6];
        rssimax=data[adr+7];
        print "%03i %3.3f %03i %03i" % (round,mhz,rssi,rssimax);
    print dump;
    sys.stdout.flush();
    



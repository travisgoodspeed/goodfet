#!/usr/bin/env python
# GoodFET Chipcon Example
#                                                                                                                                          
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#                                                                                                                                          
# This code dumps the spectrum analyzer data from Mike Ossmann's
# spectrum analyzer firmware.                                                                                                              

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

bytestart=0xf800;
maxchan=132;
round=0;

print "time freq rssi";

while 1:
    time.sleep(1);
    client.CChaltcpu();
    
    round=round+1;
    
    dump="";
    for entry in range(0,maxchan):
        adr=bytestart+entry*8;
        freq=((client.CCpeekdatabyte(adr+0)<<16)+
              (client.CCpeekdatabyte(adr+1)<<8)+
              (client.CCpeekdatabyte(adr+2)<<0));
        hz=freq*396.728515625;
        mhz=hz/1000000.0
        rssi=client.CCpeekdatabyte(adr+6);
        print "%03i %3.3f %03i" % (round,mhz,rssi);
    print dump;
    sys.stdout.flush();
    client.CCreleasecpu();



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

bytescount=8*132;
bytestart=0xf000;

while 1:
    time.sleep(1);
    client.CChaltcpu();
    
    dump="";
    for foo in range(0,bytescount):
        dump=("%s %02x" % (dump,client.CCpeekdatabyte(bytestart+foo)));
        if foo%8==7: dump=dump+"\n";
    print dump;
    sys.stdout.flush();
    client.CCreleasecpu();



#!/usr/bin/env python2
# GoodFET Chipcon Example
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys;
import binascii, time;

from GoodFETCC import GoodFETCC;
from GoodFETConsole import GoodFETConsole;
from intelhex import IntelHex;


def printpacket(packet):
    s="";
    i=0;
    for foo in packet:
        i=i+1;
        s="%s %02x" % (s,foo);
    print "# %s" %s;

simplepacketcount=0;
def handlesimplicitipacket(packet):
    s="";
    i=0;
    global simplepacketcount;
    simplepacketcount=simplepacketcount+1;
    
    len=packet[0];
    if len<12: return;
    
    dst=[packet[1],
             packet[2],
             packet[3],
             packet[4]];
    src=[packet[5],
             packet[6],
             packet[7],
             packet[8]];
    port=packet[9];
    info=packet[10];
    seq=packet[11];
    #payload begins at byte 10.
    
    if packet[len+2]&0x80==0:
        print "# Dropped broken packet.";
    elif port==0x20:
        #data packet
        counter=packet[11];
        button=packet[12];
        x=packet[13];
        if x>=128: x=0-(x^0xFF)-1;
        y=packet[14];
        if y>=128: y=0-(y^0xFF)-1;
        z=packet[15];
        if z>=128: z=0-(z^0xFF)-1;
        
        print "%09i %03i %4i %4i %4i" % (simplepacketcount,button,x,y,z);
        sys.stdout.flush();
    elif port==0x02:
        #Link request.  Gotta send a proper reply to get data.
        tid=packet[13];
        #14 ff ff ff ff 3c b7 e3 98 
        #02 03 c9
        #01 97
        #ef be ad de 3d 00 02 
        reply=[0x10,
               src[0], src[1], src[2], src[3],
               0x78,0x56,0x34,0x10, #my address.
               port, 0x21, seq,
               0x81, tid,         #reply, tid
               
               0x20,0x00,0xad,0xde, #link token
               0x00];               #no security
        #printpacket(reply);
        print "#FIXME FAST: repeatedly broadcasting ACK to catch LINK on the next attempt.";
        for foo in range(1,50):
            client.RF_txpacket(reply);
        
        pass;
    elif port==0x03:
        #print "Join request.";
        #printpacket(packet);
        if packet[12]!=1:
            print "Not a join request.  WTF?";
            return;
        tid=packet[13];
        reply=[0x12, #reply is one byte shorter
               src[0], src[1], src[2], src[3],
               0x78,0x56,0x34,0x10, #my address.
               port, 0x21, seq,
               0x81, tid,         #reply, tid
               
               0xef,0xbe,0xad,0xde, #Join token
               0x00];             #no security
        #printpacket(reply);
        print "#FIXME FAST: repeatedly broadcasting ACK to catch JOIN on the next attempt.";
        #printpacket(reply);
        for foo in range(1,20):
            client.RF_txpacket(reply);
        print "#Should be connected now.";
        
    elif port==0x04:
        print "Security request.";
    elif port==0x05:
        print "Frequency request.";
    elif port==0x06:
        print "Management request.";
    else:
        print "Unknown Port %02x" %port;
    
if(len(sys.argv)==1):
    print "Usage: %s verb [objects]\n" % sys.argv[0];
    print "%s erase" % sys.argv[0];
    print "%s flash $foo.hex" % sys.argv[0];
    print "%s test" % sys.argv[0];
    print "%s term" % sys.argv[0];
    print "    use \'?\' for list of commands";
    print "%s info" % sys.argv[0];
    print "%s infotest" % sys.argv[0];
    print "%s radioinfo [help] [REGISTER_NAME]" % sys.argv[0];
    print "%s specfuncreg [SPECIAL_REGISTER_NAME]" % sys.argv[0];
    print "%s halt"  % sys.argv[0];
    print "%s regs" % sys.argv[0];
    print "%s dumpcode $foo.hex [0x$start 0x$stop]" % sys.argv[0];
    print "%s dumpdata $foo.hex [0x$start 0x$stop]" % sys.argv[0];
    print "%s writedata $foo.hex [0x$start 0x$stop]" % sys.argv[0];
    print "%s verify $foo.hex [0x$start 0x$stop]" % sys.argv[0];
    print "%s peekdata 0x$start [0x$stop]" % sys.argv[0];
    print "%s pokedata 0x$adr 0x$val" % sys.argv[0];
    print "%s peek 0x$iram" % sys.argv[0];
    print "%s poke 0x$iram 0x$val" % sys.argv[0];
    print "%s peekcode 0x$start [0x$stop]" % sys.argv[0];
    print "\n"
    print "%s specan [freq]\n\tSpectrum Analyzer" % sys.argv[0];
    print "%s rssi [freq]\n\tGraphs signal strength on [freq] Hz." % sys.argv[0];
    print "%s carrier [freq]\n\tHolds a carrier on [freq] Hz." % sys.argv[0];
    print "%s reflex [freq]\n\tJams on [freq] Hz." % sys.argv[0];
    print "%s sniffsimpliciti [us|eu|lf]\n\tSniffs SimpliciTI packets." % sys.argv[0];
    print "%s sniffdash7 [lf]\n\tSniffs Dash7. (untested)" % sys.argv[0];
    print "%s snifficlicker [us]\n\tSniffs iClicker." % sys.argv[0];
    print "\n";
    print "%s simpliciti [us|eu|lf]\n\tSimpliciti access point for Chronos watch." % sys.argv[0];
    print "%s iclicker [us|eu|lf]\n\tSniffs iClicker packets as ASCII." % sys.argv[0];
    
    sys.exit();

#Initailize FET and set baud rate
#client=GoodFET.GoodFETCC.GoodFETCC();
client=GoodFETCC();
client.serInit()

#Connect to target
client.setup();
client.start();

#client.halt();
#client.pokebyte(0xc7,0x08);

if(sys.argv[1]=="carrier"):
    if len(sys.argv)>2:
        client.RF_setfreq(eval(sys.argv[2]));
    client.RF_carrier();
    while(1):
        time.sleep(1);

if(sys.argv[1]=="reflex"):
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_simpliciti();
    
    threshold=100;
    if len(sys.argv)>2:
        client.RF_setfreq(eval(sys.argv[2]));
    print "Listening on %f MHz." % (client.RF_getfreq()/10**6);
    print "Jamming if RSSI>=%i" % threshold;
    
    client.pokebyte(0xFE00,threshold,"xdata"); #Write threshold to shellcode.
    client.shellcodefile("reflex.ihx");
    rssi=0;
    while 1:
        while(0==client.ishalted()):
            rssi=0;
        rssi=client.peek8(0xFE00,"xdata");
        print "Activated jamming with RSSI of %i, going again for another packet." % rssi;
        client.resume();
    

if(sys.argv[1]=="rssi"):
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_simpliciti();
    
    if len(sys.argv)>2:
        client.RF_setfreq(eval(sys.argv[2]));
    print "Listening on %f MHz." % (client.RF_getfreq()/10.0**6);
        
    #FIXME, ugly
    RFST=0xDFE1
    client.CC_RFST_CAL();
    time.sleep(1);
    
    while 1:
        client.CC_RFST_RX();
        rssi=client.RF_getrssi();
        client.CC_RFST_IDLE(); #idle
        time.sleep(0.01);
        string="";
        for foo in range(0,rssi>>2):
            string=("%s."%string);
        print "%02x %04i %s" % (rssi,rssi, string); 
if(sys.argv[1]=="specan"):
    print "This doesn't work yet."
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_simpliciti();
    
    if len(sys.argv)>2:
        client.RF_setfreq(eval(sys.argv[2]));
    #print "Listening on %f MHz." % (client.RF_getfreq()/10.0**6);
    
    client.CChaltcpu();
    client.shellcodefile("specan.ihx",wait=0);
    #client.shellcodefile("crystal.ihx",wait=1);
    
    bytestart=0xf800;
    maxchan=10;
    round=0;
    
    print "time freq rssi";
    
    while 1:
        time.sleep(1);
        #client.CChaltcpu();
        
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


if(sys.argv[1]=="sniff"):
    client.CC1110_crystal();
    client.RF_idle();
    
    #client.config_simpliciti(region);
    
    print "Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        sys.stdout.flush();

if(sys.argv[1]=="sniffsimpliciti"):
    region="us";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_simpliciti(region);
    
    print "Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        sys.stdout.flush();
if(sys.argv[1]=="sniffook"):
    region="lf";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_ook(region);
    
    print "Listening for OOK on %f MHz" % (client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        sys.stdout.flush();
if(sys.argv[1]=="sniffdash7"):
    region="lf";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_dash7(region);
    
    print "Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        sys.stdout.flush();
if(sys.argv[1]=="snifficlicker"):
    region="us";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_iclicker(region);
    
    print "Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        sys.stdout.flush();
if(sys.argv[1]=="iclicker"):
    buttons=[0, 'A', 'j', 3, 4, 'B',
             6, 7, 8, 9, 'E', 0xB, 0xC,
             'C', 'D', 0xF];
    region="us";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_iclicker(region);
    
    print "Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        printpacket(packet);
        button=((packet[5]&1)<<3) | (packet[6]>>5);
        print "Button %c" % buttons[button];
        sys.stdout.flush();

if(sys.argv[1]=="simpliciti"):
    region="us";
    if len(sys.argv)>2:
        region=sys.argv[2];
    
    client.CC1110_crystal();
    client.RF_idle();
    
    client.config_simpliciti(region);
    
    print "# Listening as %x on %f MHz" % (client.RF_getsmac(),
                                           client.RF_getfreq()/10.0**6);
    #Now we're ready to get packets.
    while 1:
        packet=None;
        while packet==None:
            packet=client.RF_rxpacket();
        handlesimplicitipacket(packet);
        sys.stdout.flush();



if(sys.argv[1]=="term"):
    GoodFETConsole(client).run();
if(sys.argv[1]=="test"):
    client.test();
if(sys.argv[1]=="deadtest"):
    for i in range(1,10):
        print "IDENT as %s" % client.CCidentstr();
if(sys.argv[1]=="dumpcode"):
    f = sys.argv[2];
    start=0x0000;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    print "Dumping code from %04x to %04x as %s." % (start,stop,f);
    h = IntelHex(None);
    i=start;
    while i<=stop:
        h[i]=client.CCpeekcodebyte(i);
        if(i%0x100==0):
            print "Dumped %04x."%i;
        i+=1;
    h.write_hex_file(f);
if(sys.argv[1]=="dumpdata"):
    f = sys.argv[2];
    start=0xE000;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    print "Dumping data from %04x to %04x as %s." % (start,stop,f);
    h = IntelHex(None);
    i=start;
    while i<=stop:
        h[i]=client.CCpeekdatabyte(i);
        if(i%0x100==0):
            print "Dumped %04x."%i;
        i+=1;
    h.write_hex_file(f);
if(sys.argv[1]=="status"):
    print "Status: %s" %client.status();
if(sys.argv[1]=="halt"):
    print "Halting CPU."
    client.halt();

if(sys.argv[1]=="infotest"):
    while 1:
        client.start();
        print "Ident   %s" % client.CCidentstr();
if(sys.argv[1]=="info"):
    print "Ident   %s" % client.CCidentstr();
    
    try:
        print "Freq    %10.3f MHz" % (client.RF_getfreq()/10**6);
        print "RSSI    %02x" % client.RF_getrssi();
    except:
        print "Freq, RSSI, etc unknown.  Install SmartRF7.";
    #print "Rate    %10i kbps" % (client.RF_getrate()/1000);
    #print "PacketLen %02i bytes" % client.RF_getpacketlen();
    #print "SMAC  0x%010x" % client.RF_getsmac();
    #print "TMAC  0x%010x" % client.RF_gettmac();

if(sys.argv[1]=="radioinfo"):
    if (len(sys.argv) - 2) > 0:
        client.CMDrs(sys.argv[2:]);
    else:
        client.CMDrs();

if(sys.argv[1]=="regs"):
    client.CMDrs();

if(sys.argv[1]=="erase"):
    print "Status: %s" % client.status();
    client.CCchiperase();
    print "Status: %s" %client.status();

if(sys.argv[1]=="peekinfo"):
    print "Select info flash."
    client.CCwr_config(1);
    print "Config is %02x" % client.CCrd_config();
    
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekcodebyte(start));
        start=start+1;
if(sys.argv[1]=="poke"):
    client.CCpokeirambyte(int(sys.argv[2],16),
                          int(sys.argv[3],16));
if(sys.argv[1]=="randtest"):
    #Seed RNG
    client.CCpokeirambyte(0xBD,0x01); #RNDH=0x01
    client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
    client.CCpokeirambyte(0xBD,0x01); #RNDH=0x01
    client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
    
    #Dump values
    for foo in range(1,10):
        print "%02x" % client.CCpeekirambyte(0xBD); #RNDH
        client.CCpokeirambyte(0xB4,0x04); #ADCCON1=0x04
        client.CCreleasecpu();
        client.CChaltcpu();
    print "%02x" % client.CCpeekdatabyte(0xDF61); #CHIP ID
if(sys.argv[1]=="adctest"):
    # ADCTest 0xDF3A 0xDF3B
    print "ADC TEST %02x%02x" % (
        client.CCpeekdatabyte(0xDF3A),
        client.CCpeekdatabyte(0xDF3B));
if(sys.argv[1]=="config"):
    print "Config is %02x" % client.CCrd_config();

if(sys.argv[1]=="specfuncreg" or sys.argv[1]=="sfr"):
    if len(sys.argv) > 2:
        client.getSPR(sys.argv[2:]);
    else:
        client.getSPR();

if(sys.argv[1]=="flash"):
     f=sys.argv[2];
     start=0;
     stop=0xFFFF;
     if(len(sys.argv)>3):
         start=int(sys.argv[3],16);
     if(len(sys.argv)>4):
         stop=int(sys.argv[4],16);
   
     client.flash(f);
if(sys.argv[1]=="lock"):
    print "Status: %s" %client.status();
    client.CClockchip();
    print "Status: %s" %client.status();
if(sys.argv[1]=="flashpage"):
    target=0;
    if(len(sys.argv)>2):
        target=int(sys.argv[2],16);
    print "Writing a page of flash from 0xF000 in XDATA"
    client.CCflashpage(target);
if(sys.argv[1]=="erasebuffer"):
    print "Erasing flash buffer.";
    client.CCeraseflashbuffer();

if(sys.argv[1]=="writedata"):
    f=sys.argv[2];
    start=0;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    h = IntelHex(f);
    
    for i in h._buf.keys():
        if(i>=start and i<=stop):
            client.CCpokedatabyte(i,h[i]);
            if(i%0x100==0):
                print "%04x" % i;
#if(sys.argv[1]=="flashtest"):
#    client.CCflashtest();
if(sys.argv[1]=="peekdata"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekdatabyte(start));
        start=start+1;
if(sys.argv[1]=="peek"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekirambyte(start));
        start=start+1;
if(sys.argv[1]=="verify"):
    f=sys.argv[2];
    start=0;
    stop=0xFFFF;
    if(len(sys.argv)>3):
        start=int(sys.argv[3],16);
    if(len(sys.argv)>4):
        stop=int(sys.argv[4],16);
    
    h = IntelHex(f);
    for i in h._buf.keys():
        if(i>=start and i<stop):
            peek=client.CCpeekcodebyte(i)
            if(h[i]!=peek):
                print "ERROR at %04x, found %02x not %02x"%(i,peek,h[i]);
            if(i%0x100==0):
                print "%04x" % i;
if(sys.argv[1]=="peekcode"):
    start=0x0000;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    stop=start;
    if(len(sys.argv)>3):
        stop=int(sys.argv[3],16);
    print "Peeking from %04x to %04x." % (start,stop);
    while start<=stop:
        print "%04x: %02x" % (start,client.CCpeekcodebyte(start));
        start=start+1;
if(sys.argv[1]=="pokedata"):
    start=0x0000;
    val=0x00;
    if(len(sys.argv)>2):
        start=int(sys.argv[2],16);
    if(len(sys.argv)>3):
        val=int(sys.argv[3],16);
    print "Poking %04x to become %02x." % (start,val);
    client.CCpokedatabyte(start,val);

client.stop();

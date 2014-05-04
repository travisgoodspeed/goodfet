#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

char __xdata at 0xfdf0 cfg[5] ;
char __xdata at 0xfdf8 freq[3] ;
//! Save MDMCFG*
void save_settings(){
  cfg[0]=MDMCFG0;
  cfg[1]=MDMCFG1;
  cfg[2]=MDMCFG2;
  cfg[3]=MDMCFG3;
  cfg[4]=MDMCFG4;
  /*
  freq[0]=FREQ0;
  freq[1]=FREQ1;
  freq[2]=FREQ2;
  */
}
//! Restore MDMCFG*
void restore_settings(){
  MDMCFG0=cfg[0];
  MDMCFG1=cfg[1];
  MDMCFG2=cfg[2];
  MDMCFG3=cfg[3];
  MDMCFG4=cfg[4];
  /*
  FREQ0=freq[0];
  FREQ1=freq[1];
  FREQ2=freq[2];
  */
}

void carrier(){
  // Set the system clock source to HS XOSC and max CPU speed,
  // ref. [clk]=>[clk_xosc.c]
  /*
  SLEEP &= ~SLEEP_OSC_PD;
  while( !(SLEEP & SLEEP_XOSC_S) );
  CLKCON = (CLKCON & ~(CLKCON_CLKSPD | CLKCON_OSC)) | CLKSPD_DIV_1;
  while (CLKCON & CLKCON_OSC);
  SLEEP |= SLEEP_OSC_PD;
  */

  //FREQ0=0x5C;
  
  /* Setup radio with settings from SmartRF® Studio. The default settings are
   * used, except that "unmodulated" is chosen in the "Simple RX tab". This
   * results in an umodulated carrier with a frequency of approx. 2.433 GHz.
   */
  //FSCTRL1   = 0x0A;   // Frequency synthesizer control.
  //FSCTRL0   = 0x00;   // Frequency synthesizer control.
  
  
  //Bandwidth, Symbol Rate
  //MDMCFG4   = 0x86;
  //Symbol Rate
  //MDMCFG3   = 0x83;
  //Sensitivity, shift-keying mode
  //MDMCFG2   = 0x30;
  //FEC, Premable, Spacing
  //MDMCFG1   = 0x22;
  //Channel Spacing
  //MDMCFG0   = 0xF8;
  
  /* Settings not from SmartRF® Studio. Setting both sync word registers to
   * 0xAA = 0b10101010, i.e., the same as the preamble pattern. Not necessary,
   * but gives control of what the radio attempts to transmit.
   */
  
  //These sync values are better for jamming, but they break reception.
  //SYNC1     = 0xAA;
  //SYNC0     = 0xAA;
  
#define RFON RFST = RFST_SIDLE; RFST = RFST_STX; while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_TX);
#define RFOFF RFST = RFST_SIDLE; //while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_IDLE);
  //RFON;
  //while(1);
}


void sleepMillis(int ms) {
  int j;
  while (--ms > 0) { 
    for (j=0; j<1200;j++); // about 1 millisecond
  };
}


//! Reflexively jam on the present channel by responding to a signal with a carrier wave.
void main(){
  unsigned char threshold=packet[0], i=0, rssi=0;;
  
  //Disable interrupts.
  RFTXRXIE=0;
  
  save_settings();
  
  //carrier();
  
  
  while(1){
    //idle a bit.
    RFST=RFST_SIDLE;
    while(MARCSTATE!=MARC_STATE_IDLE);
    
    restore_settings();
    //idle a bit, unecessary
    //RFST=RFST_SFSTXON;
    //while(MARCSTATE!=MARC_STATE_FSTXON);
    
    //sleepMillis(100);
    rxwait();
    
    //idle w/ oscillator
    //RFST=RFST_SFSTXON;
    //while(MARCSTATE!=MARC_STATE_FSTXON);
    
    
    //Transmit carrier for 10ms
    carrier();
    RFON;
    //HALT;
    //while(1);
    //sleepMillis(200);
    //sleepMillis(100);
    //sleepMillis(50);
    
    
    sleepMillis(10);
    //HALT;
  }
}

//! Receives a packet out of the radio from 0xFE00.
void rxwait(){
  unsigned char len=16, i=0;
  
  //Test to always carry.
  //return;
  
  do{
    //1-out the buffer.
    for(i=0;i<64;i++)
      packet[i]=0xFF;
    i=0;
    
    //Disable interrupts.
    RFTXRXIE=0;
    
    //idle a bit.
    RFST=RFST_SIDLE;
    while(MARCSTATE!=MARC_STATE_IDLE);
    
    //Begin to receive.
    RFST=RFST_SRX;
    while(MARCSTATE!=MARC_STATE_RX);
    
    //RFST = RFST_SIDLE; //End receive.
    //return;
    
    
    //Fixed length
    packet[i++]=PKTLEN;
    while(i<3){ //PKTLEN){
      while(!RFTXRXIF); //Wait for byte to be ready.
      RFTXRXIF=0;      //Clear the flag.
      
      packet[i++]=RFD; //Grab the next byte.
    }
    
    RFST = RFST_SIDLE; //End receive.
    
    //This while loop can be used for filtering.  Unused for now.
  }while(0); //packet[0]==(char) 0x0f || packet[1]==(char) 0xFF || packet[9]==(char) 0x03);
}



#include <cc1110.h>
#include "cc1110-ext.h"

#define MAXLEN 0xFF
char __xdata at 0xfe00 packet[MAXLEN] ;

//! Receives a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=16, i=0;
  
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
    
    //Fixed length
    packet[i++]=PKTLEN;
    while(i<PKTLEN){
      while(!RFTXRXIF); //Wait for byte to be ready.
      RFTXRXIF=0;      //Clear the flag.
      
      packet[i++]=RFD; //Grab the next byte.
    }
    
    RFST = RFST_SIDLE; //End receive.
    
    //This while loop can be used for filtering.  Unused for now.
  }while(0);//packet[1]!=(char) 0xdd || packet[2]!=(char) 0x55);
  
  HALT;
}


#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

//! Transmit a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=packet[0], i=0, j;

  //idle a bit.
  RFST=RFST_SIDLE;
  while(MARCSTATE!=MARC_STATE_IDLE);
  
  RFST=RFST_STX;     //Begin transmit.
  i=0;
  while(i!=len+1){
    while(!RFTXRXIF); //Wait for byte to be ready.
    
    RFTXRXIF=0;      //Clear the flag.
    RFD=packet[i++]; //Send the next byte.
  }
  
  //Wait for completion.
  while(MARCSTATE==MARC_STATE_TX);
  
  //RFST = RFST_SIDLE; //End transmit.
  //while(MARCSTATE!=MARC_STATE_IDLE);
  
  //Begin to receive.
  RFST=RFST_SRX;
  while(MARCSTATE!=MARC_STATE_RX);
  i=0;len=16;
  while(i<len+1){
    while(!RFTXRXIF); //Wait for byte to be ready.
    RFTXRXIF=0;      //Clear the flag.
    
    if (MARCSTATE == MARC_STATE_RX) {
      packet[i]=RFD; //Grab the next byte.
      i++;
      len=packet[0];   //First byte of the packet is the length.
    }else
      HALT;

  }
  RFST = RFST_SIDLE; //End receive.
  HALT;
}

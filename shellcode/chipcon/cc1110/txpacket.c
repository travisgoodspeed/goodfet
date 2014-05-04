#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

void sleepMillis(int ms) {
	int j;
	while (--ms > 0) { 
		for (j=0; j<1200;j++); // about 1 millisecond
	};
}

//! Transmit a packet out of the radio from 0xFE00.
void main(){
  unsigned char len=packet[0], i=0;
  long j;
  
  //Disable interrupts.
  RFTXRXIE=0;
  
  //idle a bit.
  RFST=RFST_SIDLE;
  while(MARCSTATE!=MARC_STATE_IDLE);
  
  
  RFST=RFST_STX;     //Begin transmit.
  while(MARCSTATE!=MARC_STATE_TX);
  
  while(i<len+1){
    while(!RFTXRXIF); //Wait for byte to be ready.
    while(MARCSTATE!=MARC_STATE_TX); //Lockup if needed.
    RFTXRXIF=0;      //Clear the flag.
    RFD=packet[i++]; //Send the next byte.
  }
  
  //Wait for transmission to complete.
  while(MARCSTATE==MARC_STATE_TX);

  //RFST = RFST_SIDLE; //End transmit.
  HALT;
}

/*! \file command.c
  \author Travis Goodspeed
  \brief These functions manage command interpretation and timing.
*/

#include "command.h"
#include "platform.h"
#include <string.h>

unsigned char cmddata[CMDDATALEN];
unsigned char silent=0;

//! Transmit a string.
void txstring(unsigned char app,
	      unsigned char verb,
	      const char *str){
  unsigned long len=strlen(str);
  txhead(app,verb,len);
  while(len--)
    serial_tx(*(str++));
}

/*! \brief Transmit a debug string.
  
  Transmits a debugging string that is to be printed
  out of line by the client.  This is just for record-keeping;
  it is not considered a proper reply to a query.
 */
void debugstr(const char *str){
  txstring(0xFF,0xFF,str);
}

//! brief Debug a hex word string.
void debughex(u16 v) {
  debugbytes((void *)&v, 2);
}

//! brief Debug a hex word string.
void debughex32(u32 v) {
  debugbytes((void *)&v, 4);
}

/*! \brief Transmit debug bytes.
  
  Transmits bytes for debugging.
*/
void debugbytes(const char *bytes, unsigned int len){
  u16 i;
  txhead(0xFF,0xFE,len);
  for(i=0;i<len;i++)
    serial_tx(bytes[i]);
}


//! Transmit a header.
void txhead(unsigned char app,
	    unsigned char verb,
	    unsigned long len){
  serial_tx(app);
  serial_tx(verb);
  //serial_tx(len); //old protocol
  txword(len);
}

//! Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned long len){
  unsigned long i=0;
  if(silent)
    return;
  txhead(app,verb,len);
  for(i=0;i<len;i++){
    serial_tx(cmddata[i]);
  }
}

//! Receive a long.
unsigned long rxlong(){
  unsigned long toret=0;
  toret=serial_rx();
  toret|=(((long)serial_rx())<<8);
  toret|=(((long)serial_rx())<<16);
  toret|=(((long)serial_rx())<<24);
  return toret;
}
//! Receive a word.
unsigned int rxword(){
  unsigned long toret=0;
  toret=serial_rx();
  toret|=(((long)serial_rx())<<8);
  return toret;
}
//! Transmit a long.
void txlong(unsigned long l){
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
}
//! Transmit a word.
void txword(unsigned int l){
  serial_tx(l&0xFF);
  l>>=8;
  serial_tx(l&0xFF);
  l>>=8;
}

//Be very careful changing delay().
//It was chosen poorly by trial and error.

//! Delay for a count.
void delay(unsigned int count){
  volatile unsigned int i=count;
  while(i--) asm("nop");
}
//! MSDelay
void msdelay(unsigned int ms){
  volatile unsigned int i,j;
  i=100;
  while(i--){
    j=ms;
    while(j--) asm("nop");
  }
  //Using TimerA might be cleaner.
}


/* To better satisfy the somewhat odd timing requirements for
   PIC33F/24H/24F ICSP programming, and for better control of GoodFET
   timing more generally, here are a few delay routines that use Timer B.

   Note that I wrote these referring only to the MSP430x2xx family
   manual. Beware on MSP430x1xx chips. Further note that, assuming
   some minor errors will be made, I try to err on the side of
   delaying slightly longer than requested. */
void prep_timer()
{
  #ifdef MSP430
  BCSCTL2 = 0x00; /* In particular, use DCOCLK as SMCLK source with
		     divider 1. Hence, Timer B ticks with system
		     clock at 16 MHz. */

  TBCTL = 0x0204; /* Driven by SMCLK; disable Timer B interrupts;
		     reset timer in case it was previously in use */
  #else
  #warning "prep_timer() unimplemented for this platform."
  #endif
}
#if (platform != tilaunchpad)
//! Delay for specified number of milliseconds (given 16 MHz clock)
void delay_ms( unsigned int ms )
{
  #ifdef MSP430
  // 16000 ticks = 1 ms
  TBCTL |= 0x20; // Start timer!
  while (ms--) {
    while (TBR < 16000)
      asm( "nop" );
    TBCTL = 0x0224;
  }
  TBCTL = 0x0204; // Reset Timer B, till next time
  #else
  debugstr("delay_ms unimplemented");
  #endif
}

//! Delay for specified number of microseconds (given 16 MHz clock)
void delay_us( unsigned int us )
{
  #ifdef MSP430
  // 16 ticks = 1 us
  TBCTL |= 0x20; // Start timer!
  while (us--) {
    while (TBR < 16)
      asm( "nop" );
    TBCTL = 0x0224;
  }
  TBCTL = 0x0204; // Reset Timer B, till next time
  #else
  debugstr("delay_us unimplemented");
  #endif
}

//! Delay for specified number of clock ticks (16 MHz clock implies 62.5 ns per tick).
void delay_ticks( unsigned int num_ticks )
{
  #ifdef MSP430
  TBCTL |= 0x20; // Start timer
  while (TBR < num_ticks)
    asm( "nop" );
  TBCTL = 0x0204; // Reset Timer B, till next time
  #else
  debugstr("delay_ticks unimplemented");
  #endif
}
#endif

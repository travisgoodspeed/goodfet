#include<cc2430.h>

#define u8 unsigned char
#define u16 unsigned int

//! Get CHIP ID
u8 halRfGetChipId(void){
    return CHIPID;
}

// Various radio settings
#define ADR_DECODE              0x08
#define AUTO_CRC                0x20
#define AUTO_ACK                0x10
#define AUTO_TX2RX_OFF          0x08
#define RX2RX_TIME_OFF          0x04
#define ACCEPT_ACKPKT           0x01

// Selected strobes
#define ISRXON()                RFST = 0xE2;
#define ISTXON()                RFST = 0xE3;
#define ISTXONCCA()             RFST = 0xE4;
#define ISRFOFF()               RFST = 0xE5;
#define ISFLUSHRX()             RFST = 0xE6;
#define ISFLUSHTX()             RFST = 0xE7;

#define FLUSH_RX_FIFO()         ISFLUSHRX(); ISFLUSHRX();


//! Wait for things to start up.
void hangout(){
  unsigned long counter=0;
  while(counter++<0xFFFF);
}


//! Initialize RF and RNG
u8 halRfInit(void){
    u8 i;

    // turning on power to analog part of radio and waiting for voltage regulator.
    RFPWR = 0x04;
    while( RFPWR & 0x10 );

    // Setting for AUTO CRC and AUTOACK
    MDMCTRL0L |= (AUTO_CRC | AUTO_ACK);

    // Turning on AUTO_TX2RX
    FSMTC1 = ((FSMTC1 & (~AUTO_TX2RX_OFF & ~RX2RX_TIME_OFF))  | ACCEPT_ACKPKT);

    // Turning off abortRxOnSrxon.
    FSMTC1 &= ~0x20;

    // Set FIFOP threshold to maximum
    IOCFG0 = 0x7F;
    // tuning adjustments for optimal radio performance; details available in datasheet */
    RXCTRL0H = 0x32;
    RXCTRL0L = 0xF5;

    // Turning on receiver to get output from IF-ADC
    ISRXON();
    //halMcuWaitUs(1);
    hangout();//Without delay, values are always the same.
    
    // Enable random generator
    ADCCON1 &= ~0x0C;

    for(i = 0 ; i < 32 ; i++)
    {
      RNDH = ADCTSTH;
      
      // Clock random generator
      ADCCON1 |= 0x04;
    }
    //ISRFOFF();

    // Enable CC2591 with High Gain Mode
    //halPaLnaInit();

    //halRfEnableRxInterrupt();

    return 1;
}

//! Get a random byte from the LFSR.
u8 halRfGetRandomByte(void){
  // Clock the random generator
  
  /* PRNG
  ADCCON1 |= 0x04;
  return RNDH;
  */
  return ADCTSTH;
}


#define BYTECOUNT 64

u16 randcode, randcount;
u8 rands[BYTECOUNT];
void main(){
  long a;
  
  //Seems to seed with zeroes.
  halRfInit();
  
  randcount=0;
  while(1){
    //Data is invalid.
    randcode=0xdead;
    
    for(a=0;a<BYTECOUNT;a++)
      //Uncomment one of the following lines.
      //rands[a]=ADCTSTL;
      rands[a]=halRfGetRandomByte();
    
    //Data is valid.
    randcode=0xbeef;
    
    //Soft Break
    _asm
      .byte 0xa5
      _endasm;
    randcount++;
  }
}

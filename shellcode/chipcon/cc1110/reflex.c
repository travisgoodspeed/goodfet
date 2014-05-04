#include <cc1110.h>
#include "cc1110-ext.h"

char __xdata at 0xfe00 packet[256] ;

void carrier(){
  // Set the system clock source to HS XOSC and max CPU speed,
  // ref. [clk]=>[clk_xosc.c]
  SLEEP &= ~SLEEP_OSC_PD;
  while( !(SLEEP & SLEEP_XOSC_S) );
  CLKCON = (CLKCON & ~(CLKCON_CLKSPD | CLKCON_OSC)) | CLKSPD_DIV_1;
  while (CLKCON & CLKCON_OSC);
  SLEEP |= SLEEP_OSC_PD;


  /* Setup radio with settings from SmartRF® Studio. The default settings are
   * used, except that "unmodulated" is chosen in the "Simple RX tab". This
   * results in an umodulated carrier with a frequency of approx. 2.433 GHz.
   */
  FSCTRL1   = 0x0A;   // Frequency synthesizer control.
  FSCTRL0   = 0x00;   // Frequency synthesizer control.
  
  
    
  MDMCFG4   = 0x86;   // Modem configuration.
  MDMCFG3   = 0x83;   // Modem configuration.
  MDMCFG2   = 0x30;   // Modem configuration.
  MDMCFG1   = 0x22;   // Modem configuration.
  MDMCFG0   = 0xF8;   // Modem configuration.
  CHANNR    = 0x00;   // Channel number.
  DEVIATN   = 0x00;   // Modem deviation setting (when FSK modulation is enabled).
  FREND1    = 0x56;   // Front end RX configuration.
  FREND0    = 0x10;   // Front end RX configuration.
  MCSM0     = 0x14;   // Main Radio Control State Machine configuration.
  FOCCFG    = 0x16;   // Frequency Offset Compensation Configuration.
  BSCFG     = 0x6C;   // Bit synchronization Configuration.
  AGCCTRL2  = 0x03;   // AGC control.
  AGCCTRL1  = 0x40;   // AGC control.
  AGCCTRL0  = 0x91;   // AGC control.
  FSCAL3    = 0xE9;   // Frequency synthesizer calibration.
  FSCAL2    = 0x2a;   // Frequency synthesizer calibration.
  FSCAL1    = 0x00;   // Frequency synthesizer calibration.
  FSCAL0    = 0x1f;   // Frequency synthesizer calibration
  
  TEST2     = 0x88;   // Various test settings.
  TEST1     = 0x31;   // Various test settings.
  TEST0     = 0x09;   // Various test settings.
  
  //FE is too high
  PA_TABLE0 = 0xFF;   // PA output power setting.
  PKTCTRL1  = 0x04;   // Packet automation control.
  PKTCTRL0  = 0x22;   // Packet automation control.
  ADDR      = 0x00;   // Device address.
  PKTLEN    = 0xFF;   // Packet length.

  /* Settings not from SmartRF® Studio. Setting both sync word registers to
   * 0xAA = 0b10101010, i.e., the same as the preamble pattern. Not necessary,
   * but gives control of what the radio attempts to transmit.
   */
  SYNC1     = 0xAA;
  SYNC0     = 0xAA;

  /* Put radio in TX. 
  RFST      = RFST_STX;
  while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_TX);
  */

  
#define RFON RFST = RFST_SIDLE; RFST = RFST_STX; while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_TX);
#define RFOFF RFST = RFST_SIDLE; //while ((MARCSTATE & MARCSTATE_MARC_STATE) != MARC_STATE_IDLE);
  //RFON;
  //while(1);  
  
  
}


void sleepMillis(int ms) {
  int j,k;
  //k=1000;
  //while(--k>0)
  while (--ms > 0) { 
    for (j=0; j<1200;j++); // about 1 millisecond
  };
}

//! Reflexively jam on the present channel by responding to a signal with a carrier wave.
void main(){
  unsigned char threshold=packet[0], i=0, rssi=0;;
  //Disable interrupts.
  RFTXRXIE=0;

    
  carrier();
  sleepMillis(10);
  //RFON;
  
  while(1){
    
    
    //RFOFF;
    

    //Wait for the transmission.
    RFST=RFST_SRX;
    while(MARCSTATE!=MARC_STATE_RX);
    rssi=0;
    
    
    //Wait for RSSI to settle.
    sleepMillis(100);
    //RFOFF;
    
    
    //Delay until the RSSI is above the threshold.
    while(rssi<threshold){
      sleepMillis(1);
      rssi=RSSI^0x80;
      packet[0]=rssi;
      HALT;
    }
    
    RFON;
    HALT;
    while(1);
    
    
    HALT;
    //tx carrier for 10 ms
    
    RFON;
    while(1);
    RFOFF;
    sleepMillis(1000);
    
    
    while(1);
    //Carrier will clear when the loop continue,
    //but we can HALT to give the host a chance to take over.
    //HALT;
  }  
  //RFST = RFST_SIDLE; //End transmit.
  
  HALT;
}

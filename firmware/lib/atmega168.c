//! MSP430F1612/1611 clock and I/O definitions

#include "platform.h"

#include <avr/io.h>
#include <util/delay.h>

//! Receive a byte.
unsigned char serial0_rx(){
  while( !(UCSR0A & (1 << RXC0)) );
  return UDR0;
}

//! Receive a byte.
unsigned char serial1_rx(){
  return 0;
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
  while (!(UCSR0A & (1<<UDRE0)) );
  UDR0 = x;
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){
}

//! Set the baud rate.
void setbaud0(unsigned char rate){
  //TODO support multiple rates.
  #define SPEED 9600
  
  
  switch(rate){
  case 1://9600 baud
    
    break;
  case 2://19200 baud
    
    break;
  case 3://38400 baud
    
    break;
  case 4://57600 baud
    
    break;
  default:
  case 5://115200 baud
    
    break;
  }
  
#define F_CPU 8000000L
  //#define BAUD 115200L
#define BAUD 9600L
#include <util/setbaud.h>
  UBRR0H = UBRRH_VALUE;
  UBRR0L = UBRRL_VALUE;
  
  UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);
  UCSR0B = _BV(RXEN0) | _BV(TXEN0);
  return;
  
}

//! Set the baud rate of the second uart.
void setbaud1(unsigned char rate){
  //http://mspgcc.sourceforge.net/baudrate.html
  switch(rate){
  case 1://9600 baud
    
    break;
  case 2://19200 baud
    
    break;
  case 3://38400 baud
    
    break;
  case 4://57600 baud
    
    break;
  default:
  case 5://115200 baud
    
    break;
  }
}


void avr_init_uart0(){
  PORTD = _BV(PD2);
  setbaud0(0);
  _delay_ms(500); //takes a bit to stabilize
}


void avr_init_uart1(){
}




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
        /* disable briefly */
        UCSR0B = 0;

        UBRR0L = 4;   /* 500,000 baud at 20MHz */
        //UBRR0L = 1;   /* 500,000 baud at 8MHz */
        //UBRR0L = 103; /* 9600 baud */
        // XXX UBRR0L = 8;     /* 115200 baud ERROR RATE TOO HIGH */
        UBRR0H = 0;

        UCSR0A = (1 << U2X0);   /* double the baud rate */
        UCSR0C = (3 << UCSZ00); /* 8N1 */

        /* enabling rx/tx must be done after frame/baud setup */
        UCSR0B = ((1 << TXEN0) | (1 << RXEN0));

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


void donbfet_init_uart0(){
  setbaud0(0);
  _delay_ms(500); //takes a bit to stabilize
}

void 
led_on()
{
	PLEDOUT |= (1 << PLEDPIN);
}

void
led_off()
{
	PLEDOUT &= ~(1 << PLEDPIN);
}

void 
donbfet_init()
{
        uint8_t x;

        /* explicitly clear interrupts */
        cli();

        /* move the vectors */

        /* move interrupts from boot flash section */
        /* NB */
        /* you MUST use a variable during this process. even highly optimized,
         * masking the bit, shifting, ANDing, and setting MCUCR will exceed
         * 4 CPU cycles! set a variable with the desired value for MCUCR and
         * then set the register once IVCE is enabled
         */
        x = MCUCR & ~(1 << IVSEL);

        /* enable change of interrupt vectors */
        /* NOTE: setting IVCE disables interrupts until the bit is auto-unset 
         * 4 cycles after being set or after IVSEL is written
         */
        MCUCR |= (1 << IVCE);
        MCUCR = x;

        /* disable the watchdog timer; this macro will disable interrupts for us */
        /* NOTE: ensure that the WDRF flag is unset in the MCUSR or we will spinlock
         * when the watchdog times out
         */
        MCUSR &= ~(1 << WDRF);
        wdt_disable();

        /* init the USART */
        donbfet_init_uart0();

	/* set the LED as an output */
	PLEDDIR |= (1 << PLEDPIN);
	PLEDOUT |= (1 << PLEDPIN);

        /* explicitly enable interrupts */
        sei();
}

void
donbfet_reboot()
{
	MCUSR &= ~(1 << WDRF);
	wdt_enable(WDTO_15MS);
	while(1)
		_delay_ms(127);
}

void donbfet_init_uart1(){
}

uint8_t
donbfet_get_byte(uint16_t v)
{
	/* NB */
	/* we are only passed in a 16bit word. should 
	 * be increased to 32bit if we want to handle
	 * far reads as well
	 */
	return pgm_read_byte_near(v);
}

int * 
donbfet_ramend(void)
{
	/* NB */
	/* ATmega644P has 4K SRAM */
	return (int * )0x1000; 
}

void
led_toggle(void)
{
	led_on();
	_delay_ms(30);
	led_off();
}


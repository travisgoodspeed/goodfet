#include "platform.h"

#include <avr/io.h>
#include <util/delay.h>

//! Receive a byte.
unsigned char serial0_rx(){
  while( !(UCSR0A & (1 << RXC0)) );
  return UDR0;
}


//! Transmit a byte.
void serial0_tx(unsigned char x){
  while (!(UCSR0A & (1<<UDRE0)) );
  UDR0 = x;
}


//! Set the baud rate.
void setbaud0(unsigned char rate){
  /* disable everything briefly */
  UCSR0B = 0;

  int32_t r;
  switch(rate){
  case 1://9600 baud
    r = 9600;
    break;
  case 2://19200 baud
    r = 19200;
    break;
  case 3://38400 baud
    r = 38400;
    break;
  case 4://57600 baud
    r = 57600;
    break;

  default:
  case 5://115200 baud
    r = 115200;
    break;
  }

  /* enabling rx/tx must be done before frame/baud setup */
  UCSR0B = ((1 << TXEN0) | (1 << RXEN0));

  UCSR0A = (1 << U2X0);   /* double the baud rate */
  UCSR0C = (3 << UCSZ00); /* 8N1 */

  UBRR0L = (int8_t) (F_CPU/(r*8L)-1);
  UBRR0H = (F_CPU/(r*8L)-1) >> 8;

  return;

}


void zigduino_init_uart0(){
  setbaud0(0);
  _delay_ms(500); //takes a bit to stabilize
}

void led_init(){

  PLEDDIR |= (1 << PLEDPIN);
}

void  led_on() {
  PLEDOUT |= (1 << PLEDPIN);
}

void led_off() {
  PLEDOUT &= ~(1 << PLEDPIN);
}

void zigduino_init(){
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
  zigduino_init_uart0();

  /* set the LED as an output */
  led_init();

  /* enable internal internal pull-up resister
        in order to supress line noise that prevents
        bootloader from timing out */
  SPIDIR &= ~(1 << SPIPIN);
  SPIOUT |= (1 << SPIPIN);

  /* explicitly enable interrupts */
  sei();

}

void
zigduino_reboot()
{
  MCUSR &= ~(1 << WDRF);
  wdt_enable(WDTO_15MS);
  while(1)
    _delay_ms(127);
}

int *
zigduino_ramend(void)
{
  /* NB */
  /* ATmega128rfa1 has 16K SRAM */
  return (int * )0x4000;
}

void
led_toggle(void)
{
  led_on();
  _delay_ms(30);
  led_off();
}

#include <avr/io.h>
#include <util/delay.h>


int main (void)
{
  /* set PORTB for output*/
  DDRB = 0xFF;

  while (1)
    {
      /* set PORTB.6 high */
      PORTB = 0x20;

      _delay_ms(1000);

      /* set PORTB.6 low */
      PORTB = 0x00;

      _delay_ms(1000);
    }

  return 1;
}

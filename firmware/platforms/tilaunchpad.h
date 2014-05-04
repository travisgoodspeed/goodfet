/*! \file tilaunchpad.h
  \author Peter Lorenzen
  \brief Port descriptions for the TI-launchpad platform.
// Port setup on TI Launchpad
// P1.3 RTS input
// P1.4 DTR input
// P1.5 DSR output
// P1.6 CTS output
// P2.4 P4.7 P5.1 P5.2 SBWDIO 47k pull-up
// P3.1 SDA
// P3.3 SCL
// P3.4 TXD0    to TUSB3410
// P3.5 RXD0    to TUSB3410
// P3.6 TXD1    BTXD
// P3.7 RXD1    BRXD
// P4.6 Reset to TUSB3410
// P4.7 P2.4 P5.1 P5.2 SBWDIO 47k pull-up
// P5.1 P4.7 P2.4 P5.2 SBWDIO 47k pull-up
// P5.2 P4.7 P2.4 P5.1 SBWDIO 47k pull-up       labelled RST
// P5.3         SBWTCK 47k pull-down            labelled TEST
// P5.5         SMCLK 12 Mhz send to TUSG3410

The Launchpad has only four pins easily available
but this is fine for f.ex chipcon
P5.3 TCK	SCK
P5.2 IO		MISO MOSI
P3.7 rxd1	RST
P3.6 txd1	used for led in chipcon application

P2.4 could probably be made available without too much destruction
a normal goodfet has
Port SPI  JTAG
----+----+------
P5.0 SS   TMS
P5.1 MOSI TDI	TCLK
P5.2 MISO TDO
P5.2 SCK  TCK

//These are not on P5
P2.6 RST
P4.0 TST

P1.0 LED

*/
#define TI_LAUNCHPAD 1

#include <signal.h>
#include <msp430.h>
#include <iomacros.h>

// Here is how I try to remember rs232 signaling
// think of halfduplex rs485, and this makes total sense.
#define DTR BIT4                // -> Minicom has opened the device in handshake on mode
#define DSR BIT5                // <- TI Launchpad signals back that it is turned ON
#define RTS BIT3                // -> Minicom request control of rs485 bus
#define CTS BIT6                // <- we reply yes we got the rs485 bus - just carry on on

#define SBWDIO	BIT2
#define SBWTCK	BIT3

#define SPIOUT P5OUT
#define SPIDIR P5DIR
#define SPIIN  P5IN
#define SPIREN P5REN

// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl


void delay_us(unsigned int us);
void delay_ms(unsigned int ms);
void delay_sec(unsigned int s);
void led_init(char pin);
void led_on();
void led_off();
void led_toggle();
void led_blink(int n);		// long - n shorts


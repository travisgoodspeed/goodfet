/* Name: serial_io.c
 * Tabsize: 8
 * Copyright: (c) 2011 by Peter@Lorenzen.us
 * License: [BSD]eerware 
 * serput{c,s} sergetc functionality as on UNIX
 */

//FIXME This should switch to the standard GoodFET functions for the msp430f161x chips.

#include "platform.h"
#include <signal.h>
#include <msp430.h>
#include <iomacros.h>
#include "msp430_serial.h"

#if (DEBUG_LEVEL > 0)
#ifdef DEBUG_START
char dlevel = DEBUG_START;
#else
char dlevel = DEBUG_LEVEL;
#endif
#ifdef	INBAND_DEBUG
#include "command.h"
#endif
#endif

fifo_t fiforx0, fifotx0;
fifo_t fiforx1, fifotx1;
fifo_t *rxfp0;			// NULL not in use
fifo_t *txfp0;			// NULL not in use
fifo_t *rxfp1;			// NULL not in use
fifo_t *txfp1;			// NULL not in use

void fifo_init(fifo_t * fp)
{
	fp->i = 0;
	fp->o = 0;
	fp->count = 0;
	fp->empty = 1;
}

static void fifo_advance(uint8_t * ptr)
{
	if (*ptr == (FIFO_SZ - 1)) {
		*ptr = 0;
	} else {
		(*ptr)++;
	}
}

static void fifo_wr(fifo_t * fp, char c)
{
	fp->b[fp->i] = c;
	_DINT();		// only need to disable tx irq for this stream
	fifo_advance(&fp->i);
	fp->count++;
	_EINT();
}

static uint8_t fifo_rd(fifo_t * fp)	// only called if count>0
{
	uint8_t c = fp->b[fp->o];
	_DINT();		// only need to disable tx irq for this stream
	fifo_advance(&fp->o);
	fp->count--;
	_EINT();
	return c;
}

//http://mspgcc.sourceforge.net/baudrate.html
/** TI lauchpad and  EZ430/FETUIF with 12MHz crystal */
#if (platform == tilaunchpad)
uint8_t bauds[6][3] = {
	{0x68, 0x00, 0x04}	// 0 - 12000000Hz 115273bps
	, {0xE2, 0x04, 0x00}	// 1 - 12000000Hz 9600bps
	, {0x71, 0x02, 0x00}	// 2 - 12000000Hz 19200bps
	, {0x38, 0x01, 0x55}	// 3 - 12000000Hz 38400bps
	, {0xD0, 0x00, 0x4A}	// 4 - 12000000Hz 57581bps
	, {0x68, 0x00, 0x04}	// 5 - 12000000Hz 115273bps
};
#else
uint8_t bauds[6][3] = {
	{0x20, 0x00, 0x00}	// 0 - 3683400Hz 115106bps
	, {0x7F, 0x01, 0x5B}	// 1 - 3683400Hz 9599bps
	, {0xBF, 0x00, 0xF7}	// 2 - 3683400Hz 19194bps
	, {0x5F, 0x00, 0xBF}	// 3 - 3683400Hz 38408bps
	, {0x40, 0x00, 0x00}	// 4 - 3683400Hz 57553bps
	, {0x20, 0x00, 0x00}	// 5 - 3683400Hz 115106bps
};
#endif

void setbaud0(uint8_t rate)
{
	UBR00 = bauds[rate][0];
	UBR10 = bauds[rate][1];
	UMCTL0 = bauds[rate][2];
}

void setbaud1(uint8_t rate)
{
	UBR01 = bauds[rate][0];
	UBR11 = bauds[rate][1];
	UMCTL1 = bauds[rate][2];
}

// we assume rx and tx is always supplied, so no check
void ser0_init(int baud, fifo_t * rx, fifo_t * tx)
{
	rxfp0 = rx;
	txfp0 = tx;
	P3DIR &= ~BIT5;		// Select P35 for input (UART0RX)
	P3SEL |= BIT4 | BIT5;	// P3.4,5 = USART0 TXD/RXD
	P3DIR |= BIT4;

	UCTL0 = SWRST | CHAR;	/* 8-bit character, UART mode */
	ME1 &= ~USPIE0;		// USART1 SPI module disable
	UTCTL0 = SSEL1;		/* UCLK = MCLK */

	setbaud0(baud);

	ME1 &= ~USPIE0;		/* USART1 SPI module disable */
	ME1 |= (UTXE0 | URXE0);	/* Enable USART1 TXD/RXD */

	UCTL0 &= ~SWRST;

	//U0TCTL |= URXSE;	// XXX Clear pending interrupts before enable!!!
	fifo_init(rx);
	fifo_init(tx);

	IE1 |= UTXIE0;		// Enable USART0 TX interrupt
	IE1 |= URXIE0;		// Enable USART0 RX interrupt

	P1DIR |= DSR | CTS;
	P1OUT &= ~(DSR | CTS);	// We are On and we are ready
}

// we can use uart1 tx for debug messages, using rx bit for something else
// or we can use full uart1 for pass through
// or not uart1 functions at all,
void ser1_init(int baud, fifo_t * rx, fifo_t * tx)
{
	rxfp1 = rx;
	txfp1 = tx;
	if (rx) {		// RX enabled
		P3SEL |= BIT7;	// Select P37 for UART1 RX function
		P3DIR &= ~BIT7;	// P37 is input
	} else {
		P3SEL &= ~BIT7;	// No UART1 RX, can be used as a bit port
	}
	if (tx) {		// TX enabled
		P3SEL |= BIT6;	// Select P36 for UART1 TX function
		P3DIR |= BIT6;	// P36 is output UART1 TX
	} else {
		P3SEL &= ~BIT6;	// No UART1 TX, can be used as a bit port
	}
	UCTL1 = SWRST | CHAR;	// 8-bit character, UART mode  stop UART state machine
	if (rx || tx) {		// RX or TX enabled
		ME2 &= ~USPIE1;	// USART1 SPI module disable
	}
	UTCTL1 = SSEL1;		// UCLK = MCLK

	//U1TCTL |= URXSE;	// XXX Clear pending interrupts before enable!!!
	if (rx) {		// RX enabled
		ME2 |= URXE1;	// Enable USART1 RX
		fifo_init(rx);
	}
	if (tx) {		// TX enabled
		ME2 |= UTXE1;	// Enable USART1 TXD
		fifo_init(tx);
	}

	setbaud1(baud);		// we set it even when disabling uart1 - who cares

	UCTL1 &= ~SWRST;	// enable UART state machine
	if (tx) {		// TX enabled
		IE2 |= UTXIE1;	// Enable USART1 TX interrupt
	} else {
		IE2 &= ~UTXIE1;	// Disable USART1 TX interrupt
	}
	if (rx) {		// RX enabled
		IE2 |= URXIE1;	// Enable USART1 RX interrupt
	} else {
		IE2 &= ~URXIE1;	// Disable USART1 TX interrupt
	}
}


int seravailable(fifo_t * fp)
{
	return fp->count;
}

void serflush(fifo_t * fp)
{
	while (seravailable(fp) > 0) {
		delay_ms(1);
	}
}

int sergetc(fifo_t * fp)
{
	int c;
	if (fp == NULL)
		return -1;
	if (fp->count) {
		c = fifo_rd(fp);
	} else {
		fp->empty = TRUE;
		c = -1;
	}
	return c;
}

void serclear(fifo_t *fp)
{
	while (seravailable(fp) > 0) {
		sergetc(fp);
	}
}

#ifdef	INBAND_DEBUG
// send debug messages over USB-serial link encapsulated in the goodfet protocol
void dputc(char c)
{
	char two[2];
	two[0]=c;
	two[1]=0;
	debugstr(two);
}

void dputs(char *str)
{
	debugstr(str);
}
void dputb(char c)
{
	debugbytes(&c,1);
}

void dputw(int w)
{
	debugbytes((char *)&w,2);
}
#else
// defines in msp430_serial.h resolves to the functions below on txfp1
#endif

void serputc(char c, fifo_t * fp)
{
	if (fp == NULL)
		return;
	while (seravailable(fp) == FIFO_SZ) {
	}
	fifo_wr(fp, c);		// magic is in count-- indivisible, do not optimize
	if (fp->empty && fp->count) {	// buffer had been empty
		fp->empty = FALSE;
		c = fifo_rd(fp);
		if (fp == txfp0) {
			TXBUF0 = c;
		} else {
			TXBUF1 = c;
		}
	}
}

void serputs(char *cpt, fifo_t * fp)
{
	while (*cpt) {
		serputc(*cpt++, fp);
	}
}

char hex2c(char i)
{
	i &=0x0f;
	return i > 9 ? 'a' + i - 10 : '0' + i;
}

void serputb(char c, fifo_t * fp)
{
	serputc(hex2c(c>>4), fp);
	serputc(hex2c(c), fp);
}

void serputw(int w, fifo_t * fp)
{
	serputb(w >> 8, fp);
	serputb(w & 0xff, fp);
}

#if (DEBUG_LEVEL>2)
char *dddlog_input(char c)
{
	static char buf[7];
	int n = rxfp0->o;
	buf[0]='<';
	buf[1]=hex2c(c>>4);
	buf[2]=hex2c(c);
	buf[3]='>';
	buf[4]=hex2c(n>>4);
	buf[5]=hex2c(n);
	buf[6]=0;
	return buf;
}
#endif
//  These is what goodfet uses
uint8_t serial0_rx()
{
	uint8_t c;
	while (seravailable(rxfp0) == 0) {	// wait for data to be available
		// FIXME we should sleep
	}
	c = sergetc(rxfp0);
	dddputs(dddlog_input(c));
	return c;
}

uint8_t serial1_rx()
{
	uint8_t c;
	while ((seravailable(rxfp1)) == 0) {	// wait for data to be available
		// FIXME we should sleep
	}
	c = sergetc(rxfp1);
	return c;
}

void serial0_tx(uint8_t x)
{
	serputc(x, txfp0);
}

void serial1_tx(uint8_t x)
{
	serputc(x, txfp1);
}

//Interrupt routines

interrupt(UART0RX_VECTOR) UART0_RX_ISR(void)
{
	led_toggle();
	rxfp0->b[rxfp0->i] = RXBUF0;
	fifo_advance(&rxfp0->i);
	rxfp0->count++;
}

interrupt(UART1RX_VECTOR) UART1_RX_ISR(void)
{
	led_toggle();
	rxfp1->b[rxfp1->i] = RXBUF1;
	fifo_advance(&rxfp1->i);
	rxfp1->count++;
}

interrupt(UART0TX_VECTOR) UART0_TX_ISR(void)
{
	if (txfp0->count) {
		TXBUF0 = txfp0->b[txfp0->o];
		fifo_advance(&txfp0->o);
		txfp0->count--;
	} else {
		txfp0->empty = TRUE;
	}
}

interrupt(UART1TX_VECTOR) UART1_TX_ISR(void)
{
	if (txfp1->count) {
		TXBUF1 = txfp1->b[txfp1->o];
		fifo_advance(&txfp1->o);
		txfp1->count--;
	} else {
		txfp1->empty = TRUE;
	}
}

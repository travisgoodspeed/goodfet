//! tilaunchpad clock and I/O definitions

// serial io stuff moved to msp430_serial.c
// serial is common for the different versions of msp430 so it makes sense

#include "platform.h"
#include <signal.h>
#include <msp430.h>
#include <iomacros.h>

#define MSP430_CPU_SPEED 6000000UL
#include <setjmp.h>
#include "msp430_serial.h"
extern jmp_buf warmstart;
void coldstart();
#define USE_NMI_RESET_IRQ

static void delay_1us()
{
	// 6 Mhz, 6000000 cycles/sec, 6000 cycles/msec, 6 cycles/usec
	// 6 cycles = 1 usec
	// asummung loop wil be 3 cycles
	//asm("  nop");		// 1 cycle
	asm("  nop");		// 1 cycle
	asm("  nop");		// 1 cycle
	asm("  nop");		// 1 cycle
}

void delay_us(unsigned int us)
{
	while (us) {
		delay_1us();
		us--;
	}
}

void delay_ms(unsigned int ms)
{
	while (ms) {
		ms--;
		delay_us(1000);
	}
}

void delay_sec(unsigned int s)
{
	while (s) {
		s--;
		delay_ms(1000);
	}
}

static char led_pin = 0;	// since we are short on pins we might have LED on different pin 
static char led_last;
// led_pin=0 is disabled
// BIT2 and BIT3 is on port 5   SBWDIO SBWTCK
// BIT6 and BIT7 os on port 3   BRDRX BRDTX
void led_init(char pin)
{
	ddputs("led=");
	if (pin & BIT2) {
		ddputs("P5.2");
		led_pin = BIT2;
		P5DIR |= led_pin;
	} else if (pin & BIT3) {
		ddputs("P5.3");
		led_pin = BIT3;
		P5DIR |= BIT3;
	} else if (pin & BIT6) {
		ddputs("P3.6");
		led_pin = BIT6;
		P3SEL &= ~BIT6;	// do not use as uart1
		P3DIR |= BIT6;
	} else if (pin & BIT7) {
		ddputs("P3.7");
		led_pin = BIT7;
		P3SEL &= ~BIT7;	// do not use as uart1
		P3DIR |= BIT7;
	} else {
		led_pin = 0;
		ddputs("disabled");
	}
}

void led_on()			// 0 will disable, but it is up to the application to setup new use
{
//      dddputs("led_on=");
//      dddputb(led_pin);
	if (led_pin & BIT2) {
		P5OUT |= BIT2;
	} else if (led_pin & BIT3) {
		P5OUT |= BIT3;
	} else if (led_pin & BIT6) {
		P3OUT |= BIT6;
	} else if (led_pin & BIT7) {
		P3OUT |= BIT7;
	}
	led_last = 1;
}

void led_off()
{
	//dddputs("led_off=");
	//dddputb(led_pin);
	if (led_pin & BIT2) {
		P5OUT &= ~BIT2;
	} else if (led_pin & BIT3) {
		P5OUT &= ~BIT3;
	} else if (led_pin & BIT6) {
		P3OUT &= ~BIT6;
	} else if (led_pin & BIT7) {
		P3OUT &= ~BIT7;
	}
	led_last = 0;
}

void led_toggle()
{
	if (led_last) {
		led_off();
	} else {
		led_on();
	}
}

void led_blink(int n)		// long - n shorts
{
	int i;
	return;
	led_off();
	delay_ms(200);
	led_on();
	delay_ms(500);
	for (i = 0; i < n; i++) {
		led_off();
		delay_ms(100);
		led_on();
		delay_ms(150);
	}
	led_off();
}

void check_usb2serial()
{
	//ddputs("usb2serial ");
	led_init(SBWTCK);	// we will use TCK for LED
	P5DIR &= ~SBWDIO;	// input

	led_on();		// we will use TCK for LED
	if ((P5IN & SBWDIO) == 0) {	// TCK != DIO
		led_init(0);	// no led
		dputs("low no usb2serial");
		return;
	}
	led_off();		// we will use TCK for LED
	if (P5IN & SBWDIO) {	// TCK != DIO
		led_init(0);	// no led
		dputs("high no usb2serial");
		return;
	}
	// TCK is jumpered to DIO, lets start working as USB-serial converter.
	serflush(txfp0);
	serflush(txfp1);
	delay_ms(100);
	dputs("Serial pass through\n");
	serputs("Serial pass through\n", txfp0);
	while (1) {
		char c;
		if (seravailable(rxfp0) > 0) {
			c=sergetc(rxfp0);
			serputc( c, txfp1);
		}
		if (seravailable(rxfp1) > 0) {
			c=sergetc(rxfp1);
			serputc( c, txfp0);
		}
		// FIXME we should sleep
	}
}

char rts_change = 1;		// we cannot return 0 in longjmp so we take 1

interrupt(PORT1_VECTOR) POSRT1_ISR(void)
{
	if (P1IFG & RTS) {
		if ((P1IN & DTR) == 0) {
			rts_change++;
			if (rts_change > 10) {	// just there is no wrap-around
				rts_change = 10;
			}
		} else {
			rts_change = 1;
		}
		P1IFG &= ~RTS;	// clear irq
	}
	if (P1IFG & DTR) {
		int i;
		P1IFG &= ~DTR;	// clear irq
		
		for (i=0; (P1IN & DTR) == 0;i++) {	// wait for DTR high
			if (i>10000) {
				i=10000;
			}
		}
		if (i>5000) { //avoid spikes
			longjmp(warmstart, rts_change);
		}
	}
}

#ifdef USE_NMI_RESET_IRQ
// A reset is warmstart, ie. do not reset TUSB3410
// to use this wire a reset switch or connect TUSB3410 DTR to RST/NMI
// for development it is conveenient ot implement a reset function
interrupt(NMI_VECTOR) NMI_ISR(void)
{
	IFG1 &= ~NMIIFG;
	led_toggle();
	dputs("NMI(RESET)\n");
	dflush();
	longjmp(warmstart, rts_change);
}
#endif
// TI lauchpad has 12 Mhz X-tal on XT2 which also is the base clock for the TUSB34010 
// For Launchpad and probably EZ430/FETUIF 
// EZ430/FETUIF may need BCSCTL2 = SELM1 | DIVM1 | SELS;
void coldstart()
{
	_DINT();
#ifdef USE_NMI_RESET_IRQ
	WDTCTL = WDTPW + WDTHOLD + WDTNMI;	// Stop WDT, deactivate RESET
	//IE1 |= NMIIE;         // msp430f1612.pdf page 13
#else
	WDTCTL = WDTPW + WDTHOLD;	// Stop WDT
#endif
	//led_init(SBWTCK);
	led_init(0);
	led_off();
// reset for TUSB3410
	P4OUT &= ~BIT6;		// reset TUSB3410
	P4DIR |= BIT6;
// 12 Mhz on XT2
	BCSCTL1 &= ~0x80;	// turn on XT2 oscillator
	do {			// delay for X-tal to settle
		IFG1 &= ~OFIFG;
		delay_us(100);	// wait at least 50 usec
	} while (IFG1 & OFIFG);
	//BCSCTL2 = SELM_2 | DIVM_1 | SELS | DIVS_0;	// 6Mhz MCLK=XT2/2 SMCLK=XT2
	BCSCTL2 = SELM_2 | DIVM_2 | SELS | DIVS_0;	// 3Mhz MCLK=XT2/4 SMCLK=XT2
// Disable eeprom P3.1 SDA P3.3 SCL
	P3OUT &= ~(BIT1 | BIT3);	// pull dcl and sda down
	P3DIR |= BIT1 | BIT3;
// generate 12 Mhz clock for TUSB3410
	P5SEL |= BIT5;		// P5.5 is SMCLK to TUSG3410
	P5DIR |= BIT5;		// P5.5 is output
// release reset for TUSB3410
	delay_ms(100);
	P4OUT &= ~BIT6;		// release reset to TUSB3410
	P4DIR &= ~BIT6;		// and release port TUSB3410
// P1.3 RTS input, P1.4 DTR input can generate IRQ
	P1DIR &= ~(RTS | DTR);	// input
	P1SEL &= ~(RTS | DTR);	// no  special funtions
	P1IES &= ~RTS;	// low to high
	P1IES |=  DTR;	// high to low
	P1IFG &= ~(RTS | DTR);	// clear irqs if any, to avoid instant irq
	P1IE |= RTS | DTR;	// enable IRQ on pin 3,4
	IE1 |= NMIIE;		// msp430f1612.pdf page 13
	ser0_init(0, &fiforx0, &fifotx0);
	//ser1_init(0, &fiforx1, &fifotx1);
	ser1_init(0, NULL, NULL);
	_EINT();		// now we can print
	dputs("->coldstart<-\n");
	led_blink(4);
	led_on();		// led comes on after the very basic setup is done
}

void msp430_init()
{
#ifdef USE_NMI_RESET_IRQ
	WDTCTL = WDTPW + WDTHOLD + WDTNMI;	// Stop WDT, deactivate RESET
	//IFG1 &= ~NMIIFG;
	IE1 |= NMIIE;		// msp430f1612.pdf page 13
#else
	WDTCTL = WDTPW + WDTHOLD;	// Stop WDT
#endif
	serclear(rxfp0);
	ddputs("msp430_init\n");
	led_blink(10);

	check_usb2serial();	// configure as USB-serial if jumper RST-TEST
	led_blink(2);
	led_on();
}

//! Initialization is correct.
void msp430_init_dco_done()
{
}

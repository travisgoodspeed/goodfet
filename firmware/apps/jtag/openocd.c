/*! \file openocd.c
  \author Dave Huseby <dave at linuxprogrammer.org>
  \brief OpenOCD firmware
*/


#include "platform.h"
#include "command.h"
#include "openocd.h"
#include "jtag.h"

#define OPENOCD_APP

//! Handles a monitor command.
void openocd_handle_fn(uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len);

// define the openocd app's app_t
app_t const openocd_app = {

	/* app number */
	OPENOCD,

	/* handle fn */
	openocd_handle_fn,

	/* name */
	"OpenOCD",

	/* desc */
	"\tThe OpenOCD app handles the OpenOCD bitbang protocol.\n"
};

//! Clock the JTAG clock line
static void openocd_tcktock() 
{
	CLRTCK; 
	SETTCK; 
}

//! reset the cpu
static void openocd_reset_cpu(void)
{
	SETRST;
	msdelay(100);
	CLRRST;
	msdelay(100);
	SETRST;
	msdelay(100);
}

//! reset the tap logic
static void openocd_reset_test_logic(void)
{
	CLRMOSI;
	SETTMS;
	openocd_tcktock();
	openocd_tcktock();
	openocd_tcktock();
	openocd_tcktock();
	openocd_tcktock(); // now in reset-test-logic
	CLRTMS;
	openocd_tcktock();  // now in run-test-idle state
}

//! sets the LED value
void openocd_led(int led)
{
	if (led)
		/* turn the LED on */
		led_on();
	else
		/* turn the LED off */
		led_off();
}

//! resets the device/JTAG logic
void openocd_reset(int trst, int srst)
{
	if(srst && trst)
	{
		// we need to drive TST from low to high at
		// the same time as the RST
		SETTST;
		SETRST;
		msdelay(100);
		CLRTST;
		CLRRST;
		msdelay(100);
		SETTST;
		SETRST;
		msdelay(100);
	}
	else if (!srst && trst)
	{
		openocd_reset_test_logic();
	}
	else if(srst && !trst)
	{
		openocd_reset_cpu();
	}
}

//! updates the tck, tms, and tdi values
void openocd_write(int tck, int tms, int tdi)
{
	if(tms)
		SETTMS;
	else
		CLRTMS;

	if(tdi)
		SETMOSI;
	else
		CLRMOSI;

	if(tck)
		SETTCK;
	else
		CLRTCK;
}

//! Stop JTAG, release pins
void openocd_stop()
{
	P5OUT=0;
	P4OUT=0;
}

//! Set up the pins for JTAG mode.
void openocd_setup()
{
	P5DIR|=MOSI+SCK+TMS;
	P5DIR&=~MISO;
	P4DIR|=TST;
	P2DIR|=RST;
	msdelay(100);
}

//! handles OpenOCD commands
void openocd_handle_fn(uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len)
{
	switch(verb)
	{
		case START:
			/* do nothing...*/
			txdata(app,OK,0);
			break;

		case STOP:
			openocd_stop();
			txdata(app,OK,0);
			break;

		case SETUP:
			openocd_setup();
			txdata(app,OK,0);
			break;

		case OPENOCD_RESET:
			openocd_reset(cmddata[0], cmddata[1]);
			txdata(app,OK,0);
			break;

		case OPENOCD_READ:
			cmddata[0] = READMISO;
			txdata(app,OK,1);
			break;

		case OPENOCD_WRITE:
			openocd_write(cmddata[0], cmddata[1], cmddata[2]);
			txdata(app,OK,0);
			break;

		case OPENOCD_LED:
			openocd_led(cmddata[0]);
			txdata(app,OK,0);
			break;

		default:
			txdata(app,NOK,0);
	}
}



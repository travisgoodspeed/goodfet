/*! \file monitor.c
  \author Travis Goodspeed
  \brief Local debug monitor.
*/

#include "command.h"
#include "platform.h"
#include "monitor.h"
#include "builddate.h"


#if (platform == tilaunchpad)
#include <setjmp.h>
extern jmp_buf warmstart;
#endif


#define MONITOR_APP

//! Handles a monitor command.
void monitor_handle_fn(uint8_t const app,
		       uint8_t const verb,
		       uint32_t const len);

//! Overwrite all of RAM with 0xBEEF, then reboot.
void monitor_ram_pattern();

//! Return the number of contiguous bytes 0xBEEF, to measure RAM usage.
unsigned int monitor_ram_depth();

//! Call a function by address.
int fncall(unsigned int adr);


// define the monitor app's app_t
app_t const monitor_app = {

	/* app number */
	MONITOR,

	/* handle fn */
	monitor_handle_fn,

	/* name */
	"Monitor",

	/* desc */
	"\tThe monitor app handles basic operations on the MSP430\n"
	"\tsuch as peeking and poking memory, calling functions and\n"
	"\tmanaging the baud rate.\n"
};


//! Handles a monitor command.
void monitor_handle_fn(uint8_t const app,
		       uint8_t const verb,
		       uint32_t const len)
{
	int i;

	switch(verb)
	{
	default:
		debugstr("ERROR: Command unsupported by debug monitor.");
		break;

	case MONITOR_ECHO:
	  //Echo back the same buffer.
	  txdata(app,verb,len);
	  break;

	case MONITOR_LIST_APPS:
		// transmit firmware build date
		txstring(app, verb, build_date);

		// transmit app descriptions
		for(i = 0; i < num_apps; i++)
		{
			txstring(app, verb, apps[i]->name);
			// if full list, then add in description
			if(cmddata[0])
				txstring(app, verb, apps[i]->desc);
		}
		txdata(app, verb, 0);
		break;

	case PEEK:
	  #ifdef MSP430
		cmddata[0]=memorybyte[cmddataword[0]];
          #else
		debugstr("Monitor peeks are unsupported on this platform.");
		debughex(cmddataword[0]);
		cmddata[0]=0x00;
	  #endif
		txdata(app,verb,1);
		break;

	case POKE:
	  #ifdef MSP430
		//Todo, make word or byte.
		memorybyte[cmddataword[0]] = cmddata[2];
		cmddata[0] = memorybyte[cmddataword[0]];
          #else
		debugstr("Monitor pokes are unsupported on this platform.");
		debughex(cmddataword[0]);
		cmddata[0]=0x00;
	  #endif
		txdata(app,verb,1);
		break;

	case CALL:
		//Set the program counter to cmdword[0];
		cmddataword[0]=fncall(cmddataword[0]);
		txdata(app,verb,2);
		break;

	case EXEC:
		//Execute the argument as code from RAM.
		cmddataword[0]=fncall((u16) cmddataword);
		txdata(app,verb,2);
		break;

	case MONITOR_SIZEBUF:
		//TODO make the data length target-specific, varying by ram.
		cmddataword[0]=0x100;
		txdata(app,verb,2);
		break;

	case MONITOR_CHANGE_BAUD:
		//This command, and ONLY this command, does not reply.
		setbaud(cmddata[0]);
		//txdata(app,verb,0);
		break;

	case MONITOR_RAM_PATTERN:
		monitor_ram_pattern();//reboots, will never return
		break;

	case MONITOR_RAM_DEPTH:
		cmddataword[0]=monitor_ram_depth();
		txdata(app,verb,2);
		break;

	case MONITOR_DIR:
	case MONITOR_IN:
	case MONITOR_OUT:
	  debugstr("Command deprecated.");
	  txdata(app,verb,1);
	  break;

	case MONITOR_SILENT:
	  silent=cmddata[0];
	  txdata(app,verb,1);
      break;

	case MONITOR_CONNECTED:
	  #ifdef MSP430
	  msp430_init_dco_done();
	  #endif
	  txdata(app,verb,0);
	  break;

 	case MONITOR_LEDTEST:
 	  //debugstr("Enter LEDTEST.");
 	  i = 0;
      #ifdef PLEDOUT
       i++;
       led_init();
       led_on();
       msdelay(5000);
       led_off();
      #endif
      #ifdef PLED2OUT
       i++;
       led2_on();
       msdelay(5000);
       led2_off();
      #endif
      #ifdef PLED3OUT
       i++;
       led3_on();
       msdelay(5000);
       led3_off();
      #endif
      cmddata[0] = i;       //Return number of LEDs that we flashed.
      txdata(app,verb,1);
      break;

	}
}

//! Overwrite all of RAM with 0xBEEF, then reboot.
void monitor_ram_pattern()
{
	register int *a;

	//Wipe all of ram.
	for(a=(int*)0x1100;a<(int*)0x2500;a++)
	{//TODO get these from the linker.
		*((int*)a) = 0xBEEF;
	}
	txdata(0x00,0x90,0);

#if (platform == tilaunchpad)
	longjmp(warmstart,1);
#else
	//Reboot
#ifdef MSP430
	asm("br &0xfffe");
#endif
#endif
}

//! Return the number of contiguous bytes 0xBEEF, to measure RAM usage.
unsigned int monitor_ram_depth()
{
	register int a;
	register int count=0;
	for(a=0x1100;a<0x2500;a+=2)
		if(*((int*)a)==0xBEEF) count+=2;

	return count;
}

//! Call a function by address.
int fncall(unsigned int adr)
{
  #ifdef MSP430
	int (*machfn)() = 0;
	machfn = (int (*)()) adr;
	return machfn();
  #else
	debugstr("fncall() not supported on this platform.");
  #endif
}



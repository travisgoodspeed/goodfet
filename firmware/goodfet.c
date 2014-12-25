/*! \file goodfet.c
  \author Travis Goodspeed
  \brief Main module.
  
  This is the main module of the GoodFET, which calls the initialization
  routines and delegates commands to the various applications.
*/


#include "platform.h"
#include "command.h"
#include "apps.h"
#include "glitch.h"

#if (platform == tilaunchpad)
#include <setjmp.h>
jmp_buf warmstart;
void coldstart();
#include "msp430_serial.h"
#endif

#define RESET 0x80      // not a real app -- causes firmware to reset
#define DEBUGAPP 0xFF

//! General init function, calls platform-specific one.
void init(){
#ifdef MSP430
  #define INITCHIP msp430_init();
#endif

#ifdef ARDUINO
  #define INITCHIP arduino_init();
#endif

#if (platform == donbfet)
# define INITCHIP donbfet_init();
#endif

#ifdef INITCHIP
INITCHIP
#else
#warning "No init() routine for this platform!"
#endif

#ifdef INITPLATFORM
  INITPLATFORM
#endif
}



//! Handle a command.
void handle(uint8_t const app,
	    uint8_t const verb,
	    uint32_t const len){
  int i;
  
  //debugstr("GoodFET");
  //led_off();
  
  // find the app and call the handle fn
  for(i = 0; i < num_apps; i++){
    if(apps[i]->app == app){
      // call the app's handle fn
      (*(apps[i]->handle))(app, verb, len);

      // exit early
      return;
    }
  }

  // if we get here, then the desired app is not compiled into
  // this firmware
  debugstr("App missing.");
  debughex(app);
  txdata(app, NOK, 0);
}


//! Main loop.
int main(void){
  volatile unsigned int i;
  unsigned char app, verb;
  unsigned long len;
  // MSP reboot count for reset input & reboot function located at 0xFFFE
  volatile unsigned int reset_count = 0;
  
  silent=0; //Don't trust globals.
  
#if (platform == tilaunchpad)
  int ret=0;
  
  //ret = setjmp(warmstart);// needs to be here since context from init() would be gone
 warmstart:
  if (ret == 0) {	
    coldstart();	// basic hardware setup, clock to TUSB3410, and enable
  } else if (ret == 2) {
    dputs("\nalmost BSL only one RTS change\n");
  } else if (ret > 2) {	// reset released after more than two tst transisitions
    // We could write a BSL, a nice exercise for a Sunday afternoon.
    dputs("\nBSL\n");
    //call_BSL();	// once you are done uncomment ;-)
  } else {		// we come here after DTR high (release reset)
    dputs("\nWarmstart\n");
  }
#endif

#if (platform == donbfet)
  extern void donbfet_reboot(void);
  void (*reboot_function)(void) = donbfet_reboot;
#elif (platform == zigduino)
  extern void zigduino_reboot(void);
  void (*reboot_function)(void) = zigduino_reboot;
#else
  void (*reboot_function)(void) = (void *) 0xFFFE;
#endif
  
  init();
  
  txstring(MONITOR,OK,"http://goodfet.sf.net/");
  //txstring(0xab,0xcd,"http://goodfet.sf.net/");
  
  
  //Command loop.  There's no end!
  while(1){
    //Magic 3
    app = serial_rx();
    
    // If the app is the reset byte (0x80) increment and loop
    if (app == RESET){
      reset_count++;
	    
      if (reset_count > 4){
        // We could trigger the WDT with either:
        // WDTCTL = 0;
        // or
        // WDTCTL = WDTPW + WDTCNTCL + WDTSSEL + 0x00;
        // but instead we'll jump to our reboot function pointer
        (*reboot_function)();
        debugstr("Rebooting not supported on this platform.");
      }
	    
      continue;
    }else {
      reset_count = 0;
    }
	  
    verb = serial_rx();
    len = rxword();
	  
    //Read data, looking for buffer overflow.
    if(len <= CMDDATALEN){
      for(i = 0; i < len; i++)
	  cmddata[i] = serial_rx();
	    
      handle(app,verb,len);
    }else {
      //Listen to the blaberring.
      for(i = 0; i < len; i++)
        serial_rx();
	    
      //Reply with an error.
      debugstr("Buffer length exceeded.");
      txdata(MONITOR,NOK,0);
    }
  }
}


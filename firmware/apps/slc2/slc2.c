/*! \file slc2.c
   \author Alexey Borisenko <abori021@uottawa.ca>
   \brief Silicon Labs C2 Debug interface
 */

#include "command.h"

#ifdef __MSPGCC__
#include <msp430.h>
#else
#include <signal.h>
#include <msp430.h>
#include <iomacros.h>
#endif

#include "slc2.h"

#include "platform.h"


//-----------------------------------------------------------------------------------
// Global VARIABLES
//-----------------------------------------------------------------------------------
unsigned char NUM_BYTES;
unsigned int FLASH_ADDR;
unsigned char *C2_PTR;

//! Handles a monitor command.
void slc2_handle_fn( uint8_t const app,
                     uint8_t const verb,
                     uint32_t const len);

// define the spi app's app_t
app_t const slc2_app = {

	/* app number */
	SLC2,

	/* handle fn */
	slc2_handle_fn,

	/* name */
	"Silicon Labs C2",

	/* desc */
	"\tThis app handles Silicon Lab's C2 debugging protocol.\n"
};

//-----------------------------------------------------------------------------------
// FLASH Programming Routines (High Level)
//-----------------------------------------------------------------------------------
//
// These high-level routines perform the FLASH Programming Interface (FPI)
// command sequences.
//-----------------------------------------------------------------------------------
// C2_Init()
//-----------------------------------------------------------------------------------
// - Initializes the C2 Interface for FLASH programming
//
void C2_Init()
{
	C2CKOUTPUT;
	C2D_DriverOff;
	C2_Reset(); // Reset the target device
	delay_us(2); // Delay for at least 2us
	C2_WriteAR(FPCTL); // Target the C2 FLASH Programming
// Control register (FPCTL) for C2 Data
// register accesses
	C2_WriteDR(0x02); // Write the first key code to enable
// C2 FLASH programming
	C2_WriteDR(0x01); // Write the second key code to enable
// C2 FLASH programming
	delay_us(20000); // Delay for at least 20ms to ensure the
// target is ready for C2 FLASH programming
}
//-----------------------------------------------------------------------------------
// C2_GetDevID()
//-----------------------------------------------------------------------------------
// - Reads the target Devcie ID register and Revision ID register
//
unsigned char C2_GetDevID()
{
	C2_WriteAR(DEVICEID); // Select DeviceID regsiter for C2 Data
// register accesses
	return C2_ReadDR(); // Read and return the DeviceID register
}

//-----------------------------------------------------------------------------------
// C2_GetDevID()
//-----------------------------------------------------------------------------------
// - Reads the target Devcie ID register and Revision ID register
//
unsigned char C2_GetRevID()
{
	C2_WriteAR(REVID); // Select DeviceID regsiter for C2 Data
// register accesses
	return C2_ReadDR(); // Read and return the DeviceID register
}

//-----------------------------------------------------------------------------------
// C2_BlockRead()
//-----------------------------------------------------------------------------------
// - Reads a block of FLASH memory starting at <FLASH_ADDR>
// - The size of the block is defined by <NUM_BYTES>
// - Stores the read data at the location targeted by the pointer <C2_PTR>
// - Assumes that FLASH accesses via C2 have been enabled prior to the function call
// - Function call returns a ‘1’ if successful; returns a ‘0’ if unsuccessful
//
char C2_BlockRead()
{
	unsigned char i; // Counter
	unsigned char status; // FPI status information holder
	C2_WriteAR(FPDAT); // Select the FLASH Programming Data register
// for C2 Data register accesses
	C2_WriteDR(BLOCK_READ); // Send FLASH block read command
	Poll_InBusy; // Wait for input acknowledge
// Check status before starting FLASH access sequence
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
	C2_WriteDR(FLASH_ADDR >> 8); // Send address high byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(FLASH_ADDR & 0x00FF); // Send address low byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(NUM_BYTES); // Send block size
	Poll_InBusy; // Wait for input acknowledge
// Check status before reading FLASH block
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
// Read FLASH block
	for (i=0; i<NUM_BYTES; i++)
	{
		Poll_OutReady; // Wait for data ready indicator
		*C2_PTR++ = C2_ReadDR(); // Read data from the FPDAT register
	}
	return 1; // Exit and indicate success
}
//-----------------------------------------------------------------------------------
// C2_BlockWrite()
//-----------------------------------------------------------------------------------
// - Writes a block of FLASH memory starting at <FLASH_ADDR>
// - The size of the block is defined by <NUM_BYTES>
// - Writes the block stored at the location targetted by <C2_PTR>
// - Assumes that FLASH accesses via C2 have been enabled prior to the function call
// - Function call returns a ‘1’ if successful; returns a ‘0’ if unsuccessful
//
char C2_BlockWrite()
{
	unsigned char i; // Counter
	unsigned char status; // FPI status information holder
	C2_WriteAR(FPDAT); // Select the FLASH Programming Data register
// for C2 Data register accesses
	C2_WriteDR(BLOCK_WRITE); // Send FLASH block write command
	Poll_InBusy; // Wait for input acknowledge
// Check status before starting FLASH access sequence
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
	C2_WriteDR(FLASH_ADDR >> 8); // Send address high byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(FLASH_ADDR & 0x00FF); // Send address low byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(NUM_BYTES); // Send block size
	Poll_InBusy; // Wait for input acknolwedge

// Check status before starting FLASH access sequence
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
	C2_WriteDR(FLASH_ADDR >> 8); // Send address high byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(FLASH_ADDR & 0x00FF); // Send address low byte to FPDAT
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(NUM_BYTES); // Send block size
	Poll_InBusy; // Wait for input acknolwedge
// Check status before writing FLASH block
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
// Write FLASH block
	for (i=0; i<NUM_BYTES; i++)
	{
		C2_WriteDR(*C2_PTR++); // Write data to the FPDAT register
		Poll_InBusy; // Wait for input acknowledge
	}
	Poll_OutReady; // Wait for last FLASH write to complete
	return 1; // Exit and indicate success
}
//-----------------------------------------------------------------------------------
// C2_PageErase()
//-----------------------------------------------------------------------------------
// - Erases a 512-byte FLASH page
// - Targets the FLASH page containing the address <FLASH_ADDR>
// - Assumes that FLASH accesses via C2 have been enabled prior to the function call
// - Function call returns a ‘1’ if successful; returns a ‘0’ if unsuccessful
//
char C2_PageErase()
{
	unsigned char page; // Target FLASH page
	unsigned char status; // FPI status information holder

	page = (unsigned char)(FLASH_ADDR >> 9);
// <page> is the 512-byte sector containing
// the target <FLASH_ADDR>.
	if (page >= NUM_PAGES - 1) // Check that target page is within range
// (NUM_PAGES minus 1 for reserved area)
		return 0;  // Indicate error if out of range
	C2_WriteAR(FPDAT); // Select the FLASH Programming Data register
// for C2 Data register accesses
	C2_WriteDR(PAGE_ERASE); // Send FLASH page erase command
	Poll_InBusy; // Wait for input acknowledge
// Check status before starting FLASH access sequence
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
	C2_WriteDR(page); // Send FLASH page number
	Poll_InBusy; // Wait for input acknowledge
	Poll_OutReady; // Wait for ready indicator
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
	C2_WriteDR(0x00); // Dummy write to initiate erase
	Poll_InBusy; // Wait for input acknowledge
	Poll_OutReady; // Wait for erase operation to complete
	return 1; // Exit and indicate success
}
//-----------------------------------------------------------------------------------
// C2_Device_Erase()
//-----------------------------------------------------------------------------------
// - Erases the entire FLASH memory space
// - Assumes that FLASH accesses via C2 have been enabled prior to the function call
// - Function call returns a ‘1’ if successful; returns a ‘0’ if unsuccessful
//
char C2_DeviceErase()
{
	unsigned char status; // FPI status information holder
	C2_WriteAR(FPDAT); // Select the FLASH Programming Data register
// for C2 Data register accesses
	C2_WriteDR(DEVICE_ERASE); // Send Device Erase command
	Poll_InBusy; // Wait for input acknowledge
// Check status before starting FLASH access sequence
	Poll_OutReady; // Wait for status information
	status = C2_ReadDR(); // Read FLASH programming interface status
	if (status != COMMAND_OK)
		return 0;  // Exit and indicate error
// Send a three-byte arming sequence to enable the device erase. If the sequence
// is not received correctly, the command will be ignored.
// Sequence: 0xDE, 0xAD, 0xA5.

	C2_WriteDR(0xDE); // Arming sequence command 1
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(0xAD); // Arming sequence command 2
	Poll_InBusy; // Wait for input acknowledge
	C2_WriteDR(0xA5); // Arming sequence command 3
	Poll_InBusy; // Wait for input acknowledge
	Poll_OutReady; // Wait for erase operation to complete
	return 1; // Exit and indicate success
}
//-----------------------------------------------------------------------------------
// Primitive C2 Command Routines
//-----------------------------------------------------------------------------------
//
// These routines perform the low-level C2 commands:
// 1. Address Read
// 2. Address Write
// 3. Data Read
// 4. Data Write
// 5. Device Reset
//-----------------------------------------------------------------------------------
// C2_ReadAR()
//-----------------------------------------------------------------------------------
// - Performs a C2 Address register read
// - Returns the 8-bit register content
//
unsigned char C2_ReadAR()
{
	unsigned char i; // Bit counter
	unsigned char addr; // Address register read content
// START field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
// INS field (10b, LSB first)
	CLRC2D;
	C2D_DriverOn; // Enable C2D driver (output)
	StrobeC2CK;
	SETC2D;
	StrobeC2CK;
	C2D_DriverOff; // Disable C2D driver (input)
// ADDRESS field
	addr = 0;
	for (i=0; i<8; i++) // Shift in 8 bit ADDRESS field
	{ // LSB-first
		addr >>= 1;
		StrobeC2CK;
		if (READC2D)
			addr |= 0x80;
	}
// STOP field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled

	return addr; // Return Address register read value
}
//-----------------------------------------------------------------------------------
// C2_WriteAR()
//-----------------------------------------------------------------------------------
// - Performs a C2 Address register write (writes the <addr> input
// to Address register)
//
void C2_WriteAR(unsigned char addr)
{
	unsigned char i; // Bit counter
// START field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
// INS field (11b, LSB first)
	SETC2D;
	C2D_DriverOn; // Enable C2D driver (output)
	StrobeC2CK;
	SETC2D;
	StrobeC2CK;
// ADDRESS field
	for(i=0; i<8; i++) // Shift out 8-bit ADDRESS field
	{
		if(addr & 0x01)
			SETC2D;
		else
			CLRC2D;
		StrobeC2CK;
		addr >>= 1;
	}
// STOP field
	C2D_DriverOff; // Disable C2D driver
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
	return;
}
//-----------------------------------------------------------------------------------
// C2_ReadDR()
//-----------------------------------------------------------------------------------
// - Performs a C2 Data register read
// - Returns the 8-bit register content
//
unsigned char C2_ReadDR()
{
	unsigned char i; // Bit counter
	unsigned char dat; // Data register read content
// START field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
// INS field (00b, LSB first)
	CLRC2D;
	C2D_DriverOn; // Enable C2D driver (output)
	StrobeC2CK;
	CLRC2D;
	StrobeC2CK;

// LENGTH field (00b -> 1 byte)
	CLRC2D;
	StrobeC2CK;
	CLRC2D;
	StrobeC2CK;
// WAIT field
	C2D_DriverOff; // Disable C2D driver for input
	do
	{
		StrobeC2CK;
	}
	while (!READC2D); // Strobe C2CK until target transmits a ‘1’
// DATA field
	dat = 0;
	for (i=0; i<8; i++) // Shift in 8-bit DATA field
	{ // LSB-first
		dat >>= 1;
		StrobeC2CK;
		if (READC2D)
			dat |= 0x80;
	}
// STOP field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
	return dat;
}

//-----------------------------------------------------------------------------------
// C2_WriteDR()
//-----------------------------------------------------------------------------------
// - Performs a C2 Data register write (writes <dat> input to data register)
//
void C2_WriteDR(unsigned char dat)
{
	unsigned char i; // Bit counter
// START field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
// INS field (01b, LSB first)
	SETC2D;
	C2D_DriverOn; // Enable C2D driver
	StrobeC2CK;
	CLRC2D;
	StrobeC2CK;
// LENGTH field (00b -> 1 byte)
	CLRC2D;
	StrobeC2CK;
	CLRC2D;
	StrobeC2CK;
// DATA field
	for (i=0; i<8; i++) // Shift out 8-bit DATA field
	{ // LSB-first
		if(dat & 0x01)
			SETC2D;
		else
			CLRC2D;
		StrobeC2CK;
		dat >>= 1;
	}
// WAIT field
	C2D_DriverOff; // Disable C2D driver for input
	do
	{
		StrobeC2CK; // Strobe C2CK until target transmits a ‘1’
	}
	while (!READC2D);
// STOP field
	StrobeC2CK; // Strobe C2CK with C2D driver disabled
	return;
}

//-----------------------------------------------------------------------------------
// C2_Reset()
//-----------------------------------------------------------------------------------
// - Performs a target device reset by pulling the C2CK pin low for >20us
//
void C2_Reset()
{
	CLRC2CK; // Put target device in reset state by pulling
	delay_us(20); // C2CK low for >20us
	SETC2CK; // Release target device from reset
}



//! Handles a monitor command.
void slc2_handle_fn( uint8_t const app,
                     uint8_t const verb,
                     uint32_t const len)
{
	prep_timer();
	unsigned char dev_id = 0;
	unsigned char rev_id = 0;
	switch(verb)
	{
	case PEEK:
		//C2_Reset();
		//C2_Init();
		NUM_BYTES = 2;
		FLASH_ADDR = (cmddata[1] << 8) + cmddata[0];
		C2_PTR = cmddata; //cmddata + 2;
		//slc2_init();////
		if(C2_BlockRead()) {
			txdata(app, verb, 2);
		}else{
			txdata(app, NOK, 0);
		}
		break;

	case POKE:
		NUM_BYTES = len;
		FLASH_ADDR = (cmddata[1] << 8) + cmddata[0];
		C2_PTR = cmddata + 2;
		if(C2_BlockWrite()) {
			txhead(app, OK, 0);
		}else{
			txhead(app, NOK, 0);
		}
		break;

	case SETUP:
		C2_Reset();
		C2_Init();
		txdata(app,verb,0);
		break;

	case GETDEVID:
		dev_id =  C2_GetDevID();
		cmddata[0] = dev_id;
		txdata(app, verb, 1);
		break;

	case GETREVID:
		rev_id =  C2_GetRevID();
		cmddata[0] = rev_id;
		txdata(app, verb, 1);
		break;

	case PERASE:
		FLASH_ADDR = (cmddata[1] << 8) + cmddata[0];
		if(C2_PageErase()) {
			txhead(app, OK, 0);
		}else{
			txhead(app, NOK, 0);
		}
		break;

	case DERASE:
		if(C2_DeviceErase()) {
			txhead(app, OK, 0);
		}else{
			txhead(app, NOK, 0);
		}
		break;
	case VRESET:
		C2_Reset();
		txdata(app,verb,0);
		break;
	default:
		txdata(app, NOK, 0);
		break;
	}
}

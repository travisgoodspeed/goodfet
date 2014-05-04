/*! \file slc2.h
  \author Alexey Borisenko <abori021@uottawa.ca>
  \brief Definitions for Silicon Lab C2 debugging application
  NOTE: FPDAT register address can be different, based on the device
  Current address is meant for the 8051f34x
*/

#ifndef SLC2_H
#define SLC2_H

#include "app.h"

#define SLC2 0x06

//Pins and I/O
#define C2CK BIT7
#define C2D BIT6

#define SETC2CK P3OUT |= C2CK
#define CLRC2CK P3OUT &= ~C2CK
#define SETC2D P3OUT |= C2D
#define CLRC2D P3OUT &= ~C2D

#define READC2D (P3IN&C2D?1:0)

#define C2CKOUTPUT P3DIR|=C2CK
#define C2D_DriverOff P3DIR&=~C2D
#define C2D_DriverOn P3DIR|=C2D

#define DATA_READ  0x00
#define ADDR_READ  0x02
#define DATA_WRITE 0x01
#define ADDR_WRITE 0x03

// FLASH information
#define FLASH_SIZE 65536 // FLASH size in bytes
#define NUM_PAGES FLASH_SIZE/512 // Number of 512-byte FLASH pages

// C2 status return codes
#define INVALID_COMMAND 0x00
#define COMMAND_FAILED 0x02
#define COMMAND_OK 0x0D

// C2 interface commands
#define GET_VERSION 0x01
#define BLOCK_READ 0x06
#define BLOCK_WRITE 0x07
#define PAGE_ERASE 0x08
#define DEVICE_ERASE 0x03

// C2 Registers
#define FPDAT 0xAD
#define FPCTL 0x02
#define DEVICEID 0x00
#define REVID 0x01

// Program MACROS
#define Poll_OutReady while(!(C2_ReadAR()&0x01))
#define Poll_InBusy while((C2_ReadAR()&0x02))
#define StrobeC2CK CLRC2CK; SETC2CK

// C2 verbs
#define GETDEVID 0x80
#define GETREVID 0x81
#define PERASE 0x82
#define DERASE 0x83
#define VRESET 0x84

void slc2_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

extern app_t const slc2_app;

// FLASH programming functions
void C2_Init();
unsigned char C2_GetDevID(void);
char C2_BlockRead(void);
char C2_BlockWrite(void);
char C2_PageErase(void);
char C2_DeviceErase(void);
// Primitive C2 functions
void C2_Reset(void);
void C2_WriteAR(unsigned char);
unsigned char C2_ReadAR(void);
void C2_WriteDR(unsigned char);
unsigned char C2_ReadDR(void);
unsigned char C2_ReadDeviceID(void);
unsigned char C2_ReadRevID(void);


#endif

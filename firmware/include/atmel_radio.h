/*! \file atmel_radio.h
  \author bx but forked from neighbor Travis Goodspeed
  \brief Constants for ATMEL_RADIO Driver
*/

#ifndef ATMEL_RADIO_H
#define ATMEL_RADIO_H

#include "app.h"

#define ATMEL_RADIO   0x53

//Nordic RF Commands

//Grab a packet, if one is available.
#define ATMEL_RADIO_RX 0x80
//Send a packet.
#define ATMEL_RADIO_TX 0x81
//Flush RX
#define ATMEL_RADIO_RX_FLUSH 0x82
//Flush TX
#define ATMEL_RADIO_TX_FLUSH 0x83
//Start sniffing in extented oparating (AACK) mode
#define ATMEL_RADIO_AACK_ON 0x84
//Sopt sniffing in extented oparating (AACK) mode, sniff in basic operating mode
#define ATMEL_RADIO_AACK_OFF 0x85
// enable auto CRC generation
#define ATMEL_RADIO_AUTOCRC_ON 0x86
// diasble auto CRC generation (disabled by default)
#define ATMEL_RADIO_AUTOCRC_OFF 0x87


//ATMEL_RADIO24L01+ Registers
//These aren't yet used, but are included for later
//translation to XML.
#define ATMEL_RADIO_CONFIG      0x00
#define ATMEL_RADIO_EN_AA       0x01
#define ATMEL_RADIO_EN_RXADDR   0x02
#define ATMEL_RADIO_SETUP_AW    0x03
#define ATMEL_RADIO_SETUP_RETR  0x04
#define ATMEL_RADIO_RF_CH       0x05
#define ATMEL_RADIO_RF_SETUP    0x06
#define ATMEL_RADIO_STATUS      0x07
#define ATMEL_RADIO_OBSERVE_TX  0x08
#define ATMEL_RADIO_RPD         0x09
#define ATMEL_RADIO_RX_ADDR_P0  0x0A
#define ATMEL_RADIO_RX_ADDR_P1  0x0B
#define ATMEL_RADIO_RX_ADDR_P2  0x0C
#define ATMEL_RADIO_RX_ADDR_P3  0x0D
#define ATMEL_RADIO_RX_ADDR_P4  0x0E
#define ATMEL_RADIO_RX_ADDR_P5  0x0F
#define ATMEL_RADIO_TX_ADDR     0x10
#define ATMEL_RADIO_RX_PW_P0    0x11
#define ATMEL_RADIO_RX_PW_P1    0x12
#define ATMEL_RADIO_RX_PW_P2    0x13
#define ATMEL_RADIO_RX_PW_P3    0x14
#define ATMEL_RADIO_RX_PW_P4    0x15
#define ATMEL_RADIO_RX_PW_P5    0x16
#define ATMEL_RADIO_FIFO_STATUS 0x17
#define ATMEL_RADIO_DYNPD       0x1C
//Also 32-byte buffers for ACK_PLD, TX_PLD, and RX_PLD.
//Separate SPI commands.

extern app_t const atmel_radio_app;

#endif // ATMEL_RADIO_H

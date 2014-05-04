/*! \file nrf.h
  \author Travis Goodspeed
  \brief Constants for NRF Driver
*/

#ifndef NRF_H
#define NRF_H

#include "app.h"

#define NRF   0x50

//Nordic RF Commands

//Grab a packet, if one is available.
#define NRF_RX 0x80
//Send a packet.
#define NRF_TX 0x81
//Flush RX
#define NRF_RX_FLUSH 0x82
//Flush TX
#define NRF_TX_FLUSH 0x83


//Nordic RF SPI Instructions
#define NRF_R_REGISTER   0x00
#define NRF_W_REGISTER   0x20
#define NRF_R_RX_PAYLOAD 0x61
#define NRF_W_TX_PAYLOAD 0xA0
#define NRF_FLUSH_TX     0xE1
#define NRF_FLUSH_RX     0xE2
#define NRF_REUSE_TX_PL  0xE3
#define NRF_NOP          0xFF


//NRF24L01+ Registers
//These aren't yet used, but are included for later
//translation to XML.
#define NRF_CONFIG      0x00
#define NRF_EN_AA       0x01
#define NRF_EN_RXADDR   0x02
#define NRF_SETUP_AW    0x03
#define NRF_SETUP_RETR  0x04
#define NRF_RF_CH       0x05
#define NRF_RF_SETUP    0x06
#define NRF_STATUS      0x07
#define NRF_OBSERVE_TX  0x08
#define NRF_RPD         0x09
#define NRF_RX_ADDR_P0  0x0A
#define NRF_RX_ADDR_P1  0x0B
#define NRF_RX_ADDR_P2  0x0C
#define NRF_RX_ADDR_P3  0x0D
#define NRF_RX_ADDR_P4  0x0E
#define NRF_RX_ADDR_P5  0x0F
#define NRF_TX_ADDR     0x10
#define NRF_RX_PW_P0    0x11
#define NRF_RX_PW_P1    0x12
#define NRF_RX_PW_P2    0x13
#define NRF_RX_PW_P3    0x14
#define NRF_RX_PW_P4    0x15
#define NRF_RX_PW_P5    0x16
#define NRF_FIFO_STATUS 0x17
#define NRF_DYNPD       0x1C
//Also 32-byte buffers for ACK_PLD, TX_PLD, and RX_PLD.
//Separate SPI commands.

extern app_t const nrf_app;

#endif // NRF_H


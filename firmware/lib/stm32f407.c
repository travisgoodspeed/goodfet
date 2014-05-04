/*! \file stm32f407.h
  \author Travis Goodspeed
  \brief STM32F407 port definitions.
*/

#include "platform.h"

#include "stm32f4xx.h"
//#include "stm322xg_eval.h"
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <stm32f4xx_usart.h>
#include "stm32f4_discovery.h"

void ioinit(){
  GPIO_InitTypeDef  GPIO_InitStructure;
  
  /* GPIOD Periph clock enable */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOD, ENABLE);

  /* Configure PD12, PD13, PD14 and PD15 in output pushpull mode */
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12 | GPIO_Pin_13| GPIO_Pin_14| GPIO_Pin_15;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_OUT;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_UP;
  GPIO_Init(GPIOD, &GPIO_InitStructure);
}

void stmdelay(){
  //IO so it doesn't get swapped out.
  __IO uint32_t count=   0x1000;   // >1kbit/s
  //__IO uint32_t count= 0x100000; // 5 bits per second, for testing
  while(count--);
}

/* Used for debugging only.

void ledon(){
  GPIO_SetBits(GPIOD, GPIO_Pin_14);
}
void ledoff(){
  GPIO_ResetBits(GPIOD, GPIO_Pin_14);
}
void clkon(){
  GPIO_SetBits(GPIOD, GPIO_Pin_12);
}
void clkoff(){
  GPIO_ResetBits(GPIOD, GPIO_Pin_12);
}



void spibit(int one){
  if(one) ledon();
  else    ledoff();
  clkon();
  stmdelay();
  clkoff();
  stmdelay();
}

void spiword(uint32_t word){
  int i=32;
  while(i--){
    //morsebit(word&1);
    //manchesterbit(word&1);
    spibit(word&1);
    word=(word>>1);
  }
}
void spibyte(uint8_t word){
  int i=8;
  while(i--){
    //morsebit(word&1);
    //manchesterbit(word&1);
    spibit(word&1);
    word=(word>>1);
  }
}

*/

//! Count the length of a string.
uint32_t strlen(const char *s){
  int i=0;
  while(s[i++]);
  return i-1;
}


/**************************************************************************************/
void Repair_Data();
void RCC_Configuration(void)
{
  /* --------------------------- System Clocks Configuration -----------------*/
  /* USART1 clock enable */
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
 
  /* GPIOB clock enable */
  RCC_AHB1PeriphClockCmd(RCC_AHB1Periph_GPIOB, ENABLE);
}
 
/**************************************************************************************/
 
void GPIO_Configuration(void)
{
  GPIO_InitTypeDef GPIO_InitStructure;
 
  /*-------------------------- GPIO Configuration ----------------------------*/
  GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6 | GPIO_Pin_7;
  GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF;
  GPIO_InitStructure.GPIO_OType = GPIO_OType_PP;
  GPIO_InitStructure.GPIO_PuPd = GPIO_PuPd_NOPULL;
  GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
  GPIO_Init(GPIOB, &GPIO_InitStructure);
 
  /* Connect USART pins to AF */
  GPIO_PinAFConfig(GPIOB, GPIO_PinSource6, GPIO_AF_USART1); // USART1_TX
  GPIO_PinAFConfig(GPIOB, GPIO_PinSource7, GPIO_AF_USART1); // USART1_RX
}
 
/**************************************************************************************/
 
void USART1_Configuration(void)
{
  USART_InitTypeDef USART_InitStructure;
 
  /* USARTx configuration ------------------------------------------------------*/
  /* USARTx configured as follow:
        - BaudRate = 115200 baud
        - Word Length = 8 Bits
        - One Stop Bit
        - No parity
        - Hardware flow control disabled (RTS and CTS signals)
        - Receive and transmit enabled
  */
  //USART_InitStructure.USART_BaudRate = 9600;
  //USART_InitStructure.USART_BaudRate = 10000; //Close enough to 9600
  //USART_InitStructure.USART_BaudRate = 115200;
  //USART_InitStructure.USART_BaudRate = 125200;  //Close enough to 115200
  
  //135000 is too high
  //115200 is too low
  USART_InitStructure.USART_BaudRate = 125000;  //Close enough to 115200
  
  USART_InitStructure.USART_WordLength = USART_WordLength_8b;
  USART_InitStructure.USART_StopBits = USART_StopBits_1;
  USART_InitStructure.USART_Parity = USART_Parity_No;
  USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
 
  USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
 
  USART_Init(USART1, &USART_InitStructure);
 
  USART_Cmd(USART1, ENABLE);
}
 

//! Initialize the USART
void usartinit(){
  RCC_Configuration();
 
  GPIO_Configuration();
 
  USART1_Configuration();
}


//! Initialize the STM32F4xx ports and USB.
void stm32f4xx_init(){
  int i=20;
  
  SystemInit();
  ioinit();
  usartinit();
  
  while(i--) stmdelay();
  
  return;
}

//! Receive a byte.
unsigned char serial0_rx(){
  while(USART_GetFlagStatus(USART1, USART_FLAG_RXNE) == RESET); // Wait for Character
  return USART_ReceiveData(USART1);
}

//! Receive a byte.
unsigned char serial1_rx(){
}

//! Transmit a byte.
void serial0_tx(unsigned char x){
  
  //Send through USART1 on PB6
  while(USART_GetFlagStatus(USART1, USART_FLAG_TXE) == RESET); //original
  USART_SendData(USART1, (uint16_t) x);
  
  //Spare goes to SPI.
  //spibyte(x);
}

//! Transmit a byte on the second UART.
void serial1_tx(unsigned char x){

}

//! Set the baud rate.
void setbaud0(unsigned char rate){
  //Ignore this, as we'll be in USB.
}

//! Set the baud rate of the second uart.
void setbaud1(unsigned char rate){

}


//Declarations
void nmi_handler(void);
void hardfault_handler(void);
int main(void);

//From min.s
void Reset_Handler(void);

// Define the vector table
unsigned int * myvectors[50] 
   __attribute__ ((section("vectors")))= {
   	(unsigned int *)	0x20000800,	        // stack pointer
   	(unsigned int *) 	Reset_Handler,		        // code entry point
   	(unsigned int *)	main,		// NMI handler (not really)
   	(unsigned int *)	main,	// hard fault handler (let's hope not)	
};

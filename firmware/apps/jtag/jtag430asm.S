.globl jtag430_tclk_flashpulses
.type jtag430_tclk_flashpulses,@function //for linking

#define _GNU_ASSEMBLER_
#include "config.h"

//We need to include port definitions,
//but msp430.h is no long asm clean.
#include <msp430f1612.h>

//This detects model, chooses appropriate timing.
jtag430_tclk_flashpulses:
	mov &0x0ff0, r14
	cmp  #0x6cf1, r14	;Is the chip an MSP430F1xx?
	jz jtag430_tclk_flashpulses_3mhz
	jmp jtag430_tclk_flashpulses_16mhz
	
// At 3.68MHz, 7 to 14 cycles/loop are allowed for 257 to 475kHz.
// At 16MHz, 33 to 62 cycles/loop are allowed.
jtag430_tclk_flashpulses_3mhz:
	mov #P5OUT, r14
pulseloop3:
	bis.b #2, @r14		;SETTCLK, 3 cycles
	sub #1, r15		; 1 cycle
	;;  1+3+3+1+2=10, within limits
	nop
	nop
	nop			;10+3=13
	
	bic.b #2, @r14		;CLRTCLK, 3 cycles
	tst r15			; 1 cycle
	jnz pulseloop3		; 2 cycles
	ret

jtag430_tclk_flashpulses_16mhz:
	mov #P5OUT, r14
pulseloop16:	
	bis.b #2, @r14		;SETTCLK, 3 cycles
	sub #1, r15		; 1 cycle
	;;  1+3+3+1+2=10, beneath limits,

	;; +3+2=5, repeat 8 times to get 10+40=50, within limits
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	push r11		; 3 cycles
	pop r11			; 2 cycles
	
	
	bic.b #2, @r14		;CLRTCLK, 3 cycles
	tst r15			; 1 cycle
	jnz pulseloop16		; 2 cycles
	ret


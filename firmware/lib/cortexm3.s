  .syntax unified
  .cpu cortex-m3
  .fpu softvfp
  .thumb


.section  .text.Reset_Handler
  .weak  Reset_Handler
  .type  Reset_Handler, %function

Reset_Handler:
	mov r0, #0
	ldr r13, =0x20002000
	bl main


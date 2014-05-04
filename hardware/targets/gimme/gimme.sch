EESchema Schematic File Version 2  date Tue Sep 18 22:52:17 2012
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:gimme-cache
EELAYER 25  0
EELAYER END
$Descr A4 11700 8267
encoding utf-8
Sheet 1 1
Title "GIMME"
Date "14 sep 2012"
Rev "$Rev: 1260 $"
Comp "Copyright 2012 Michael Ossmann"
Comment1 "License: BSD 3-Clause, http://goodfet.sourceforge.net/"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 6950 4950 0    40   ~ 0
LED indicates power on the target board.\n\nIf power is supplied by the GoodFET through SW1 (recommended),\nLED illuminates at all times GoodFET is connected.  If power is not\nsupplied by the GoodFET, LED only illuminates when contact is made\nwith target.\n\nDo not attempt to program target if LED does not indicate target power.\n\nDo not supply power from GoodFET through SW1 if target is\npowered from another source.
$Comp
L 3V3 #PWR01
U 1 1 50523842
P 4300 3950
F 0 "#PWR01" H 4300 4050 40  0001 C CNN
F 1 "3V3" H 4300 4075 40  0000 C CNN
	1    4300 3950
	-1   0    0    1   
$EndComp
Connection ~ 8100 3350
Wire Wire Line
	8100 3250 8100 3450
Wire Wire Line
	8100 3350 8000 3350
Wire Wire Line
	8100 4550 8100 4450
Wire Wire Line
	5750 3650 5450 3650
Wire Wire Line
	5750 3350 5450 3350
Wire Wire Line
	4300 3850 4300 3950
Wire Wire Line
	4100 3850 4100 4150
Wire Wire Line
	4000 3850 4000 4150
Wire Wire Line
	4200 3850 4200 4150
Wire Wire Line
	4400 3850 4400 3950
Wire Wire Line
	5750 3550 5450 3550
Wire Wire Line
	5750 3750 5550 3750
Wire Wire Line
	7000 3350 6550 3350
Wire Wire Line
	8100 4050 8100 3950
Wire Wire Line
	5550 3750 5550 3850
$Comp
L 3V3 #PWR02
U 1 1 5052383E
P 8100 3250
F 0 "#PWR02" H 8100 3350 40  0001 C CNN
F 1 "3V3" H 8100 3375 40  0000 C CNN
	1    8100 3250
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR03
U 1 1 50523829
P 4400 3950
F 0 "#PWR03" H 4400 3950 30  0001 C CNN
F 1 "GND" H 4400 3880 30  0001 C CNN
	1    4400 3950
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR04
U 1 1 505237D4
P 5550 3850
F 0 "#PWR04" H 5550 3850 30  0001 C CNN
F 1 "GND" H 5550 3780 30  0001 C CNN
	1    5550 3850
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR05
U 1 1 505237C3
P 8100 4550
F 0 "#PWR05" H 8100 4550 30  0001 C CNN
F 1 "GND" H 8100 4480 30  0001 C CNN
	1    8100 4550
	1    0    0    -1  
$EndComp
$Comp
L R R1
U 1 1 505237B8
P 8100 3700
F 0 "R1" V 8180 3700 50  0000 C CNN
F 1 "330" V 8100 3700 50  0000 C CNN
F 4 "Stackpole" H 8100 3700 60  0001 C CNN "Manufacturer"
F 5 "RMCF0603JT330R" H 8100 3700 60  0001 C CNN "Part Number"
F 6 "RES 330 OHM 1/10W 5% 0603 SMD" H 8100 3700 60  0001 C CNN "Description"
	1    8100 3700
	1    0    0    -1  
$EndComp
$Comp
L LED D1
U 1 1 505237B2
P 8100 4250
F 0 "D1" H 8100 4350 50  0000 C CNN
F 1 "LED" H 8100 4150 50  0000 C CNN
F 4 "OSRAM" H 8100 4250 60  0001 C CNN "Manufacturer"
F 5 "LG Q971-KN-1" H 8100 4250 60  0001 C CNN "Part Number"
F 6 "LED CHIPLED 570NM GREEN 0603 SMD" H 8100 4250 60  0001 C CNN "Description"
	1    8100 4250
	0    1    1    0   
$EndComp
NoConn ~ 6550 3950
NoConn ~ 6550 3850
NoConn ~ 6550 3750
NoConn ~ 6550 3650
NoConn ~ 6550 3550
NoConn ~ 6550 3450
NoConn ~ 5750 3950
NoConn ~ 5750 3850
NoConn ~ 5750 3450
Text Label 5450 3650 0    40   ~ 0
DC
Text Label 5450 3550 0    40   ~ 0
RESET_N
Text Label 5450 3350 0    40   ~ 0
DD
Text Label 4200 4150 1    40   ~ 0
DC
Text Label 4100 4150 1    40   ~ 0
DD
Text Label 4000 4150 1    40   ~ 0
RESET_N
$Comp
L SPST SW1
U 1 1 505236F1
P 7500 3350
F 0 "SW1" H 7500 3450 70  0000 C CNN
F 1 "SPST" H 7500 3250 70  0000 C CNN
F 4 "ALPS" H 7500 3350 60  0001 C CNN "Manufacturer"
F 5 "SSSS810701" H 7500 3350 60  0001 C CNN "Part Number"
F 6 "Slide Switches Horiz 1 Pole 2 Pos 1.1 Knob 1.5 Travel" H 7500 3350 60  0001 C CNN "Description"
F 7 "Alternate: https://www.sparkfun.com/products/10860" H 7500 3350 60  0001 C CNN "Note"
	1    7500 3350
	1    0    0    -1  
$EndComp
$Comp
L CONN_5 P1
U 1 1 505236D2
P 4200 3450
F 0 "P1" V 4150 3450 50  0000 C CNN
F 1 "POGOPINS" V 4250 3450 50  0000 C CNN
F 4 "SparkFun" H 4200 3450 60  0001 C CNN "Manufacturer"
F 5 "PRT-09174" H 4200 3450 60  0001 C CNN "Part Number"
F 6 "Pogo Pins w/ Pointed Tip" H 4200 3450 60  0001 C CNN "Description"
F 7 "quantity 5" H 4200 3450 60  0001 C CNN "Note"
	1    4200 3450
	0    -1   -1   0   
$EndComp
$Comp
L CONN_7X2 P2
U 1 1 505236A9
P 6150 3650
F 0 "P2" H 6150 4050 60  0000 C CNN
F 1 "GOODFET" V 6150 3650 60  0000 C CNN
	1    6150 3650
	1    0    0    -1  
$EndComp
$EndSCHEMATC

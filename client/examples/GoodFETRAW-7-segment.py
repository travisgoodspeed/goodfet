#!/usr/bin/env python
''' GoodFET RAW Client Library
(C) 2015 Thomas Tannhaeuser <hecke at naberius.de>
'''

import os, sys, time
sys.path.insert(1, os.path.dirname(os.path.realpath(sys.argv[0] +  '/..')))

from GoodFETRAW import GoodFETRAW

def seven_segment(raw, num):

    ''' 0..9 on SA03-11GWA (7 segment + decimal point, 
        green, common anode), wire schema:

          TDO:1
          ------
    TCK:2|      | TDI:13
         |RST:11|
          ------
    RXD:7|      | TMS:10
         |      |
          ------
          TXD:8

          Vcc:14
    '''

    raw.set_direction_output('all')

    nums = [
        ['TDO', 'TDI', 'TMS', 'TXD', 'RXD', 'TCK'],
        ['TDI', 'TMS'],
        ['TDO', 'TDI', 'RST', 'RXD', 'TXD' ],
        ['TDO', 'TDI', 'RST', 'TMS', 'TXD'],
        ['TDI', 'RST', 'TMS', 'TCK' ],
        ['TDO', 'RST', 'TMS', 'TXD', 'TCK'],
        ['TDO', 'RST', 'TMS', 'TXD', 'RXD', 'TCK'],
        ['TDO', 'TDI', 'TMS' ],
        ['TDO', 'TDI', 'RST', 'TMS', 'TXD', 'RXD', 'TCK'],
        ['TDO', 'TDI', 'RST', 'TMS', 'TXD', 'TCK']
    ]

    all_pin = ['TDO', 'TDI', 'RST', 'TMS', 'TXD', 'RXD', 'TCK']

    pins_low = nums[num % 10]
    pins_high = [x for x in all_pin if x not in pins_low]

    raw.set_pins(pins_high)
    raw.clear_pins(pins_low)


if __name__ == '__main__':

    RAW = GoodFETRAW()
    RAW.serInit()
    RAW.setup()

    while True:
        for i in range(0, 10):
            seven_segment(RAW, i)
            time.sleep(1.0)

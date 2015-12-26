#!/usr/bin/env python
''' GoodFET RAW Client Library
(C) 2015 Thomas Tannhaeuser <hecke at naberius.de>
'''

from GoodFET import GoodFET
import time

class GoodFETRAW(GoodFET):
    ''' implements raw access to the PINS of the GoodFET '''
    
    APP_RAW             = 0x42

    VERB_SETUP          = 0x10
    VERB_NOK            = 0x7e
    VERB_OK             = 0x7f
    VERB_SET_DIR_INPUT  = 0x80
    VERB_SET_DIR_OUTPUT = 0x81
    VERB_READ           = 0x82
    VERB_CLEAR          = 0x83
    VERB_SET            = 0x84

    PINS = {
        'tdo' : 1 << 0,
        'tdi' : 1 << 1,
        'tms' : 1 << 2,
        'tck' : 1 << 3,
        'rst' : 1 << 4,
        'tst' : 1 << 5,
        'rxd' : 1 << 6,
        'txd' : 1 << 7
    }
    def setup(self):
        ''' enable RAW application on the GoodFET '''
        self.writecmd(self.APP_RAW, 0x10, 0, self.data)

    def get_pin_mask(self, pins):
        ''' return the bit-mask representing the requested pins 

            >>> from GoodFETRAW import *
            >>> raw = GoodFETRAW()
            >>> raw.get_pin_mask('all')
            255
            >>> raw.get_pin_mask(['RST', 'rxd', 'tDi'])
            82
            >>> raw.get_pin_mask('RST')
            16
        '''

        mask = 0
        try:
            if isinstance(pins, list) is True:
                for k in pins:
                    mask += self.PINS[k.lower()]
            else:
                if pins.lower() == 'all':
                    mask = sum(self.PINS.itervalues())
                else:
                    mask += self.PINS[pins.lower()]
        except KeyError as err:
            raise Exception('unknown pin given: %s' % (err))

        return mask

    def _run_verb(self, verb, pins):
        ''' run the given verb on selected pins, return tuple mask, data '''

        mask = self.get_pin_mask(pins)
        
        try:
            ret = self.writecmd(self.APP_RAW, verb, 1, [mask])

            return ord(ret[0]), (ord(ret[1]) if len(ret) == 2 else None)
        except IndexError:
            raise Exception('IO-error - failed to run app ' \
                            '\'0x%02x\' verb \'0x%02x\': ' \
                            'invalid response (APP/verb not known?)' % \
                            (self.APP_RAW, verb))
        except Exception as err:
            raise Exception('IO-error - failed to run app ' \
                            '\'0x%02x\' verb \'0x%02x\': %s' % \
                            (self.APP_RAW, verb, err))

    def set_direction_output(self, pins = 'all'):
        ''' set the direction of the selected pins to output '''

        return self._run_verb(self.VERB_SET_DIR_OUTPUT, pins)[0]

    def set_direction_input(self, pins = 'all'):
        ''' set the direction of the selected pins to input '''

        return self._run_verb(self.VERB_SET_DIR_INPUT, pins)[0]

    def set_pins(self, pins = 'all'):
        ''' set the selected pins to HIGH '''

        return self._run_verb(self.VERB_SET, pins)[0]

    def clear_pins(self, pins = 'all'):
        ''' set the selected pins to LOW '''

        return self._run_verb(self.VERB_CLEAR, pins)[0]

    def read_pins(self, pins = 'all'):
        ''' read the state of the selected pins '''

        return self._run_verb(self.VERB_READ, pins)[1]

if __name__ == '__main__':

    def run_test(raw, grp_a, grp_b):
        ''' run a cross test to check IO function, connect pins as given below:
        tdo - rst
        tdi - tst
        tms - rxd
        tck - txd
        '''
        if raw.verbose:
            print 'grp_a - set dir inp: %02d' % \
                    (raw.set_direction_input(grp_a))
            print 'grp_b - set dir outp: %02d' % \
                    (raw.set_direction_output(grp_b))

            print 'clear all: %02d' % (raw.clear_pins(grp_b))
        else:
            raw.set_direction_input(grp_a)
            raw.set_direction_output(grp_b)
            raw.clear_pins(grp_b)

        for idx, pin in enumerate(grp_b):
            if raw.verbose:
                print '----'
                print 'clear all: %02d' % (raw.clear_pins(grp_b))
                print 'set %02x: %02x' % \
                    (raw.get_pin_mask(pin), raw.set_pins(pin))
            else:
                raw.clear_pins(grp_b)
                raw.set_pins(pin)


            val = raw.get_pin_mask(grp_a[idx])
            ret = raw.read_pins(grp_a)

            if raw.verbose:
                print 'read: %02x' % (ret)

            if val != ret:
                raise Exception('invalid value read - wiring broken?')

    RAW = GoodFETRAW()
    RAW.serInit()
    RAW.setup()
    #RAW.verbose = True
    
    GRP_A = ['tdo', 'tdi', 'tms', 'tck']
    GRP_B = ['rst', 'tst', 'rxd', 'txd']

    run_test(RAW, GRP_A, GRP_B)
    run_test(RAW, GRP_B, GRP_A)

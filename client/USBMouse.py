# USBMouse.py
#
# Contains class definitions to implement a USB mouse.
#
# http://www.usb.org/developers/hidpage/HID1_11.pdf
# http://www.usb.org/developers/hidpage/Hut1_12v2.pdf

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBClass import *
from math import *


class USBHIDClass(USBClass):
    name = "USB HID class"

    def setup_request_handlers(self):
        self.request_handlers = {
            0x0A : self.handle_set_idle_request,
        }

    def handle_set_idle_request(self, req):
        print(self.name, "received SET_IDLE request, duration %d, report %d" \
              % (req.value >> 8, req.value & 0xFF))
        self.interface.configuration.device.send_control_message(b'')


class USBMouseInterface(USBInterface):
    name = "USB mouse interface"

    hid_descriptor = b'\x09\x21\x10\x01\x00\x01\x22\x2c\x01'
    report_descriptor = ( b'\x05\x01\x09\x02\xa1\x01\x09\x01\xa1'
                          #                ^-- usage 2 = mouse
                          b'\x00\x05\x09\x19\x01\x29\x03\x15\x00\x25\x01'
                          #     first button --^       ^-- last button
                          b'\x95\x03\x75\x01\x81\x02\x95\x01\x75\x05\x81\x03'
                          #        ^-- no. of buttons              ^-- padding
                          b'\x05\x01\x09\x30\x09\x31\x09\x38\x15\x81\x25\x7f'
                          #               ^-- X   ^-- Y   ^-- wheel
                          b'\x75\x08\x95\x03\x81\x06\xc0\xc0' )
                          #                ^-- no. of axes

    def __init__(self, device, verbose=0):
        descriptors = { 
                USB.desc_type_hid    : self.hid_descriptor,
                USB.desc_type_report : self.report_descriptor
        }

        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                10,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
        )

        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                0,          # interface number
                0,          # alternate setting
                3,          # interface class
                0,          # subclass
                0,          # protocol
                0,          # string index
                verbose,
                [ self.endpoint ],
                descriptors
        )

        self.device_class = USBHIDClass()
        self.device_class.set_interface(self)

        self.t = 0

    def handle_buffer_available(self):
        t = self.t
        if t>10:
            self.move(10*sin(t), 10*cos(t))
        self.t += 0.1

    def move(self, x, y):
        data = bytes([ 0, (256+trunc(x))%255, (256+trunc(y))%255, 0 ])

        self.endpoint.send(data)


class USBMouseDevice(USBDevice):
    name = "USB mouse device"

    def __init__(self, maxusb_app, verbose=0):
        config = USBConfiguration(
                1,                                          # index
                "Emulated Mouse",    # string desc
                [ USBMouseInterface(self) ]                 # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                0x610b,                 # vendor id
                0x4653,                 # product id
                0x3412,                 # device revision
                "Maxim",                # manufacturer string
                "MAX3420E Enum Code",   # product string
                "S/N3420E",             # serial number string
                [ config ],
                verbose=verbose
        )

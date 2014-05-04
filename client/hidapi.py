from ctypes import *

# Python doesn't define any sort of ABI string, so we need to manually probe for it.
# If your OS/arch isn't supported yet, see lib/README for help.

import platform
import sys

def _get_shared_lib_name():
    if sys.platform.startswith('linux'):
        # This may fail for a x86_32 userland on a x86_64 kernel. platform.architecture can be used to work around it, if necessary
        arch = platform.machine()
        if arch == 'amd64':
            # old 64-bit linux.
            arch = 'x86_64'
        if arch == 'x86_64' and platform.architecture()[0] == '32bit':
            # Whee! 32-bit python on a 64-bit kernel. The horror!
            arch = 'x86_32'
        if arch[0] == 'i' and arch[2:] == '86':
            arch = 'x86_32'
        # Any other variations need to be dealt with here.

        return "lib/hidapi-%(platform)s-%(arch)s.so" % {"platform": sys.platform, "arch": arch}
    elif sys.platform == 'darwin':
        # This is completely backwards... both 32 and 64 report an i386.
        # However, it may not matter; darwin supports fat binaries.
        # If necessary, here's what I've found (very incomplete):
        #
        # arch*  machine    desired build
        # 64bit  i386       x86_64
        return "lib/hidapi-darwin.dylib"
    elif sys.platform == 'win32':
        # not yet fully supported. For now, assuming 32-bit x86.
        return "lib/hidapi-win32-x86_32.dll"
    else:
        print >>sys.stderr, "Your platform is not yet supported. Please let the devs know, or read lib/README for help fixing it."
        raise Exception("Unsupported platform")

if __name__ == '__main__':
    print "Would try to load %s" % _get_shared_lib_name()

_hidapi = CDLL(_get_shared_lib_name())

class _HidDeviceInfo(Structure):
    pass

_HidDeviceInfo._fields_ = [
    ("path", c_char_p),
    ("vendor_id", c_ushort),
    ("product_id", c_ushort),
    ("serial_number", c_wchar_p),
    ("release_number", c_ushort),
    ("manufacturer_string", c_wchar_p),
    ("product_string", c_wchar_p),
    ("usage_page", c_ushort),
    ("usage", c_ushort),
    ("interface_number", c_int),
    ("next", POINTER(_HidDeviceInfo))]

class HidDeviceInfo(object):
    """User-facing version of the _HidDeviceInfo structure."""

    def __init__(self, raw):
        for attr in ("path", "vendor_id", "product_id", "serial_number", "release_number", "manufacturer_string", "product_string", "usage_page", "usage", "interface_number"):
            setattr(self, attr, getattr(raw, attr))

    def open(self):
        return HidDevice(self.vendor_id, self.product_id, self.serial_number)

class _HidDevice_p(c_void_p):
    pass

class HidDevice(object):
    def __init__(self, vid, pid=None, serial=None):
        if type(vid) is str:
            assert pid is None and serial is None
            self._device = _hidapi.hid_open_path(vid)
        else:
            self._device = _hidapi.hid_open(vid, pid, serial)
        if not self._device:
            raise IOError("Failed to open device")

    def write(self, string):
        return _hidapi.hid_write(self._device, create_string_buffer(string), len(string))
    def read(self, length):
        buf = create_string_buffer(length)
        olen = _hidapi.hid_read(self._device, buf, length)
        return buf.raw[:length]
    def set_nonblocking(self, nonblocking = True):
        _hidapi.hid_set_nonblocking(self._device, nonblocking)
    def send_feature_report(self, report_id, data):
        buf = create_string_buffer(chr(report_id) + data)

        return _hidapi.hid_send_feature_report(self._device, buf, len(data) + 1)
    def get_feature_report(self, report_id, length):
        # length does not include report id
        buf = create_string_buffer(length + 1)
        buf[0] = report_id
        olen = _hidapi.hid_get_feature_report(self._device, buf, length + 1)
        # BUG(thequux): Possible off-by-one error
        return buf.raw[1:olen]

    def close(self):
        _hidapi.hid_close(self._device)
        self._device = None

    def get_manufacturer_string(_device):
        buf = create_unicode_buffer(257)
        _hidapi.hid_get_manufacturer_string(self._device, buf, 257)
        return buf.value

    def get_product_string(_device):
        buf = create_unicode_buffer(257)
        _hidapi.hid_get_product_string(self._device, buf, 257)
        return buf.value

    def get_serial_number_string(_device):
        buf = create_unicode_buffer(257)
        _hidapi.hid_get_serial_number_string(self._device, buf, 257)
        return buf.value

    def get_indexed_string(_device, index):
        buf = create_unicode_buffer(257)
        _hidapi.hid_get_indexed_string(self._device, index, buf, 257)
        return buf.value




class HidApiError(IOError):
    pass

def _check_hid_error(result, func, args):
    if result == -1:
        print args, _hidapi.hid_error(args[0])
        raise HidApiError(_hidapi.hid_error(args[0]))
    return result

# signatures
_hidapi.hid_enumerate.argtypes = [c_ushort, c_ushort]
_hidapi.hid_enumerate.restype = POINTER(_HidDeviceInfo)

_hidapi.hid_free_enumeration.argtypes = [POINTER(_HidDeviceInfo)]

_hidapi.hid_open.argtypes = [c_ushort, c_ushort, c_wchar_p]
_hidapi.hid_open.restype = _HidDevice_p

_hidapi.hid_open_path.argtypes = [c_char_p]
_hidapi.hid_open_path.restype = _HidDevice_p

_hidapi.hid_write.argtypes = [_HidDevice_p, POINTER(c_char), c_size_t]
_hidapi.hid_write.restype = c_int
_hidapi.hid_write.errcheck = _check_hid_error

_hidapi.hid_read.argtypes = [_HidDevice_p, POINTER(c_char), c_size_t]
_hidapi.hid_read.restype = c_int
_hidapi.hid_read.errcheck = _check_hid_error

_hidapi.hid_set_nonblocking.argtypes = [_HidDevice_p, c_int]
_hidapi.hid_set_nonblocking.restype = c_int
_hidapi.hid_set_nonblocking.errcheck = _check_hid_error

_hidapi.hid_send_feature_report.argtypes = [_HidDevice_p, POINTER(c_char), c_size_t]
_hidapi.hid_send_feature_report.restype = c_int
_hidapi.hid_send_feature_report.errcheck = _check_hid_error

_hidapi.hid_get_feature_report.argtypes = [_HidDevice_p, POINTER(c_char), c_size_t]
_hidapi.hid_get_feature_report.restype = c_int
_hidapi.hid_get_feature_report.errcheck = _check_hid_error

_hidapi.hid_close.argtypes = [_HidDevice_p]

_hidapi.hid_get_manufacturer_string.argtypes = [_HidDevice_p, POINTER(c_wchar), c_size_t]
_hidapi.hid_get_manufacturer_string.restype = c_int
_hidapi.hid_get_manufacturer_string.errcheck = _check_hid_error

_hidapi.hid_get_product_string.argtypes = [_HidDevice_p, POINTER(c_wchar), c_size_t]
_hidapi.hid_get_product_string.restype = c_int
_hidapi.hid_get_product_string.errcheck = _check_hid_error

_hidapi.hid_get_serial_number_string.argtypes = [_HidDevice_p, POINTER(c_wchar), c_size_t]
_hidapi.hid_get_serial_number_string.restype = c_int
_hidapi.hid_get_serial_number_string.errcheck = _check_hid_error

_hidapi.hid_get_indexed_string.argtypes = [_HidDevice_p, c_int, POINTER(c_wchar), c_size_t]
_hidapi.hid_get_indexed_string.restype = c_int
_hidapi.hid_get_indexed_string.errcheck = _check_hid_error

_hidapi.hid_error.argtypes = [_HidDevice_p]
_hidapi.hid_error.restype = c_wchar_p

def hid_enumerate(vid=0, pid=0):
    """Enumerate the HID devices.

    If vid == pid == 0, will enumerate all hid devices. Otherwise, just the ones with the given vid/pid.

    Returns:
       List of HidDeviceInfo structures.
    """

    devs = _hidapi.hid_enumerate(vid,pid)

    raw_list = devs
    ret = []
    while raw_list:
        raw = raw_list.contents
        raw_list = raw.next
        ret.append(HidDeviceInfo(raw))

    _hidapi.hid_free_enumeration(devs)
    return ret

def hid_open(vid, pid, serial_number = None):
    return HidDevice(vid, pid, serial_number)

def hid_open_path(path):
    return HidDevice(path)

if __name__ == '__main__':
    for dev in hid_enumerate():
        print "%04x:%04x %30s <%s> <%s> %d" % (dev.vendor_id, dev.product_id, dev.serial_number, dev.manufacturer_string, dev.product_string, dev.interface_number)

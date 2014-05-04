# util.py
#
# Random helpful functions.

def bytes_as_hex(b, delim=" "):
    return delim.join(["%02x" % x for x in b])


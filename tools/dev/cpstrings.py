"""Constant-pool reader used by cpgrep.py: read_utf8_constants(class_bytes) -> list of the class file's UTF8 constants
(class names, method names, descriptors, string literals). Pure Python, no JVM."""
import struct

_SIZES = {3: 4, 4: 4, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4, 12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}


def read_utf8_constants(data):
    if data[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("not a class file")
    count = struct.unpack_from(">H", data, 8)[0]
    pos, i, out = 10, 1, []
    while i < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            n = struct.unpack_from(">H", data, pos)[0]
            pos += 2
            out.append(data[pos:pos + n].decode("utf-8", errors="replace"))
            pos += n
        elif tag in (5, 6):
            pos += 8
            i += 1  # long/double take two slots
        elif tag in _SIZES:
            pos += _SIZES[tag]
        else:
            raise ValueError("bad constant tag %d at %d" % (tag, pos - 1))
        i += 1
    return out

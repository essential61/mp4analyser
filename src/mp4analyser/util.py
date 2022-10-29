"""
util.py

Utility functions to save me typing struct.unpack all the time.

"""
import struct


def read_u8(fp):
    return struct.unpack('>B', fp.read(1))[0]


def read_u16(fp):
    return struct.unpack('>H', fp.read(2))[0]


def read_u32(fp):
    return struct.unpack('>I', fp.read(4))[0]


def read_u64(fp):
    return struct.unpack('>Q', fp.read(8))[0]


def read_i8(fp):
    return struct.unpack('>b', fp.read(1))[0]


def read_i16(fp):
    return struct.unpack('>h', fp.read(2))[0]


def read_i32(fp):
    return struct.unpack('>i', fp.read(4))[0]


def read_i64(fp):
    return struct.unpack('>q', fp.read(8))[0]


def read_u8_8(fp):
    ipart, fpart = struct.unpack('>2B', fp.read(2))
    return ipart + (fpart / 256)


def read_u16_16(fp):
    ipart, fpart = struct.unpack('>2H', fp.read(4))
    return ipart + (fpart / 65536)


def read_i8_8(fp):
    ipart = struct.unpack('>b', fp.read(1))[0]
    fpart = struct.unpack('B', fp.read(1))[0]
    return ipart + (fpart / 256)



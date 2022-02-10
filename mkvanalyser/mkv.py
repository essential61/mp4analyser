"""
mkv.py


"""
import datetime
import struct
import logging

from mkvanalyser import idlookups


def element_factory(fp, elementid_tuple, parent):
    """
    element_factory() takes a box type as a parameter and, if a class has been defined for that type, returns
    an instance of that class.
    """
    (elementid, elementidbytes) = elementid_tuple
    if elementid not in idlookups.id_table:
        element_type = 'Unhandled'
    else:
        element_type = idlookups.id_table[elementid]['type']
    if element_type == 'binary':
        return BinaryElement(fp, elementid_tuple, parent)
    if element_type == 'master':
        return MasterElement(fp, elementid_tuple, parent)
    if element_type == 'utf-8':
        return Utf_8Element(fp, elementid_tuple, parent)
    if element_type == 'string':
        return StringElement(fp, elementid_tuple, parent)
    if element_type == 'uinteger':
        return UintegerElement(fp, elementid_tuple, parent)
    if element_type == 'integer':
        return IntegerElement(fp, elementid_tuple, parent)
    if element_type == 'date':
        return DateElement(fp, elementid_tuple, parent)
    if element_type == 'float':
        return FloatElement(fp, elementid_tuple, parent)
    else:
        return UnhandledElement(fp, elementid_tuple, parent)


def read_id(fp):
    """
    reads value of an element id expressed as a VINT in a file, returns the id as an unsigned
    integer. A side-effect of this function is to advance the file pointer by the
    size in bytes of the VINT.
    """
    leftmostbyte = struct.unpack('>B', fp.read(1))[0]
    if leftmostbyte > 127:
        return leftmostbyte, 1
    elif leftmostbyte > 63:
        return (leftmostbyte << 8) + struct.unpack('>B', fp.read(1))[0], 2
    elif leftmostbyte > 31:
        return (leftmostbyte << 16) + struct.unpack('>H', fp.read(2))[0], 3
    elif leftmostbyte > 15:
        return (leftmostbyte << 24) + struct.unpack('>I', b'\x00' + fp.read(3))[0], 4


def read_data_length(fp):
    """
    reads value of an unsigned expressed as a VINT in a file, returns an unsigned integer and the size
    in bytes of the VINT (unlike element id, data length does not need to be smallest possible VINT).
     A side-effect of this function is to advance the file pointer by the size in bytes of the VINT.
    """
    leftmostbyte = struct.unpack('>B', fp.read(1))[0]
    if leftmostbyte > 127:
        return leftmostbyte % 128, 1
    elif leftmostbyte > 63:
        return (leftmostbyte % 64 << 8) + struct.unpack('>B', fp.read(1))[0], 2
    elif leftmostbyte > 31:
        return (leftmostbyte % 32 << 16) + struct.unpack('>H', fp.read(2))[0], 3
    elif leftmostbyte > 15:
        return (leftmostbyte % 16 << 24) + struct.unpack('>I', b'\x00' + fp.read(3))[0], 4
    elif leftmostbyte > 7:
        return (leftmostbyte % 8 << 32) + struct.unpack('>I', fp.read(4))[0], 5
    elif leftmostbyte > 3:
        return (leftmostbyte % 4 << 40) + (struct.unpack('>B', fp.read(1))[0] << 32) + struct.unpack('>I',
                                                                                                     fp.read(4))[0], 6
    elif leftmostbyte > 1:
        return (leftmostbyte % 2 << 48) + (struct.unpack('>H', fp.read(2))[0] << 32) + struct.unpack('>I',
                                                                                                     fp.read(4))[0], 7
    elif leftmostbyte == 1:
        return (struct.unpack('>B', fp.read(1))[0] << 48) + (struct.unpack('>H', fp.read(2))[0] << 32) + struct.unpack(
            '>I', fp.read(4))[0], 8
    else:
        return 0, 1


class MkvFile:
    """ MkvFile Class, effectively the top-level container """

    def __init__(self, filename):
        self.filename = filename
        self.type = 'file'
        self.elementid = 0
        self.children = []
        self.summary = {}
        with open(filename, 'rb') as f:
            end_of_file = False
            while not end_of_file:
                elementid_tuple = read_id(f)
                current_element = element_factory(f, elementid_tuple, self)
                self.children.append(current_element)
                if len(f.read(4)) != 4:
                    end_of_file = True
                else:
                    f.seek(-4, 1)
        f.close()

    def read_bytes(self, offset, num_bytes):
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            bytes_read = f.read(num_bytes)
        f.close()
        return bytes_read

    def get_summary(self):
        return 'TODO'


# Element classes

class MkvElement():

    def __init__(self, fp, elementid_tuple, parent):
        (self.elementid, self.elementidbytes) = elementid_tuple
        self.type = idlookups.id_table[self.elementid]['type'] if self.elementid in idlookups.id_table else 'unknown'
        self.parent = parent
        self.element_position = fp.tell() - self.elementidbytes
        (self.datasize, self.datasizebytes) = read_data_length(fp)
        self.children = []
        self.datavalue = None

    def get_file(self):
        if isinstance(self.parent, MkvFile):
            return self.parent
        else:
            return self.parent.get_file()

    def get_bytes(self):
        myfile = self.get_file()
        num_bytes = self.elementidbytes + self.datasizebytes + self.datasize
        # Truncate if over 100000
        if num_bytes > 100000:
            num_bytes = 100000
        return myfile.read_bytes(self.element_position, num_bytes)


class UnhandledElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
        finally:
            fp.seek(start_of_element_data + self.datasize)


class BinaryElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
        finally:
            fp.seek(start_of_element_data + self.datasize)


class MasterElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            # after calling superclass, fp will have advanced to the data i.e. the actual payload/data of the element
            start_of_element_data = fp.tell()
            bytes_left = self.datasize
            while bytes_left > 4:
                elementid_tuple = read_id(fp)
                current_element = element_factory(fp, elementid_tuple, self)
                self.children.append(current_element)
                bytes_left -= current_element.elementidbytes + current_element.datasizebytes + current_element.datasize
        finally:
            fp.seek(start_of_element_data + self.datasize)


class Utf_8Element(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            self.datavalue = fp.read(self.datasize).decode('utf-8', errors="ignore")
        finally:
            fp.seek(start_of_element_data + self.datasize)


StringElement = Utf_8Element


class UintegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            self.datavalue = struct.unpack('>Q', bytearray(8 - self.datasize) + fp.read(self.datasize))[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)


class IntegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            bytesread = fp.read(self.datasize)
            padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
            self.datavalue = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)


class DateElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            bytesread = fp.read(self.datasize)
            padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
            timedelta = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
            self.datavalue = (datetime.datetime(2001, 1, 1
                                                ) + datetime.timedelta(microseconds=timedelta / 1000)).isoformat()
        finally:
            fp.seek(start_of_element_data + self.datasize)


class FloatElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0:
                self.datavalue = 0.0
            elif self.datasize == 4:
                self.datavalue = struct.unpack('>f', fp.read(4))[0]
            elif self.datasize == 8:
                self.datavalue = struct.unpack('>d', fp.read(8))[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)

# ======

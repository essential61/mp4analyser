"""
mkv.py


"""
import datetime
import struct
import logging

from mkvanalyser import idlookups


def element_factory(fp, elementid, parent):
    """
    element_factory() takes a box type as a parameter and, if a class has been defined for that type, returns
    an instance of that class.
    """
    element_type = 'Unhandled' if elementid not in idlookups.id_table else idlookups.id_table[elementid]['type']
    element_type.replace("-", "_")
    _element_class = globals().get(
        element_type.capitalize() + 'Element')  # globals() Return a dictionary representing the current global symbol table
    if _element_class:
        the_element = _element_class(fp, elementid, parent)
        return the_element
    else:
        return UnhandledElement(fp, elementid, parent)


def read_id(fp):
    """
    reads value of an element id expressed as a VINT in a file, returns the id as an unsigned
    integer. A side-effect of this function is to advance the file pointer by the
    size in bytes of the VINT.
    """
    leftmostbyte = struct.unpack('>B', fp.read(1))[0]
    if leftmostbyte > 127:
        return leftmostbyte
    elif leftmostbyte > 63:
        return (leftmostbyte << 8) + struct.unpack('>B', fp.read(1))[0]
    elif leftmostbyte > 31:
        return (leftmostbyte << 16) + struct.unpack('>H', fp.read(2))[0]
    elif leftmostbyte > 15:
        return (leftmostbyte << 24) + struct.unpack('>I', b'\x00' + fp.read(3))[0]


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
        return (leftmostbyte % 8 << 40) + (struct.unpack('>B', fp.read(1))[0] << 32) + struct.unpack('>I',
                                                                                                     fp.read(4))[0], 6


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
                elementid = read_id(f)
                current_element = element_factory(f, elementid, self)
                self.children.append(current_element)
                if len(f.read(4)) != 4:
                    end_of_file = True
                else:
                    f.seek(-4, 1)
        f.close()

    def get_summary(self):
        return 'TODO'


# Element classes

class MkvElement():

    def __init__(self, fp, elementid, parent):
        self.elementid = elementid
        self.parent = parent
        self.element_position = fp.tell() - (len(f"{elementid:0x}") // 2)
        (self.datasize, self.datasizebytes) = read_data_length(fp)
        self.children = []
        self.data = {}
        self.byte_string = None
        if parent.elementid == 0:
            current_position = fp.tell()
            fp.seek(self.element)

    def get_top(self):
        if self.parent.elementid == 0:
            return self
        else:
            return self.parent.get_top()

    def get_bytes(self):
        top_box = self.get_top()
        offset = self.element_position - top_box.element_position
        return top_box.byte_string[offset:offset + (
                len(f"{self.elementid:0x}") // 2) + self.datasizebytes + self.datasize]


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
                elementid = read_id(fp)
                bytes_left -= len(f"{elementid:0x}") // 2
                current_element = element_factory(fp, elementid, self)
                self.children.append(current_element)
                bytes_left -= current_element.datasize + current_element.datasizebytes
            #    self.child_boxes.append(current_box)
            #    bytes_left -= current_box.size
        finally:
            fp.seek(start_of_element_data + self.datasize)


class Utf_8Element(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            self.data['string'] = fp.read(self.datasize).decode('utf-8', errors="ignore")
        finally:
            fp.seek(start_of_element_data + self.datasize)


StringElement = Utf_8Element


class UintegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            self.data['uinteger'] = struct.unpack('>Q', bytearray(8 - self.datasize) + fp.read(self.datasize))[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)


class IntegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            bytesread = fp.read(self.datasize)
            padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
            self.data['integer'] = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)


class DateElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            bytesread = fp.read(self.datasize)
            padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
            self.data['date'] = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
        finally:
            fp.seek(start_of_element_data + self.datasize)

# ======

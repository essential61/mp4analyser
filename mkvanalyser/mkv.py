"""
mkv.py


"""
import datetime
import struct
import logging
import binascii

from mkvanalyser.idlookups import id_table


class DataLengthError(Exception):
    # uinteger, integer, float should be 8 bytes or less
    pass


def element_factory(fp, elementid_tuple, parent):
    """
    element_factory() takes a box type as a parameter and, if a class has been defined for that type, returns
    an instance of that class.
    """
    (elementid, elementidbytes) = elementid_tuple
    if elementid not in id_table:
        element_type = 'Unhandled'
    else:
        element_type = id_table[elementid]['type']
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
    else:
        return 0, 0


def read_vint(fp):
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
            try:
                while not end_of_file:
                    elementid_tuple = read_id(f)
                    current_element = element_factory(f, elementid_tuple, self)
                    self.children.append(current_element)
                    if len(f.read(4)) != 4:
                        end_of_file = True
                    else:
                        f.seek(-4, 1)
            except Exception as e:
                logging.error(f'error in {filename} after child {len(self.children)}')

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
    """ Base class for all elements """

    def __init__(self, fp, elementid_tuple, parent):
        (self.elementid, self.elementidbytes) = elementid_tuple
        self.type = id_table[self.elementid]['type'] if self.elementid in id_table else 'unknown'
        self.parent = parent
        self.element_position = fp.tell() - self.elementidbytes
        (self.datasize, self.datasizebytes) = read_vint(fp)
        self.children = []
        self.datavalue = None

    def _get_file(self):
        if isinstance(self.parent, MkvFile):
            return self.parent
        else:
            return self.parent._get_file()

    def get_bytes(self):
        myfile = self._get_file()
        num_bytes = self.elementidbytes + self.datasizebytes + self.datasize
        # Truncate if over 100000
        if num_bytes > 100000:
            num_bytes = 100000
        return myfile.read_bytes(self.element_position, num_bytes)


class UnhandledElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        """ Gets called if element id is unknown (usually a corrupted file),
         side effect of initializer is to advance file pointer """
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            logging.debug(self.elementid)
        finally:
            if self.datasize <= self.parent.datasize:
                fp.seek(start_of_element_data + self.datasize)


class BinaryElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.elementid == 0xA3:
                # It's a SimpleBlock, we'll decode the header
                (trackentry, ignore) = read_vint(fp)
                self.datavalue = {'trackentry': trackentry, 'timestamp':struct.unpack('>h', fp.read(2))[0]}
                blockheaderflags = struct.unpack('>B', fp.read(1))[0]
                self.datavalue['blockheaderflags'] = f'{blockheaderflags:08b}'
                self.datavalue['keyframe'] = True if (blockheaderflags & 0x80) else False
                self.datavalue['invisible'] = True if (blockheaderflags & 0x10) else False
                if (blockheaderflags & 0x06) == 2:
                    self.datavalue['lacing'] = 'xiph'
                elif (blockheaderflags & 0x06) == 6:
                    self.datavalue['lacing'] = 'ebml'
                    self.datavalue['frames'] = struct.unpack('>B', fp.read(1))[0] + 1
                    # first frame length is unsigned
                    (length, numbytes) =  read_vint(fp)
                    self.datavalue['frame lengths'] = [length]
                    for i in range(self.datavalue['frames'] - 2):
                        datavalue = self._read_signed_vint(fp)
                        self.datavalue['frame lengths'].append(datavalue + self.datavalue['frame lengths'][-1])
                    last_sz = self.datasize - sum(self.datavalue['frame lengths']) - (fp.tell() - start_of_element_data)
                    self.datavalue['frame lengths'].append(last_sz)
                elif (blockheaderflags & 0x06) == 4:
                    self.datavalue['lacing'] = 'fixed'
                else:
                    self.datavalue['lacing'] = 'none'
            elif self.datasize < 80:
                self.datavalue = binascii.b2a_hex(fp.read(self.datasize)).decode('utf-8')
            else:
                self.datavalue = binascii.b2a_hex(fp.read(80)).decode('utf-8') + '...'
        finally:
            fp.seek(start_of_element_data + self.datasize)

    def _read_signed_vint(self, fp):
        # used to read frame size deltas
        leftuint = struct.unpack('>B', fp.read(1))[0]
        if leftuint & 0x80:
            return (leftuint % 128) - 0x3F
        elif leftuint & 0x40:
            return ((leftuint % 64) << 8) + struct.unpack('>B', fp.read(1))[0] - 0x1FFF
        elif leftuint & 0x20:
            return ((leftuint % 32) << 16) + struct.unpack('>H', fp.read(2))[0] - 0x0FFFFF
        elif leftuint & 0x10:
            return ((leftuint % 16) << 24) + struct.unpack('>I', b'\x00' + fp.read(3))[0] - 0x07fFFFFF
        else:
            return 0


class MasterElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            # after calling superclass, fp will have advanced to the data i.e. the actual payload/data of the element
            start_of_element_data = last_known_end_of_child = fp.tell()
            # special case of unknown datasize (1 byte, all 1's)
            unknown_datasize = True if self.datasize == 127 and self.datasizebytes == 1 else False
            bytes_left = self.datasize  # bytes left is only useful if size known
            end_of_file = False
            masterlevel = id_table[self.elementid]['level']
            while bytes_left > 2 and not end_of_file:
                elementid_tuple = read_id(fp)
                # do tests here to check it's a permitted child before adding to master
                if elementid_tuple[0] in id_table and id_table[elementid_tuple[0]]['level'] > masterlevel:
                    current_element = element_factory(fp, elementid_tuple, self)
                    self.children.append(current_element)
                    if not unknown_datasize:
                        bytes_left -= current_element.elementidbytes + current_element.datasizebytes + current_element.datasize
                elif unknown_datasize:
                    break
                else:
                     bytes_left -= elementid_tuple[1]
                if len(fp.read(2)) == 2:
                    fp.seek(-2, 1)
                else:
                    end_of_file = True
                last_known_end_of_child = fp.tell()
        except DataLengthError:
            this_elementname = id_table[self.elementid]['name']
            logging.error(f'data length error in {this_elementname} after child {len(self.children)}')
        except struct.error as err:
            this_elementname = id_table[self.elementid]['name']
            logging.error(f'struct.error in {this_elementname} after child {len(self.children)}')
        finally:
            if unknown_datasize or end_of_file:
                fp.seek(last_known_end_of_child)
            else:
                fp.seek(start_of_element_data + self.datasize)


class Utf_8Element(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0:
                self.datavalue = id_table[self.elementid]['default'] if 'default' in id_table[self.elementid] else ''
            else:
                self.datavalue = fp.read(self.datasize).decode('utf-8', errors="ignore")
        finally:
            fp.seek(start_of_element_data + self.datasize)


StringElement = Utf_8Element


class UintegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0:
                self.datavalue = id_table[self.elementid]['default'] if 'default' in id_table[self.elementid] else 0
            elif self.datasize <= 8:
                self.datavalue = struct.unpack('>Q', bytearray(8 - self.datasize) + fp.read(self.datasize))[0]
            else:
                logging.error(f'data length error {self.datasize } in {self.elementid:0x}')
                raise DataLengthError
        finally:
            fp.seek(start_of_element_data + self.datasize)


class IntegerElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0:
                self.datavalue = id_table[self.elementid]['default'] if 'default' in id_table[self.elementid] else 0
            elif self.datasize <= 8:
                bytesread = fp.read(self.datasize)
                padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
                self.datavalue = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
            else:
                logging.error(f'data length error {self.datasize } in {self.elementid:0x}')
                raise DataLengthError
        finally:
            fp.seek(start_of_element_data + self.datasize)


class DateElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0 :
                self.datavalue = id_table[self.elementid]['default'] if 'default' in id_table[
                    self.elementid] else '2001-01-01T00:00:00.000000000 UTC'
            elif self.datasize <= 8:
                bytesread = fp.read(self.datasize)
                padbyte = b'\x00' if int(bytesread[0]) < 128 else b'\xff'
                timedelta = struct.unpack('>q', bytearray(padbyte * (8 - self.datasize)) + bytesread)[0]
                self.datavalue = (datetime.datetime(2001, 1, 1
                                                ) + datetime.timedelta(microseconds=timedelta / 1000)).isoformat()
            else:
                logging.error(f'data length error {self.datasize } in {self.elementid:0x}')
                raise DataLengthError
        finally:
            fp.seek(start_of_element_data + self.datasize)


class FloatElement(MkvElement):

    def __init__(self, fp, elementid, parent):
        super().__init__(fp, elementid, parent)
        try:
            start_of_element_data = fp.tell()
            if self.datasize == 0:
                self.datavalue = id_table[self.elementid]['default'] if 'default' in id_table[self.elementid] else 0.0
            elif self.datasize == 4:
                self.datavalue = struct.unpack('>f', fp.read(4))[0]
            elif self.datasize == 8:
                self.datavalue = struct.unpack('>d', fp.read(8))[0]
            else:
                logging.error(f'data length error {self.datasize } in {self.elementid:0x}')
                raise DataLengthError
        finally:
            fp.seek(start_of_element_data + self.datasize)

# ======

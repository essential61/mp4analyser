"""
core.py contains class definitions used by both iso.py and non_iso.py, namely classes (Mp4Box and Mp4FullBox)
that are used as parents for all the real, instantiated boxes. Also contains a header class definition.
"""
import binascii
import logging

from mp4analyser.util import *


class Mp4Box:
    """
    The superclass for all box classes

    """
    def __init__(self, fp, header, parent):
        """ the file pointer, fp will at the same position on exit as entry i.e. at the end of the header"""
        self.header = header
        self.parent = parent
        self.start_of_box = fp.tell() - self.header.header_size
        self.children = []
        self.box_info = {}
        self.byte_string = None
        # only top-level boxes contain an actual byte array for displaying the hex view, lower-level boxes simply
        # take a slice from the top-level box.
        if parent.type == 'file':
            end_of_header = fp.tell()
            fp.seek(self.start_of_box)
            if self.type == 'mdat' and self.size > 1000001:
                self.byte_string = fp.read(1000001)
            else:
                self.byte_string = fp.read(self.size)
            fp.seek(end_of_header)

    @property
    def size(self):
        return self.header.size

    @property
    def type(self):
        return self.header.type

    @type.setter
    def type(self, new_value):
        self.header.type = new_value

    def get_top(self):
        if self.parent.type == 'file':
            return self
        else:
            return self.parent.get_top()

    def get_bytes(self):
        top_box = self.get_top()
        offset = self.start_of_box - top_box.start_of_box
        return top_box.byte_string[offset:offset + self.size]

    def search_child_boxes_for_type(self, box_type):
        type_matches = []
        for box in self.children:
            if box.type == box_type:
                # append object onto array
                type_matches.append(box)
            if box.children:
                # add array onto array
                type_matches += box.search_child_boxes_for_type(box_type)
        return type_matches


class Mp4FullBox(Mp4Box):
    """
    Derived from Mp4Box, but with version and flags.
    """
    def __init__(self, fp, header, parent):
        """ The file pointer, fp will move forward 4 bytes """
        super().__init__(fp, header, parent)
        four_bytes = read_u32(fp)
        self.version = four_bytes >> 24
        self.flags = four_bytes & 0xFFFFFF


class Header:
    """
    All Mp4Boxes contain a header with size and type information.
     """
    def __init__(self, fp):
        """
        The file pointer, fp will be located at the start of the box on entry and at the end of the header on exit
        """
        start_of_box = fp.tell()
        self._size = read_u32(fp)
        my_4bytes = fp.read(4)
        if (struct.unpack('>I', my_4bytes)[0]) >> 24 == 169:
            self.type = my_4bytes[1:].decode('utf-8', errors='ignore')
        else:
            self.type = my_4bytes.decode('utf-8', errors='ignore')
        if self._size == 1:
            self._largesize = read_u64(fp)
        if self.type == 'uuid':
            self.uuid = binascii.b2a_hex(fp.read(16)).decode('utf-8', errors="ignore")
        self.header_size = fp.tell() - start_of_box
        # throw error if size < 8 as 8 bytes is smallest box (free, skip etc)
        if self.size < 8:
            raise Exception('box size {} should be at least 8 bytes.'
                            ' The value of size was: {}'.format(self.type, self.size))

    @property
    def size(self):
        if self._size == 1:
            return self._largesize
        else:
            return self._size

    def get_header(self):
        """ returns all header properties as a dictionary """
        ret_header = {"size": self._size, "type": self.type}
        if self._size == 1:
            ret_header['largesize'] = self._largesize
        if self.type == 'uuid':
            ret_header['uuid'] = self.uuid
        return ret_header

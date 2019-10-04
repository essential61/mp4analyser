from mp4.util import *


class Mp4Box:

    def __init__(self, fp, header, parent):
        self.header = header
        self.parent = parent
        self.start_of_box = fp.tell()
        self.child_boxes = []
        self.box_info = {}
        self.byte_string = None
        if parent.type == 'file':
            if self.type == 'mdat' and self.size > 1000001:
                self.byte_string = fp.read(1000001)
            else:
                self.byte_string = fp.read(self.size)
            fp.seek(self.start_of_box)

    @property
    def size(self):
        return self.header.size

    @property
    def type(self):
        return self.header.type

    def get_children_types(self):
        return [box.type for box in self.child_boxes]

    def get_top(self):
        if self.parent.type == 'file':
            return self
        else:
            return self.parent.get_top()

    def get_hex_view(self):
        top_box = self.get_top()
        offset = self.start_of_box - top_box.start_of_box
        return top_box.byte_string[offset:offset + self.size]


class Mp4FullBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)

    def set_version_and_flags(self, fp):
        four_bytes = read_u32(fp)
        return {'version': four_bytes // 16777216, 'flags': "{0:#08x}".format(four_bytes % 16777216)}


class Header:

    def __init__(self, fp):
        start_of_box = fp.tell()
        self._size = read_u32(fp)
        self.type = fp.read(4).decode('utf-8')
        if self._size == 1:
            self._largesize = read_u64(fp)
        if self.type == 'uuid':
            self.uuid = fp.read(16)
        self.header_size = fp.tell() - start_of_box
        # throw error if size < 8 as 8 bytes is smallest box (free, skip etc)
        if self.size < 8:
            raise Exception('box size should be 8 or more. The value of size was: {}'.format(self.size))
        fp.seek(start_of_box)

    @property
    def size(self):
        if self._size == 1:
            return self._largesize
        else:
            return self._size

    def get_header(self):
        ret_header = {"size": self._size, "type": self.type}
        if self._size == 1:
            ret_header['largesize'] = self._largesize
        if self.type == 'uuid':
            ret_header['uuid'] = self.uuid
        return ret_header

import json
from mp4.util import *

class Mp4Box:

    def __init__(self, header, parent):
        self.header = header
        self.parent = parent
        self.start_of_box = 0
        self.child_boxes = []
        self.box_info = {}

    def get_box_data(self):
        return json.dumps(self.box_info, indent=4) if len(self.box_info) > 0 else ""

    @property
    def size(self):
        return self.header.size

    @property
    def type(self):
        return self.header.type

    def get_children(self):
        return json.dumps([box.type for box in self.child_boxes]) if len(self.child_boxes) > 0 else ""


class Mp4FullBox(Mp4Box):

    def __init__(self, header, parent):
        super().__init__(header, parent)

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
        return json.dumps(ret_header, indent=4)


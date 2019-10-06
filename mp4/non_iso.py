"""
non_iso.py

This file contains class definitions for boxes not defined in ISO/IEC 14496-12.
It may be useful to look here:
https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/QTFFChap2/qtff2.html#//apple_ref/doc/uid/TP40000939-CH204-55265

"""
import mp4.iso
from mp4.util import *
from mp4.core import *


def box_factory_non_iso(fp, header, parent):
    the_box = None
    if header.type == 'avc1':
        the_box = Avc1Box(fp, header, parent)
    elif header.type == 'avcC':
        the_box = AvcCBox(fp, header, parent)
    elif header.type == 'mp4a':
        the_box = Mp4aBox(fp, header, parent)
    elif header.type == 'esds':
        the_box = EsdsBox(fp, header, parent)
    else:
        the_box = UndefinedBox(fp, header, parent)
    return the_box


class UndefinedBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['message'] = 'TODO'
        finally:
            fp.seek(self.start_of_box + self.size)


class Avc1Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(20, 1)
            self.box_info['width'] = read_u16(fp)
            self.box_info['height'] = read_u16(fp)
            self.box_info['horizresolution'] = "{0:#010x}".format(read_u32(fp))
            self.box_info['vertresolution'] = "{0:#010x}".format(read_u32(fp))
            fp.seek(4, 1)
            self.box_info['frame_count'] = read_u16(fp)
            self.box_info['compressorname'] = "{0:#010x}".format(read_u32(fp))
            # a 16-bit int value of -1 seems to be used as a marker in front of any child boxes
            bytes_left = self.start_of_box + self.size - fp.tell()
            while bytes_left > 0 and read_i16(fp) != -1:
                bytes_left -= 2
            fp.seek(-4, 1)
            self.box_info['depth'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['pre-defined'] = read_i16(fp)
            # need to check this is correct
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = mp4.iso.box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


class AvcCBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['configuration_version'] = read_u8(fp)
            self.box_info['avc_profile_indication'] = read_u8(fp)
            self.box_info['avc_compatibility'] = read_u8(fp)
            self.box_info['avc_level_indication'] = read_u8(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class Mp4aBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(2, 1)
            self.box_info['reference_index'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_encoding_version'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_encoding_revision'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_encoding_vendor'] = "{0:#010x}".format(read_u32(fp))
            self.box_info['audio_channel_count'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_sample_size'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_compression_id'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_packet_size'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['audio_sample_rate'] = read_u16_16(fp)
            # need to check this is correct
            bytes_left = self.start_of_box + self.size - fp.tell()
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = mp4.iso.box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


class EsdsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            pass
            # TODO
        finally:
            fp.seek(self.start_of_box + self.size)

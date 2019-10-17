"""
non_iso.py

This file is meant to contain class definitions for boxes not defined in ISO/IEC 14496-12.
It may be useful to look here:
https://developer.apple.com/library/archive/documentation/QuickTime/QTFF/QTFFChap2/qtff2.html#//apple_ref/doc/uid/TP40000939-CH204-55265

"""
import binascii

import mp4.iso
from mp4.util import *
from mp4.core import *


def box_factory_non_iso(fp, header, parent):
    the_box = None
    if header.type == 'avc1':
        the_box = Avc1Box(fp, header, parent)
    elif header.type == 'hvc1':
        the_box = Hvc1Box(fp, header, parent)
    elif header.type == 'avcC':
        the_box = AvcCBox(fp, header, parent)
    elif header.type == 'hvcC':
        the_box = HvcCBox(fp, header, parent)
    elif header.type == 'btrt':
        the_box = BtrtBox(fp, header, parent)
    elif header.type == 'pasp':
        the_box = PaspBox(fp, header, parent)
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
            self.box_info['num_of_entries'] = read_u32(fp)
            fp.seek(16, 1)
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


Hvc1Box = Avc1Box


class AvcCBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['configuration_version'] = read_u8(fp)
            self.box_info['avc_profile_indication'] = read_u8(fp)
            self.box_info['avc_compatibility'] = read_u8(fp)
            self.box_info['avc_level_indication'] = read_u8(fp)
            self.box_info['lengthSizeMinusOne'] = read_u8(fp) % 4
            self.box_info['numOfSequenceParameterSets'] = read_u8(fp) % 32
            self.box_info['SequenceParameterSets_list'] = []
            for i in range(self.box_info['numOfSequenceParameterSets']):
                spsl = read_u16(fp)
                sequence_param = {
                                    'sequenceParameterSetLength': spsl,
                                    'sequenceParameterSetNALUnit': binascii.b2a_hex(fp.read(spsl)).decode('utf-8')
                                 }
                self.box_info['SequenceParameterSets_list'].append(sequence_param)
            self.box_info['numOfPictureParameterSets'] = read_u8(fp)
            self.box_info['PictureParameterSets_list'] = []
            for i in range(self.box_info['numOfPictureParameterSets']):
                ppsl = read_u16(fp)
                picture_param = {
                                    'pictureParameterSetLength': ppsl,
                                    'pictureParameterSetNALUnit': binascii.b2a_hex(fp.read(ppsl)).decode('utf-8')
                                }
                self.box_info['PictureParameterSets_list'].append(picture_param)
            if (self.box_info['avc_profile_indication'] == 100 or self.box_info['avc_profile_indication'] == 110 or \
                    self.box_info['avc_profile_indication'] == 122 or self.box_info['avc_profile_indication'] == 144) \
                    and (self.start_of_box + self.size - fp.tell()) > 7:
                self.box_info['chroma_format'] = read_u8(fp) % 4
                self.box_info['bit_depth_luma_minus8'] = read_u8(fp) % 8
                self.box_info['bit_depth_chroma_minus8'] = read_u8(fp) % 8
                self.box_info['numOfSequenceParameterSetExtLength'] = read_u8(fp)
                self.box_info['SequenceParameterSetExt_list'] = []
                for i in range(self.box_info['numOfSequenceParameterSetExtLength']):
                    spse = read_u16(fp)
                    sequence_param = {
                        'sequenceParameterSetExtLength': spse,
                        'sequenceParameterSetExtNALUnit': binascii.b2a_hex(fp.read(spse)).decode('utf-8')
                    }
                    self.box_info['SequenceParameterSetExt_list'].append(sequence_param)
        finally:
            fp.seek(self.start_of_box + self.size)


class HvcCBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['configuration_version'] = read_u8(fp)
            profile_info = read_u8(fp)
            self.box_info['general_profile_space'] = profile_info // 64
            self.box_info['general_tier_flag'] = profile_info % 64 // 32
            self.box_info['general_profile_idc'] = profile_info % 32
            self.box_info['general_profile_compatibility_flags'] = "{0:#010x}".format(read_u32(fp))
            self.box_info['general_constraint_indicator_flags'] = "0x" + binascii.b2a_hex(fp.read(6)).decode('utf-8')
            self.box_info['general_level_idc'] = read_u8(fp)
            self.box_info['min_spatial_segmentation_idc'] = read_u16(fp) % 4096
            self.box_info['parallelismType'] = read_u8(fp) % 4
            self.box_info['chroma_format_idc'] = read_u8(fp) % 4
            self.box_info['bit_depth_luma_minus8'] = read_u8(fp) % 8
            self.box_info['bit_depth_chroma_minus8'] = read_u8(fp) % 8
            self.box_info['avg_frame_rate'] = read_u16(fp)
            fr = read_u8(fp)
            self.box_info['constant_frame_rate'] = fr // 64
            self.box_info['num_temporal_layers'] = fr % 64 // 8
            self.box_info['temporal_id_nested'] = fr % 8 // 4
            self.box_info['length_size_minus1'] = fr % 4
            self.box_info['num_of_arrays'] = read_u8(fp)
            self.box_info['array_list'] = []
            for i in range(self.box_info['num_of_arrays']):
                nt = read_u8(fp)
                nal_dict = {'array_completeness': nt // 128, 'NAL_unit_type': nt % 64}
                nal_dict['num_nalus'] = read_u16(fp)
                nal_dict['nalu_list'] = []
                for j in range(nal_dict['num_nalus']):
                    nul = read_u16(fp)
                    nal_dict['nalu_list'].append({
                                                    'nal_unit_length': nul,
                                                    'nal_unit': binascii.b2a_hex(fp.read(nul)).decode('utf-8')
                                                })
                self.box_info['array_list'].append(nal_dict)
        finally:
            fp.seek(self.start_of_box + self.size)


class BtrtBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['bufferSizeDB'] = read_u32(fp)
            self.box_info['maxBitrate'] = read_u32(fp)
            self.box_info['avgBitrate'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class PaspBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['hSpacing'] = read_u32(fp)
            self.box_info['vSpacing'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class Mp4aBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(6, 1)
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
            self.box_info['elementary_stream_descriptor'] = \
                binascii.b2a_hex(fp.read(self.size -(self.header.header_size + 4))).decode('utf-8')
        finally:
            fp.seek(self.start_of_box + self.size)

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
    # Normalise header type so it can be expressed in a Python Class name
    box_type = header.type.replace(" ", "_").replace("-", "_").lower()
    # globals() Return a dictionary representing the current global symbol table
    _box_class = globals().get(box_type.capitalize()+'Box')
    if _box_class:
        the_box = _box_class(fp, header, parent)
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
            compressorname_size = read_u8(fp)
            self.box_info['compressorname'] = fp.read(compressorname_size).decode('utf-8', errors="ignore")
            padding = fp.read(31 - compressorname_size)
            self.box_info['depth'] = "{0:#06x}".format(read_u16(fp))
            self.box_info['pre_defined'] = read_i16(fp)
            bytes_left = self.start_of_box + self.size - fp.tell()
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = mp4.iso.box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


DvheBox = Dvh1Box = DvavBox = Dva1Box = Avc1Box
Hvc1Box = Hev1Box = Avc1Box
Avc4Box = Avc3Box = Avc2Box = Avc1Box


class AvccBox(Mp4Box):

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
            if (self.box_info['avc_profile_indication'] == 100 or self.box_info['avc_profile_indication'] == 110 or
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


class HvccBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['configuration_version'] = read_u8(fp)
            profile_info = read_u8(fp)
            self.box_info['general_profile_space'] = profile_info >> 6
            self.box_info['general_tier_flag'] = profile_info >> 5 & 1
            self.box_info['general_profile_idc'] = profile_info & 31
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
            self.box_info['constant_frame_rate'] = fr >> 6
            self.box_info['num_temporal_layers'] = fr >> 3 & 7
            self.box_info['temporal_id_nested'] = fr >> 2 & 1
            self.box_info['length_size_minus1'] = fr & 3
            self.box_info['num_of_arrays'] = read_u8(fp)
            self.box_info['array_list'] = []
            for i in range(self.box_info['num_of_arrays']):
                nt = read_u8(fp)
                nal_dict = {'array_completeness': nt >> 7, 'NAL_unit_type': nt % 64}
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

HvceBox = HvccBox
            
            
class DvccBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['dv_version_major'] = read_u8(fp)
            self.box_info['dv_version_minor'] = read_u8(fp)
            nextTwoBytes = read_u16(fp)
            self.box_info['dv_profile'] = (nextTwoBytes >> 9) & 0x7f
            self.box_info['dv_level'] = (nextTwoBytes >> 3) & 0x3f
            self.box_info['rpu_present_flag'] = (nextTwoBytes >> 2) & 0x01
            self.box_info['el_present_flag'] = (nextTwoBytes >> 1) & 0x01
            self.box_info['bl_present_flag'] = nextTwoBytes & 0x01
            self.box_info['dv_bl_signal_compatibility_id'] = read_u8(fp) >> 4
        finally:
            fp.seek(self.start_of_box + self.size)


DvvcBox = DvccBox


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


Ac_3Box = Ec_3Box = Mp4aBox


class EsdsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['elementary_stream_descriptor'] = \
                binascii.b2a_hex(fp.read(self.size - (self.header.header_size + 4))).decode('utf-8')
        finally:
            fp.seek(self.start_of_box + self.size)


class Dac3Box(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            my_data = struct.unpack('>I', b'\0' + fp.read(3))[0]
            self.box_info['fscod'] = my_data >> 22
            self.box_info['bsid'] = my_data >> 17 & 31
            self.box_info['bsmod'] = my_data >> 14 & 7
            self.box_info['acmod'] = my_data >> 11 & 7
            self.box_info['lfeon'] = my_data >> 10 & 1
            self.box_info['bit_rate_code'] = my_data >> 5 % 31
        finally:
            fp.seek(self.start_of_box + self.size)


class Dec3Box(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            my_data_sub = read_u16(fp)
            self.box_info['data_rate'] = my_data_sub >> 3
            self.box_info['num_ind_sub'] = my_data_sub & 7
            self.box_info['ind_sub_list'] = []
            for i in range(self.box_info['num_ind_sub']):
                in_s = read_u16(fp)
                fscod = in_s >> 14
                bsid = in_s >> 9 & 31
                asvc = in_s >> 7 & 1
                bsmod = in_s >> 4 & 7
                acmod = in_s >> 1 & 7
                lfeon = in_s & 1
                dep_s = read_u8(fp)
                num_dep_sub = dep_s >> 1 & 15
                bit_9 = dep_s & 1
                sub_dict = {'fscod': fscod, 'bsid': bsid, 'asvc': asvc, 'bsmod': bsmod, 'acmod': acmod,
                            'lfeon': lfeon, 'num_dep_sub': num_dep_sub}
                if num_dep_sub > 0:
                    sub_dict['chan_loc'] = (bit_9 * 512) + read_u8(fp)
                self.box_info['ind_sub_list'].append(sub_dict)
        finally:
            fp.seek(self.start_of_box + self.size)


class DataBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(4, 1)
            self.box_info['text'] = fp.read(self.size - (self.header.header_size + 8)).decode('utf-8')
        finally:
            fp.seek(self.start_of_box + self.size)


class PsshBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['system_id'] = binascii.b2a_hex(fp.read(16)).decode('utf-8')
            if self.box_info['system_id'] == '1077efecc0b24d02ace33c1e52e2fb4b':
                # it is cenc
                self.box_info['key_count'] = read_u32(fp)
                self.box_info['key_list'] = []
                for i in range(self.box_info['key_count']):
                    self.box_info['key_list'].append(binascii.b2a_hex(fp.read(16)).decode('utf-8'))
        finally:
            fp.seek(self.start_of_box + self.size)


class SencBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['sample_count'] = read_u32(fp)
            iv_size_guess = ((self.size - 16) // self.box_info['sample_count'])
            if int(self.box_info['flags'][-1], 16) & 2:
                # I don't think this logic is infallible
                if iv_size_guess < 10:
                    iv_size = 0
                elif 10 <= iv_size_guess < 18:
                    iv_size = 8
                else:
                    iv_size = 16
                self.box_info['iv_size'] = iv_size
                self.box_info['sample_list'] = []
                for i in range(self.box_info['sample_count']):
                    sample_dict = {'iv': binascii.b2a_hex(fp.read(iv_size)).decode('utf-8'),
                                   'subsample_count': read_u16(fp), 'subsample_list': []}
                    for j in range(sample_dict['subsample_count']):
                        sample_dict['subsample_list'].append({
                                                            'BytesOfClearData': read_u16(fp),
                                                            'BytesOfEncryptedData': read_u32(fp)
                                                            })
                    self.box_info['sample_list'].append(sample_dict)
            else:
                iv_size = iv_size_guess
                self.box_info['iv_size'] = iv_size
                self.box_info['sample_list'] = []
                for i in range(self.box_info['sample_count']):
                    self.box_info['sample_list'].append({'iv': binascii.b2a_hex(fp.read(iv_size)).decode('utf-8')})
        finally:
            fp.seek(self.start_of_box + self.size)

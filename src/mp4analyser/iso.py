"""
iso.py

This file, if and when complete ;-), contains all the class definitions of boxes that are specified in ISO/IEC 14496-12.
Additionally a class to represent the MP4 file that contains the MP4 boxes has been defined.
A box_factory function has also been defined, primarily to minimise coupling between modules.

"""
import datetime
import logging
import os

import mp4analyser.non_iso
from mp4analyser.core import *
from mp4analyser.util import *
from mp4analyser.summary import *


# Supported box
# 'ftyp', 'pdin', 'moov', 'mvhd', 'meta', 'trak', 'tkhd', 'tref', 'trgr', 'edts', 'elst', 'mdia',
# 'mdhd', 'hdlr', 'elng', 'minf', 'vmhd', 'smhd', 'hmhd', 'nmhd', 'dinf', 'dref', 'url ', 'urn ',
# 'stbl', 'stsd', 'stts', 'ctts', 'cslg', 'stsc', 'stsz', 'stz2', 'stco', 'co64', 'stss', 'stsh',
# 'padb', 'stdp', 'sdtp', 'sbgp', 'sgpd', 'subs', 'saiz', 'saio', 'udta', 'mvex', 'mehd', 'trex',
# 'leva', 'moof', 'mfhd', 'traf', 'tfhd', 'trun', 'tfdt', 'mfra', 'tfra', 'mfro', 'mdat', 'free',
# 'skip', 'cprt', 'tsel', 'strk', 'stri', 'strd', 'iloc', 'ipro', 'rinf', 'sinf', 'frma', 'schm',
# 'xml ', 'pitm', 'iref', 'meco', 'mere', 'styp', 'sidx', 'ssix', 'prft', 'avc1', 'hvc1', 'avcC',
# 'hvcC', 'btrt', 'pasp', 'mp4a', 'ac-3', 'ec-3', 'esds', 'dac3', 'dec3', 'ilst', 'data', 'pssh',
# 'senc'
# Not supported
# 'sthd', 'iinf', 'bxml', 'fiin', 'paen', 'fire', 'fpar', 'fecr', 'segr', 'gitn', 'idat'

def box_factory(fp, header, parent):
    """
    box_factory() takes a box type as a parameter and, if a class has been defined for that type, returns
    an instance of that class.
    """
    the_box = None
    # Normalise header type so it can be expressed in a Python Class name
    box_type = header.type.replace(" ", "_").replace("-", "_").lower()
    _box_class = globals().get(
        box_type.capitalize() + 'Box')  # globals() Return a dictionary representing the current global symbol table
    if _box_class:
        the_box = _box_class(fp, header, parent)
        return the_box
    else:
        return mp4analyser.non_iso.box_factory_non_iso(fp, header, parent)


class Mp4File:
    """ Mp4File Class, effectively the top-level container """
    def __init__(self, filename):
        self.filename = filename
        self.type = 'file'
        self.children = []
        self.summary= {}
        try:
            with open(filename, 'rb') as f:
                end_of_file = False
                while not end_of_file:
                    current_header = Header(f)
                    current_box = box_factory(f, current_header, self)
                    self.children.append(current_box)
                    if current_box.size == 0:
                        end_of_file = True
                    if len(f.read(4)) != 4:
                        end_of_file = True
                    else:
                        f.seek(-4, os.SEEK_CUR)
            f.close()
            self._generate_samples_from_moov()
            self._generate_samples_from_moofs()
        except Exception as e:
            # catch exception in case we can continue
            logging.exception(f'error in {filename} after child {len(self.children)}')

    def _generate_samples_from_moov(self):
        """ identify media samples in mdat for full mp4 file """
        mdats = [mbox for mbox in self.children if mbox.type == 'mdat']
        # generate a sample list if there is a moov that contains traks N.B only ever 0,1 moov boxes
        if [box for box in self.children if box.type == 'moov']:
            moov = [box for box in self.children if box.type == 'moov'][0]
            traks = [tbox for tbox in moov.children if tbox.type == 'trak']
            sample_list = []
            for trak in traks:
                trak_id = [box for box in trak.children if box.type == 'tkhd'][0].box_info['track_ID']
                timescale = [box for box in [box for box in trak.children
                                             if box.type == 'mdia'][0].children
                             if box.type == 'mdhd'][0].box_info['timescale']
                samplebox = [box for box in [box for box in [box for box in trak.children
                                                             if box.type == 'mdia'][0].children
                                             if box.type == 'minf'][0].children
                             if box.type == 'stbl'][0]
                chunk_offsets = [box for box in samplebox.children
                                 if box.type == 'stco' or box.type == 'co64'][0].box_info['entry_list']
                sample_size_box = [box for box in samplebox.children if box.type == 'stsz' or box.type == 'stz2'][0]
                if sample_size_box.box_info['sample_size'] > 0:
                    sample_sizes = [{'entry_size': sample_size_box.box_info['sample_size']}
                                    for i in range(sample_size_box.box_info['sample_count'])]
                else:
                    sample_sizes = sample_size_box.box_info['entry_list']
                sample_to_chunks = [box for box in samplebox.children
                                    if box.type == 'stsc'][0].box_info['entry_list']
                s2c_index = 0
                next_run = 0
                sample_idx = 0
                for i, chunk in enumerate(chunk_offsets, 1):
                    if i >= next_run:
                        samples_per_chunk = sample_to_chunks[s2c_index]['samples_per_chunk']
                        s2c_index += 1
                        next_run = sample_to_chunks[s2c_index]['first_chunk'] \
                            if s2c_index < len(sample_to_chunks) else len(chunk_offsets) + 1
                    chunk_dict = {'track_ID': trak_id,
                                  'chunk_ID': i,
                                  'chunk_offset': chunk['chunk_offset'],
                                  'samples_per_chunk': samples_per_chunk,
                                  'chunk_samples': []
                                  }
                    sample_offset = chunk['chunk_offset']
                    for j, sample in enumerate(sample_sizes[sample_idx:sample_idx + samples_per_chunk], sample_idx + 1):
                        chunk_dict['chunk_samples'].append({
                            'sample_ID': j,
                            'size': sample['entry_size'],
                            'offset': sample_offset
                        })
                        sample_offset += sample['entry_size']
                    sample_list.append(chunk_dict)
                    sample_idx += samples_per_chunk
            # sample_list could be empty, say, for mpeg-dash initialization segment
            if sample_list:
                # sort by chunk offset to get interleaved list
                sample_list.sort(key=lambda k: k['chunk_offset'])
                for mdat in mdats:
                    mdat_sample_list = [sample for sample in sample_list if
                                        mdat.start_of_box < sample['chunk_offset'] < (mdat.start_of_box + mdat.size)]
                    if len(mdat_sample_list):
                        mdat.box_info['message'] = 'Has samples.'
                    mdat.sample_list = mdat_sample_list

    def _generate_samples_from_moofs(self):
        """
        generate samples within mdats of media segments for fragmented mp4 files
        media segments are 1 moof (optionally preceded by an styp) followed by 1 or more contiguous mdats
        I've only ever seen 1 mdat in a media segment though
        """
        i = 0
        while i < len(self.children) - 1:
            if self.children[i].type == 'moof':
                moof = self.children[i]
                media_segment = {'moof_box': moof, 'mdat_boxes': []}
                sequence_number = [mfhd for mfhd in moof.children
                                   if mfhd.type == 'mfhd'][0].box_info['sequence_number']
                while i < len(self.children) - 1 and self.children[i + 1].type == 'mdat':
                    media_segment['mdat_boxes'].append(self.children[i + 1])
                    i += 1
                # I've only ever seen 1 traf in a moof, but the standard says there could be more
                data_offset = 0
                for j,traf in enumerate([tbox for tbox in moof.children if tbox.type == 'traf']):
                    # read tfhd, there will be one
                    tfhd = [hbox for hbox in traf.children if hbox.type == 'tfhd'][0]
                    trak_id = tfhd.box_info['track_id']
                    if 'base_data_offset' in tfhd.box_info:
                        data_offset = tfhd.box_info['base_data_offset']
                    elif tfhd.box_info['default_base_is_moof']:
                        data_offset = media_segment['moof_box'].start_of_box
                    elif j > 0:
                        # according to spec. should be set end of data for last fragment
                        pass
                    else:
                        base_data_offset = media_segment['moof_box'].start_of_box
                    for k, trun in enumerate([rbox for rbox in traf.children if rbox.type == 'trun'], 1):
                        if 'data_offset' in trun.box_info:
                            data_offset += trun.box_info['data_offset']
                        run_dict = {'sequence_number': sequence_number,
                                    'track_ID': trak_id,
                                    'run_ID': k,
                                    'run_offset': data_offset,
                                    'sample_count': trun.box_info['sample_count'],
                                    'run_samples': []
                                    }
                        has_sample_size = True if trun.flags & 0x0200 == 0x0200 else False
                        for l, sample in enumerate(trun.box_info['samples'], 1):
                            if not has_sample_size:
                                sample_size = tfhd.box_info['default_sample_size']
                            else:
                                sample_size = sample['sample_size']
                            run_dict['run_samples'].append({'sample_ID': l,
                                                            'size': sample_size,
                                                            'offset': data_offset
                                                            })
                            data_offset += sample_size
                        for mdat in media_segment['mdat_boxes']:
                            if mdat.start_of_box < run_dict['run_offset'] and (mdat.start_of_box
                                                                               + mdat.size) >= data_offset:
                                mdat.box_info['message'] = 'Has samples.'
                                mdat.sample_list.append(run_dict)
            i += 1

    def read_bytes(self, offset, num_bytes):
        with open(self.filename, 'rb') as f:
            f.seek(offset)
            bytes_read = f.read(num_bytes)
        f.close()
        return bytes_read

    def get_summary(self):
        if not self.summary:
            self.summary = Summary(self)
        return self.summary.data

    def search_boxes_for_type(self, box_type):
        type_matches = []
        for box in self.children:
            if box.type == box_type:
                type_matches.append(box)
            if box.children:
                type_matches += box.search_child_boxes_for_type(box_type)
        return type_matches
# Box classes


class FreeBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            pass
        finally:
            fp.seek(self.start_of_box + self.size)


SkipBox = FreeBox


class FtypBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info = {
                'major_brand': fp.read(4).decode('utf-8'),
                'minor_version': "{0:#010x}".format(read_u32(fp)),
                'compatible_brands': []
            }
            bytes_left = self.size - (self.header.header_size + 8)
            while bytes_left > 0:
                self.box_info['compatible_brands'].append(fp.read(4).decode('utf-8'))
                bytes_left -= 4
        finally:
            fp.seek(self.start_of_box + self.size)


StypBox = FtypBox


class ColrBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['color_type'] = fp.read(4).decode('utf-8')
            if self.box_info['color_type'] == 'nclx':
                self.box_info['color_primaries'] = read_u16(fp)
                self.box_info['transfer_characteristics'] = read_u16(fp)
                self.box_info['matrix_coefficients'] = read_u16(fp)
                self.box_info['full_range_flag'] = read_u8(fp) >> 7
        finally:
            fp.seek(self.start_of_box + self.size)


class PdinBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        end_of_box = self.start_of_box + self.size
        try:
            self.box_info['rates'] = []
            while fp.tell() < end_of_box:
                self.box_info('rates').append({'rate': read_u32(fp), 'initial_delay': read_u32(fp)})
        finally:
            fp.seek(end_of_box)


class ContainerBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            bytes_left = self.size - self.header.header_size
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


# All these are pure container boxes
DinfBox = MinfBox = MdiaBox = TrefBox = EdtsBox = TrakBox = MoofBox = MoovBox = ContainerBox
UdtaBox = TrgrBox = MvexBox = MfraBox = StrkBox = StrdBox = RinfBox = SinfBox = MecoBox = ContainerBox
GmhdBox = SchiBox = ContainerBox


class MetaBox(Mp4Box):
    """
    Seems to be a discrepancy between Apple atom spec and ISO about whether this is a versioned box
    """
    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            bytes_left = self.size - self.header.header_size
            first_four_bytes = read_u32(fp)
            second_four_bytes = fp.read(4)
            if second_four_bytes.decode('utf-8', errors="ignore") == 'hdlr':
                # it's non-versioned
                fp.seek(-8, os.SEEK_CUR)
            else:
                # it's versioned
                self.version = first_four_bytes >> 24
                self.flags = first_four_bytes & 0xFFFFFF
                fp.seek(-4, os.SEEK_CUR)
                bytes_left -= 4
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


class MdatBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        self.sample_list = []
        try:
            self.box_info['message'] = 'No samples found.'
        finally:
            fp.seek(self.start_of_box + self.size)


class MvhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.version == 1:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                self.box_info['duration'] = read_u64(fp)
            else:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                self.box_info['duration'] = read_u32(fp)
            self.box_info['rate'] = read_u16_16(fp)
            self.box_info['volume'] = read_u8_8(fp)
            fp.seek(10, os.SEEK_CUR)
            self.box_info['matrix'] = ["{0:#010x}".format(b) for b in struct.unpack('>9I', fp.read(36))]
            fp.seek(24, os.SEEK_CUR)
            self.box_info['next_track_id'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class MfhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['sequence_number'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class MehdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.version == 1:
                self.box_info['fragment_duration'] = read_u64(fp)
            else:
                self.box_info['fragment_duration'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class ElstBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                if self.version == 1:
                    self.box_info['entry_list'].append({
                        'segment_duration': read_u64(fp),
                        'media_time': read_i64(fp),
                        'media_rate_integer': read_i16(fp),
                        'media_rate_fraction': read_i16(fp)
                    })
                else:
                    self.box_info['entry_list'].append({
                        'segment_duration': read_u32(fp),
                        'media_time': read_i32(fp),
                        'media_rate_integer': read_i16(fp),
                        'media_rate_fraction': read_i16(fp)
                    })
        finally:
            fp.seek(self.start_of_box + self.size)


class TkhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.version == 1:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['track_ID'] = read_u32(fp)
                fp.seek(4, os.SEEK_CUR)
                self.box_info['duration'] = read_u64(fp)
            else:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['track_ID'] = read_u32(fp)
                fp.seek(4, os.SEEK_CUR)
                self.box_info['duration'] = read_u32(fp)
            fp.seek(8, os.SEEK_CUR)
            self.box_info['layer'] = read_i16(fp)
            self.box_info['alternate_group'] = read_i16(fp)
            self.box_info['volume'] = read_u8_8(fp)
            fp.seek(2, os.SEEK_CUR)
            self.box_info['matrix'] = ["{0:#010x}".format(b) for b in struct.unpack('>9I', fp.read(36))]
            self.box_info['width'] = read_u16_16(fp)
            self.box_info['height'] = read_u16_16(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class TfhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['track_id'] = read_u32(fp)
            if self.flags  & 0x000001 == 0x000001:
                self.box_info['base_data_offset'] = read_u64(fp)
            if self.flags  & 0x000002 == 0x000002:
                self.box_info['sample_description_index'] = read_u32(fp)
            if self.flags  & 0x000008 == 0x000008:
                self.box_info['default_sample_duration'] = read_u32(fp)
            if self.flags  & 0x000010 == 0x000010:
                self.box_info['default_sample_size'] = read_u32(fp)
            if self.flags  & 0x000020 == 0x000020:
                self.box_info['default_sample_flags'] = "{0:#08x}".format(read_u32(fp))
            self.box_info['duration_is_empty'] = True if self.flags  & 0x010000 == 0x010000 else False
            # depending on value of base data offset this flag mght be ignored
            self.box_info['default_base_is_moof'] = True if self.flags  & 0x020000 == 0x020000 else False
        finally:
            fp.seek(self.start_of_box + self.size)


class TrexBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['track_ID'] = read_u32(fp)
            self.box_info['default_sample_description_index'] = read_u32(fp)
            self.box_info['default_sample_duration'] = read_u32(fp)
            self.box_info['default_sample_size'] = read_u32(fp)
            self.box_info['default_sample_flags'] = "{0:#08x}".format(read_u32(fp))
        finally:
            fp.seek(self.start_of_box + self.size)


class LevaBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['level_count'] = read_u8(fp)
            self.box_info['level_list'] = []
            for i in range(self.box_info['level_count']):
                level_dict = {'track_ID': read_u32(fp)}
                pad_assign = read_u8(fp)
                level_dict['padding_flag'] = pad_assign // 128
                level_dict['assignment_type'] = pad_assign % 128
                if level_dict['assignment_type'] == 0:
                    level_dict['grouping_type'] = fp.read(4).decode('utf-8')
                elif level_dict['assignment_type'] == 1:
                    level_dict['grouping_type'] = fp.read(4).decode('utf-8')
                    level_dict['grouping_type_parameter'] = read_u32(fp)
                elif level_dict['assignment_type'] == 4:
                    level_dict['sub_track_id'] = read_u32(fp)
                self.box_info['level_list'].append(level_dict)
        finally:
            fp.seek(self.start_of_box + self.size)


class TfraBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['track_ID'] = read_u32(fp)
            length_fields = read_u32(fp)
            self.box_info['length_size_of_traf_num'] = length_fields >> 4 & 3
            self.box_info['length_size_of_trun_num'] = length_fields >> 2 & 3
            self.box_info['length_size_of_sample_num'] = length_fields & 3
            self.box_info['number_of_entry'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['number_of_entry']):
                entry_dict = {}
                if self.version == 1:
                    entry_dict['time'] = read_u64(fp)
                    entry_dict['moof_offset'] = read_u64(fp)
                else:
                    entry_dict['time'] = read_u32(fp)
                    entry_dict['moof_offset'] = read_u32(fp)
                if self.box_info['length_size_of_traf_num'] == 0:
                    entry_dict['traf_number'] = read_u8(fp)
                elif self.box_info['length_size_of_traf_num'] == 1:
                    entry_dict['traf_number'] = read_u16(fp)
                elif self.box_info['length_size_of_traf_num'] == 3:
                    entry_dict['traf_number'] = read_u32(fp)
                if self.box_info['length_size_of_trun_num'] == 0:
                    entry_dict['trun_number'] = read_u8(fp)
                elif self.box_info['length_size_of_trun_num'] == 1:
                    entry_dict['trun_number'] = read_u16(fp)
                elif self.box_info['length_size_of_trun_num'] == 3:
                    entry_dict['trun_number'] = read_u32(fp)
                if self.box_info['length_size_of_sample_num'] == 0:
                    entry_dict['sample_number'] = read_u8(fp)
                elif self.box_info['length_size_of_sample_num'] == 1:
                    entry_dict['sample_number'] = read_u16(fp)
                elif self.box_info['length_size_of_sample_num'] == 3:
                    entry_dict['sample_number'] = read_u32(fp)
                self.box_info['entry_list'].append(entry_dict)
        finally:
            fp.seek(self.start_of_box + self.size)


class MfroBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['size'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class CprtBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            # I think this is right
            lang = read_u16(fp)
            if lang == 0:
                self.box_info['language'] = '0x00'
            else:
                ch1 = str(chr(96 + (lang >> 10 & 31)))
                ch2 = str(chr(96 + (lang >> 5 & 31)))
                ch3 = str(chr(96 + (lang & 31)))
                self.box_info['language'] = ch1 + ch2 + ch3
            bytes_left = self.size - (self.header.header_size + 2)
            self.box_info['name'] = fp.read(bytes_left).decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class TselBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['switch_group'] = read_u32(fp)
            bytes_left = self.size - (self.header.header_size + 8)
            attr_list = []
            while bytes_left > 0:
                attr_list.append(fp.read(4).decode('utf-8'))
                bytes_left -= 4
            self.box_info['attributes'] = attr_list
        finally:
            fp.seek(self.start_of_box + self.size)


class StriBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['switch_group'] = read_u16(fp)
            self.box_info['alternate_group'] = read_u16(fp)
            self.box_info['sub_track_ID'] = read_u32(fp)
            bytes_left = self.size - (self.header.header_size + 12)
            attr_list = []
            while bytes_left > 0:
                attr_list.append(fp.read(4).decode('utf-8'))
                bytes_left -= 4
            self.box_info['attributes'] = attr_list
        finally:
            fp.seek(self.start_of_box + self.size)


class IlocBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['offset_size'] = read_u32(fp)
            self.box_info['length_size'] = read_u32(fp)
            self.box_info['base_offset_size'] = read_u32(fp)
            if self.version == 1 or self.version == 2:
                self.box_info['index_size'] = read_u32(fp)
            else:
                self.box_info['reserved'] = read_u32(fp)
            if self.version < 2:
                self.box_info['item_count'] = read_u16(fp)
            elif self.version == 2:
                self.box_info['item_count'] = read_u32(fp)
            self.box_info['item_list'] = []
            for i in range(self.box_info['item_count']):
                item = {}
                if self.version < 2:
                    item['item_ID'] = read_u16(fp)
                elif self.version == 2:
                    item['item_ID'] = read_u32(fp)
                if self.version == 1 or self.version == 2:
                    item['construction_method'] = read_u16(fp) % 16
                item['data_reference_index'] = read_u16(fp)
                if self.box_info['offset_size'] == 4:
                    item['base_offset'] = read_u32(fp)
                elif self.box_info['offset_size'] == 8:
                    item['base_offset'] = read_u64(fp)
                item['extent_count'] = read_u16(fp)
                item['extent_list'] = []
                for j in range(item['extent_count']):
                    extent = {}
                    if self.version == 1 or self.version == 2:
                        if self.box_info['index_size'] == 4:
                            extent['extent_index'] = read_u32(fp)
                        elif self.box_info['index_size'] == 8:
                            extent['extent_index'] = read_u64(fp)
                    if self.box_info['offset_size'] == 4:
                        extent['extent_offset'] = read_u32(fp)
                    elif self.box_info['offset_size'] == 8:
                        extent['extent_offset'] = read_u64(fp)
                    if self.box_info['length_size'] == 4:
                        extent['extent_length'] = read_u32(fp)
                    elif self.box_info['length_size'] == 8:
                        extent['extent_length'] = read_u64(fp)
                    item['extent_list'].append(extent)
                self.box_info['item_list'].append(item)
        finally:
            fp.seek(self.start_of_box + self.size)


class IproBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['protection_count'] = read_u16(fp)
            for i in range(self.box_info['protection_count']):
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
        finally:
            fp.seek(self.start_of_box + self.size)


class FrmaBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['data_format'] = fp.read(4).decode('utf-8')
        finally:
            fp.seek(self.start_of_box + self.size)


class SchmBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['scheme_type'] = fp.read(4).decode('utf-8')
            self.box_info['scheme_version'] = read_u32(fp)
            if self.flags & 0x000001 == 0x000001:
                self.box_info['data_offset'] = fp.read(self.size - (self.header.header_size + 12)).decode('utf-8')
        finally:
            fp.seek(self.start_of_box + self.size)


class Xml_Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['xml_data'] = fp.read(self.size - (self.header.header_size + 4)).decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class PitmBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.version == 0:
                self.box_info['item_ID'] = read_u16(fp)
            else:
                self.box_info['item_ID'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


# This is just a versioned container box
class IrefBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            bytes_left = self.size - self.header.header_size
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


class MereBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['first_metabox_handler_type'] = fp.read(4).decode('utf-8')
            self.box_info['second_metabox_handler_type'] = fp.read(4).decode('utf-8')
            self.box_info['metabox_relation'] = read_u8(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class TrunBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['sample_count'] = read_u32(fp)
            if self.flags & 0x000001 == 0x000001:
                self.box_info['data_offset'] = read_i32(fp)
            if self.flags & 0x000004 == 0x000004:
                self.box_info['first_sample_flags'] = "{0:#08x}".format(read_u32(fp))
            has_sample_duration = True if self.flags & 0x000100 == 0x000100 else False
            has_sample_size = True if self.flags & 0x000200 == 0x000200 else False
            has_sample_flags = True if self.flags & 0x000400 == 0x000400 else False
            has_scto = True if self.flags & 0x000800 == 0x000800 else False
            sample_list = []
            for i in range(self.box_info['sample_count']):
                sample = {}
                if has_sample_duration:
                    sample['sample_duration'] = read_u32(fp)
                if has_sample_size:
                    sample['sample_size'] = read_u32(fp)
                if has_sample_flags:
                    sample['sample_flags'] = "{0:#08x}".format(read_u32(fp))
                if has_scto:
                    if self.version == 1:
                        self.box_info['sample_composition_time_offset'] = read_i32(fp)
                    else:
                        self.box_info['sample_composition_time_offset'] = read_u32(fp)
                sample_list.append(sample)
            self.box_info['samples'] = sample_list
        finally:
            fp.seek(self.start_of_box + self.size)


class TfdtBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.version == 1:
                self.box_info['baseMediaDecode'] = read_u64(fp)
            else:
                self.box_info['baseMediaDecode'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class MdhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.version == 1:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                self.box_info['duration'] = read_u64(fp)
            else:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                self.box_info['duration'] = read_u32(fp)
            # I think this is right
            lang = struct.unpack('>H', fp.read(2))[0]
            if lang == 0:
                self.box_info['language'] = '0x00'
            else:
                ch1 = str(chr(96 + (lang >> 10 & 31)))
                ch2 = str(chr(96 + (lang >> 5 & 31)))
                ch3 = str(chr(96 + (lang % 32)))
                self.box_info['language'] = ch1 + ch2 + ch3
        finally:
            fp.seek(self.start_of_box + self.size)


class ElngBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['extended_language'] = fp.read(self.size - (self.header.header_size + 4)).split(b'\x00')[0]
        finally:
            fp.seek(self.start_of_box + self.size)


class DrefBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            for i in range(self.box_info['entry_count']):
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
        finally:
            fp.seek(self.start_of_box + self.size)


class Url_Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.flags & 0x000001 != 1:
                data_entry = fp.read(self.size - (self.header.header_size + 4))
                self.box_info['location'] = data_entry.decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class Urn_Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.flags & 0x000001 != 1:
                name, ignore, location = fp.read(self.size - (self.header.header_size + 4)).partition(b'\x00')
                self.box_info['name'] = location.decode('utf-8', errors="ignore")
                self.box_info['location'] = location.decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class HdlrBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(4, os.SEEK_CUR)
            self.box_info['handler_type'] = fp.read(4).decode('utf-8')
            fp.seek(12, os.SEEK_CUR)
            bytes_left = self.size - (self.header.header_size + 25)  # string is null terminated
            self.box_info['name'] = fp.read(bytes_left).decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class StblBox(ContainerBox):
    # Sub-class from container box so we can do some extra things with child boxes
    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            # Some sample table boxes have dependencies on other sample table table boxes in order to read correctly
            # Fill stdp, sdtp lists using sample count in stsz
            sz = [box for box in self.children if box.type == 'stsz' or box.type == 'stz2'][0] if [
                box for box in self.children if box.type == 'stsz' or box.type == 'stz2'] else False
            sc = sz.box_info['sample_count'] if sz else False
            sdtp = [box for box in self.children if box.type == 'sdtp'][0] if [
                box for box in self.children if box.type == 'sdtp'] else False
            stdp = [box for box in self.children if box.type == 'stdp'][0] if [
                box for box in self.children if box.type == 'stdp'] else False
            if sc and sdtp:
                sdtp.update_table(fp, sc)
            if sc and stdp:
                stdp.update_table(fp, sc)
        finally:
            fp.seek(self.start_of_box + self.size)


class TrafBox(ContainerBox):
    # Sub-class from container box so we can do some extra things with child boxes
    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            # if we have a senc box
            senc = [box for box in self.children if box.type == 'senc'][0] if [
                box for box in self.children if box.type == 'senc'] else False
            if senc:
                # check if it has sub-sampling before getting IV_size from sgpd or saiz
                if senc.flags & 0x000002 == 0x000002:
                    per_sample_iv_size = 0
                    sgpd = [box for box in self.children if box.type == 'sgpd'][0] if [
                       box for box in self.children if box.type == 'sgpd'] else False
                    saiz = [box for box in self.children if box.type == 'saiz'][0] if [
                        box for box in self.children if box.type == 'saiz'] else False
                    if sgpd and sgpd.box_info['grouping_type'] == 'seig':
                        # I've only ever seen a single entry in seig so get IV size from this
                        per_sample_iv_size = sgpd.box_info['entry_list'][0]['per_sample_iv_size']
                    # try saiz
                    elif saiz:
                        # does it have non-zero default size?
                        if saiz.box_info['default_sample_info_size'] > 0:
                            sample_size = saiz.box_info['default_sample_info_size']
                        else:
                            sample_size = min([sample['sample_info_size']
                                                for sample in saiz.box_info['sample_info_size_list']])
                        # deduct 10 or 18 from sample size (8 or 16 byte IV + 2 byte sub-sample count) and divide by six
                        # (2 bytes clear data size + 4 bytes enc data size)
                        per_sample_iv_size = 8 if (sample_size - 10) % 6 == 0 else 16 if (sample_size - 18) % 6 == 0 else 0
                    senc.populate_sample_table(fp, per_sample_iv_size)
        finally:
            fp.seek(self.start_of_box + self.size)


class VmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['graphicsmode'] = read_u16(fp)
            self.box_info['opcolor'] = struct.unpack('>3H', fp.read(6))
        finally:
            fp.seek(self.start_of_box + self.size)


class SmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['balance'] = read_i8_8(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class HmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['maxPDUsize'] = read_u16(fp)
            self.box_info['avgPDUsize'] = read_u16(fp)
            self.box_info['maxbitrate'] = read_u32(fp)
            self.box_info['avgbitrate'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class NmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)

        try:
            pass
        finally:
            fp.seek(self.start_of_box + self.size)


class StsdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            for i in range(self.box_info['entry_count']):
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.children.append(current_box)
        finally:
            fp.seek(self.start_of_box + self.size)


class SttsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_delta': read_u32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class CttsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                if self.version == 1:
                    self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_offset': read_i32(fp)})
                else:
                    self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_offset': read_i32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class CslgBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.version == 1:
                self.box_info['compositionToDTSShift'] = read_i64(fp)
                self.box_info['leastDecodeToDisplayDelta'] = read_i64(fp)
                self.box_info['greatestDecodeToDisplayDelta'] = read_i64(fp)
                self.box_info['compositionStartTime'] = read_i64(fp)
                self.box_info['compositionEndTime'] = read_i64(fp)
            else:
                self.box_info['compositionToDTSShift'] = read_i32(fp)
                self.box_info['leastDecodeToDisplayDelta'] = read_i32(fp)
                self.box_info['greatestDecodeToDisplayDelta'] = read_i32(fp)
                self.box_info['compositionStartTime'] = read_i32(fp)
                self.box_info['compositionEndTime'] = read_i32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class StssBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({'sample_number': read_u32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class StshBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({
                    'shadowed_sample_number': read_u32(fp),
                    'sync_sample_number': read_u32(fp)
                })
        finally:
            fp.seek(self.start_of_box + self.size)


class StscBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                first_chunk = read_u32(fp)
                samples_per_chunk = read_u32(fp)
                samples_description_index = read_u32(fp)
                self.box_info['entry_list'].append({'first_chunk': first_chunk, 'samples_per_chunk': samples_per_chunk,
                                                    'samples_description_index': samples_description_index})
        finally:
            fp.seek(self.start_of_box + self.size)


class StcoBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({'chunk_offset': read_u32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class Co64Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({'chunk_offset': read_u64(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class PadbBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['sample_count'] = read_u32(fp)
            self.box_info['sample_list'] = []
            for i in range(self.box_info['sample_count']):
                pads = read_u8(fp)
                self.box_info['entry_list'].append({'pad1': pads // 16, 'pad2': pads % 16})
        finally:
            fp.seek(self.start_of_box + self.size)


class SubsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                sample_delta = read_u32(fp)
                subsample_count = read_u16(fp)
                if subsample_count > 0:
                    subsample_list = []
                    for j in range(subsample_count):
                        if self.version == 1:
                            subsample_size = read_u32(fp)
                        else:
                            subsample_size = read_u16(fp)
                        subsample_priority = read_u8(fp)
                        discardable = read_u8(fp)
                        codec_specific_parameters = read_u32(fp)
                        subsample_list.append({
                            'subsample_size': subsample_size,
                            'subsample_priority': subsample_priority,
                            'discardable': discardable,
                            'codec_specific_parameters': codec_specific_parameters
                        })
                    self.box_info['entry_list'].append({
                        'sample_delta': sample_delta,
                        'subsample_count': subsample_count,
                        'subsample_list': subsample_list
                    })
        finally:
            fp.seek(self.start_of_box + self.size)


class SbgpBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['grouping_type'] = fp.read(4).decode('utf-8')
            if self.version == 1:
                self.box_info['grouping_type_parameter'] = read_u32(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({
                    'sample_count': read_u32(fp),
                    'group_description_index': read_u32(fp)
                })
        finally:
            fp.seek(self.start_of_box + self.size)


class SgpdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['grouping_type'] = fp.read(4).decode('utf-8')
            if self.version == 1:
                self.box_info['default_length'] = read_u32(fp)
            elif self.version >= 2:
                self.box_info['default_sample_description_index'] = read_u32(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                if self.box_info['default_length'] == 0 and self.version == 1:
                    description_length = read_u32(fp)
                else:
                    description_length = self.box_info['default_length']
                sample_group_entry = binascii.b2a_hex(fp.read(description_length)).decode('utf-8')
                if self.box_info['grouping_type'] == 'seig':
                    seig_dict = {'crypto_byte_block': int(sample_group_entry[2], 16),
                                                            'skip_byte_block': int(sample_group_entry[3], 16),
                                                            'is_encrypted': int(sample_group_entry[5], 16),
                                                            'per_sample_iv_size': int(sample_group_entry[6:8], 16),
                                                            'kid': sample_group_entry[8:40]}
                    if seig_dict['is_encrypted'] == 1 and seig_dict['per_sample_iv_size'] == 0:
                        seig_dict['constant_IV_size'] = int(sample_group_entry[40:42], 16)
                        seig_dict['constant_IV'] = sample_group_entry[42:]
                    self.box_info['entry_list'].append(seig_dict)
                else:
                    self.box_info['entry_list'].append({'sample_group_entry': sample_group_entry})
        finally:
            fp.seek(self.start_of_box + self.size)


class SaizBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.flags & 0x000001 == 0x000001:
                self.box_info['aux_info_type'] = fp.read(4).decode('utf-8')
                self.box_info['aux_info_type_parameter'] = read_u32(fp)
            self.box_info['default_sample_info_size'] = read_u8(fp)
            self.box_info['sample_count'] = read_u32(fp)
            if self.box_info['default_sample_info_size'] == 0:
                self.box_info['sample_info_size_list'] = []
                for i in range(self.box_info['sample_count']):
                    self.box_info['sample_info_size_list'].append({'sample_info_size': read_u8(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class SaioBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            if self.flags & 0x000001 == 0x000001:
                self.box_info['aux_info_type'] = fp.read(4).decode('utf-8')
                self.box_info['aux_info_type_parameter'] = read_u32(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['offset_list'] = []
            for i in range(self.box_info['entry_count']):
                if self.version == 0:
                    self.box_info['offset_list'].append({'offset': read_u32(fp)})
                else:
                    self.box_info['offset_list'].append({'offset': read_u64(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class StszBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['sample_size'] = read_u32(fp)
            self.box_info['sample_count'] = read_u32(fp)
            if self.box_info['sample_size'] == 0:
                self.box_info['entry_list'] = []
                for i in range(self.box_info['sample_count']):
                    self.box_info['entry_list'].append({'entry_size': read_u32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class Stz2Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['field_size'] = read_u32(fp)
            self.box_info['sample_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['sample_count']):
                if self.box_info['field_size'] == 4:
                    mybyte = read_u8(fp)
                    self.box_info['entry_list'].append({'entry_size': mybyte // 16}, {'entry_size+': mybyte % 16})
                if self.box_info['field_size'] == 8:
                    self.box_info['entry_list'].append({'entry_size': read_u8(fp)})
                if self.box_info['field_size'] == 16:
                    self.box_info['entry_list'].append({'entry_size': read_u16(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class StdpBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            pass
        finally:
            fp.seek(self.start_of_box + self.size)

    def update_table(self, fp, sc):
        fp_orig = fp.tell()
        fp.seek(self.start_of_box + self.header.header_size + 4)
        self.box_info['sample_list'] = []
        for i in range(sc):
            self.box_info['sample_list'].append({'priority': read_u16(fp)})
        fp.seek(fp_orig)


class SdtpBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            pass
        finally:
            fp.seek(self.start_of_box + self.size)

    def update_table(self, fp, sc):
        fp_orig = fp.tell()
        fp.seek(self.start_of_box + self.header.header_size + 4)
        self.box_info['sample_list'] = []
        for i in range(sc):
            the_byte = read_u8(fp)
            is_leading = the_byte >> 6
            depends_on = the_byte >> 4 & 3
            is_depended_on = the_byte >> 2 & 3
            has_redundancy = the_byte & 3
            self.box_info['sample_list'].append({
                'is_leading': is_leading,
                'sample_depends_on': depends_on,
                'sample_is_depended_on': is_depended_on,
                'sample_has_redundancy': has_redundancy
            })
        fp.seek(fp_orig)


class SidxBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['reference_ID'] = read_u32(fp)
            self.box_info['timescale'] = read_u32(fp)
            if self.version == 0:
                self.box_info['earliest_presentation_time'] = read_u32(fp)
                self.box_info['first_offset'] = read_u32(fp)
            else:
                self.box_info['earliest_presentation_time'] = read_u64(fp)
                self.box_info['first_offset'] = read_u64(fp)
            fp.seek(2, os.SEEK_CUR)
            self.box_info['reference_count'] = read_u16(fp)
            self.box_info['reference_list'] = []
            for i in range(self.box_info['reference_count']):
                rt_sz = read_u32(fp)
                subsegment_dur = read_u32(fp)
                st_sz = read_u32(fp)
                self.box_info['reference_list'].append({
                    'reference_type': rt_sz >> 31,
                    'reference_size': rt_sz % 2147483648,
                    'subsegment_duration': subsegment_dur,
                    'starts_with_sap': st_sz >> 31,
                    'SAP_type': st_sz >> 28 & 7,
                    'SAP_delta_time': st_sz % 268435456
                })
        finally:
            fp.seek(self.start_of_box + self.size)


class SsixBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['subsegment_count'] = read_u32(fp)
            self.box_info['subsegment_list'] = []
            for i in range(self.box_info['subsegment_count']):
                subsegment_dict = {'range_count': read_u32(fp)}
                range_list = []
                for j in range(self.box_info['range_count']):
                    l_r = read_u32(fp)
                    range_list.append({'level': l_r // 16777216, 'range_size': l_r % 16777216})
                subsegment_dict['range_list'] = range_list
                self.box_info['subsegment_list'].append(subsegment_dict)
        finally:
            fp.seek(self.start_of_box + self.size)


class PrftBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['reference_track_id'] = read_u32(fp)
            self.box_info['ntp_timestamp'] = read_u64(fp)
            if self.version == 0:
                self.box_info['media_time'] = read_u32(fp)
            else:
                self.box_info['media_time'] = read_u64(fp)
        finally:
            fp.seek(self.start_of_box + self.size)



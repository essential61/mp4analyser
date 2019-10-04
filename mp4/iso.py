import datetime
import mp4.non_iso
from mp4.core import *
from mp4.util import *


# Box Factory Function


def box_factory(fp, header, parent):
    the_box = None
    if header.type == 'ftyp':
        the_box = FtypBox(fp, header, parent)
    elif header.type == 'pdin':
        the_box = PdinBox(fp, header, parent)
    elif header.type == 'moov':
        the_box = MoovBox(fp, header, parent)
    elif header.type == 'mvhd':
        the_box = MvhdBox(fp, header, parent)
    elif header.type == 'meta':
        the_box = MetaBox(fp, header, parent)
    elif header.type == 'trak':
        the_box = TrakBox(fp, header, parent)
    elif header.type == 'tkhd':
        the_box = TkhdBox(fp, header, parent)
    elif header.type == 'tref':
        the_box = TrefBox(fp, header, parent)
    elif header.type == 'trgr':
        the_box = TrgrBox(fp, header, parent)
    elif header.type == 'edts':
        the_box = EdtsBox(fp, header, parent)
    elif header.type == 'elst':
        the_box = ElstBox(fp, header, parent)
    elif header.type == 'mdia':
        the_box = MdiaBox(fp, header, parent)
    elif header.type == 'mdhd':
        the_box = MdhdBox(fp, header, parent)
    elif header.type == 'hdlr':
        the_box = HdlrBox(fp, header, parent)
    elif header.type == 'elng':
        the_box = ElngBox(fp, header, parent)
    elif header.type == 'minf':
        the_box = MinfBox(fp, header, parent)
    elif header.type == 'vmhd':
        the_box = VmhdBox(fp, header, parent)
    elif header.type == 'smhd':
        the_box = SmhdBox(fp, header, parent)
    elif header.type == 'hmhd':
        the_box = HmhdBox(fp, header, parent)
#    elif header.type == 'sthd':
#        the_box = SthdBox(fp, header, parent)
    elif header.type == 'nmhd':
        the_box = NmhdBox(fp, header, parent)
    elif header.type == 'dinf':
        the_box = DinfBox(fp, header, parent)
    elif header.type == 'dref':
        the_box = DrefBox(fp, header, parent)
    elif header.type == 'url ':
        the_box = Url_Box(fp, header, parent)
    elif header.type == 'urn ':
        the_box = Urn_Box(fp, header, parent)
    elif header.type == 'stbl':
        the_box = StblBox(fp, header, parent)
    elif header.type == 'stsd':
        the_box = StsdBox(fp, header, parent)
    elif header.type == 'stts':
        the_box = SttsBox(fp, header, parent)
    elif header.type == 'ctts':
        the_box = CttsBox(fp, header, parent)
    elif header.type == 'cslg':
        the_box = CslgBox(fp, header, parent)
    elif header.type == 'stsc':
        the_box = StscBox(fp, header, parent)
    elif header.type == 'stsz':
        the_box = StszBox(fp, header, parent)
    elif header.type == 'stz2':
        the_box = Stz2Box(fp, header, parent)
    elif header.type == 'stco':
        the_box = StcoBox(fp, header, parent)
    elif header.type == 'co64':
        the_box = VmhdBox(fp, header, parent)
    elif header.type == 'stss':
        the_box = StssBox(fp, header, parent)
    elif header.type == 'stsh':
        the_box = HmhdBox(fp, header, parent)
    elif header.type == 'padb':
        the_box = PadbBox(fp, header, parent)
    elif header.type == 'stdp':
        the_box = StdpBox(fp, header, parent)
    elif header.type == 'sdtp':
        the_box = SdtpBox(fp, header, parent)
    elif header.type == 'sbgp':
        the_box = SbgpBox(fp, header, parent)
#    elif header.type == 'sgpd':
#        the_box = SgpdBox(fp, header, parent)
    elif header.type == 'subs':
        the_box = SubsBox(fp, header, parent)
#    elif header.type == 'saiz':
#        the_box = SaizBox(fp, header, parent)
#    elif header.type == 'saio':
#        the_box = SaioBox(fp, header, parent)
    elif header.type == 'udta':
        the_box = UdtaBox(fp, header, parent)
#    elif header.type == 'mvex':
#        the_box = MvexBox(fp, header, parent)
#    elif header.type == 'mehd':
#        the_box = MehdBox(fp, header, parent)
#    elif header.type == 'trex':
#        the_box = TrexBox(fp, header, parent)
#    elif header.type == 'leva':
#        the_box = LevaBox(fp, header, parent)
    elif header.type == 'moof':
        the_box = MoofBox(fp, header, parent)
    elif header.type == 'mfhd':
        the_box = MfhdBox(fp, header, parent)
    elif header.type == 'traf':
        the_box = TrafBox(fp, header, parent)
    elif header.type == 'tfhd':
        the_box = TfhdBox(fp, header, parent)
    elif header.type == 'trun':
        the_box = TrunBox(fp, header, parent)
    elif header.type == 'tfdt':
        the_box = TfdtBox(fp, header, parent)
#    elif header.type == 'mfra':
#        the_box = MfraBox(fp, header, parent)
#    elif header.type == 'tfra':
#        the_box = TfraBox(fp, header, parent)
#    elif header.type == 'mfro':
#        the_box = MfroBox(fp, header, parent)
    elif header.type == 'mdat':
        the_box = MdatBox(fp, header, parent)
    elif header.type == 'free':
        the_box = FreeBox(fp, header, parent)
    elif header.type == 'skip':
        the_box = SkipBox(fp, header, parent)
#    elif header.type == 'cprt':
#        the_box = CprtBox(fp, header, parent)
#    elif header.type == 'tsel':
#        the_box = TselBox(fp, header, parent)
#    elif header.type == 'strk':
#        the_box = StrkBox(fp, header, parent)
#    elif header.type == 'stri':
#        the_box = StriBox(fp, header, parent)
#    elif header.type == 'strd':
#       the_box = StrdBox(fp, header, parent)
#    elif header.type == 'iloc':
#        the_box = IlocBox(fp, header, parent)
#    elif header.type == 'ipro':
#        the_box = IproBox(fp, header, parent)
#    elif header.type == 'sinf':
#        the_box = SinfBox(fp, header, parent)
#    elif header.type == 'frma':
#        the_box = FrmaBox(fp, header, parent)
#    elif header.type == 'schm:
#       the_box = SchmBox(fp, header, parent)
#    elif header.type == 'iinf':
#        the_box = IinfBox(fp, header, parent)
#    elif header.type == 'xml ':
#        the_box = Xml_Box(fp, header, parent)
#    elif header.type == 'bxml':
#        the_box = BxmlBox(fp, header, parent)
#    elif header.type == 'pitm':
#        the_box = PitmBox(fp, header, parent)
#    elif header.type == 'fiin':
#       the_box = FiinBox(fp, header, parent)
#    elif header.type == 'paen':
#        the_box = PaenBox(fp, header, parent)
#    elif header.type == 'fire':
#        the_box = FireBox(fp, header, parent)
#    elif header.type == 'fpar':
#        the_box = FparBox(fp, header, parent)
#    elif header.type == 'fecr':
#        the_box = FecrBox(fp, header, parent)
#    elif header.type == 'segr:
#       the_box = SegrBox(fp, header, parent)
#    elif header.type == 'gitn':
#        the_box = GitnBox(fp, header, parent)
#    elif header.type == 'idat':
#        the_box = IdatBox(fp, header, parent)
#    elif header.type == 'iref:
#       the_box = IrefBox(fp, header, parent)
#    elif header.type == 'meco':
#        the_box = MecoBox(fp, header, parent)
#    elif header.type == 'mere':
#        the_box = MereBox(fp, header, parent)
    elif header.type == 'styp':
        the_box = StypBox(fp, header, parent)
    elif header.type == 'sidx':
        the_box = SidxBox(fp, header, parent)
    elif header.type == 'ssix':
        the_box = SsixBox(fp, header, parent)
    elif header.type == 'prft':
        the_box = PrftBox(fp, header, parent)
    else:
        return mp4.non_iso.box_factory_non_iso(fp, header, parent)
    return the_box
# Box classes


class Mp4File:

    def __init__(self, filename):
        self.filename = filename
        self.type = 'file'
        self.child_boxes = []
        with open(filename, 'rb') as f:
            end_of_file = False
            while not end_of_file:
                current_header = Header(f)
                current_box = box_factory(f, current_header, self)
                self.child_boxes.append(current_box)
                if current_box.size == 0:
                    end_of_file = True
                if len(f.read(4)) != 4:
                    end_of_file = True
                else:
                    f.seek(-4, 1)
        f.close()


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
            fp.seek(self.header.header_size, 1)
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


class PdinBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        end_of_box = self.start_of_box + self.size
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['rates'] = []
            while fp.tell() < end_of_box:
                self.box_info('rates').append({'rate': read_u32(fp), 'initial_delay': read_u32(fp)})
        finally:
            fp.seek(end_of_box)


class ContainerBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            bytes_left = self.size - self.header.header_size
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


DinfBox = MinfBox = MdiaBox = TrefBox = EdtsBox = TrafBox = TrakBox = MoofBox = MoovBox = ContainerBox
UdtaBox = TrgrBox = ContainerBox


class MetaBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            bytes_left = self.size - (self.header.header_size + 4)
            while bytes_left > 7:
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                bytes_left -= current_box.size
        finally:
            fp.seek(self.start_of_box + self.size)


class MdatBox(Mp4Box):
    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            self.box_info['message'] = 'If mdat > 1 MB only the first 1 MB will be shown in the hex view'
        finally:
            fp.seek(self.start_of_box + self.size)


class MvhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.box_info['version'] == 1:
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
            fp.seek(10, 1)
            self.box_info['matrix'] = ["{0:#010x}".format(b) for b in struct.unpack('>9I', fp.read(36))]
            fp.seek(24, 1)
            self.box_info['next_track_id'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class MfhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['sequence_number'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class ElstBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            for i in range(self.box_info['entry_count']):
                if self.box_info['version'] == 1:
                    self.box_info['segment_duration'] = read_u64(fp)
                    self.box_info['media_time'] = read_i64(fp)
                else:
                    self.box_info['segment_duration'] = read_u32(fp)
                    self.box_info['media_time'] = read_i32(fp)
                self.box_info['media_rate_integer'] = read_i16(fp)
            self.box_info['media_rate_fraction'] = read_i16(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class TkhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.box_info['version'] == 1:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['track_ID'] = read_u32(fp)
                fp.seek(4, 1)
                self.box_info['duration'] = read_u64(fp)
            else:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['track_ID'] = read_u32(fp)
                fp.seek(4, 1)
                self.box_info['duration'] = read_u32(fp)
            fp.seek(8, 1)
            self.box_info['layer'] = read_i16(fp)
            self.box_info['alternate_group'] = read_i16(fp)
            self.box_info['volume'] = read_u8_8(fp)
            fp.seek(2, 1)
            self.box_info['matrix'] = ["{0:#010x}".format(b) for b in struct.unpack('>9I', fp.read(36))]
            fp.seek(24, 1)
            self.box_info['width'] = read_u16_16(fp)
            self.box_info['height'] = read_u16_16(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class TfhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['track_id'] = read_u32(fp)
            if int(self.box_info['flags'][-1]) & 1 == 1:
                self.box_info['base_data_offset'] = read_u64(fp)
            if int(self.box_info['flags'][-1]) & 2 == 2:
                self.box_info['sample_description_index'] = read_u32(fp)
            if int(self.box_info['flags'][-2]) & 1 == 1:
                self.box_info['default_sample_duration'] = read_u32(fp)
            if int(self.box_info['flags'][-2]) & 2 == 2:
                self.box_info['default_sample_size'] = read_u32(fp)
            if int(self.box_info['flags'][-5]) & 2 == 2:
                self.box_info['default_sample_flags'] = "{0:#08x}".format(read_u32(fp))
        finally:
            fp.seek(self.start_of_box + self.size)


class TrunBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['sample_count'] = read_u32(fp)
            has_sample_duration = False
            has_sample_size = False
            has_sample_flags = False
            has_scto = False
            if int(self.box_info['flags'][-1]) & 1 == 1:
                self.box_info['data_offset'] = read_i32(fp)
            if int(self.box_info['flags'][-1]) & 4 == 4:
                self.box_info['first_sample_flags'] = read_u32(fp)
            if int(self.box_info['flags'][-3]) & 1 == 1:
                has_sample_duration = True
            if int(self.box_info['flags'][-3]) & 2 == 2:
                has_sample_size = True
            if int(self.box_info['flags'][-3]) & 4 == 4:
                has_sample_flags = True
            if int(self.box_info['flags'][-3]) & 8 == 8:
                has_scto = True
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
                    if int(self.box_info['version']) == 1:
                        self.box_info['sample_composition_time_offset'] = read_u64(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            if int(self.box_info['version']) == 1:
                self.box_info['baseMediaDecode'] = read_u64(fp)
            else:
                self.box_info['baseMediaDecode'] = read_u32(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class MdhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            dt_base = datetime.datetime(1904, 1, 1, 0, 0, 0)
            if self.box_info['version'] == 1:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u64(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                fp.seek(4, 1)
                self.box_info['duration'] = read_u64(fp)
            else:
                self.box_info['creation_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['modification_time'] = (
                        dt_base + datetime.timedelta(seconds=(read_u32(fp)))).strftime('%Y-%m-%d %H:%M:%S')
                self.box_info['timescale'] = read_u32(fp)
                fp.seek(4, 1)
                self.box_info['duration'] = read_u32(fp)
            # I think this is right
            lang = struct.unpack('>H', fp.read(2))[0]
            if lang == 0:
                self.box_info['language'] = '0x00'
            else:
                ch1 = str(chr(60 + (lang % 32768 // 1024)))
                ch2 = str(chr(60 + (lang % 1024 // 32)))
                ch3 = str(chr(60 + (lang % 32)))
                self.box_info['language'] = ch1 + ch2 + ch3
        finally:
            fp.seek(self.start_of_box + self.size)


class ElngBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['extended_language'] = fp.read(self.size - (self.header.header_size + 4)).split(b'\x00')[0]
        finally:
            fp.seek(self.start_of_box + self.size)


class DrefBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            for i in range(self.box_info['entry_count']):
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
        finally:
            fp.seek(self.start_of_box + self.size)


class Url_Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            if int(self.box_info['flags'][-1]) != 1:
                data_entry = fp.read(self.size - (self.header.header_size + 4))
                self.box_info['location'] = data_entry.decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class Urn_Box(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            if int(self.box_info['flags'][-1]) != 1:
                name, ignore, location = fp.read(self.size - (self.header.header_size + 4)).partition(b'\x00')
                self.box_info['name'] = location.decode('utf-8', errors="ignore")
                self.box_info['location'] = location.decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class HdlrBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            fp.seek(4, 1)
            self.box_info['handler_type'] = fp.read(4).decode('utf-8')
            fp.seek(12, 1)
            bytes_left = self.size - (self.header.header_size + 25)  # string is null terminated
            self.box_info['name'] = fp.read(bytes_left).decode('utf-8', errors="ignore")
        finally:
            fp.seek(self.start_of_box + self.size)


class StblBox(Mp4Box):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            bytes_left = self.size - self.header.header_size
            while bytes_left > 7:
                saved_file_position = fp.tell()
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
                fp.seek(saved_file_position + current_box.size)
                bytes_left -= current_box.size
            # fill stdp list using sample count in stsz
            sc = None
            stdp_ord = None
            sdtp_ord = None
            for i, this_child in enumerate(self.child_boxes):
                if this_child.type == 'stsz' or this_child.type == 'stz2':
                    sc = this_child.box_info['sample_count']
                    if stdp_ord is not None and sdtp_ord is not None:
                        break
                if this_child.type == 'sdtp':
                    sdtp_ord = i
                    if sc is not None and stdp_ord is not None:
                        break
                if this_child.type == 'stdp':
                    stdp_ord = i
                    if sc is not None and sdtp_ord is not None:
                        break
            if sdtp_ord is not None:
                self.child_boxes[sdtp_ord].update_table(fp, sc)
            if stdp_ord is not None:
                self.child_boxes[stdp_ord].update_table(fp, sc)
        finally:
            fp.seek(self.start_of_box + self.size)


class VmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['graphicsmode'] = read_u16(fp)
            self.box_info['opcolor'] = struct.unpack('>3H', fp.read(6))
        finally:
            fp.seek(self.start_of_box + self.size)


class SmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['balance'] = read_i8_8(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class HmhdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
        finally:
            fp.seek(self.start_of_box + self.size)


class StsdBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            for i in range(self.box_info['entry_count']):
                current_header = Header(fp)
                current_box = box_factory(fp, current_header, self)
                self.child_boxes.append(current_box)
        finally:
            fp.seek(self.start_of_box + self.size)


class SttsBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                if self.box_info['version'] == 1:
                    self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_offset': read_i32(fp)})
                else:
                    self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_offset': read_i32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class CslgBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            if self.box_info['version'] == 1:
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                self.box_info['entry_list'].append({'sample_count': read_u32(fp), 'sample_delta': read_u32(fp)})
        finally:
            fp.seek(self.start_of_box + self.size)


class StscBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['entry_count'] = read_u32(fp)
            self.box_info['entry_list'] = []
            for i in range(self.box_info['entry_count']):
                sample_delta = read_u32(fp)
                subsample_count = read_u16(fp)
                if subsample_count > 0:
                    subsample_list = []
                    for j in range(subsample_count):
                        if self.box_info['version'] == 1:
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['grouping_type'] = read_u32(fp)
            if self.box_info['version'] == 1:
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


class SaizBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            if int(self.box_info['flags'][-1]) == 1:
                self.box_info['aux_info_type'] = read_u32(fp)
                self.box_info['aux_info_type_parameter'] = read_u32(fp)
            self.box_info['default_sample_info_size'] = read_u8(fp)
            self.box_info['sample_count'] = read_u32(fp)
            # TODO spec is unclear, is it an array?
        finally:
            fp.seek(self.start_of_box + self.size)


class StszBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['field_size'] = read_u32(fp)
            self.box_info['sample_count'] = read_u32(fp)
            if self.box_info['sample_size'] == 0:
                self.box_info['entry_list'] = []
                for i in range(self.box_info['sample_count']):
                    if self.box_info['field_size'] == 4:
                        mybyte = read_u8(fp)
                        self.box_info['entry_list'].append({'entry_size': mybyte // 16, 'entry_size+': mybyte % 16})
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
        finally:
            fp.seek(self.start_of_box + self.size)

    def update_table(self, fp, sc):
        fp_orig = fp.tell()
        fp.seek(self.start_of_box + self.header.header_size + 4)
        self.box_info['sample_list'] = []
        for i in range(sc):
            the_byte = read_u8(fp)
            is_leading = the_byte // 64
            depends_on = (the_byte % 64) // 16
            is_depended_on = (the_byte % 16) // 4
            has_redundancy = the_byte % 4
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['reference_ID'] = read_u32(fp)
            self.box_info['timescale'] = read_u32(fp)
            if self.box_info['version'] == 0:
                self.box_info['earliest_presentation_time'] = read_u32(fp)
                self.box_info['first_offset'] = read_u32(fp)
            else:
                self.box_info['earliest_presentation_time'] = read_u64(fp)
                self.box_info['first_offset'] = read_u64(fp)
            fp.seek(2, 1)
            self.box_info['reference_count'] = read_u16(fp)
            self.box_info['reference_list'] = []
            for i in range(self.box_info['reference_count']):
                rt_sz = read_u32(fp)
                subsegment_dur = read_u32(fp)
                st_sz = read_u32(fp)
                self.box_info['reference_list'].append({
                                                        'reference_type': rt_sz // 2147483648,
                                                        'reference_size': rt_sz % 2147483648,
                                                        'subsegment_duration': subsegment_dur,
                                                        'starts_with_sap': st_sz // 2147483648,
                                                        'SAP_type': (st_sz % 2147483648) // 268435456,
                                                        'SAP_delta_time': st_sz // 268435456
                                                      })
        finally:
            fp.seek(self.start_of_box + self.size)


class SsixBox(Mp4FullBox):

    def __init__(self, fp, header, parent):
        super().__init__(fp, header, parent)
        try:
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
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
            fp.seek(self.header.header_size, 1)
            self.box_info = self.set_version_and_flags(fp)
            self.box_info['reference_track_id'] = read_u32(fp)
            self.box_info['ntp_timestamp'] = read_u64(fp)
            if self.box_info['version'] == 0:
                self.box_info['media_time'] = read_u32(fp)
            else:
                self.box_info['media_time'] = read_u64(fp)
        finally:
            fp.seek(self.start_of_box + self.size)

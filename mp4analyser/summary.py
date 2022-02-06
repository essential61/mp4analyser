"""
summary.py
"""
import os


class Summary:
    """ Summary Class for an Mp4File Class """

    def __init__(self, mp4file):
        boxes = mp4file.children
        self.data = {}
        self.data['filename'] = mp4file.filename
        self.data['filesize (bytes)'] = os.path.getsize(mp4file.filename)
        if [box for box in boxes if box.type == 'ftyp' or box.type == 'styp']:
            fstyp = [box for box in boxes if box.type == 'ftyp' or box.type == 'styp'][0]
            self.data['brand'] = fstyp.box_info['major_brand']
        # check if there is a moov and if there is a moov that contains traks N.B only ever 0,1 moov boxes
        if [box for box in boxes if box.type == 'moov']:
            moov = [box for box in boxes if box.type == 'moov'][0]
            mvhd = [mvbox for mvbox in moov.children if mvbox.type == 'mvhd'][0]
            self.data['creation_time'] = mvhd.box_info['creation_time']
            self.data['modification_time'] = mvhd.box_info['modification_time']
            self.data['duration (secs)'] = round(mvhd.box_info['duration'] / mvhd.box_info['timescale'])
            if self.data['duration (secs)'] > 0:
                self.data['bitrate (bps)'] = round(8 * self.data['filesize (bytes)'] / self.data['duration (secs)'])
            traks = [tbox for tbox in moov.children if tbox.type == 'trak']
            self.data['track_list'] = []
            for trak in traks:
                this_trak = {}
                this_trak['track_id'] = [box for box in trak.children if box.type == 'tkhd'][0].box_info['track_ID']
                mdia = [box for box in trak.children if box.type == 'mdia'][0]
                mdhd = [box for box in mdia.children if box.type == 'mdhd'][0]
                hdlr = [box for box in mdia.children if box.type == 'hdlr'][0]
                stbl = [box for box in [box for box in mdia.children if box.type == 'minf'][0].children
                             if box.type == 'stbl'][0]
                t = mdhd.box_info['timescale']
                d = mdhd.box_info['duration']
                v = mdhd.version

                sz = [box for box in stbl.children if box.type == 'stsz' or box.type == 'stz2'][0]
                sc = sz.box_info['sample_count']
                if sz.box_info['sample_size'] > 0:
                    # uniform sample size
                    trak_size = sz.box_info['sample_size'] * sc
                else:
                    trak_size = sum([entry['entry_size'] for entry in sz.box_info['entry_list']])

                sample_rate = None
                if (d < 0xffffffff and v == 0) or (d < 0xffffffffffffffff and v == 1):
                    this_trak['track_duration (secs)'] = round(d / t)
                    if trak_size > 0 and this_trak['track_duration (secs)'] > 0:
                        this_trak['track_bitrate (calculated bps)'] = round(8 * trak_size / this_trak['track_duration (secs)'])
                        sample_rate = round((sc * t) / d, 2)

                codec_info = ([box for box in stbl.children if box.type == 'stsd'][0]).children[0]
                media = hdlr.box_info['handler_type']
                if media == 'vide':
                    this_trak['media_type'] = 'video'
                    this_trak['codec_type'] = codec_info.type
                    this_trak['width'] = codec_info.box_info['width'] if 'width' in codec_info.box_info else "unknown"
                    this_trak['height'] = codec_info.box_info['height'] if 'height' in codec_info.box_info else "unknown"
                    if sample_rate is not None:
                        this_trak['frame_rate'] = sample_rate
                elif media == 'soun':
                    this_trak['media_type'] = 'audio'
                    this_trak['codec_type'] = codec_info.type
                    this_trak['channel_count'] = codec_info.box_info['audio_channel_count'] \
                        if 'audio_channel_count' in codec_info.box_info else "unknown"
                    this_trak['sample_rate'] = codec_info.box_info['audio_sample_rate'] \
                        if 'audio_sample_rate' in codec_info.box_info else "unknown"
                else:
                    this_trak['media_type'] = media
                    this_trak['codec_type'] = codec_info.type

                self.data['track_list'].append(this_trak)
        else:
            # no moov found
            self.data['contains_moov'] = False

        if [box for box in boxes if box.type == 'moof']:
            self.data['contains_fragments'] = True




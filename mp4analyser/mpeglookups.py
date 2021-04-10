""" Mpeg lookup tables """

mp4ra_table = {
    0x20: '0x20, mp4v',
    0x21: '0x21, avc1|avc2|avc3|avc4',
    0x22: '0x22, avcp',
    0x23: '0x23, hev1|hev2|hev3|hvc1|hvc2|hvc3',
    0x40: '0x40, m4ae|mp4a',
    0xA0: '0xA0, sevc',
    0xA1: '0xA1, ssmv',
    0xA3: '0xA3, vc-1',
    0xA4: '0xA4, drac',
    0xA5: '0xA5, ac-3',
    0xA6: '0xA6, ec-3',
    0xA7: '0xA7, dra1',
    0xA8: '0xA8, g719',
    0xA9: '0xA9, dtsc',
    0xAA: '0xAA, dtsh',
    0xAB: '0xAB, dtsl',
    0xAC: '0xAC, dtse',
    0xAD: '0xAD, Opus',
    0xAE: '0xAE, ac-4',
    0xB0: '0xB0, rv60',
    0xB1: '0xB1, vp09',
    0xB2: '0xB2, dtsx',
    0xB3: '0xB3, dtsy',
    0xE1: '0xE1, sqcp'
    }

es_table = {
    0x00: '0x00,Forbidden',
    0x01: '0x01,ObjectDescriptorStream (see 8.5)',
    0x02: '0x02,ClockReferenceStream (see 10.2.5)',
    0x03: '0x03,SceneDescriptionStream (see 9.2.1)',
    0x04: '0x04,VisualStream',
    0x05: '0x05,AudioStream',
    0x06: '0x06,MPEG7Stream',
    0x07: '0x07,IPMPStream (see 8.3.2)',
    0x08: '0x08,ObjectContentInfoStream (see 8.4.2)',
    0x09: '0x09,MPEGJStream',
    0x0A: '0x0A,Interaction Stream',
    0x0B: '0x0B,IPMPToolStream',
    0x0C: '0x0C,FontDataStream',
    0x0D: '0x0D,StreamingText'
    }

sound_codec_table = {
    0: '0, Null',
    1: '1, AAC Main',
    2: '2, AAC LC (Low Complexity)',
    3: '3, AAC SSR (Scalable Sample Rate)',
    4: '4, AAC LTP (Long Term Prediction)',
    5: '5, SBR (Spectral Band Replication)',
    6: '6, AAC Scalable',
    7: '7, TwinVQ',
    8: '8, CELP (Code Excited Linear Prediction)',
    9: '9, HXVC (Harmonic Vector eXcitation Coding)',
    10: '10, Reserved',
    11: '11, Reserved',
    12: '12, TTSI (Text-To-Speech Interface)',
    13: '13, Main Synthesis',
    14: '14, Wavetable Synthesis',
    15: '15, General MIDI',
    16: '16, Algorithmic Synthesis and Audio Effects',
    17: '17, ER (Error Resilient) AAC LC',
    18: '18, Reserved',
    19: '19, ER AAC LTP',
    20: '20, ER AAC Scalable',
    21: '21, ER TwinVQ',
    22: '22, ER BSAC (Bit-Sliced Arithmetic Coding)',
    23: '23, ER AAC LD (Low Delay)',
    24: '24, ER CELP',
    25: '25, ER HVXC',
    26: '26, ER HILN (Harmonic and Individual Lines plus Noise)',
    27: '27, ER Parametric',
    28: '28, SSC (SinuSoidal Coding)',
    29: '29, PS (Parametric Stereo)',
    30: '30, MPEG Surround',
    31: '31, (Escape value)',
    32: '32, Layer-1',
    33: '33, Layer-2',
    34: '34, Layer-3',
    35: '35, DST (Direct Stream Transfer)',
    36: '36, ALS (Audio Lossless)',
    37: '37, SLS (Scalable LosslesS)',
    38: '38, SLS non-core',
    39: '39, ER AAC ELD (Enhanced Low Delay)',
    40: '40, SMR (Symbolic Music Representation) Simple',
    41: '41, SMR Main',
    42: '42, USAC (Unified Speech and Audio Coding) (no SBR)',
    43: '43, SAOC (Spatial Audio Object Coding)',
    44: '44, LD MPEG Surround',
    45: '45, USAC',
    46: '46,Unknown',
    47: '47,Unknown',
    48: '48,Unknown',
    49: '49,Unknown',
    50: '50,Unknown',
    51: '51,Unknown',
    52: '52,Unknown',
    53: '53,Unknown',
    54: '54,Unknown',
    55: '55,Unknown',
    56: '56,Unknown',
    57: '57,Unknown',
    58: '58,Unknown',
    59: '59,Unknown',
    60: '60,Unknown',
    61: '61,Unknown',
    62: '62,Unknown',
    63: '63,Unknown'
    }

freq_table = {
    0: '0, 96000 Hz',
    1: '1, 88200 Hz',
    2: '2, 64000 Hz',
    3: '3, 48000 Hz',
    4: '4, 44100 Hz',
    5: '5, 32000 Hz',
    6: '6, 24000 Hz',
    7: '7, 22050 Hz',
    8: '8, 16000 Hz',
    9: '9, 12000 Hz',
    10: '10, 11025 Hz',
    11: '11, 8000 Hz',
    12: '12, 7350 Hz',
    13: '13, Reserved',
    14: '14, Reserved',
    15: '15, frequency is written explicitly'
    }

sound_channel_table = {
    0: '0, Defined in AOT Specifc Config',
    1: '1, 1 channel',
    2: '2, 2 channels',
    3: '3, 3 channels',
    4: '4, 4 channels',
    5: '5, 5 channels',
    6: '6, 6 channels',
    7: '7, 8 channels',
    8: '8,unknown',
    9: '9,unknown',
    10: '10,unknown',
    11: '11,unknown',
    12: '12,unknown',
    13: '13,unknown',
    14: '14,unknown',
    15: '15,unknown'
}

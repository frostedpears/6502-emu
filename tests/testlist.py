tests = [
    {
        'name': 'Indexed indirect: ($c0,X)',
        'prog_start': 0x0600,
        'prog_len': 0x11,
        'prog_hex': "a2 01 a9 05 85 01 a9 07 85 02 a0 0a 8c 05 07 a1 00",
        'out_start': 0x00,
        'out_len': 0x10,
        'out_hex': "00 05 07 00 00 00 00 00 00 00 00 00 00 00 00 00",
        'out_flags': 0b00110000,
        'out_reg': [0x0a, 0x01, 0x0a]
    },
    {
        'name': 'inx 16 times',
        'prog_start': 0x0600,
        'prog_len': 0x10,
        'prog_hex': "e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8 e8",
        'out_start': 0x00,
        'out_len': 0x10,
        'out_hex': "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
        'out_flags': 0b00110000,
        'out_reg': [0x00, 0x10, 0x00]
    },
    {
        'name': 'intentional fail',
        'prog_start': 0x0600,
        'prog_len': 0x8,
        'prog_hex': "ea ea ea ea ea ea ea ea",
        'out_start': 0x00,
        'out_len': 0x08,
        'out_hex': "00 00 00 00 00 00 00 00",
        'out_flags': 0b11111111,
        'out_reg': [0x10, 0x10, 0x10]
    },
]
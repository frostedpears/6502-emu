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
        'name': 'increment',
        'prog_start': 0x0600,
        'prog_len': 0x04,
        'prog_hex': "e8 c8 e6 05",
        'out_start': 0x00,
        'out_len': 0x10,
        'out_hex': "00 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00",
        'out_flags': 0b00110000,
        'out_reg': [0x00, 0x01, 0x01]
    },
    {
        'name': 'add with carry',
        'prog_start': 0x0600,
        'prog_len': 0x1d,
        'prog_hex': "a9 60 aa e8 69 64 18 85 00 85 01 85 03 65 00 a9 30 a2 02 6d 01 00 85 01 7d 01 00 85 03",
        'out_start': 0x00,
        'out_len': 0x10,
        'out_hex': "c4 f5 00 b9 00 00 00 00 00 00 00 00 00 00 00 00",
        'out_flags': 0b10110001,
        'out_reg': [0xb9, 0x02, 0x00]
    },
    {
        'name': 'rotate',
        'prog_start': 0x0600,
        'prog_len': 0x10,
        'prog_hex': "a9 40 8d 00 02 6e 00 02 a9 ff 8d 01 02 6e 01 02",
        'out_start': 0x200,
        'out_len': 0x02,
        'out_hex': "20 7f",
        'out_flags': 0b00110001,
        'out_reg': [0xff, 0x00, 0x00]
    },
    {
        'name': 'subtract',
        'prog_start': 0x0600,
        'prog_len': 0x0d,
        'prog_hex': "a9 20 85 00 38 e9 10 85 01 e5 00 e5 00",
        'out_start': 0x00,
        'out_len': 0x02,
        'out_hex': "20 10",
        'out_flags': 0b10110001,
        'out_reg': [0xcf, 0x00, 0x00]
    },
    {
        'name': 'jump/branch',
        'prog_start': 0x0600,
        'prog_len': 0x0F,
        'prog_hex': "a9 77 4c 07 06 85 00 85 01 d0 02 85 00 85 02",
        'out_start': 0x00,
        'out_len': 0x03,
        'out_hex': "00 77 77",
        'out_flags': 0b00110000,
        'out_reg': [0x77, 0x00, 0x00]
    },
]
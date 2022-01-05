# op modes
class m(object):
    NON = 0  # 'none'         
    IMP = 1  # 'implied'      - 
    IMM = 2  # 'immediate'    - #$44
    ZP  = 3  # 'zeropage'     - $44
    ZPX = 4  # 'zeropage,x'   - $44,X
    ZPY = 5  # 'zeropage,y'   - $44,Y
    IZX = 6  # '(indirect,x)' - ($44,X)
    IZY = 7  # 'indirect,y'   - ($44),Y
    ABS = 8  # 'absolute'     - $4400
    ABX = 9  # 'absolute,x'   - $4400,X
    ABY = 10 # 'absolute,y'   - $4400,Y
    IND = 11 # 'indirect'     - ($4400)
    REL = 12 # 'relative'     - $44

# byte length by mode
class bl(object):
    NON = 1  # 'none'         
    IMP = 1  # 'implied'      - 
    IMM = 2  # 'immediate'    - #$44
    ZP  = 2  # 'zeropage'     - $44
    ZPX = 2  # 'zeropage,x'   - $44,X
    ZPY = 2  # 'zeropage,y'   - $44,Y
    IZX = 2  # '(indirect,x)' - ($44,X)
    IZY = 2  # '(indirect),y' - ($44),Y
    ABS = 3  # 'absolute'     - $4400
    ABX = 3  # 'absolute,x'   - $4400,X
    ABY = 3  # 'absolute,y'   - $4400,Y
    IND = 3  # 'indirect'     - ($4400)
    REL = 2  # 'relative'     - $44

relativeCodes = [
    'bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq'
]

# ------------------------------------------------
# -----------------  byte codes  -----------------
# ------------------------------------------------

byteCodes = {
    # ------------ logical and arithmetic commands ------------
    'ora': {
        m.IMM: 0x09,
        m.ZP: 0x05,
        m.ZPX: 0x15,
        m.IZX: 0x01,
        m.IZY: 0x11,
        m.ABS: 0x0d,
        m.ABX: 0x1d,
        m.ABY: 0x19,
    },
    'and': {
        m.IMM: 0x29,
        m.ZP: 0x25,
        m.ZPX: 0x35,
        m.IZX: 0x21,
        m.IZY: 0x31,
        m.ABS: 0x2d,
        m.ABX: 0x3d,
        m.ABY: 0x39,
    },
    'eor': {
        m.IMM: 0x49,
        m.ZP: 0x45,
        m.ZPX: 0x55,
        m.IZX: 0x41,
        m.IZY: 0x51,
        m.ABS: 0x4d,
        m.ABX: 0x5d,
        m.ABY: 0x59,
    },
    'adc': {
        m.IMM: 0x69,
        m.ZP: 0x65,
        m.ZPX: 0x75,
        m.IZX: 0x61,
        m.IZY: 0x71,
        m.ABS: 0x6d,
        m.ABX: 0x7d,
        m.ABY: 0x79,
    },
    'sbc': {
        m.IMM: 0xe9,
        m.ZP: 0xe5,
        m.ZPX: 0xf5,
        m.ABS: 0xed,
        m.ABX: 0xfd,
        m.ABY: 0xf9,
        m.IZX: 0xe1,
        m.IZY: 0xf1,
    },
    'cmp': {
        m.IMM: 0xc9,
        m.ZP: 0xc5,
        m.ZPX: 0xd5,
        m.IZX: 0xc1,
        m.IZY: 0xd1,
        m.ABS: 0xcd,
        m.ABX: 0xdd,
        m.ABY: 0xd9,
    },
    'cpx': {
        m.IMM: 0xe0,
        m.ZP: 0xe4,
        m.ABS: 0xec,
    },
    'cpy': {
        m.IMM: 0xc0,
        m.ZP: 0xc4,
        m.ABS: 0xcc,
    },
    'dec': {
        m.ZP: 0xc6,
        m.ZPX: 0xd6,
        m.ABS: 0xce,
        m.ABX: 0xde,
    },
    'dex': {
        m.IMP: 0xca,
    },
    'dey': {
        m.IMP: 0x88,
    },
    'inc': {
        m.ZP: 0xe6,
        m.ZPX: 0xf6,
        m.ABS: 0xee,
        m.ABX: 0xfe,
    },
    'inx': {
        m.IMP: 0xe8,
    },
    'iny': {
        m.IMP: 0xc8,
    },
    'asl': {
        m.IMP: 0x0a,
        m.ZP: 0x06,
        m.ZPX: 0x16,
        m.ABS: 0x0e,
        m.ABX: 0x1e,
    },
    'rol': {
        m.ZP: 0x26,
        m.ZPX: 0x36,
        m.ABS: 0x2e,
        m.ABX: 0x3e,
        m.IMP: 0x2a,
    },
    'lsr': {
        m.IMP: 0x4a,
        m.ZP: 0x46,
        m.ZPX: 0x56,
        m.ABS: 0x4e,
        m.ABX: 0x5e,
    },
    'ror': {
        m.ZP: 0x66,
        m.ZPX: 0x76,
        m.ABS: 0x6e,
        m.ABX: 0x7e,
        m.IMP: 0x6a,
    },
    # ------------ move commands ------------
    'lda': {
        m.IMM: 0xa9,
        m.ZP: 0xa5,
        m.ZPX: 0xb5,
        m.IZX: 0xa1,
        m.IZY: 0xb1,
        m.ABS: 0xad,
        m.ABX: 0xbd,
        m.ABY: 0xb9,
    },
    'sta': {
        m.ZP: 0x85,
        m.ZPX: 0x95,
        m.ABS: 0x8d,
        m.ABX: 0x9d,
        m.ABY: 0x99,
        m.IZX: 0x81,
        m.IZY: 0x91,
    },
    'ldx': {
        m.IMM: 0xa2,
        m.ZP: 0xa6,
        m.ZPY: 0xb6,
        m.ABS: 0xae,
        m.ABY: 0xbe,
    },
    'stx': {
        m.ZP: 0x86,
        m.ZPY: 0x96,
        m.ABS: 0x8e,
    },
    'ldy': {
        m.IMM: 0xa0,
        m.ZP: 0xa4,
        m.ZPX: 0xb4,
        m.ABS: 0xac,
        m.ABX: 0xbc,
    },
    'sty': {
        m.ZP: 0x84,
        m.ZPX: 0x94,
        m.ABS: 0x8c,
    },
    'tax': {
        m.IMP: 0xaa,
    },
    'txa': {
        m.IMP: 0x8a,
    },
    'tay': {
        m.IMP: 0xa8,
    },
    'tya': {
        m.IMP: 0x98,
    },
    'tsx': {
        m.IMP: 0xba,
    },
    'txs': {
        m.IMP: 0x9a,
    },
    'pla': {
        m.IMP: 0x68,
    },
    'pha': {
        m.IMP: 0x48,
    },
    'plp': {
        m.IMP: 0x28,
    },
    'php': {
        m.IMP: 0x08,
    },
    # ------------ jump/flag commands ------------
    'bpl': {
        m.REL: 0x10,
    },
    'bmi': {
        m.REL: 0x30,
    },
    'bvc': {
        m.REL: 0x50,
    },
    'bvs': {
        m.REL: 0x70,
    },
    'bcc': {
        m.REL: 0x90,
    },
    'bcs': {
        m.REL: 0xb0,
    },
    'bne': {
        m.REL: 0xd0,
    },
    'beq': {
        m.REL: 0xf0,
    },
    'brk': {
        m.IMP: 0x00,
    },
    'rti': {
        m.IMP: 0x40,
    },
    'jsr': {
        m.ABS: 0x20,
    },
    'rts': {
        m.IMP: 0x60,
    },
    'jmp': {
        m.ABS: 0x4c,
        m.IND: 0x6c,
    },
    'bit': {
        m.ZP: 0x24,
        m.ABS: 0x2c,
    },
    'clc': {
        m.IMP: 0x18,
    },
    'sec': {
        m.IMP: 0x38,
    },
    'cld': {
        m.IMP: 0xd8,
    },
    'sed': {
        m.IMP: 0xf8,
    },
    'cli': {
        m.IMP: 0x58,
    },
    'sei': {
        m.IMP: 0x78,
    },
    'clv': {
        m.IMP: 0xb8,
    },
    'nop': {
        m.IMP: 0xea,
    },
}

# ------------------------------------------------
# -----------------  cycle time  -----------------
# ------------------------------------------------

# TODO
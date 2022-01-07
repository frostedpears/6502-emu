# processor flags
class FLAG(object):
    NEG = 128 # NEGATIVE
    OVR = 64  # OVERFLOW
    UND = 32  # UNUSED
    BRK = 16  # BREAK
    DEC = 8   # DECIMAL
    INT = 4   # INTERRUPT
    ZER = 2   # ZERO
    CAR = 1   # CARRY

# op modes
class MODE(object):
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
byteLength = {
    MODE.NON: 1,  # 'none'         
    MODE.IMP: 1,  # 'implied'      - 
    MODE.IMM: 2,  # 'immediate'    - #$44
    MODE.ZP:  2,  # 'zeropage'     - $44
    MODE.ZPX: 2,  # 'zeropage,x'   - $44,X
    MODE.ZPY: 2,  # 'zeropage,y'   - $44,Y
    MODE.IZX: 2,  # '(indirect,x)' - ($44,X)
    MODE.IZY: 2,  # '(indirect),y' - ($44),Y
    MODE.ABS: 3,  # 'absolute'     - $4400
    MODE.ABX: 3,  # 'absolute,x'   - $4400,X
    MODE.ABY: 3,  # 'absolute,y'   - $4400,Y
    MODE.IND: 3,  # 'indirect'     - ($4400)
    MODE.REL: 2,  # 'relative'     - $44
}

relativeCodes = [
    'bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq'
    # cast np.uint8 to np.int8 for signed value
]

# ------------------------------------------------
# -----------  opcodes by asm & mode  ------------
# ------------------------------------------------

opCodes = {
    # ------------ logical and arithmetic commands ------------
    'ora': {
        MODE.IMM: 0x09,
        MODE.ZP: 0x05,
        MODE.ZPX: 0x15,
        MODE.IZX: 0x01,
        MODE.IZY: 0x11,
        MODE.ABS: 0x0d,
        MODE.ABX: 0x1d,
        MODE.ABY: 0x19,
    },
    'and': {
        MODE.IMM: 0x29,
        MODE.ZP: 0x25,
        MODE.ZPX: 0x35,
        MODE.IZX: 0x21,
        MODE.IZY: 0x31,
        MODE.ABS: 0x2d,
        MODE.ABX: 0x3d,
        MODE.ABY: 0x39,
    },
    'eor': {
        MODE.IMM: 0x49,
        MODE.ZP: 0x45,
        MODE.ZPX: 0x55,
        MODE.IZX: 0x41,
        MODE.IZY: 0x51,
        MODE.ABS: 0x4d,
        MODE.ABX: 0x5d,
        MODE.ABY: 0x59,
    },
    'adc': {
        MODE.IMM: 0x69,
        MODE.ZP: 0x65,
        MODE.ZPX: 0x75,
        MODE.IZX: 0x61,
        MODE.IZY: 0x71,
        MODE.ABS: 0x6d,
        MODE.ABX: 0x7d,
        MODE.ABY: 0x79,
    },
    'sbc': {
        MODE.IMM: 0xe9,
        MODE.ZP: 0xe5,
        MODE.ZPX: 0xf5,
        MODE.ABS: 0xed,
        MODE.ABX: 0xfd,
        MODE.ABY: 0xf9,
        MODE.IZX: 0xe1,
        MODE.IZY: 0xf1,
    },
    'cmp': {
        MODE.IMM: 0xc9,
        MODE.ZP: 0xc5,
        MODE.ZPX: 0xd5,
        MODE.IZX: 0xc1,
        MODE.IZY: 0xd1,
        MODE.ABS: 0xcd,
        MODE.ABX: 0xdd,
        MODE.ABY: 0xd9,
    },
    'cpx': {
        MODE.IMM: 0xe0,
        MODE.ZP: 0xe4,
        MODE.ABS: 0xec,
    },
    'cpy': {
        MODE.IMM: 0xc0,
        MODE.ZP: 0xc4,
        MODE.ABS: 0xcc,
    },
    'dec': {
        MODE.ZP: 0xc6,
        MODE.ZPX: 0xd6,
        MODE.ABS: 0xce,
        MODE.ABX: 0xde,
    },
    'dex': {
        MODE.IMP: 0xca,
    },
    'dey': {
        MODE.IMP: 0x88,
    },
    'inc': {
        MODE.ZP: 0xe6,
        MODE.ZPX: 0xf6,
        MODE.ABS: 0xee,
        MODE.ABX: 0xfe,
    },
    'inx': {
        MODE.IMP: 0xe8,
    },
    'iny': {
        MODE.IMP: 0xc8,
    },
    'asl': {
        MODE.IMP: 0x0a,
        MODE.ZP: 0x06,
        MODE.ZPX: 0x16,
        MODE.ABS: 0x0e,
        MODE.ABX: 0x1e,
    },
    'rol': {
        MODE.ZP: 0x26,
        MODE.ZPX: 0x36,
        MODE.ABS: 0x2e,
        MODE.ABX: 0x3e,
        MODE.IMP: 0x2a,
    },
    'lsr': {
        MODE.IMP: 0x4a,
        MODE.ZP: 0x46,
        MODE.ZPX: 0x56,
        MODE.ABS: 0x4e,
        MODE.ABX: 0x5e,
    },
    'ror': {
        MODE.ZP: 0x66,
        MODE.ZPX: 0x76,
        MODE.ABS: 0x6e,
        MODE.ABX: 0x7e,
        MODE.IMP: 0x6a,
    },
    # ------------ move commands ------------
    'lda': {
        MODE.IMM: 0xa9,
        MODE.ZP: 0xa5,
        MODE.ZPX: 0xb5,
        MODE.IZX: 0xa1,
        MODE.IZY: 0xb1,
        MODE.ABS: 0xad,
        MODE.ABX: 0xbd,
        MODE.ABY: 0xb9,
    },
    'sta': {
        MODE.ZP: 0x85,
        MODE.ZPX: 0x95,
        MODE.ABS: 0x8d,
        MODE.ABX: 0x9d,
        MODE.ABY: 0x99,
        MODE.IZX: 0x81,
        MODE.IZY: 0x91,
    },
    'ldx': {
        MODE.IMM: 0xa2,
        MODE.ZP: 0xa6,
        MODE.ZPY: 0xb6,
        MODE.ABS: 0xae,
        MODE.ABY: 0xbe,
    },
    'stx': {
        MODE.ZP: 0x86,
        MODE.ZPY: 0x96,
        MODE.ABS: 0x8e,
    },
    'ldy': {
        MODE.IMM: 0xa0,
        MODE.ZP: 0xa4,
        MODE.ZPX: 0xb4,
        MODE.ABS: 0xac,
        MODE.ABX: 0xbc,
    },
    'sty': {
        MODE.ZP: 0x84,
        MODE.ZPX: 0x94,
        MODE.ABS: 0x8c,
    },
    'tax': {
        MODE.IMP: 0xaa,
    },
    'txa': {
        MODE.IMP: 0x8a,
    },
    'tay': {
        MODE.IMP: 0xa8,
    },
    'tya': {
        MODE.IMP: 0x98,
    },
    'tsx': {
        MODE.IMP: 0xba,
    },
    'txs': {
        MODE.IMP: 0x9a,
    },
    'pla': {
        MODE.IMP: 0x68,
    },
    'pha': {
        MODE.IMP: 0x48,
    },
    'plp': {
        MODE.IMP: 0x28,
    },
    'php': {
        MODE.IMP: 0x08,
    },
    # ------------ jump/flag commands ------------
    'bpl': {
        MODE.REL: 0x10,
    },
    'bmi': {
        MODE.REL: 0x30,
    },
    'bvc': {
        MODE.REL: 0x50,
    },
    'bvs': {
        MODE.REL: 0x70,
    },
    'bcc': {
        MODE.REL: 0x90,
    },
    'bcs': {
        MODE.REL: 0xb0,
    },
    'bne': {
        MODE.REL: 0xd0,
    },
    'beq': {
        MODE.REL: 0xf0,
    },
    'brk': {
        MODE.IMP: 0x00,
    },
    'rti': {
        MODE.IMP: 0x40,
    },
    'jsr': {
        MODE.ABS: 0x20,
    },
    'rts': {
        MODE.IMP: 0x60,
    },
    'jmp': {
        MODE.ABS: 0x4c,
        MODE.IND: 0x6c,
    },
    'bit': {
        MODE.ZP: 0x24,
        MODE.ABS: 0x2c,
    },
    'clc': {
        MODE.IMP: 0x18,
    },
    'sec': {
        MODE.IMP: 0x38,
    },
    'cld': {
        MODE.IMP: 0xd8,
    },
    'sed': {
        MODE.IMP: 0xf8,
    },
    'cli': {
        MODE.IMP: 0x58,
    },
    'sei': {
        MODE.IMP: 0x78,
    },
    'clv': {
        MODE.IMP: 0xb8,
    },
    'nop': {
        MODE.IMP: 0xea,
    },
}


# ------------------------------------------------
# --------------  modes by opcode  ---------------
# ------------------------------------------------

# ------------ logical and arithmetic commands ------------

modes = {
#ora'
    0x09: MODE.IMM,
    0x05: MODE.ZP, 
    0x15: MODE.ZPX, 
    0x01: MODE.IZX, 
    0x11: MODE.IZY, 
    0x0d: MODE.ABS, 
    0x1d: MODE.ABX, 
    0x19: MODE.ABY, 
#and'
    0x29: MODE.IMM, 
    0x25: MODE.ZP, 
    0x35: MODE.ZPX, 
    0x21: MODE.IZX, 
    0x31: MODE.IZY, 
    0x2d: MODE.ABS, 
    0x3d: MODE.ABX, 
    0x39: MODE.ABY, 
#eor
    0x49: MODE.IMM, 
    0x45: MODE.ZP, 
    0x55: MODE.ZPX, 
    0x41: MODE.IZX, 
    0x51: MODE.IZY, 
    0x4d: MODE.ABS, 
    0x5d: MODE.ABX, 
    0x59: MODE.ABY, 
#adc
    0x69: MODE.IMM, 
    0x65: MODE.ZP, 
    0x75: MODE.ZPX, 
    0x61: MODE.IZX, 
    0x71: MODE.IZY, 
    0x6d: MODE.ABS, 
    0x7d: MODE.ABX, 
    0x79: MODE.ABY, 
#sbc
    0xe9: MODE.IMM, 
    0xe5: MODE.ZP, 
    0xf5: MODE.ZPX, 
    0xed: MODE.ABS,
    0xfd: MODE.ABX, 
    0xf9: MODE.ABY, 
    0xe1: MODE.IZX, 
    0xf1: MODE.IZY,
#cmp
    0xc9: MODE.IMM, 
    0xc5: MODE.ZP, 
    0xd5: MODE.ZPX, 
    0xc1: MODE.IZX,
    0xd1: MODE.IZY, 
    0xcd: MODE.ABS, 
    0xdd: MODE.ABX, 
    0xd9: MODE.ABY, 
#cpx
    0xe0: MODE.IMM,
    0xe4: MODE.ZP, 
    0xec: MODE.ABS, 
#cpy
    0xc0: MODE.IMM, 
    0xc4: MODE.ZP, 
    0xcc: MODE.ABS, 
#dec
    0xc6: MODE.ZP, 
    0xd6: MODE.ZPX, 
    0xce: MODE.ABS, 
    0xde: MODE.ABX, 
#dex
    0xca: MODE.IMP, 
#dey
    0x88: MODE.IMP, 
#inc
    0xe6: MODE.ZP, 
    0xf6: MODE.ZPX, 
    0xee: MODE.ABS, 
    0xfe: MODE.ABX, 
#inx
    0xe8: MODE.IMP, 
#iny
    0xc8: MODE.IMP, 
#asl
    0x0a: MODE.IMP, 
    0x06: MODE.ZP, 
    0x16: MODE.ZPX, 
    0x0e: MODE.ABS, 
    0x1e: MODE.ABX, 
#rol
    0x26: MODE.ZP, 
    0x36: MODE.ZPX, 
    0x2e: MODE.ABS, 
    0x3e: MODE.ABX, 
    0x2a: MODE.IMP, 
#lsr
    0x4a: MODE.IMP, 
    0x46: MODE.ZP, 
    0x56: MODE.ZPX, 
    0x4e: MODE.ABS, 
    0x5e: MODE.ABX, 
#ror
    0x66: MODE.ZP, 
    0x76: MODE.ZPX, 
    0x6e: MODE.ABS, 
    0x7e: MODE.ABX, 
    0x6a: MODE.IMP, 
# ------------ move commands ------------
#lda', {
    0xa9: MODE.IMM, 
    0xa5: MODE.ZP, 
    0xb5: MODE.ZPX, 
    0xa1: MODE.IZX, 
    0xb1: MODE.IZY, 
    0xad: MODE.ABS, 
    0xbd: MODE.ABX, 
    0xb9: MODE.ABY, 
#sta
    0x85: MODE.ZP, 
    0x95: MODE.ZPX, 
    0x8d: MODE.ABS, 
    0x9d: MODE.ABX, 
    0x99: MODE.ABY, 
    0x81: MODE.IZX, 
    0x91: MODE.IZY, 
#ldx
    0xa2: MODE.IMM, 
    0xa6: MODE.ZP, 
    0xb6: MODE.ZPY, 
    0xae: MODE.ABS, 
    0xbe: MODE.ABY, 
#stx
    0x86: MODE.ZP, 
    0x96: MODE.ZPY, 
    0x8e: MODE.ABS, 
#ldy
    0xa0: MODE.IMM, 
    0xa4: MODE.ZP, 
    0xb4: MODE.ZPX, 
    0xac: MODE.ABS, 
    0xbc: MODE.ABX, 
#sty
    0x84: MODE.ZP, 
    0x94: MODE.ZPX, 
    0x8c: MODE.ABS, 
#tax
    0xaa: MODE.IMP, 
#txa
    0x8a: MODE.IMP,
#tay
    0xa8: MODE.IMP, 
#tya
    0x98: MODE.IMP, 
#tsx
    0xba: MODE.IMP, 
#txs
    0x9a: MODE.IMP, 
#pla
    0x68: MODE.IMP, 
#pha
    0x48: MODE.IMP, 
#plp
    0x28: MODE.IMP, 
#php
    0x08: MODE.IMP, 
# ------------ jump/flag commands ------------
#bpl
    0x10: MODE.REL, 
#bmi
    0x30: MODE.REL, 
#bvc
    0x50: MODE.REL, 
#bvs
    0x70: MODE.REL, 
#bcc
    0x90: MODE.REL, 
#bcs
    0xb0: MODE.REL, 
#bne
    0xd0: MODE.REL, 
#beq
    0xf0: MODE.REL, 
#brk
    0x00: MODE.IMP, 
#rti
    0x40: MODE.IMP, 
#jsr
    0x20: MODE.ABS, 
#rts
    0x60: MODE.IMP, 
#jmp
    0x4c: MODE.ABS, 
    0x6c: MODE.IND, 
#bit
    0x24: MODE.ZP, 
    0x2c: MODE.ABS, 
#clc
    0x18: MODE.IMP, 
#sec
    0x38: MODE.IMP, 
#cld
    0xd8: MODE.IMP, 
#sed
    0xf8: MODE.IMP, 
#cli
    0x58: MODE.IMP, 
#sei
    0x78: MODE.IMP, 
#clv
    0xb8: MODE.IMP, 
#nop
    0xea: MODE.IMP, 
}

# ------------------------------------------------
# -----------  instruction by opcode  ------------
# ------------------------------------------------
instructions = {
    # ------------ logical and arithmetic commands ------------
 #ora'
    0x09: 'ora',
    0x05: 'ora',
    0x15: 'ora',
    0x01: 'ora',
    0x11: 'ora',
    0x0d: 'ora',
    0x1d: 'ora',
    0x19: 'ora',
#and'
    0x29: 'and',
    0x25: 'and',
    0x35: 'and',
    0x21: 'and',
    0x31: 'and',
    0x2d: 'and',
    0x3d: 'and',
    0x39: 'and',
#eor
    0x49: 'eor',
    0x45: 'eor',
    0x55: 'eor',
    0x41: 'eor',
    0x51: 'eor',
    0x4d: 'eor',
    0x5d: 'eor',
    0x59: 'eor',
#adc
    0x69: 'adc',
    0x65: 'adc',
    0x75: 'adc',
    0x61: 'adc',
    0x71: 'adc',
    0x6d: 'adc',
    0x7d: 'adc',
    0x79: 'adc',
#sbc
    0xe9: 'sbc',
    0xe5: 'sbc',
    0xf5: 'sbc',
    0xed: 'sbc',
    0xfd: 'sbc',
    0xf9: 'sbc',
    0xe1: 'sbc',
    0xf1: 'sbc',
#cmp
    0xc9: 'cmp',
    0xc5: 'cmp',
    0xd5: 'cmp',
    0xc1: 'cmp',
    0xd1: 'cmp',
    0xcd: 'cmp',
    0xdd: 'cmp',
    0xd9: 'cmp',
#cpx
    0xe0: 'cpx',
    0xe4: 'cpx',
    0xec: 'cpx',
#cpy
    0xc0: 'cpy',
    0xc4: 'cpy',
    0xcc: 'cpy',
#dec
    0xc6: 'dec',
    0xd6: 'dec',
    0xce: 'dec',
    0xde: 'dec',
#dex
    0xca: 'dex',
#dey
    0x88: 'dey',
#inc
    0xe6: 'inc',
    0xf6: 'inc',
    0xee: 'inc',
    0xfe: 'inc',
#inx
    0xe8: 'inx',
#iny
    0xc8: 'iny',
#asl
    0x0a: 'asl',
    0x06: 'asl',
    0x16: 'asl',
    0x0e: 'asl',
    0x1e: 'asl',
#rol
    0x26: 'rol',
    0x36: 'rol',
    0x2e: 'rol',
    0x3e: 'rol',
    0x2a: 'rol',
#lsr
    0x4a: 'lsr',
    0x46: 'lsr',
    0x56: 'lsr',
    0x4e: 'lsr',
    0x5e: 'lsr',
#ror
    0x66: 'ror',
    0x76: 'ror',
    0x6e: 'ror',
    0x7e: 'ror',
    0x6a: 'ror',
# ------------ move commands ------------
#lda', {
    0xa9: 'lda',
    0xa5: 'lda',
    0xb5: 'lda',
    0xa1: 'lda',
    0xb1: 'lda',
    0xad: 'lda',
    0xbd: 'lda',
    0xb9: 'lda',
#sta
    0x85: 'sta',
    0x95: 'sta',
    0x8d: 'sta',
    0x9d: 'sta',
    0x99: 'sta',
    0x81: 'sta',
    0x91: 'sta',
#ldx
    0xa2: 'ldx',
    0xa6: 'ldx',
    0xb6: 'ldx',
    0xae: 'ldx',
    0xbe: 'ldx',
#stx
    0x86: 'stx',
    0x96: 'stx',
    0x8e: 'stx',
#ldy
    0xa0: 'ldy',
    0xa4: 'ldy',
    0xb4: 'ldy',
    0xac: 'ldy',
    0xbc: 'ldy',
#sty
    0x84: 'sty',
    0x94: 'sty',
    0x8c: 'sty',
#tax
    0xaa: 'tax',
#txa
    0x8a: 'txa',
#tay
    0xa8: 'tay',
#tya
    0x98: 'tya',
#tsx
    0xba: 'tsx',
#txs
    0x9a: 'txs',
#pla
    0x68: 'pla',
#pha
    0x48: 'pha',
#plp
    0x28: 'plp',
#php
    0x08: 'php',
# ------------ jump/flag commands ------------
#bpl
    0x10: 'bpl',
#bmi
    0x30: 'bmi',
#bvc
    0x50: 'bvc',
#bvs
    0x70: 'bvs',
#bcc
    0x90: 'bcc',
#bcs
    0xb0: 'bcs',
#bne
    0xd0: 'bne',
#beq
    0xf0: 'beq',
#brk
    0x00: 'brk',
#rti
    0x40: 'rti',
#jsr
    0x20: 'jsr',
#rts
    0x60: 'rts',
#jmp
    0x4c: 'jmp',
    0x6c: 'jmp',
#bit
    0x24: 'bit',
    0x2c: 'bit',
#clc
    0x18: 'clc',
#sec
    0x38: 'sec',
#cld
    0xd8: 'cld',
#sed
    0xf8: 'sed',
#cli
    0x58: 'cli',
#sei
    0x78: 'sei',
#clv
    0xb8: 'clv',
#nop
    0xea: 'nop',
}
# ------------------------------------------------
# -----------------  cycle time  -----------------
# ------------------------------------------------

# TODO


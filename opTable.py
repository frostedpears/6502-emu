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
byteLength = {
    m.NON: 1,  # 'none'         
    m.IMP: 1,  # 'implied'      - 
    m.IMM: 2,  # 'immediate'    - #$44
    m.ZP:  2,  # 'zeropage'     - $44
    m.ZPX: 2,  # 'zeropage,x'   - $44,X
    m.ZPY: 2,  # 'zeropage,y'   - $44,Y
    m.IZX: 2,  # '(indirect,x)' - ($44,X)
    m.IZY: 2,  # '(indirect),y' - ($44),Y
    m.ABS: 3,  # 'absolute'     - $4400
    m.ABX: 3,  # 'absolute,x'   - $4400,X
    m.ABY: 3,  # 'absolute,y'   - $4400,Y
    m.IND: 3,  # 'indirect'     - ($4400)
    m.REL: 2,  # 'relative'     - $44
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
# --------------  modes by opcode  ---------------
# ------------------------------------------------

# ------------ logical and arithmetic commands ------------

modes = {
#ora'
    0x09: m.IMM,
    0x05: m.ZP, 
    0x15: m.ZPX, 
    0x01: m.IZX, 
    0x11: m.IZY, 
    0x0d: m.ABS, 
    0x1d: m.ABX, 
    0x19: m.ABY, 
#and'
    0x29: m.IMM, 
    0x25: m.ZP, 
    0x35: m.ZPX, 
    0x21: m.IZX, 
    0x31: m.IZY, 
    0x2d: m.ABS, 
    0x3d: m.ABX, 
    0x39: m.ABY, 
#eor
    0x49: m.IMM, 
    0x45: m.ZP, 
    0x55: m.ZPX, 
    0x41: m.IZX, 
    0x51: m.IZY, 
    0x4d: m.ABS, 
    0x5d: m.ABX, 
    0x59: m.ABY, 
#adc
    0x69: m.IMM, 
    0x65: m.ZP, 
    0x75: m.ZPX, 
    0x61: m.IZX, 
    0x71: m.IZY, 
    0x6d: m.ABS, 
    0x7d: m.ABX, 
    0x79: m.ABY, 
#sbc
    0xe9: m.IMM, 
    0xe5: m.ZP, 
    0xf5: m.ZPX, 
    0xed: m.ABS,
    0xfd: m.ABX, 
    0xf9: m.ABY, 
    0xe1: m.IZX, 
    0xf1: m.IZY,
#cmp
    0xc9: m.IMM, 
    0xc5: m.ZP, 
    0xd5: m.ZPX, 
    0xc1: m.IZX,
    0xd1: m.IZY, 
    0xcd: m.ABS, 
    0xdd: m.ABX, 
    0xd9: m.ABY, 
#cpx
    0xe0: m.IMM,
    0xe4: m.ZP, 
    0xec: m.ABS, 
#cpy
    0xc0: m.IMM, 
    0xc4: m.ZP, 
    0xcc: m.ABS, 
#dec
    0xc6: m.ZP, 
    0xd6: m.ZPX, 
    0xce: m.ABS, 
    0xde: m.ABX, 
#dex
    0xca: m.IMP, 
#dey
    0x88: m.IMP, 
#inc
    0xe6: m.ZP, 
    0xf6: m.ZPX, 
    0xee: m.ABS, 
    0xfe: m.ABX, 
#inx
    0xe8: m.IMP, 
#iny
    0xc8: m.IMP, 
#asl
    0x0a: m.IMP, 
    0x06: m.ZP, 
    0x16: m.ZPX, 
    0x0e: m.ABS, 
    0x1e: m.ABX, 
#rol
    0x26: m.ZP, 
    0x36: m.ZPX, 
    0x2e: m.ABS, 
    0x3e: m.ABX, 
    0x2a: m.IMP, 
#lsr
    0x4a: m.IMP, 
    0x46: m.ZP, 
    0x56: m.ZPX, 
    0x4e: m.ABS, 
    0x5e: m.ABX, 
#ror
    0x66: m.ZP, 
    0x76: m.ZPX, 
    0x6e: m.ABS, 
    0x7e: m.ABX, 
    0x6a: m.IMP, 
# ------------ move commands ------------
#lda', {
    0xa9: m.IMM, 
    0xa5: m.ZP, 
    0xb5: m.ZPX, 
    0xa1: m.IZX, 
    0xb1: m.IZY, 
    0xad: m.ABS, 
    0xbd: m.ABX, 
    0xb9: m.ABY, 
#sta
    0x85: m.ZP, 
    0x95: m.ZPX, 
    0x8d: m.ABS, 
    0x9d: m.ABX, 
    0x99: m.ABY, 
    0x81: m.IZX, 
    0x91: m.IZY, 
#ldx
    0xa2: m.IMM, 
    0xa6: m.ZP, 
    0xb6: m.ZPY, 
    0xae: m.ABS, 
    0xbe: m.ABY, 
#stx
    0x86: m.ZP, 
    0x96: m.ZPY, 
    0x8e: m.ABS, 
#ldy
    0xa0: m.IMM, 
    0xa4: m.ZP, 
    0xb4: m.ZPX, 
    0xac: m.ABS, 
    0xbc: m.ABX, 
#sty
    0x84: m.ZP, 
    0x94: m.ZPX, 
    0x8c: m.ABS, 
#tax
    0xaa: m.IMP, 
#txa
    0x8a: m.IMP,
#tay
    0xa8: m.IMP, 
#tya
    0x98: m.IMP, 
#tsx
    0xba: m.IMP, 
#txs
    0x9a: m.IMP, 
#pla
    0x68: m.IMP, 
#pha
    0x48: m.IMP, 
#plp
    0x28: m.IMP, 
#php
    0x08: m.IMP, 
# ------------ jump/flag commands ------------
#bpl
    0x10: m.REL, 
#bmi
    0x30: m.REL, 
#bvc
    0x50: m.REL, 
#bvs
    0x70: m.REL, 
#bcc
    0x90: m.REL, 
#bcs
    0xb0: m.REL, 
#bne
    0xd0: m.REL, 
#beq
    0xf0: m.REL, 
#brk
    0x00: m.IMP, 
#rti
    0x40: m.IMP, 
#jsr
    0x20: m.ABS, 
#rts
    0x60: m.IMP, 
#jmp
    0x4c: m.ABS, 
    0x6c: m.IND, 
#bit
    0x24: m.ZP, 
    0x2c: m.ABS, 
#clc
    0x18: m.IMP, 
#sec
    0x38: m.IMP, 
#cld
    0xd8: m.IMP, 
#sed
    0xf8: m.IMP, 
#cli
    0x58: m.IMP, 
#sei
    0x78: m.IMP, 
#clv
    0xb8: m.IMP, 
#nop
    0xea: m.IMP, 
}
# ------------------------------------------------
# -----------------  cycle time  -----------------
# ------------------------------------------------

# TODO
import re

from numpy import byte
import emu6502 as emu

def read_file(file_name):
    file_str = ''
    try:
        file = open(file_name, 'r')
        file_str = file.read()
        file.close()
    except Exception as e:
        print(e)
    return file_str

def save_binary(file_name, byte_list):
    try:
        file = open(file_name, 'w+b')
        bin = bytearray(byte_list)
        file.write(bin)
        file.close()
    except Exception as e:
        print(e)
    return

def hex_file_to_byte_list(file_name):
    file_str = read_file(file_name)
    return hex_to_byte_list(file_str)

def asm_file_to_byte_list(file_name):
    file_str = read_file(file_name)
    return asm_to_byte_list(file_str)

def hex_to_byte_list(hex_string):
    byte_list = []

    # remove anything after semicolon
    rx_comment = ';.*\n'
    comment_match = re.search(rx_comment, hex_string)
    if comment_match:
        hex_string = hex_string.replace(comment_match.group(), '')
    # strip whitespace
    hex_string = "".join(hex_string.split())

    for i in range(0, len(hex_string), 2):
        byte = int(f"{hex_string[i]}{hex_string[i+1]}", 16)
        byte_list.append(byte)

    return byte_list

def byte_list_to_hex_str(byte_list):
    return " ".join([f"{byte:02x}" for byte in byte_list])

def asm_to_byte_list(asm_string):
    """convert a string containing asm code into a list of bytes,
    which the emulator can use.
    """  
    byte_list = []
    asm_string_lines = re.split('\n', asm_string)
    for line in asm_string_lines:
        bytes = asm_to_opcode(line)
        for b in bytes:
            byte_list.append(b)
    return byte_list

def asm_to_opcode(string):
    """Convert a single line of asm code into an opcode byte."""
    instruction, mode, low_byte, high_byte = None, None, None, None

    # remove anything after semicolon
    rx_comment = ';.*'
    comment_match = re.search(rx_comment, string)
    if comment_match:
        string = string.replace(comment_match.group(), '')

    # convert to lowercase and strip whitespace
    string = string.lower().strip()

    # 3 letter instruction
    rx_instruction = '[a-z]{3}'
    instruction_match = re.match(rx_instruction, string)
    if not instruction_match:
        return get_opcode(instruction, mode, low_byte, high_byte)
    instruction = instruction_match.group()

    # everything after instruction
    rx_args = '(?<=.{4}).*'
    args_match = re.search(rx_args, string)
    if not args_match:
        mode = 'imp'
        return get_opcode(instruction, mode, low_byte, high_byte)
    args_string = args_match.group().replace(' ', '')

    # dollar sign, for hex
    rx_hex = '\$'
    hex_match = re.search(rx_hex, args_string)
    if hex_match:
        # TODO: consider decimal support
        pass

    # 1 bytes, or 2?
    rx_double = '\w{4}'
    double_match = re.search(rx_double, args_string)
    if double_match:
        low_byte = int(double_match.group()[2:4], 16)
        high_byte = int(double_match.group()[0:2], 16)
    else:
        rx_single = '\w{2}'
        single_match = re.search(rx_single, args_string)
        if single_match:
            low_byte = int(single_match.group(), 16)

    # characters after paren/comma, for indexed
    rx_indexed = '\)?,.+'
    indexed_match = re.search(rx_indexed, args_string)
    if indexed_match:
        indexed_string = indexed_match.group()
        if indexed_string.startswith('\)'):
            mode = 'izy'
        elif indexed_string.endswith('\)'):
            mode = 'izx'
        elif indexed_string.__contains__('x'):
            if high_byte is not None:
                mode = 'abx'
            else:
                mode = 'zpx'
        elif indexed_string.__contains__('y'):
            if high_byte is not None:
                mode = 'aby'
            else:
                mode = 'zpy'
    # 2 bytes
    elif high_byte is not None:
        if args_string.endswith(')'):
            mode = 'ind'
        else:
            mode = 'abs'
    elif low_byte is not None:
        if instruction in relative_codes:
            mode = 'rel'
        else:
            mode = 'zp'

    # A for implied/accumulator
    rx_a = 'a'
    a_match = re.match(rx_a, args_string)
    if a_match:
        mode = 'imp'
        return get_opcode(instruction, mode, low_byte, high_byte)

    # pound sign, for immediate
    rx_imm = '#'
    imm_string = re.search(rx_imm, args_string)
    if imm_string:
        mode = 'imm'

    return get_opcode(instruction, mode, low_byte, high_byte)

def get_opcode(instruction, mode, low_byte, high_byte):
    byte_list = []
    if (instruction is not None and mode is not None):
        try:
            for k in op_table.keys():
                if (op_table[k]['name'] == instruction and 
                        op_table[k]['mode'] == mode):
                    opcode = k
                    byte_list.append(opcode)
        except Exception as e:
            print(f"{e} at get_opcode")
        if low_byte is not None:
            byte_list.append(low_byte)
            if high_byte is not None:
                byte_list.append(high_byte)
    return byte_list

"""to distingiush from zeropage"""
relative_codes = [
    'bpl', 'bmi', 'bvc', 'bvs', 'bcc', 'bcs', 'bne', 'beq'
]

"""opcode: {(name, mode), func, length}"""
op_table = {
    0x09: {'name': 'ora', 'mode': 'imm', 'len': 2},
    0x05: {'name': 'ora', 'mode': 'zp', 'len': 2},
    0x15: {'name': 'ora', 'mode': 'zpx', 'len': 2},
    0x01: {'name': 'ora', 'mode': 'izx', 'len': 2},
    0x11: {'name': 'ora', 'mode': 'izy', 'len': 2},
    0x0d: {'name': 'ora', 'mode': 'abs', 'len': 3},
    0x1d: {'name': 'ora', 'mode': 'abx', 'len': 3},
    0x19: {'name': 'ora', 'mode': 'aby', 'len': 3},
    0x29: {'name': 'and', 'mode': 'imm', 'len': 2},
    0x25: {'name': 'and', 'mode': 'zp', 'len': 2},
    0x35: {'name': 'and', 'mode': 'zpx', 'len': 2},
    0x21: {'name': 'and', 'mode': 'izx', 'len': 2},
    0x31: {'name': 'and', 'mode': 'izy', 'len': 2},
    0x2d: {'name': 'and', 'mode': 'abs', 'len': 3},
    0x3d: {'name': 'and', 'mode': 'abx', 'len': 3},
    0x39: {'name': 'and', 'mode': 'aby', 'len': 3},
    0x49: {'name': 'eor', 'mode': 'imm', 'len': 2},
    0x45: {'name': 'eor', 'mode': 'zp', 'len': 2},
    0x55: {'name': 'eor', 'mode': 'zpx', 'len': 2},
    0x41: {'name': 'eor', 'mode': 'izx', 'len': 2},
    0x51: {'name': 'eor', 'mode': 'izy', 'len': 2},
    0x4d: {'name': 'eor', 'mode': 'abs', 'len': 3},
    0x5d: {'name': 'eor', 'mode': 'abx', 'len': 3},
    0x59: {'name': 'eor', 'mode': 'aby', 'len': 3},
    0x69: {'name': 'adc', 'mode': 'imm', 'len': 2},
    0x65: {'name': 'adc', 'mode': 'zp', 'len': 2},
    0x75: {'name': 'adc', 'mode': 'zpx', 'len': 2},
    0x61: {'name': 'adc', 'mode': 'izx', 'len': 2},
    0x71: {'name': 'adc', 'mode': 'izy', 'len': 2},
    0x6d: {'name': 'adc', 'mode': 'abs', 'len': 3},
    0x7d: {'name': 'adc', 'mode': 'abx', 'len': 3},
    0x79: {'name': 'adc', 'mode': 'aby', 'len': 3},
    0xe9: {'name': 'sbc', 'mode': 'imm', 'len': 2},
    0xe5: {'name': 'sbc', 'mode': 'zp', 'len': 2},
    0xf5: {'name': 'sbc', 'mode': 'zpx', 'len': 2},
    0xed: {'name': 'sbc', 'mode': 'abs', 'len': 3},
    0xfd: {'name': 'sbc', 'mode': 'abx', 'len': 3},
    0xf9: {'name': 'sbc', 'mode': 'aby', 'len': 3},
    0xe1: {'name': 'sbc', 'mode': 'izx', 'len': 2},
    0xf1: {'name': 'sbc', 'mode': 'izy', 'len': 2},
    0xc9: {'name': 'cmp', 'mode': 'imm', 'len': 2},
    0xc5: {'name': 'cmp', 'mode': 'zp', 'len': 2},
    0xd5: {'name': 'cmp', 'mode': 'zpx', 'len': 2},
    0xc1: {'name': 'cmp', 'mode': 'izx', 'len': 2},
    0xd1: {'name': 'cmp', 'mode': 'izy', 'len': 2},
    0xcd: {'name': 'cmp', 'mode': 'abs', 'len': 3},
    0xdd: {'name': 'cmp', 'mode': 'abx', 'len': 3},
    0xd9: {'name': 'cmp', 'mode': 'aby', 'len': 3},
    0xe0: {'name': 'cpx', 'mode': 'imm', 'len': 2},
    0xe4: {'name': 'cpx', 'mode': 'zp', 'len': 2},
    0xec: {'name': 'cpx', 'mode': 'abs', 'len': 3},
    0xc0: {'name': 'cpy', 'mode': 'imm', 'len': 2},
    0xc4: {'name': 'cpy', 'mode': 'zp', 'len': 2},
    0xcc: {'name': 'cpy', 'mode': 'abs', 'len': 3},
    0xc6: {'name': 'dec', 'mode': 'zp', 'len': 2},
    0xd6: {'name': 'dec', 'mode': 'zpx', 'len': 2},
    0xce: {'name': 'dec', 'mode': 'abs', 'len': 3},
    0xde: {'name': 'dec', 'mode': 'abx', 'len': 3},
    0xca: {'name': 'dex', 'mode': 'imp', 'len': 1},
    0x88: {'name': 'dey', 'mode': 'imp', 'len': 1},
    0xe6: {'name': 'inc', 'mode': 'zp', 'len': 2},
    0xf6: {'name': 'inc', 'mode': 'zpx', 'len': 2},
    0xee: {'name': 'inc', 'mode': 'abs', 'len': 3},
    0xfe: {'name': 'inc', 'mode': 'abx', 'len': 3},
    0xe8: {'name': 'inx', 'mode': 'imp', 'len': 1},
    0xc8: {'name': 'iny', 'mode': 'imp', 'len': 1},
    0x0a: {'name': 'asl', 'mode': 'imp', 'len': 1},
    0x06: {'name': 'asl', 'mode': 'zp', 'len': 2},
    0x16: {'name': 'asl', 'mode': 'zpx', 'len': 2},
    0x0e: {'name': 'asl', 'mode': 'abs', 'len': 3},
    0x1e: {'name': 'asl', 'mode': 'abx', 'len': 3},
    0x26: {'name': 'rol', 'mode': 'zp', 'len': 2},
    0x36: {'name': 'rol', 'mode': 'zpx', 'len': 2},
    0x2e: {'name': 'rol', 'mode': 'abs', 'len': 3},
    0x3e: {'name': 'rol', 'mode': 'abx', 'len': 3},
    0x2a: {'name': 'rol', 'mode': 'imp', 'len': 1},
    0x4a: {'name': 'lsr', 'mode': 'imp', 'len': 1},
    0x46: {'name': 'lsr', 'mode': 'zp', 'len': 2},
    0x56: {'name': 'lsr', 'mode': 'zpx', 'len': 2},
    0x4e: {'name': 'lsr', 'mode': 'abs', 'len': 3},
    0x5e: {'name': 'lsr', 'mode': 'abx', 'len': 3},
    0x66: {'name': 'ror', 'mode': 'zp', 'len': 2},
    0x76: {'name': 'ror', 'mode': 'zpx', 'len': 2},
    0x6e: {'name': 'ror', 'mode': 'abs', 'len': 3},
    0x7e: {'name': 'ror', 'mode': 'abx', 'len': 3},
    0x6a: {'name': 'ror', 'mode': 'imp', 'len': 1},
    0xa9: {'name': 'lda', 'mode': 'imm', 'len': 2},
    0xa5: {'name': 'lda', 'mode': 'zp', 'len': 2},
    0xb5: {'name': 'lda', 'mode': 'zpx', 'len': 2},
    0xa1: {'name': 'lda', 'mode': 'izx', 'len': 2},
    0xb1: {'name': 'lda', 'mode': 'izy', 'len': 2},
    0xad: {'name': 'lda', 'mode': 'abs', 'len': 3},
    0xbd: {'name': 'lda', 'mode': 'abx', 'len': 3},
    0xb9: {'name': 'lda', 'mode': 'aby', 'len': 3},
    0x85: {'name': 'sta', 'mode': 'zp', 'len': 2},
    0x95: {'name': 'sta', 'mode': 'zpx', 'len': 2},
    0x8d: {'name': 'sta', 'mode': 'abs', 'len': 3},
    0x9d: {'name': 'sta', 'mode': 'abx', 'len': 3},
    0x99: {'name': 'sta', 'mode': 'aby', 'len': 3},
    0x81: {'name': 'sta', 'mode': 'izx', 'len': 2},
    0x91: {'name': 'sta', 'mode': 'izy', 'len': 2},
    0xa2: {'name': 'ldx', 'mode': 'imm', 'len': 2},
    0xa6: {'name': 'ldx', 'mode': 'zp', 'len': 2},
    0xb6: {'name': 'ldx', 'mode': 'zpy', 'len': 2},
    0xae: {'name': 'ldx', 'mode': 'abs', 'len': 3},
    0xbe: {'name': 'ldx', 'mode': 'aby', 'len': 3},
    0x86: {'name': 'stx', 'mode': 'zp', 'len': 2},
    0x96: {'name': 'stx', 'mode': 'zpy', 'len': 2},
    0x8e: {'name': 'stx', 'mode': 'abs', 'len': 3},
    0xa0: {'name': 'ldy', 'mode': 'imm', 'len': 2},
    0xa4: {'name': 'ldy', 'mode': 'zp', 'len': 2},
    0xb4: {'name': 'ldy', 'mode': 'zpx', 'len': 2},
    0xac: {'name': 'ldy', 'mode': 'abs', 'len': 3},
    0xbc: {'name': 'ldy', 'mode': 'abx', 'len': 3},
    0x84: {'name': 'sty', 'mode': 'zp', 'len': 2},
    0x94: {'name': 'sty', 'mode': 'zpx', 'len': 2},
    0x8c: {'name': 'sty', 'mode': 'abs', 'len': 3},
    0xaa: {'name': 'tax', 'mode': 'imp', 'len': 1},
    0x8a: {'name': 'txa', 'mode': 'imp', 'len': 1},
    0xa8: {'name': 'tay', 'mode': 'imp', 'len': 1},
    0x98: {'name': 'tya', 'mode': 'imp', 'len': 1},
    0xba: {'name': 'tsx', 'mode': 'imp', 'len': 1},
    0x9a: {'name': 'txs', 'mode': 'imp', 'len': 1},
    0x68: {'name': 'pla', 'mode': 'imp', 'len': 1},
    0x48: {'name': 'pha', 'mode': 'imp', 'len': 1},
    0x28: {'name': 'plp', 'mode': 'imp', 'len': 1},
    0x08: {'name': 'php', 'mode': 'imp', 'len': 1},
    0x10: {'name': 'bpl', 'mode': 'rel', 'len': 2},
    0x30: {'name': 'bmi', 'mode': 'rel', 'len': 2},
    0x50: {'name': 'bvc', 'mode': 'rel', 'len': 2},
    0x70: {'name': 'bvs', 'mode': 'rel', 'len': 2},
    0x90: {'name': 'bcc', 'mode': 'rel', 'len': 2},
    0xb0: {'name': 'bcs', 'mode': 'rel', 'len': 2},
    0xd0: {'name': 'bne', 'mode': 'rel', 'len': 2},
    0xf0: {'name': 'beq', 'mode': 'rel', 'len': 2},
    0x00: {'name': 'brk', 'mode': 'imp', 'len': 1},
    0x40: {'name': 'rti', 'mode': 'imp', 'len': 1},
    0x20: {'name': 'jsr', 'mode': 'abs', 'len': 3},
    0x60: {'name': 'rts', 'mode': 'imp', 'len': 1},
    0x4c: {'name': 'jmp', 'mode': 'abs', 'len': 3},
    0x6c: {'name': 'jmp', 'mode': 'ind', 'len': 3},
    0x24: {'name': 'bit', 'mode': 'zp', 'len': 2},
    0x2c: {'name': 'bit', 'mode': 'abs', 'len': 3},
    0x18: {'name': 'clc', 'mode': 'imp', 'len': 1},
    0x38: {'name': 'sec', 'mode': 'imp', 'len': 1},
    0xd8: {'name': 'cld', 'mode': 'imp', 'len': 1},
    0xf8: {'name': 'sed', 'mode': 'imp', 'len': 1},
    0x58: {'name': 'cli', 'mode': 'imp', 'len': 1},
    0x78: {'name': 'sei', 'mode': 'imp', 'len': 1},
    0xb8: {'name': 'clv', 'mode': 'imp', 'len': 1},
    0xea: {'name': 'nop', 'mode': 'imp', 'len': 1},
}

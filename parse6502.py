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
            for k in emu.op_table.keys():
                if (emu.op_table[k]['name'] == instruction and 
                        emu.op_table[k]['mode'] == mode):
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
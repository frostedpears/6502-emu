import emu6502 as emu

class monitor():
    def subscribe(self, mem_map):
        mem_map.register(self)
        pass

    def update(self, message):
        print(message)

    # ------------ print / format ------------
    def value_changed(self, mem_map, address):
        if (address > 0x30 and address < 0x35):
            print_range(mem_map, 0x31, 0x35)
        return

    def print_step(self, mem_map, step):
        print(self.term.home + self.term.clear, end='')
        print('step: ' + str(step))
        print_range(mem_map, 0x31, 0x35)
        print_registers(mem_map)
        print_flags(mem_map)

# ------------ print / format ------------
def print_range(mem_map, start_address, end_address):
    print('{:04x}'.format(start_address), end=': ')
    column = 0
    row = 0
    for address in range(start_address, end_address):
        print('{:02x}'.format(emu.get_byte(mem_map, address)), end=' ')
        column += 1
        if column > 15:
            column = 0
            row += 1
            print()
            print('{:04x}'.format(start_address + (row * 16)), end=': ')

    print()
    return

def print_registers(mem_map):
    print('AXY', end=' ')
    print('{:02X}'.format(mem_map.a), end=' ')
    print('{:02X}'.format(mem_map.x), end=' ')
    print('{:02X}'.format(mem_map.y), end=' ')
    print()
    return

def print_flags(mem_map):
    flags_string = '{:08b}'.format(mem_map.sr)
    print('N V U B D I Z C')
    print(' '.join(flags_string))
    return

def print_byte_list(bytes):
    for b in bytes:
        print('{:02X}'.format(b), end=' ')
    print()
    return

def print_error(e):
    print(e)
    return

def print_not_implemented(opcode, low_byte = None, high_byte = None):
    print('not implemented:', end=' ')
    print_instruction(opcode, low_byte, high_byte)
    return

def print_instruction(opcode, low_byte = None, high_byte = None):
    instruction = emu.op_table[opcode]
    print(instruction, end=' ')
    if (low_byte):
        print('${:02x}'.format(low_byte), end='')
    if (high_byte):
        print('{:02x}'.format(high_byte), end='')
    print()
    return

# TODO add logic to create proper syntax
def get_asm_line(mode, opcode, arg8, arg16):
    asm_line = ''
    if (opcode):
        asm_line = asm_line + str(opcode).upper() + ' '
    if (mode == 'imm'):
        asm_line = asm_line + '#'
    if (mode != 'imp'):
        asm_line = asm_line + '$'
    if (arg8):
        asm_line = asm_line + '{:02x}'.format(arg8)
    if (arg16):
        asm_line = asm_line + '{:02x}'.format(arg16)
    return asm_line
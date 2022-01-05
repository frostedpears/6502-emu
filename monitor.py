from opTable import m

# ------------ print / format ------------
def printRange(emu, startAddress, endAddress):
    print('{:02X}'.format(startAddress), end=': ')
    for address in range(startAddress, endAddress):
        print('{:02X}'.format(emu.memory[address]), end=' ')
    print()
    return

def printRegisters(emu):
    print('AXY', end=' ')
    print('{:02X}'.format(emu.a), end=' ')
    print('{:02X}'.format(emu.x), end=' ')
    print('{:02X}'.format(emu.y), end=' ')
    print()
    return

def printFlags(emu):
    flagsString = '{:08b}'.format(emu.sr)
    print('N V U B D I Z C')
    print(' '.join(flagsString))
    return

def printByteList(bytes):
    for b in bytes:
        print('{:02X}'.format(b), end=' ')
    print()
    return

# TODO add logic to create proper syntax
def getAsmLine(emu, mode, opcode, arg8, arg16):
    asmLine = ''
    if (opcode):
        asmLine = asmLine + str(opcode).upper() + ' '
    if (mode == m.IMM):
        asmLine = asmLine + '#'
    if (mode != m.IMP):
        asmLine = asmLine + '$'
    if (arg8):
        asmLine = asmLine + '{:02X}'.format(arg8)
    if (arg16):
        asmLine = asmLine + '{:02X}'.format(arg16)
    return asmLine
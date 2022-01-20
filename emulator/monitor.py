import emulator.opTable as ot
from emulator.opTable import MODE
from blessed import Terminal

class monitor():
    def __init__(self):
        self.term = Terminal()

    # ------------ print / format ------------
    def valueChanged(self, emu, address):
        if (address > 0x30 and address < 0x35):
            printRange(emu, 0x31, 0x35)
        return

    def printStep(self, emu, step):
        print(self.term.home + self.term.clear, end='')
        print('step: ' + str(step))
        printRange(emu, 0x31, 0x35)
        printRegisters(emu)
        printFlags(emu)
        return

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

def printError(e):
    print(e)
    return

def printNotImplemented(opcode, lowByte = None, highByte = None):
    print('not implemented:', end=' ')
    printInstruction(opcode, lowByte, highByte)
    return

def printInstruction(opcode, lowByte = None, highByte = None):
    instuction = ot.instructions[opcode]
    print(instuction, end=' ')
    if (lowByte):
        print('${:02x}'.format(lowByte), end='')
    if (highByte):
        print('{:02x}'.format(highByte), end='')
    print()
    return

# TODO add logic to create proper syntax
def getAsmLine(emu, mode, opcode, arg8, arg16):
    asmLine = ''
    if (opcode):
        asmLine = asmLine + str(opcode).upper() + ' '
    if (mode == MODE.IMM):
        asmLine = asmLine + '#'
    if (mode != MODE.IMP):
        asmLine = asmLine + '$'
    if (arg8):
        asmLine = asmLine + '{:02x}'.format(arg8)
    if (arg16):
        asmLine = asmLine + '{:02x}'.format(arg16)
    return asmLine
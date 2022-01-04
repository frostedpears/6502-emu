import interpreter as it
from interpreter import m
import numpy as np
import re

class Flags(object):
    # processor flags
    NEGATIVE = 128
    OVERFLOW = 64
    UNUSED = 32
    BREAK = 16
    DECIMAL = 8
    INTERRUPT = 4
    ZERO = 2
    CARRY = 1

class emu6502():
    def __init__(self):
        # settings
        self.verbose = False

        # registers
        self.a = np.uint8(0x00) # accumulator
        self.x = np.uint8(0x00) # x register
        self.y = np.uint8(0x00) # y register
        self.cc = np.uint8(0x00) # condition code register

        self.pc = np.uint16(0x2000) # program counter
        self.sp = np.uint8(0xFF) # stack pointer

        self.memory = np.zeros(0x4000, dtype=np.uint8)

# ------------------------ functions ------------------------
    def run(self, string):
        stringLines = re.split('\n', string)
        for line in stringLines:
            if (line.startswith(';') or len(line) == 0):
                continue
            mode, opcode, arg8, arg16 = it.parseLine(line)
            if (self.verbose):
                print (opcode + ' ' + str(mode) + ' ' + '{:02X}'.format(arg8) + ' ' + '{:02X}'.format(arg16))
            try:
                self.runLine(mode, opcode, arg8, arg16,)
            except:
                pass
        return
    
    def runLine(self, mode, opcode, arg8, arg16):
        if (opcode == 'lda' and mode == m.ZP):
            hexByte = '{:02X}'.format(it.getByteCode(mode, opcode))
            eval('self.c' + hexByte + '(mode, opcode, arg8, arg16)')
        elif (opcode):
            code = eval('self.' + opcode.upper() + '(mode, opcode, arg8, arg16)')
            if (code == 1 and self.verbose == True):
                print('not run: ' + self.getAsmLine(mode, opcode, arg8, arg16))
        return
    
    # ------------ getters / setters ------------
    def getByte(self, addressLow, addressHigh = 0x00):
        address = addressLow + (addressHigh << 8)
        return np.uint8(self.memory[address])

    def setByte(self, value, addressLow, addressHigh = 0x00):
        address = addressLow + (addressHigh << 8)
        self.memory[address] = np.uint8(value)
        return
    
    def setRegister(self, register, value):
        if (register == 'a'):
            self.a = np.uint8(value)
        elif (register == 'x'):
            self.x = np.uint8(value)
        elif (register == 'y'):
            self.y = np.uint8(value)
        return

    def getFlag(self):
        return

    def setFlag(self):
        return

# ----------------------------------------------------------
# ------------------------ op codes ------------------------
# ----------------------------------------------------------

# ------------ Logical and arithmetic commands -------------
    def ORA(self, mode, opcode, arg8, arg16):
        return

    def AND(self, mode, opcode, arg8, arg16):
        return

    def EOR(self, mode, opcode, arg8, arg16):
        return

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ADC --- $69 $65 $75 --- $61 $71 $6D $7D $79 --- ---
    # Flags: N Z
    def ADC(self, mode, opcode, arg8, arg16):
        carry = 1 if (self.cc & Flags.CARRY == Flags.CARRY) else 0

        # get value based on mode
        value = np.uint8(0x00)
        if (mode == m.IMM):
            value = arg8
        elif (mode == m.ZP):
            value = self.getByte(arg8)
        else:
            return 1

        # add value to accumulator
        sum = int(value) + int(self.a) + int(carry)
        
        # set carry flag
        if (sum & 0x100):
            self.cc = self.cc | Flags.CARRY

        # store sum
        self.setRegister('a', sum)
        return 0

    def SBC(self, mode, opcode, arg8, arg16):
        return 1

    def CMP(self, mode, opcode, arg8, arg16):
        return 1

    def CPX(self, mode, opcode, arg8, arg16):
        return 1

    def CPY(self, mode, opcode, arg8, arg16):
        return 1

    def DEC(self, mode, opcode, arg8, arg16):
        return 1

    def DEX(self, mode, opcode, arg8, arg16):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # DEY $88 --- --- --- --- --- --- --- --- --- --- ---
    # Flags: N,Z
    def DEY(self, mode, opcode, arg8, arg16):
        value = self.y - 1
        self.setRegister('y', value)
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # INC --- --- $E6 $F6 --- --- --- $EE $FE --- --- ---
    # Flags: N,Z
    def INC(self, mode, opcode, arg8, arg16):
        if (mode == m.ZP):
            value = self.getByte(arg8)
            value = value + 1
            value = value & 0xFF
            self.setByte(value, arg8)
        return 0
    
    def INX(self, mode, opcode, arg8, arg16):
        return 1

    def INY(self, mode, opcode, arg8, arg16):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ASL $0A --- $06 $16 --- --- --- $0E $1E --- --- ---
    # Flags: N,Z,C
    def ASL(self, mode, opcode, arg8, arg16):
        if (mode == m.IMP):
            value = int(self.a)
            value = value << 1
            if (value > 0xFF):
                self.cc = self.cc | Flags.CARRY
            else:
                self.cc = self.cc & ~Flags.CARRY
            value = value & 0xFF
            self.setRegister('a', value)
        else:
            return 1
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ROL $2A --- $26 $36 --- --- --- $2E $3E --- --- ---
    # Flags: N,Z,C
    def ROL(self, mode, opcode, arg8, arg16):
        carry = 1 if (self.cc & Flags.CARRY == Flags.CARRY) else 0
        if (mode == m.IMP):
            value = int(self.a)
            value = value << 1
            value = value + carry
            if (value > 0xFF):
                self.cc = self.cc | Flags.CARRY
            else:
                self.cc = self.cc & ~Flags.CARRY
            value = value & 0xFF
            self.setRegister('a', value)
        else:
            return 1
        return 0

    def LSR(self, mode, opcode, arg8, arg16):
        return 1

    def ROR(self, mode, opcode, arg8, arg16):
        return 1

# --------------------- Move commands ----------------------

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # LDA --- $A9 $A5 $B5 --- $A1 $B1 $AD $BD $B9 --- ---
    # Flags: N,Z
    def LDA(self, mode, opcode, arg8, arg16):
        # get value based on mode
        value = np.uint8(0x00)
        if (mode == m.IMM):
            value = arg8
        elif (mode == m.ZP):
            value = self.getByte(arg8)
        else:
            return 1

        # store value
        self.setRegister('a', value)
        return 0

    # LDA - IMM
    def cA9(self, mode, opcode, arg8, arg16):
        value = arg8
        self.setRegister('a', value)
        return 0

    # LDA - ZP
    def cA5(self, mode, opcode, arg8, arg16):
        value = self.getByte(arg8)
        self.setRegister('a', value)
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # STA --- --- $85 $95 --- $81 $91 $8D $9D $99 --- ---
    # Flags: None
    def STA(self, mode, opcode, arg8, arg16):
        value = self.a

        # get address based on mode
        if (mode == m.ZP):
            address = arg8
        else:
            return 1

        # store value
        self.setByte(value, address)
        return 0

    def LDX(self, mode, opcode, arg8, arg16):
        return 1

    def STX(self, mode, opcode, arg8, arg16):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # LDY --- $A0 $A4 $B4 --- --- --- $AC $BC --- --- ---
    # Flags: N,Z
    def LDY(self, mode, opcode, arg8, arg16):
        # get value based on mode
        value = np.uint8(0x00)
        if (mode == m.IMM):
            value = arg8
        elif (mode == m.ZP):
            value = self.getByte(arg8)
        else:
            return 1

        # store value
        self.setRegister('y', value)
        return 0

    def STY(self, mode, opcode, arg8, arg16):
        return 1

    def TAX(self, mode, opcode, arg8, arg16):
        return 1

    def TXA(self, mode, opcode, arg8, arg16):
        return 1

    def TAY(self, mode, opcode, arg8, arg16):
        return 1

    def TYA(self, mode, opcode, arg8, arg16):
        return 1

    def TSX(self, mode, opcode, arg8, arg16):
        return 1

    def TXS(self, mode, opcode, arg8, arg16):
        return 1

    def PLA(self, mode, opcode, arg8, arg16):
        return 1

    def PHA(self, mode, opcode, arg8, arg16):
        return 1

    def PLP(self, mode, opcode, arg8, arg16):
        return 1

    def PHP(self, mode, opcode, arg8, arg16):
        return 1

# ------------------- Jump/Flag commands -------------------

    def BPL(self, mode, opcode, arg8, arg16):
        return 1

    def BMI(self, mode, opcode, arg8, arg16):
        return 1

    def BVC(self, mode, opcode, arg8, arg16):
        return 1

    def BVS(self, mode, opcode, arg8, arg16):
        return 1

    def BCC(self, mode, opcode, arg8, arg16):
        return 1

    def BCS(self, mode, opcode, arg8, arg16):
        return 1

    def BNE(self, mode, opcode, arg8, arg16):
        return 1

    def BEQ(self, mode, opcode, arg8, arg16):
        return 1

    def BRK(self, mode, opcode, arg8, arg16):
        return 1

    def RTI(self, mode, opcode, arg8, arg16):
        return 1

    def JSR(self, mode, opcode, arg8, arg16):
        return 1

    def RTS(self, mode, opcode, arg8, arg16):
        return 1

    def JMP(self, mode, opcode, arg8, arg16):
        return 1

    def BIT(self, mode, opcode, arg8, arg16):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # CLC $18 --- --- --- --- --- --- --- --- --- --- ---
    # Flags: C
    def CLC(self, mode, opcode, arg8, arg16):
        self.cc = self.cc & ~Flags.CARRY
        return 0

    def SEC(self, mode, opcode, arg8, arg16):
        return 1

    def CLD(self, mode, opcode, arg8, arg16):
        return 1

    def SED(self, mode, opcode, arg8, arg16):
        return 1

    def CLI(self, mode, opcode, arg8, arg16):
        return 1

    def SEI(self, mode, opcode, arg8, arg16):
        return 1

    def CLV(self, mode, opcode, arg8, arg16):
        return 1

    def NOP(self, mode, opcode, arg8, arg16):
        return 1


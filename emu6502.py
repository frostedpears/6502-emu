import interpreter as it
from interpreter import m
import numpy as np
import monitor as mon

class Flags(object):
    # processor flags
    NEG = 128 # NEGATIVE
    OVR = 64  # OVERFLOW
    UND = 32  # UNUSED
    BRK = 16  # BREAK
    DEC = 8   # DECIMAL
    INT = 4   # INTERRUPT
    ZER = 2   # ZERO
    CAR = 1   # CARRY

class emu6502():
    def __init__(self):
        # registers
        self.a = np.uint8(0x00)     # accumulator
        self.x = np.uint8(0x00)     # x register
        self.y = np.uint8(0x00)     # y register

        self.pc = np.uint16(0x2000) # program counter
        self.sr = np.uint8(0x00)    # status register (flags)
        self.sp = np.uint8(0xFF)    # stack pointer

        self.memory = np.zeros(0x4000, dtype=np.uint8)

# ------------------------ functions ------------------------
    def run(self, string):
        commands = it.parseAsm(string)
        mon.printByteList(commands)

        return
    
    def runLine(self, opcode, lowByte, highByte):
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
    def ORA(self, opcode, lowByte, highByte):
        return

    def AND(self, opcode, lowByte, highByte):
        return

    def EOR(self, opcode, lowByte, highByte):
        return

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ADC --- $69 $65 $75 --- $61 $71 $6D $7D $79 --- ---
    # Flags: N Z
    def ADC(self, opcode, lowByte, highByte):
        carry = self.sr & Flags.CAR == Flags.CAR

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
            self.sr = self.sr | Flags.CAR

        # store sum
        self.setRegister('a', sum)
        return 0

    def SBC(self, opcode, lowByte, highByte):
        return 1

    def CMP(self, opcode, lowByte, highByte):
        return 1

    def CPX(self, opcode, lowByte, highByte):
        return 1

    def CPY(self, opcode, lowByte, highByte):
        return 1

    def DEC(self, opcode, lowByte, highByte):
        return 1

    def DEX(self, opcode, lowByte, highByte):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # DEY $88 --- --- --- --- --- --- --- --- --- --- ---
    # Flags: N,Z
    def DEY(self, opcode, lowByte, highByte):
        value = self.y - 1
        self.setRegister('y', value)
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # INC --- --- $E6 $F6 --- --- --- $EE $FE --- --- ---
    # Flags: N,Z
    def INC(self, opcode, lowByte, highByte):
        if (mode == m.ZP):
            value = self.getByte(arg8)
            value = value + 1
            value = value & 0xFF
            self.setByte(value, arg8)
        return 0
    
    def INX(self, opcode, lowByte, highByte):
        return 1

    def INY(self, opcode, lowByte, highByte):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ASL $0A --- $06 $16 --- --- --- $0E $1E --- --- ---
    # Flags: N,Z,C
    def ASL(self, opcode, lowByte, highByte):
        if (mode == m.IMP):
            value = int(self.a)
            value = value << 1
            if (value > 0xFF):
                self.sr = self.sr | Flags.CAR
            else:
                self.sr = self.sr & ~Flags.CAR
            value = value & 0xFF
            self.setRegister('a', value)
        else:
            return 1
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ROL $2A --- $26 $36 --- --- --- $2E $3E --- --- ---
    # Flags: N,Z,C
    def ROL(self, opcode, lowByte, highByte):
        carry = self.sr & Flags.CAR == Flags.CAR
        if (mode == m.IMP):
            value = int(self.a)
            value = value << 1
            value = value + carry
            if (value > 0xFF):
                self.sr = self.sr | Flags.CAR
            else:
                self.sr = self.sr & ~Flags.CAR
            value = value & 0xFF
            self.setRegister('a', value)
        else:
            return 1
        return 0

    def LSR(self, opcode, lowByte, highByte):
        return 1

    def ROR(self, opcode, lowByte, highByte):
        return 1

# --------------------- Move commands ----------------------

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # LDA --- $A9 $A5 $B5 --- $A1 $B1 $AD $BD $B9 --- ---
    # Flags: N,Z
    def LDA(self, opcode, lowByte, highByte):
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
    def cA9(self, opcode, lowByte, highByte):
        value = lowByte
        self.setRegister('a', value)
        return 0

    # LDA - ZP
    def cA5(self, opcode, lowByte, highByte):
        value = self.getByte(lowByte)
        self.setRegister('a', value)
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # STA --- --- $85 $95 --- $81 $91 $8D $9D $99 --- ---
    # Flags: None
    def STA(self, opcode, lowByte, highByte):
        value = self.a

        # get address based on mode
        if (mode == m.ZP):
            address = arg8
        else:
            return 1

        # store value
        self.setByte(value, address)
        return 0

    def LDX(self, opcode, lowByte, highByte):
        return 1

    def STX(self, opcode, lowByte, highByte):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # LDY --- $A0 $A4 $B4 --- --- --- $AC $BC --- --- ---
    # Flags: N,Z
    def LDY(self, opcode, lowByte, highByte):
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

    def STY(self, opcode, lowByte, highByte):
        return 1

    def TAX(self, opcode, lowByte, highByte):
        return 1

    def TXA(self, opcode, lowByte, highByte):
        return 1

    def TAY(self, opcode, lowByte, highByte):
        return 1

    def TYA(self, opcode, lowByte, highByte):
        return 1

    def TSX(self, opcode, lowByte, highByte):
        return 1

    def TXS(self, opcode, lowByte, highByte):
        return 1

    def PLA(self, opcode, lowByte, highByte):
        return 1

    def PHA(self, opcode, lowByte, highByte):
        return 1

    def PLP(self, opcode, lowByte, highByte):
        return 1

    def PHP(self, opcode, lowByte, highByte):
        return 1

# ------------------- Jump/Flag commands -------------------

    def BPL(self, opcode, lowByte, highByte):
        return 1

    def BMI(self, opcode, lowByte, highByte):
        return 1

    def BVC(self, opcode, lowByte, highByte):
        return 1

    def BVS(self, opcode, lowByte, highByte):
        return 1

    def BCC(self, opcode, lowByte, highByte):
        return 1

    def BCS(self, opcode, lowByte, highByte):
        return 1

    def BNE(self, opcode, lowByte, highByte):
        return 1

    def BEQ(self, opcode, lowByte, highByte):
        return 1

    def BRK(self, opcode, lowByte, highByte):
        return 1

    def RTI(self, opcode, lowByte, highByte):
        return 1

    def JSR(self, opcode, lowByte, highByte):
        return 1

    def RTS(self, opcode, lowByte, highByte):
        return 1

    def JMP(self, opcode, lowByte, highByte):
        return 1

    def BIT(self, opcode, lowByte, highByte):
        return 1

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # CLC $18 --- --- --- --- --- --- --- --- --- --- ---
    # Flags: C
    def CLC(self, opcode, lowByte, highByte):
        self.sr = self.sr & ~Flags.CAR
        return 0

    def SEC(self, opcode, lowByte, highByte):
        return 1

    def CLD(self, opcode, lowByte, highByte):
        return 1

    def SED(self, opcode, lowByte, highByte):
        return 1

    def CLI(self, opcode, lowByte, highByte):
        return 1

    def SEI(self, opcode, lowByte, highByte):
        return 1

    def CLV(self, opcode, lowByte, highByte):
        return 1

    def NOP(self, opcode, lowByte, highByte):
        return 1


import interpreter as it
from interpreter import m
import numpy as np
import monitor as mon
import opTable as ot

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

        self.memory = np.zeros(0xE000, dtype=np.uint8)

        self.keepRunning = True

# ------------------------ functions ------------------------
    def runAsm(self, string):
        commands = it.parseAsm(string)
        #mon.printByteList(commands)

        return

    def writeAsm(self, string, addressStart):
        commands = it.parseAsm(string)
        self.writeListToMemory(commands, addressStart)
        return
    
    def writeListToMemory(self, bytes, addressStart):
        if (addressStart + len(bytes) > len(self.memory)):
            print ('error: address ' + hex(addressStart) + '-' + 
                    hex(addressStart + len(bytes)) + ' out of range')
            return 1
        for index, value in enumerate(bytes):
            self.setByte(value, address = addressStart + index)
        return

    def runAt(self, address):
        self.pc = address
        self.runAtPc()
        return

    def runAtPc(self):
        while (self.keepRunning):
            opCode = self.getByte(self.pc)
            byteLength = ot.byteLength[ot.modes[opCode]]
            self.pc = self.pc + 1
            if (byteLength == 1):
                eval('self._' + '{:02x}'.format(opCode) + '()')
            elif (byteLength == 2):
                lowByte = self.getByte(self.pc)
                self.pc = self.pc + 1
                eval('self._' + '{:02x}'.format(opCode) + '(' + 'lowByte)')
            elif (byteLength == 3):
                lowByte = self.getByte(self.pc)
                self.pc = self.pc + 1
                highByte = self.getByte(self.pc)
                self.pc = self.pc + 1
                eval('self._' + '{:02x}'.format(opCode) + '(' + 'lowByte, highByte)')
        return

    # ------------ getters / setters ------------
    def getByteZP(self, addressLow, addressHigh = 0x00):
        address = addressLow + (addressHigh << 8)
        return self.getByte(address)

    def getByte(self, address):
        return np.uint8(self.memory[address])

    def setByteZP(self, value, addressLow, addressHigh = 0x00):
        address = addressLow + (addressHigh << 8)
        self.setByte(value, address)
        return

    def setByte(self, value, address):
        self.memory[address] = np.uint8(value)
        return
    
    def setA(self, value):
        self.a = np.uint8(value)
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

    # ---- adc ----
    def _69(self, lowByte): # adc imm
        carry = self.sr & Flags.CAR == Flags.CAR
        value = lowByte
        sum = int(value) + int(self.a) + int(carry)
        if (sum & 0x100):
            self.sr = self.sr | Flags.CAR
        self.setA(sum)
        return 0

    def _65(self, lowByte): # adc zp
        carry = self.sr & Flags.CAR == Flags.CAR
        value = self.getByte(lowByte)
        sum = int(value) + int(self.a) + int(carry)
        if (sum & 0x100):
            self.sr = self.sr | Flags.CAR
        self.setA(sum)
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

    # ---- lda ----
    def _a9(self, lowByte): # lda imm
        value = lowByte
        self.setA(value)
        return 0

    def _a5(self, lowByte): # lda zp
        value = self.getByte(lowByte)
        self.setA(value)
        return 0

    # ---- sta ----
    def _85(self, lowByte): # sta zp
        value = self.a
        self.setByteZP(value, lowByte)
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

    # ---- brk ----
    def _00(self): # brk imp
        self.keepRunning = False
        return 0

    def RTI(self, opcode, lowByte, highByte):
        return 1

    def JSR(self, opcode, lowByte, highByte):
        return 1

    def RTS(self, opcode, lowByte, highByte):
        return 1

    def JMP(self, lowByte, highByte):
        return 1

    # ---- jmp ----
    def _4c(self, lowByte, highByte): # jmp abs
        address = lowByte + (highByte << 8)
        self.pc = address
        return 0


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


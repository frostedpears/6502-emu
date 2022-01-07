import numpy as np
import emulator.interpreter as it
from emulator.interpreter import MODE
import emulator.opTable as ot
from emulator.opTable import FLAG
import emulator.monitor as mon

class emu6502():
    def __init__(self):
        # registers
        self.a = np.uint8(0x00)     # accumulator
        self.x = np.uint8(0x00)     # x register
        self.y = np.uint8(0x00)     # y register

        self.pc = np.uint16(0xc000) # program counter
        self.sr = np.uint8(0x00)    # status register (flags)
        self.sp = np.uint8(0xFF)    # stack pointer

        self.memory = np.zeros(0xffff, dtype=np.uint8)

        # should the pc increment before running the next instruction?
        # The pc should usually move before instructions,
        # but not before the first, or before jumps, etc
        # TODO find a more accurate way to replicate this logic
        self.incrementPc = False

# ------------------------ functions ------------------------
    # ---- assembly ----
    def runAsm(self, string):
        commands = it.parseAsm(string)
        #mon.printByteList(commands)

        return

    def writeAsm(self, string, addressStart):
        commands = it.parseAsm(string)
        self.writeListToMemory(commands, addressStart)
        return
    
    # ---- hex ----
    def writeListToMemory(self, bytes, addressStart):
        if (addressStart + len(bytes) > len(self.memory)):
            print ('error: address ' + hex(addressStart) + '-' + 
                    hex(addressStart + len(bytes)) + ' out of range')
            return 1
        for index, value in enumerate(bytes):
            address = addressStart + index
            lowbyte = address & 0xff
            highByte = (address & 0xff00) >> 8
            self.setByte(value, lowbyte, highByte)
        return

    # ---- run ----
    def movePcAndRun(self, address):
        self.pc = address
        self.run()
        return

    def run(self):
        while (self.keepRunning()):
            self.runInstruction()
        return
    
    def runInstruction(self):
        if (self.incrementPc):
            self.pc += 1
        else:
            self.incrementPc = True
        opCode = self.getByte(self.pc)
        byteLength = ot.byteLength[ot.modes[opCode]]
        status, lowByte, highByte = None, None, None
        if (byteLength == 1):
            try:
                status = eval('self._' + '{:02x}'.format(opCode) + '()')
            except Exception as e:
                mon.printError(e)
        elif (byteLength == 2):
            self.pc += 1
            lowByte = self.getByte(self.pc)
            try:
                status = eval('self._' + '{:02x}'.format(opCode) + '(' + 'lowByte)')
            except Exception as e:
                mon.printError(e)
        elif (byteLength == 3):
            self.pc += 1
            lowByte = self.getByte(self.pc)
            self.pc += 1
            highByte = self.getByte(self.pc)
            try:
                status = eval('self._' + '{:02x}'.format(opCode) + '(' + 'lowByte, highByte)')
            except Exception as e:
                mon.printError(e)
        if (status == 1):
            mon.printNotImplemented(opCode, lowByte, highByte)
        return 0
    
    def keepRunning(self):
        if (self.sr & FLAG.INT == FLAG.INT or 
            self.sr & FLAG.BRK == FLAG.BRK):
            return False
        return True

    # ------------ getters / setters ------------
    # ---- memory ----
    def getByte(self, lowByte, highByte = None):
        if (highByte == None):
            address = lowByte
        else:
            address = lowByte + (highByte << 8)
        return np.uint8(self.memory[address])

    def setByte(self, value, lowByte, highByte = None):
        if (highByte == None):
            address = lowByte
        else:
            address = lowByte + (highByte << 8)
        self.memory[address] = np.uint8(value)
        return

    # ---- stack ----
    def push(self, byte):
        self.setByte(byte, self.sp, 0x1)
        self.sp -= 1
        return 
    
    def pull(self):
        self.sp += 1
        byte = self.getByte(self.sp, 0x1)
        return byte
    
    # ---- registers ----
    def setA(self, value, updateFlags = False):
        self.a = np.uint8(value)
        if (updateFlags):
            self.updateFlagNegative(value)
            self.updateFlagZero(value)
        return

    def setX(self, value, updateFlags = False):
        self.x = np.uint8(value)
        if (updateFlags):
            self.updateFlagNegative(value)
            self.updateFlagZero(value)
        return

    def setY(self, value, updateFlags = False):
        self.y = np.uint8(value)
        if (updateFlags):
            self.updateFlagNegative(value)
            self.updateFlagZero(value)
        return
    
    # ---- flags ----
    def updateFlagZero(self, value):
        value = np.uint8(value)
        if (value == 0):
            self.sr = self.sr | FLAG.ZER
        else:
            self.sr = self.sr & ~FLAG.ZER
        return

    def updateFlagNegative(self, value):
        value = np.int8(value)
        if (value < 0):
            self.sr = self.sr | FLAG.NEG
        else:
            self.sr = self.sr & ~FLAG.NEG
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

    # ---- adc ---- NVZC
    def _69(self, lowByte): # adc imm NVZC
        carry = self.sr & FLAG.CAR == FLAG.CAR
        value = lowByte
        sum = int(value) + int(self.a) + int(carry)
        if (sum > 255):
            self.sr = self.sr | FLAG.CAR
        self.setA(sum)
        return 0

    def _65(self, lowByte): # adc zp NVZC
        carry = self.sr & FLAG.CAR == FLAG.CAR
        value = self.getByte(lowByte)
        sum = int(value) + int(self.a) + int(carry)
        if (sum > 255):
            self.sr = self.sr | FLAG.CAR
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

    def _ca(self): # dex imp NZ
        value = self.x - 1
        self.setX(value, True)
        return 0
    
    def _88(self): # dey imp NZ
        value = self.y - 1
        self.setY(value, True)
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # INC --- --- $E6 $F6 --- --- --- $EE $FE --- --- ---
    # Flags: N,Z
    def INC(self, opcode, lowByte, highByte):
        if (mode == MODE.ZP):
            value = self.getByte(arg8)
            value += 1
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
        if (mode == MODE.IMP):
            value = int(self.a)
            value = value << 1
            if (value > 0xFF):
                self.sr = self.sr | FLAG.CAR
            else:
                self.sr = self.sr & ~FLAG.CAR
            value = value & 0xFF
            self.setRegister('a', value)
        else:
            return 1
        return 0

    # Opc imp imm zp  zpx zpy izx izy abs abx aby ind rel
    # ROL $2A --- $26 $36 --- --- --- $2E $3E --- --- ---
    # Flags: N,Z,C
    def ROL(self, opcode, lowByte, highByte):
        carry = self.sr & FLAG.CAR == FLAG.CAR
        if (mode == MODE.IMP):
            value = int(self.a)
            value = value << 1
            value = value + carry
            if (value > 0xFF):
                self.sr = self.sr | FLAG.CAR
            else:
                self.sr = self.sr & ~FLAG.CAR
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
    def _a9(self, lowByte): # lda imm NZ
        value = lowByte
        self.setA(value)
        return 0

    def _a5(self, lowByte): # lda zp NZ
        value = self.getByte(lowByte)
        print(self.a)
        self.setA(value)
        return 0

    # ---- sta ----
    def _85(self, lowByte): # sta zp none
        value = self.a
        self.setByte(value, lowByte)
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
        if (mode == MODE.IMM):
            value = arg8
        elif (mode == MODE.ZP):
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

    def _d0(self, lowByte): # bne rel none
        zero = self.sr & FLAG.ZER == FLAG.ZER
        if (zero):
            self.pc += np.int8(lowByte)
        return 0

    def BEQ(self, opcode, lowByte, highByte):
        return 1

    # ---- brk ----
    def _00(self): # brk imp B=1 I=1
        self.sr = self.sr | FLAG.INT
        self.sr = self.sr | FLAG.BRK
        return 0

    def RTI(self, opcode, lowByte, highByte):
        return 1

    def _20(self, lowByte, highByte): # jsr abs none
        returnLowByte = int(self.pc & 0xFF)
        returnHighByte = int((self.pc & 0xFF00) >> 8)
        self.push(returnHighByte)
        self.push(returnLowByte)

        address = lowByte + (highByte << 8)
        self.pc = address
        self.incrementPc = False
        return 0

    def _60(self): # rts imp none
        lowByte = self.pull()
        highByte = self.pull()
        address = int(lowByte) + int(highByte << 8)
        self.pc = address
        return 0

    # ---- jmp ----
    def _4c(self, lowByte, highByte): # jmp abs none
        address = lowByte + (highByte << 8)
        self.pc = address
        self.incrementPc = False
        return 0

    # ---- bit ----
    def _24(self, lowByte): # bit zp NVZ
        return 1

    def _2c(self, lowByte, highByte): # bit abs NVZ
        return 1

    def _18(self): # clc imp c=0
        self.sr = self.sr & ~FLAG.CAR
        return 0
    
    def _38(self): # sec imp c=1
        self.sr = self.sr | FLAG.CAR
        return 0

    def _d8(self): # cld imp d=0
        self.sr = self.sr & ~FLAG.DEC
        return 0

    def _f8(self): # sed imp d=1
        self.sr = self.sr | FLAG.DEC
        return 0

    def _58(self): # cli imp i=0
        self.sr = self.sr & ~FLAG.INT
        return 0

    def _78(self): # sei imp i=1
        self.sr = self.sr | FLAG.INT
        return 0

    def _b8(self): # clv imp v=0
        self.sr = self.sr & ~FLAG.OVR
        return 0

    def _ea(self): # nop imp none
        return 0


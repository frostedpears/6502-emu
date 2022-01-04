import numpy as np
import re
import opTable as ot
from opTable import m

def parseAsm(string):
    commands = []
    return

def asmToByteCode(string):
    mode, opcode, arg8, arg16 = '', '', -1, -1

    # remove anything after semicolon
    rxComment = ';.*'
    commentMatch = re.search(rxComment, string)
    if (commentMatch):
        string = string.replace(commentMatch.group, '')

    # convert to lowercase and strip whitespace
    string = string.lower().strip()

    # 3 letter opcode
    rxOpcode = '[a-z]{3}' 
    opcodeMatch = re.match(rxOpcode, string)
    if (not opcodeMatch):
        return mode, opcode, arg8, arg16
    opcode = opcodeMatch.group()

    # everything after opcode
    rxArgs = '(?<=.{4}).*'
    argsMatch = re.search(rxArgs, string)
    if (not argsMatch):
        mode = m.IMP
        return mode, opcode, arg8, arg16
    argsString = argsMatch.group().replace(' ', '')

    # dollar sign, for hex
    rxHex = '\$'
    hexMatch = re.search(rxHex, argsString)
    if (hexMatch):
        pass # TODO: support decimal

    # 1 bytes, or 2?
    rxDouble = '\w{4}'
    doubleMatch = re.search(rxDouble, argsString)
    if (doubleMatch):
        arg8 = int(doubleMatch.group()[0:2], 16)
        arg16 = int(doubleMatch.group()[2:4], 16)
    else:
        rxSingle = '\w{2}'
        singleMatch = re.search(rxSingle, argsString)
        if (singleMatch):
            arg8 = int(singleMatch.group(), 16)

    # characters after paren/comma, for indexed
    rxIndexed = '\)?,.+'
    indexedMatch = re.search(rxIndexed, argsString)
    if (indexedMatch):
        indexedString = indexedMatch.group()
        if (indexedString.startswith('\)')):
            mode = m.IZY
        elif (indexedString.endswith('\)')):
            mode = m.IZX
        elif (indexedString.__contains__('x')):
            if (arg16 != -1):
                mode = m.ABX
            else:
                mode = m.ZPX
        elif (indexedString.__contains__('y')):
            if (arg16 != -1):
                mode = m.ABY
            else:
                mode = m.ZPY
    # 2 bytes
    elif (arg16 != -1):
        if (argsString.endswith(')')):
            mode = m.IND
        else:
            mode = m.ABS
    elif (arg8 != -1):
        mode = m.ZP # could also be relative?

    # A for implied/accumulator
    rxA = 'a'
    aMatch = re.match(rxA, argsString)
    if (aMatch):
        mode = m.IMP
        return mode, opcode, arg8, arg16

    # pound sign, for immediate
    rxImm = '#'
    immString = re.search(rxImm, argsString)
    if (immString):
        mode = m.IMM

    return mode, opcode, arg8, arg16

def getByteCode(mode, opcode):
    byteCode = ot.byteCodes[opcode][mode]
    return byteCode


import numpy as np
import re
import opTable as ot
from opTable import m

def parseAsm(asmString):
    byteList = []
    asmStringLines = re.split('\n', asmString)
    for line in asmStringLines:
        bytes = asmToOpcode(line)
        for b in bytes:
            byteList.append(b)
    return byteList

def asmToOpcode(string):
    instruction, mode, lowByte, highByte = None, None, None, None

    # remove anything after semicolon
    rxComment = ';.*'
    commentMatch = re.search(rxComment, string)
    if (commentMatch):
        string = string.replace(commentMatch.group(), '')

    # convert to lowercase and strip whitespace
    string = string.lower().strip()

    # 3 letter instruction
    rxInstruction = '[a-z]{3}'
    instructionMatch = re.match(rxInstruction, string)
    if (not instructionMatch):
        return getOpcode(instruction, mode, lowByte, highByte)
    instruction = instructionMatch.group()

    # everything after instruction
    rxArgs = '(?<=.{4}).*'
    argsMatch = re.search(rxArgs, string)
    if (not argsMatch):
        mode = m.IMP
        return getOpcode(instruction, mode, lowByte, highByte)
    argsString = argsMatch.group().replace(' ', '')

    # dollar sign, for hex
    rxHex = '\$'
    hexMatch = re.search(rxHex, argsString)
    if (hexMatch):
        # TODO: consider decimal support
        pass

    # 1 bytes, or 2?
    rxDouble = '\w{4}'
    doubleMatch = re.search(rxDouble, argsString)
    if (doubleMatch):
        lowByte = int(doubleMatch.group()[0:2], 16)
        highByte = int(doubleMatch.group()[2:4], 16)
    else:
        rxSingle = '\w{2}'
        singleMatch = re.search(rxSingle, argsString)
        if (singleMatch):
            lowByte = int(singleMatch.group(), 16)

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
            if (highByte != None):
                mode = m.ABX
            else:
                mode = m.ZPX
        elif (indexedString.__contains__('y')):
            if (highByte != None):
                mode = m.ABY
            else:
                mode = m.ZPY
    # 2 bytes
    elif (highByte != None):
        if (argsString.endswith(')')):
            mode = m.IND
        else:
            mode = m.ABS
    elif (lowByte != None):
        if (instruction in ot.relativeCodes):
            mode = m.REL
        else:
            mode = m.ZP

    # A for implied/accumulator
    rxA = 'a'
    aMatch = re.match(rxA, argsString)
    if (aMatch):
        mode = m.IMP
        return getOpcode(instruction, mode, lowByte, highByte)

    # pound sign, for immediate
    rxImm = '#'
    immString = re.search(rxImm, argsString)
    if (immString):
        mode = m.IMM

    return getOpcode(instruction, mode, lowByte, highByte)

def getOpcode(instruction, mode, lowByte, highByte):
    byteList = []
    if (instruction != None and mode != None):
        byteList.append(np.uint8(ot.byteCodes[instruction][mode]))
        if (lowByte != None):
            byteList.append(np.uint8(lowByte))
            if (highByte != None):
                byteList.append(np.uint8(highByte))
    return byteList

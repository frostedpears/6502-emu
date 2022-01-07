import numpy as np
import re
import emulator.opTable as ot
from emulator.opTable import MODE
import emulator.monitor as mon

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
        mode = MODE.IMP
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
        lowByte = int(doubleMatch.group()[2:4], 16)
        highByte = int(doubleMatch.group()[0:2], 16)
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
            mode = MODE.IZY
        elif (indexedString.endswith('\)')):
            mode = MODE.IZX
        elif (indexedString.__contains__('x')):
            if (highByte != None):
                mode = MODE.ABX
            else:
                mode = MODE.ZPX
        elif (indexedString.__contains__('y')):
            if (highByte != None):
                mode = MODE.ABY
            else:
                mode = MODE.ZPY
    # 2 bytes
    elif (highByte != None):
        if (argsString.endswith(')')):
            mode = MODE.IND
        else:
            mode = MODE.ABS
    elif (lowByte != None):
        if (instruction in ot.relativeCodes):
            mode = MODE.REL
        else:
            mode = MODE.ZP

    # A for implied/accumulator
    rxA = 'a'
    aMatch = re.match(rxA, argsString)
    if (aMatch):
        mode = MODE.IMP
        return getOpcode(instruction, mode, lowByte, highByte)

    # pound sign, for immediate
    rxImm = '#'
    immString = re.search(rxImm, argsString)
    if (immString):
        mode = MODE.IMM

    return getOpcode(instruction, mode, lowByte, highByte)

def getOpcode(instruction, mode, lowByte, highByte):
    byteList = []
    if (instruction != None and mode != None):
        try:
            byteList.append(np.uint8(ot.opCodes[instruction][mode]))
        except Exception as e:
            mon.printError(e)
        if (lowByte != None):
            byteList.append(np.uint8(lowByte))
            if (highByte != None):
                byteList.append(np.uint8(highByte))
    return byteList

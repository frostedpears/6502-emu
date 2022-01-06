import emu6502 as emu
import monitor as mon

testAsm = '''
LDA #$44
JMP $1007
LDA #$22
ADC #$44
STA $44
LDA #$10
STA $45
'''

def main():
    e = emu.emu6502()
    e.verbose = False

    e.writeAsm(testAsm, 0x1000)
    mon.printRange(e, 0x1000, 0x1010)
    e.runAt(0x1000)
    mon.printRange(e, 0x40, 0x50)
    
    mon.printRegisters(e)
    mon.printFlags(e)
    return

main()
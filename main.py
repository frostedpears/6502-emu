import emu6502 as emu
import numpy as np
import monitor as mon

dd63 = '''
;TYA
;PHA
;TXA
;PHA
LDA $31
STA $33
LDA $32
STA $34
'''
dd63_2 = '''
JSR $DDA2
JSR $DDA2
JSR $DDAD
JSR $DDA2
JSR $DDAD
JSR $DDA2
JSR $DDA2
JSR $DDAD
JSR $DDA2
'''

dd63_2 = '''
LDY #$07
JSR $DDA2
JSR $DDAD
DEY
BNE $DD8C
'''

dd63_3 = '''
INC $31
;BNE $DD9B
;INC $32
PLA
TAX
PLA
TAY
LDA $32
;RTS
'''

dda2 = '''
LDA $33
ASL A 
STA $33
LDA $34 
ROL A 
STA $34 
;RTS 
'''

ddad = '''
LDA $33
CLC 
ADC $31 
STA $31 
LDA $34 
ADC $32 
STA $32 
;RTS 
'''

def main():
    e = emu.emu6502()
    e.verbose = False
    e.setByte(0x24, 0x31)
    e.setByte(0xA1, 0x32)
    mon.printRange(e, 0x31, 0x35)

    e.run(dd63)
    e.run(dda2)
    e.run(dda2)
    e.run(ddad)
    e.run(dda2)
    e.run(ddad)
    e.run(dda2)
    e.run(dda2)
    e.run(ddad)
    e.run(dda2)
    for i in range(0,7):
        e.run(dda2)
        e.run(ddad)
    e.run(dd63_3)
    # mon.printFlags(e)
    mon.printRegisters(e)
    mon.printRange(e, 0x31, 0x35)
    return

main()
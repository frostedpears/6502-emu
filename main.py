import emulator.emu6502 as emu
import emulator.monitor as mon

dd63 = '''
TYA
PHA
TXA
PHA
LDA $31
STA $33
LDA $32
STA $34

JSR $DDA2
JSR $DDA2
JSR $DDAD
JSR $DDA2
JSR $DDAD
JSR $DDA2
JSR $DDA2
JSR $DDAD
JSR $DDA2
LDY #$07
JSR $DDA2
JSR $DDAD
DEY
BNE $F7

INC $31
BNE $02
INC $32
PLA
TAX
PLA
TAY
LDA $32
RTS

;dda2
LDA $33
ASL A 

STA $33
LDA $34 
ROL A 
STA $34 
RTS 

;ddad
LDA $33
CLC 
ADC $31 
STA $31 
LDA $34 
ADC $32 
STA $32 
RTS 
'''

def main():
    e = emu.emu6502()
    e.setByte(0x20, 0x31)
    e.setByte(0x40, 0x32)
    e.writeAsm(dd63, 0xdd63)
    mon.printRange(e, 0xdd60, 0xdd70)
    mon.printRange(e, 0xdd70, 0xdd80)
    mon.printRange(e, 0xdd80, 0xdd90)
    mon.printRange(e, 0xdd90, 0xdda0)
    mon.printRange(e, 0xdda0, 0xddb0)
    mon.printRange(e, 0xddb0, 0xddc0)
    #e.movePcAndRun(0xc000)
    e.movePcAndRun(0xdd63)
    mon.printRange(e, 0x30, 0x40)
    
    mon.printRegisters(e)
    mon.printFlags(e)
    return

main()
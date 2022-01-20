import emulator.emu6502 as emu
import emulator.monitor as mon
from blessed import Terminal

f = open('./input/dd63.txt', 'r')
dd63 = f.read()
f.close()

def main():
    e = emu.emu6502()
    e.writeAsm(dd63, 0xdd63)
    rng1 = 0
    rng2 = 0

    f = open('./output/gb_rng.txt', 'a')
    for i in range (0,70000):
        e.setByte(rng1, 0x31)
        e.setByte(rng2, 0x32)
        e.movePCAndRun(0xdd63)
        rng1 = e.getByte(0x31)
        rng2 = e.getByte(0x32)
        f.write('{:02X}'.format(rng1))
        f.write(' ')
        f.write('{:02X}'.format(rng2))
        f.write('\n')
        e.resetState()



    m = mon.monitor()
    term = Terminal()
    inp = None
    steps = 0
    e.movePC(0xdd63)
    m.printStep(e, steps)
    while (e.keepRunning() and repr(inp) != 'KEY_ESCAPE'):
        e.stepInto()
        steps += 1
        if (steps > 300):
            m.printStep(e, steps)
            with term.cbreak(), term.hidden_cursor():
                inp = term.inkey()
    m.printStep(e, steps)

    
    '''
    mon.printRange(e, 0xdd60, 0xdd70)
    mon.printRange(e, 0xdd70, 0xdd80)
    mon.printRange(e, 0xdd80, 0xdd90)
    mon.printRange(e, 0xdd90, 0xdda0)
    mon.printRange(e, 0xdda0, 0xddb0)
    mon.printRange(e, 0xddb0, 0xddc0)
    '''
    #e.movePcAndRun(0xc000)
    #e.movePCAndRun(0xdd63)
    #mon.printRange(e, 0x30, 0x40)
    
    #mon.printRegisters(e)
    #mon.printFlags(e)
    return

main()
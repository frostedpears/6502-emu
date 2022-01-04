import emu6502 as emu
import numpy as np

def test():
    a = 0x42
    a = a << 8
    a = a + 0x43
    print('{:02X}'.format(a))
    #print('{:02X}'.format(0x42 << 1))

    return

test()
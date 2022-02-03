import emu6502 as emu
import monitor as mon
import parse6502 as parser

def main():
    e = emu.Emu6502()
    code = parser.asm_file_to_byte_list('./input/asm1.txt')
    e.write_list(code, 0x600)
    e.run_at(0x600)
    print('asm ram')
    mon.print_range(e, 0x200, 0x210)

main()

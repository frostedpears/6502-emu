import emu6502 as emu
import monitor as mon
import parse6502 as parser

def main():
    snake_mem = emu.MemoryMap()
    m = mon.monitor()
    m.subscribe(snake_mem)   
    code = parser.hex_file_to_byte_list('./input/snake6502.txt')
    parser.save_binary('./input/snake6502.rom', code)
    emu.write_list(snake_mem, code, 0x600)
    emu.move_pc(snake_mem, 0x600)
    for i in range(0,50):
        emu.step_into(snake_mem)
    print('snake rom')
    mon.print_range(snake_mem, 0x600, 0x735)
    
    asm_mem = emu.MemoryMap()
    code = parser.asm_file_to_byte_list('./input/asm1.txt')
    emu.write_list(asm_mem, code, 0x600)
    emu.move_pc_and_run(asm_mem, 0x600)
    print('asm ram')
    mon.print_range(asm_mem, 0x200, 0x210)

main()

class Emu6502():
    def __init__(self):    
        # Number of bytes. Memory map will be from: 0 to (size - 1)
        self.size = 0x10000
        self.memory = [0] * self.size
        self.pc = 0xc000  # program counter

        # extended/internal memory
        self.x_mem = {
            'a': 0,
            'x': 0,
            'y': 0,
            '#': 0,  # immediate value / temp register
            's': 0xff,  # stack pointer
        }

        self.flag = {
            'n': False,  # negative.128
            'v': False,  # overflow..64
            'u': True,  # unused....32
            'b': True,  # break.....16
            'd': False,  # decimal....8
            'i': False,  # interrupt..4
            'z': False,  # zero.......2
            'c': False,  # carry......1
        }

        # observers / events
        self.subscribers = set()

    # ---------------------- observers / events ----------------------
    def register(self, who):
        self.subscribers.add(who)

    def unregister(self, who):
        self.subscribers.discard(who)

    def dispatch(self, message):
        for subscriber in self.subscribers:
            subscriber.update(message)

    # ------------------------ functions ------------------------
    # ---- run ----
    def run_at(self, addr):
        self.jmp(addr)
        self.run()

    def run_range(self, address_start, address_end):
        self.pc = address_start
        while self.keep_running() and self.pc < address_end:
            self.run_instruction()

    def run(self):
        while self.keep_running():
            self.run_instruction()

    def step_into(self):
        self.run_instruction()

    def run_instruction(self):
        opcode = self.get_mem(self.pc)
        self.pc += 1
        low_byte, high_byte = None, None
        if opcode in self.op_length[1]:
            try:
                self.func_table[opcode](self)
            except Exception as e:
                print(e)
        elif opcode in self.op_length[2]:
            low_byte = self.get_mem(self.pc)
            self.pc += 1
            self.set_mem(low_byte, '#')
            try:
                self.func_table[opcode](self, low_byte)
            except Exception as e:
                try:
                    self.func_table[opcode](self)
                except Exception as e:
                    print(e)
        elif  opcode in self.op_length[3]:
            low_byte = self.get_mem(self.pc)
            self.pc += 1
            high_byte = self.get_mem(self.pc)
            self.pc += 1
            try:
                self.func_table[opcode](self, low_byte, high_byte)
            except Exception as e:
                try:
                    self.func_table[opcode](self)
                except Exception as e:
                    print(e)
        return 0

    def keep_running(self):
        """Return true if the hardware is in a state to keep running
        TODO expand on what affects this
        """
        if (self.flag['i']):
            return False
        return True

    # ---- memory ----
    def get_mem(self, addr):
        if str(addr).isdigit():
            return self.memory[addr]
        elif addr in self.x_mem.keys():
            return self.x_mem[addr]
        else:
            print(f"Invalid address, get: {addr}")

    def set_mem(self, value, addr, flags=None):
        if flags:
            self.update_flags(value, flags)
        value = value & 0xff
        if str(addr).isdigit():
            self.memory[addr] = value
        elif addr in self.x_mem.keys():
            self.x_mem[addr] = value
        else:
            print(f"Invalid address, set: {addr}")

    def get_range(self, address_start, address_end):
        byte_list = []
        if address_start > self.size or address_end > self.size:
            print('error: address ' + hex(address_start)
                    + '-' + hex(address_end) + ' out of range')
            return byte_list

        for address in range(address_start, address_end):
            byte_list.append(self.get_mem(address))

        return byte_list

    def write_list(self, byte_list, address_start):
        """write list of 8-bit ints to memory"""
        if address_start + len(byte_list) > self.size:
            print ('error: address ' + hex(address_start) + '-'
                    + hex(address_start + len(byte_list)) + ' out of range')
            return 1
        for index, value in enumerate(byte_list):
            address = address_start + index
            low_byte = address & 0xff
            high_byte = (address & 0xff00) >> 8
            self.set_mem(value, self.abs(low_byte, high_byte))

    # ---- flags ----
    def get_flags_byte(self):
        """Return status of flags as byte"""
        return (self.flag['n'] * 128
              + self.flag['v'] * 64
              + self.flag['u'] * 32
              + self.flag['b'] * 16
              + self.flag['d'] * 8
              + self.flag['i'] * 4
              + self.flag['z'] * 2
              + self.flag['c'] * 1)

    def set_flags_byte(self, value):
        """Set all flags from a byte"""
        self.flag['n'] = value & 128 > 0
        self.flag['v'] = value & 64 > 0
        self.flag['u'] = value & 32 > 0
        self.flag['b'] = value & 16 > 0
        self.flag['d'] = value & 8 > 0
        self.flag['i'] = value & 4 > 0
        self.flag['z'] = value & 2 > 0
        self.flag['c'] = value & 1 > 0
        
    def set_flag(self, value, flags):
        for flag in flags:
            self.flag[flag] = value

    def update_flags(self, value, flags):
        if 'z' in flags:
            self.set_flag(value == 0, 'z')
        if 'n' in flags:
            self.set_flag(value > 0x7f or value < 0, 'n')
        if 'c' in flags:
            self.set_flag(value > 0xff, 'c')

    # ------------------- utilities -------------------
    def twos_comp(self, value):
        """compute the 2's complement of 8-bit value"""
        if (value & (1 << (8 - 1))) != 0:
            value = value - (1 << 8)
        return value
    
    # ------------------- instructions -------------------
    def adc(self, addr):
        """A:=A+{adr} | NVZC"""
        carry_in = self.flag['c']
        value = self.get_mem(addr) + self.get_mem('a') + carry_in
        self.set_mem(value, 'a', 'nvzc')

    def _and(self, addr):
        """A:=A&{adr} | NZ"""
        value = self.get_mem(addr) & self.get_mem('a')
        self.set_mem(value, 'a', 'nz')

    def asl(self, addr):
        """{adr}:={adr}*2 | NZC"""
        value = self.get_mem(addr) << 1
        self.set_mem(value, 'a', 'nzc')

    def branch(self, lo, bool):
        if bool:
            self.jmp(self.rel(lo))

    def dec(self, addr):
        """{adr}:={adr}-1 | NZ"""
        value = self.get_mem(addr) - 1
        self.set_mem(value, addr, 'nz')

    def eor(self, addr):
        """A:=A exor {adr} | NZ"""
        value = self.get_mem(addr) ^ self.get_mem('a')
        self.set_mem(value, 'a', 'nz')
    
    def inc(self, addr):
        """{adr}:={adr}+1 | NZ"""
        value = self.get_mem(addr) + 1
        self.set_mem(value, addr, 'nz')

    def jmp(self, addr):
        """Set stack pointer to an address"""
        self.pc = addr

    def lsr(self, addr):
        """{adr}:={adr}/2 | NZC"""
        value = self.get_mem(addr)
        carry_out = value & 1 == 1
        value = (value >> 1)
        self.set_flag(carry_out, 'c')
        self.set_mem(value, addr, 'nz')

    def ora(self, addr):
        """A:=A or {adr} | NZ"""
        value = self.get_mem(addr) | self.get_mem('a')
        self.set_mem(value, 'a', 'nz')

    def pull_to(self, addr):
        """Pull a value from the stack, and store it in an address"""
        value = self.pull()
        self.set_mem(value, addr)

    def pull(self):
        """Pull a value from the stack, and return it"""
        self.inc('s')
        stk_p = self.abs(self.get_mem('s'), 0x1)
        return self.get_mem(stk_p)

    def push_from(self, addr):
        """Take the value from an address, and push it to the stack"""
        value = self.get_mem(addr)
        self.push(value)

    def push(self, value):
        """Push the given value to the stack"""
        stk_p = self.abs(self.get_mem('s'), 0x1)
        self.set_mem(value, stk_p)
        self.dec('s')

    def rol(self, addr):
        """{adr}:={adr}*2+C | NZC"""
        value = self.get_mem(addr)
        carry_in = self.flag['c']
        value = (value << 1) + carry_in
        self.set_mem(value, addr, 'nzc')

    def ror(self, addr):
        """{adr}:={adr}/2+C*128 | NZC"""
        value = self.get_mem(addr)
        carry_in = self.flag['c']
        carry_out = value & 1 == 1
        value = (value >> 1) + (carry_in * 128)
        self.set_flag(carry_out, 'c')
        self.set_mem(value, addr, 'nz')

    def sbc(self, addr):
        """A:=A+{adr} | NVZC"""
        carry_in = self.flag['c']
        value_in = self.get_mem(addr) + (not carry_in)
        carry_out = value_in > self.get_mem('a')
        value = self.get_mem('a') - value_in
        self.set_flag((not carry_out), 'c')
        self.set_mem(value, 'a', 'nvz')
    
    def tsf(self, src, tgt):
        """{tgt}:={src} | NZ"""
        value = self.get_mem(src)
        self.set_mem(value, tgt, 'nz')

    # ------------------- addressing -------------------
    def abs(self, lo, hi):
        """Turn 2 bytes into a single address integer"""
        return lo + (hi << 8)
    
    def abx(self, lo, hi):
        """absolute, x"""
        return (lo + (hi << 8)) + self.get_mem('x')
    
    def izx(self, lo):
        """x-indexed, indirect | TODO handle crossing page boundries"""
        index = lo + self.get_mem('x')
        low_byte = self.get_mem(index)
        high_byte = self.get_mem(index + 1)
        return self.abs(low_byte, high_byte)
    
    def rel(self, lo):
        return self.pc + self.twos_comp(lo)

    def zpx(self, lo):
        """zero page, x"""
        return (lo + self.get_mem('x')) & 0xFF

    # ------------------- Jump / Flag commands -------------------
    def op_20(self, low_byte, high_byte):
        """jsr abs | (S)-:=PC PC:={adr} | none"""
        return_low_byte = self.pc & 0xFF
        return_high_byte = (self.pc & 0xFF00) >> 8
        self.push(return_high_byte)
        self.push(return_low_byte)
        address = low_byte + (high_byte << 8)
        self.pc = address

    def op_60(self): #  none
        """rts imp | PC:=+(S) | none"""
        low_byte = self.pull()
        high_byte = self.pull()
        address = low_byte + (high_byte << 8)
        self.pc = address

# ---------------------------------------------------------------------
# ------------------------- lookup tables -----------------------------
# ---------------------------------------------------------------------
    op_length = {
        1: [0x08, 0x18, 0x28, 0x38, 0x48, 0x58, 0x68, 0x78, 0x88, 0x98,
            0xa8, 0xb8, 0xc8, 0xd8, 0xe8, 0xf8, 0x0a, 0x2a, 0x4a, 0x6a,
            0x8a, 0x9a, 0xaa, 0xba, 0xca, 0xea, 0x00, 0x40, 0x60],
        2: [0x01, 0x11, 0x21, 0x31, 0x41, 0x51, 0x61, 0x71, 0x81, 0x91,
            0xa1, 0xb1, 0xc1, 0xd1, 0xe1, 0xf1, 0xa2, 0x24, 0x84, 0x94,
            0xa4, 0xb4, 0xc4, 0xe4, 0x05, 0x15, 0x25, 0x35, 0x45, 0x55,
            0x65, 0x75, 0x85, 0x95, 0xa5, 0xb5, 0xc5, 0xd5, 0xe5, 0xf5,
            0x06, 0x16, 0x26, 0x36, 0x46, 0x56, 0x66, 0x76, 0x86, 0x96,
            0xa6, 0xb6, 0xc6, 0xd6, 0xe6, 0xf6, 0x10, 0x30, 0x50, 0x70,
            0x90, 0xa0, 0xb0, 0xc0, 0xd0, 0xe0, 0xf0, 0x09, 0x29, 0x49,
            0x69, 0xa9, 0xc9, 0xe9],
        3: [0x2c, 0x4c, 0x6c, 0x8c, 0xac, 0xbc, 0xcc, 0xec, 0x0d, 0x1d,
            0x2d, 0x3d, 0x4d, 0x5d, 0x6d, 0x7d, 0x8d, 0x9d, 0xad, 0xbd,
            0xcd, 0xdd, 0xed, 0xfd, 0x0e, 0x1e, 0x2e, 0x3e, 0x4e, 0x5e,
            0x6e, 0x7e, 0x8e, 0xae, 0xbe, 0xce, 0xde, 0xee, 0xfe, 0x20,
            0x19, 0x39, 0x59, 0x79, 0x99, 0xb9, 0xd9, 0xf9]
    }

    func_table = {
        0x00: lambda self: self.set_flag(True, 'ib'),
                #"""brk imp | (S)-:=PC,P PC:=($FFFE) | B:=1 I:=1 | TODO ?"""
        0x10: lambda self, lo: self.branch(lo, (not self.flag['n'])),  # bpl rel
        0x20: op_20,
        0x30: lambda self, lo: self.branch(lo, self.flag['n']),  # bmi rel
        0x40: lambda self: None,  #---
        0x50: lambda self, lo: self.branch(lo, (not self.flag['v'])),  # bvc rel
        0x60: op_60,
        0x70: lambda self, lo: self.branch(lo, self.flag['v']),  # bvs rel
        0x90: lambda self, lo: self.branch(lo, (not self.flag['c'])),  # bcc rel
        0xa0: lambda self, lo: self.tsf('#', 'y'),  # ldy imm
        0xb0: lambda self, lo: self.branch(lo, self.flag['c']),  # bcs rel
        0xc0: lambda self: None,  #---
        0xd0: lambda self, lo: self.branch(lo, (not self.flag['z'])),  # bne rel
        0xe0: lambda self: None,  #---
        0xf0: lambda self, lo: self.branch(lo, self.flag['z']),  # beq rel
        0x01: lambda self, lo: self.ora(self.izx(lo), 'a'),  # ora izx
        0x11: lambda self: None,  #---
        0x21: lambda self, lo: self._and(self.izx(lo), 'a'),  # and izx
        0x31: lambda self: None,  #---
        0x41: lambda self, lo: self.eor(self.izx(lo), 'a'),  # eor izx
        0x51: lambda self: None,  #---
        0x61: lambda self, lo: self.adc(self.izx(lo), 'a'),  # adc izx
        0x71: lambda self: None,  #---
        0x81: lambda self, lo: self.tsf('a', self.izx(lo)),  # sta izx
        0x91: lambda self: None,  #---
        0xa1: lambda self, lo: self.tsf(self.izx(lo), 'a'),  # lda izx
        0xb1: lambda self: None,  #---
        0xc1: lambda self: None,  #---
        0xd1: lambda self: None,  #---
        0xe1: lambda self, lo: self.sbc(self.izx(lo), 'a'),  # sbc izx
        0xf1: lambda self: None,  #---
        0xa2: lambda self, lo: self.tsf('#', 'x'),  # ldx imm
        0x24: lambda self: None,  #---
        0x84: lambda self, lo: self.tsf('y', lo),  # sty zp
        0x94: lambda self, lo: self.tsf('y', self.zpx(lo)),  # sty zpx
        0xa4: lambda self, lo: self.tsf(lo, 'y'),  # ldy zp
        0xb4: lambda self, lo: self.tsf(self.zpx(lo), 'y'),  # ldy zpx
        0xc4: lambda self: None,  #---
        0xe4: lambda self: None,  #---
        0x05: lambda self, lo: self.ora(lo),  # ora zp
        0x15: lambda self, lo: self.ora(self.zpx(lo)),  # ora zpx
        0x25: lambda self, lo: self._and(lo),  # and zp
        0x35: lambda self, lo: self._and(self.zpx(lo)),  # and zpx
        0x45: lambda self, lo: self.eor(lo),  # eor zp
        0x55: lambda self, lo: self.eor(self.zpx(lo)),  # eor zpx
        0x65: lambda self, lo: self.adc(lo),  # adc zp
        0x75: lambda self, lo: self.adc(self.zpx(lo)),  # adc zpx
        0x85: lambda self, lo: self.tsf('a', lo),  # sta zp
        0x95: lambda self, lo: self.tsf('a', self.zpx(lo)),  # sta zpx
        0xa5: lambda self, lo: self.tsf(lo, 'a'),  # lda zp
        0xb5: lambda self, lo: self.tsf(self.zpx(lo), 'a'),  # lda zpx
        0xc5: lambda self: None,  #---
        0xd5: lambda self: None,  #---
        0xe5: lambda self, lo: self.sbc(lo),  # sbc zp
        0xf5: lambda self, lo: self.sbc(self.zpx(lo)),  # sbc zpx
        0x06: lambda self, lo: self.asl(lo),  # asl zp
        0x16: lambda self, lo: self.asl(self.zpx(lo)),  # asl zpx
        0x26: lambda self, lo: self.rol(lo),  # rol zp
        0x36: lambda self, lo: self.rol(self.zpx(lo)),  # rol zpx
        0x46: lambda self, lo: self.lsr(lo),  # lsr zp
        0x56: lambda self, lo: self.lsr(self.zpx(lo)),  # lsr zpx
        0x66: lambda self, lo: self.ror(lo),  # ror zp
        0x76: lambda self, lo: self.ror(self.zpx(lo)),  # ror zpx
        0x86: lambda self, lo: self.tsf('x', lo),  # stx zp
        0x96: lambda self: None,  #---
        0xa6: lambda self, lo: self.tsf(lo, 'x'),  # ldx zp
        0xb6: lambda self: None,  #---
        0xc6: lambda self, lo: self.dec(lo),  # dec zp
        0xd6: lambda self, lo: self.dec(self.zpx(lo)),  # dec zpx
        0xe6: lambda self, lo: self.inc(lo),  # inc zp
        0xf6: lambda self, lo: self.inc(self.zpx(lo)),  # inc zpx
        0x08: lambda self: self.push(
                self.get_flags_byte() | 0b00110000),
                #"""php imp | (S)-:=P | none | TODO FIX"""
        0x18: lambda self: self.set_flag(False, 'c'), # clc imp
        0x28: lambda self: self.set_flags_byte(
                (self.pull() & 0b11001111) | (self.sr & 0b00110000)),
                #"""plp imp | P:=+(S) | NVDIZC | TODO FIX"""
        0x38: lambda self: self.set_flag(True, 'c'), # sec imp
        0x48: lambda self: self.push('a'), # pla imp
        0x58: lambda self: self.set_flag(False, 'i'), # cli imp
        0x68: lambda self: self.pull('a'), # pla imp
        0x78: lambda self: self.set_flag(True, 'i'), # sei imp
        0x88: lambda self: self.dec('y'),  # dey imp
        0x98: lambda self: self.tsf('a', 'x'),  # tax imp
        0xa8: lambda self: self.tsf('a', 'y'),  # tay imp
        0xb8: lambda self: self.set_flag(False, 'v'), # clv imp
        0xc8: lambda self: self.inc('y'),  # iny imp
        0xd8: lambda self: self.set_flag(False, 'd'), # cld imp
        0xe8: lambda self: self.inc('x'),  # inx imp
        0xf8: lambda self: self.set_flag(True, 'd'), # sed imp
        0x09: lambda self, lo: self.ora('#'),  # ora imm
        0x19: lambda self: None,  #---
        0x29: lambda self, lo: self._and('#'),  # and imm
        0x39: lambda self: None,  #---
        0x49: lambda self, lo: self.eor('#'),  # eor imm
        0x59: lambda self: None,  #---
        0x69: lambda self, lo: self.adc('#'),  # adc imm
        0x79: lambda self: None,  #---
        0x99: lambda self: None,  #---
        0xa9: lambda self, lo: self.tsf('#', 'a'),  # lda imm
        0xb9: lambda self: None,  #---
        0xc9: lambda self: None,  #---
        0xd9: lambda self: None,  #---
        0xe9: lambda self, lo: self.sbc('#'),  # sbc imm
        0xf9: lambda self: None,  #---
        0x0a: lambda self: self.asl('a'),  # asl imp
        0x2a: lambda self: self.rol('a'),  # rol imp
        0x4a: lambda self: self.lsr('a'),  # lsr imp
        0x6a: lambda self: self.ror('a'),  # ror imp
        0x8a: lambda self: self.tsf('x', 'a'),  # txa imp
        0x9a: lambda self: self.tsf('x', 's'),  # txs imp
        0xaa: lambda self: self.tsf('a', 'x'),  # tax imp
        0xba: lambda self: self.tsf('s', 'x'),  # tsx imp
        0xca: lambda self: self.dec('x'),  # dex imp
        0xea: lambda self: None,  # nop imp
        0x2c: lambda self: None,  #---
        0x4c: lambda self, lo, hi: self.jmp(self.abs(lo, hi)),  # jmp abs
        0x6c: lambda self: None,  #---
        0x8c: lambda self, lo, hi: self.tsf('y', self.abs(lo, hi)),  # sty abs
        0xac: lambda self, lo, hi: self.tsf(self.abs(lo, hi), 'y'),  # ldy abs
        0xbc: lambda self, lo, hi: self.tsf(self.abx(lo, hi), 'y'),  # ldy abx
        0xcc: lambda self: None,  #---
        0xec: lambda self: None,  #---
        0x0d: lambda self, lo, hi: self.ora(self.abs(lo, hi)),  # ora abs
        0x1d: lambda self, lo, hi: self.ora(self.abx(lo, hi)),  # ora abx
        0x2d: lambda self, lo, hi: self._and(self.abs(lo, hi)),  # and abs
        0x3d: lambda self, lo, hi: self._and(self.abx(lo, hi)),  # and abx
        0x4d: lambda self, lo, hi: self.eor(self.abs(lo, hi)),  # eor abs
        0x5d: lambda self, lo, hi: self.eor(self.abx(lo, hi)),  # eor abx
        0x6d: lambda self, lo, hi: self.adc(self.abs(lo, hi)),  # adc abs
        0x7d: lambda self, lo, hi: self.adc(self.abx(lo, hi)),  # adc abx
        0x8d: lambda self, lo, hi: self.tsf('a', self.abs(lo, hi)),  # sta abs
        0x9d: lambda self, lo, hi: self.tsf('a', self.abx(lo, hi)),  # sta abx
        0xad: lambda self, lo, hi: self.tsf(self.abs(lo, hi), 'a'),  # lda abs
        0xbd: lambda self, lo, hi: self.tsf(self.abx(lo, hi), 'a'),  # lda abx
        0xcd: lambda self: None,  #---
        0xdd: lambda self: None,  #---
        0xed: lambda self, lo, hi: self.sbc(self.abs(lo, hi)),  # sbc abs
        0xfd: lambda self, lo, hi: self.sbc(self.abx(lo, hi)),  # sbc abx
        0x0e: lambda self, lo, hi: self.asl(self.abs(lo, hi)),  # asl abs
        0x1e: lambda self, lo, hi: self.asl(self.abx(lo, hi)),  # asl abx
        0x2e: lambda self, lo, hi: self.rol(self.abs(lo, hi)),  # rol abs
        0x3e: lambda self, lo, hi: self.rol(self.abx(lo, hi)),  # rol abx
        0x4e: lambda self, lo, hi: self.lsr(self.abs(lo, hi)),  # lsr abs
        0x5e: lambda self, lo, hi: self.lsr(self.abx(lo, hi)),  # lsr abx
        0x6e: lambda self, lo, hi: self.ror(self.abs(lo, hi)),  # ror abs
        0x7e: lambda self, lo, hi: self.ror(self.abx(lo, hi)),  # ror abx
        0x8e: lambda self, lo, hi: self.tsf('x', self.abs(lo, hi)),  # stx abs
        0xae: lambda self, lo, hi: self.tsf(self.abs(lo, hi), 'x'),  # ldx abs
        0xbe: lambda self: None,  #---
        0xce: lambda self, lo, hi: self.dec(self.abs(lo, hi)),  # dec abs
        0xde: lambda self, lo, hi: self.dec(self.abx(lo, hi)),  # dec abx
        0xee: lambda self, lo, hi: self.inc(self.abs(lo, hi)),  # inc abs
        0xfe: lambda self, lo, hi: self.inc(self.abx(lo, hi)),  # inc abx
    }

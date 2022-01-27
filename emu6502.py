class MemoryMap():
    def __init__(self, size=0xffff):        
        # registers
        self._a = 0x00  # accumulator
        self._x = 0x00  # x register
        self._y = 0x00  # y register
        self.pc = 0xc000  # program counter
        self.sr = 0b00110000  # status register (flags)
        self.sp = 0xff  # stack pointer

        # Number of bytes. Memory map will be from: 0 to (size - 1)
        self.size = size
        self.memory = [0] * self.size

        # Should the pc increment before running the next instruction?
        # The pc should usually move before instructions,
        # but not before the first, or before jumps, etc
        # TODO find a more accurate way to replicate this logic
        self.increment_pc = False

        # observers / events
        activate_mem_map(self)
        self.subscribers = set()

    @property
    def a(self):
        return self._a
    
    @a.setter
    def a(self, value):
        self._a = value & 0xff
    
    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value & 0xff

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value & 0xff

    def register(self, who):
        self.subscribers.add(who)

    def unregister(self, who):
        self.subscribers.discard(who)

    def dispatch(self, message):
        for subscriber in self.subscribers:
            subscriber.update(message)

# ------------------------ collection ------------------------
active_mem_maps = []

def activate_mem_map(mem_map):
    """Add a memory map to the list of active maps"""
    active_mem_maps.append(mem_map)

def remove_mem_map(mem_map):
    """Remove a memory map TODO more cleanup"""
    active_mem_maps.remove(mem_map)

def get_active_mem_maps():
    return active_mem_maps

# ------------------------ functions ------------------------
def write_list(mem_map, byte_list, address_start):
    """write list of 8-bit ints to memory"""
    if address_start + len(byte_list) > mem_map.size:
        print ('error: address ' + hex(address_start) + '-'
                + hex(address_start + len(byte_list)) + ' out of range')
        return 1
    for index, value in enumerate(byte_list):
        address = address_start + index
        low_byte = address & 0xff
        high_byte = (address & 0xff00) >> 8
        set_byte(mem_map, value, low_byte, high_byte)
    return 0

# ---- run ----
def move_pc_and_run(mem_map, address):
    mem_map.pc = address
    run(mem_map)

def move_pc(mem_map, address):
    mem_map.pc = address

def run_range(mem_map, address_start, address_end):
    mem_map.dispatch(f"running range: {address_start:04x}-{address_end:04x}")
    mem_map.pc = address_start
    while keep_running(mem_map) and mem_map.pc < address_end - 1:
        run_instruction(mem_map)

def run(mem_map):
    mem_map.dispatch("running")
    while keep_running(mem_map):
        run_instruction(mem_map)

def step_into(mem_map):
    run_instruction(mem_map)

def run_instruction(mem_map):
    if mem_map.increment_pc:
        mem_map.pc += 1
    else:
        mem_map.increment_pc = True
    opcode = get_byte(mem_map, mem_map.pc)
    length = op_table[opcode]['len']
    low_byte, high_byte = None, None
    if length == 1:
        try:
            op_table[opcode]['func'](mem_map)
        except Exception as e:
            print(e)
    elif length == 2:
        mem_map.pc += 1
        low_byte = get_byte(mem_map, mem_map.pc)
        try:
            op_table[opcode]['func'](mem_map, low_byte)
        except Exception as e:
            print(e)
    elif length == 3:
        mem_map.pc += 1
        low_byte = get_byte(mem_map, mem_map.pc)
        mem_map.pc += 1
        high_byte = get_byte(mem_map, mem_map.pc)
        try:
            op_table[opcode]['func'](mem_map, low_byte, high_byte)
        except Exception as e:
            print(e)
    return 0

def keep_running(mem_map):
    """Return true if the hardware is in a state to keep running
    TODO expand on what affects this
    """
    if (get_flag(mem_map, FLAG.INT)):
        return False
    return True

# ---- memory ----
def get_byte(mem_map, low_byte, high_byte = None):
    """get the value of a byte from a given address"""
    if high_byte is None:
        address = low_byte
    else:
        address = low_byte + (high_byte << 8)
    if address >= mem_map.size or address < 0:
        print(f"address:{address} out of range")
        return None
    return mem_map.memory[address]

def set_byte(mem_map, value, low_byte, high_byte = None):
    """convert a value to 8-bit, and store it in a given address"""
    value = value & 0xff
    if high_byte is None:
        address = low_byte
    else:
        address = low_byte + (high_byte << 8)
    mem_map.memory[address] = value
    return

def get_range(mem_map, address_start, address_end):
    byte_list = []
    if address_start > mem_map.size or address_end > mem_map.size:
        print('error: address ' + hex(address_start)
                + '-' + hex(address_end) + ' out of range')
        return byte_list

    for address in range(address_start, address_end):
        low_byte = address & 0xff
        high_byte = (address & 0xff00) >> 8
        byte_list.append(get_byte(mem_map, low_byte, high_byte))

    return byte_list

# ---- stack ----
def push(mem_map, byte):
    set_byte(mem_map, byte, mem_map.sp, 0x1)
    mem_map.sp -= 1

def pull(mem_map):
    mem_map.sp += 1
    byte = get_byte(mem_map, mem_map.sp, 0x1)
    return byte

# ---- flags ----
def get_flag(mem_map, flag):
    """Return bool status of flag"""
    return mem_map.sr & flag == flag

def set_flag(mem_map, flag, bool_val):
    if (bool_val):
        mem_map.sr = mem_map.sr | flag
    else:
        mem_map.sr = mem_map.sr & ~flag

def update_flags(mem_map, value, flag_set):
    if FLAG.ZER in flag_set:
        update_flag_zero(mem_map, value)
    if FLAG.NEG in flag_set:
        update_flag_negative(mem_map, value)
    if FLAG.CAR in flag_set:
        update_flag_carry(mem_map, value)

def update_flag_zero(mem_map, value):
    bool_val = value == 0
    set_flag(mem_map, FLAG.ZER, bool_val)

def update_flag_negative(mem_map, value):
    bool_val = value > 0x7f
    set_flag(mem_map, FLAG.NEG, bool_val)

def update_flag_carry(mem_map, value):
    """Set carry flag to True, if value is > 255"""
    bool_val = value > 0xff
    set_flag(mem_map, FLAG.CAR, bool_val)

# ------------------- utilities -------------------
def twos_comp(value):
    """compute the 2's complement of 8-bit value"""
    if (value & (1 << (8 - 1))) != 0:
        value = value - (1 << 8)
    return value

# ---------------------------------------------------------------------
# --------------------------- op codes --------------------------------
# ---------------------------------------------------------------------

# ------------ Logical and arithmetic commands -------------
def op_09(mem_map, low_byte):
    """ora imm | A:=A or {adr} | NZ"""
    value = low_byte | mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_05(mem_map, low_byte):
    """ora zp | A:=A or {adr} | NZ"""
    value = get_byte(mem_map, low_byte) | mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_15(mem_map):
    """ora zpx | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_15: not implemented")

def op_01(mem_map):
    """ora izx | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_01: not implemented")

def op_11(mem_map):
    """ora izy | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_11: not implemented")

def op_0d(mem_map):
    """ora abs | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_0d: not implemented")

def op_1d(mem_map):
    """ora abx | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_1d: not implemented")

def op_19(mem_map):
    """ora aby | A:=A or {adr} | NZ"""
    mem_map.dispatch("op_19: not implemented")

def op_29(mem_map, low_byte):
    """and imm | A:=A&{adr} | NZ"""
    value = low_byte & mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_25(mem_map, low_byte):
    """and zp | A:=A&{adr} | NZ"""
    value = get_byte(mem_map, low_byte) & mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_35(mem_map):
    """and zpx | A:=A&{adr} | NZ"""
    mem_map.dispatch("op_35: not implemented")

def op_21(mem_map):
    """and izx |A:=A&{adr}  | NZ"""
    mem_map.dispatch("op_21: not implemented")

def op_31(mem_map):
    """and izy | A:=A&{adr} | NZ"""
    mem_map.dispatch("op_31: not implemented")

def op_2d(mem_map):
    """and abs | A:=A&{adr} | NZ"""
    mem_map.dispatch("op_2d: not implemented")

def op_3d(mem_map):
    """and abx | A:=A&{adr} | NZ"""
    mem_map.dispatch("op_3d: not implemented")

def op_39(mem_map):
    """and aby | A:=A&{adr} | NZ"""
    mem_map.dispatch("op_39: not implemented")

def op_49(mem_map, low_byte):
    """eor imm | A:=A exor {adr} | NZ"""
    value = low_byte ^ mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_45(mem_map, low_byte):
    """eor zp | A:=A exor {adr} | NZ"""
    value = get_byte(mem_map, low_byte) ^ mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_55(mem_map):
    """eor zpx | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_55: not implemented")

def op_41(mem_map):
    """eor izx | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_41: not implemented")

def op_51(mem_map):
    """eor izy | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_51: not implemented")

def op_4d(mem_map):
    """eor abs | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_4d: not implemented")

def op_5d(mem_map):
    """eor abx | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_5d: not implemented")

def op_59(mem_map):
    """eor aby | A:=A exor {adr} | NZ"""
    mem_map.dispatch("op_59: not implemented")

def op_69(mem_map, low_byte):
    """adc imm | A:=A+{adr} | NVZC
    TODO look into overflow flag
    """
    carry_in = get_flag(mem_map, FLAG.CAR)
    value = low_byte + mem_map.a + carry_in
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER, FLAG.CAR))
    mem_map.a = value

def op_65(mem_map, low_byte):
    """adc zp | A:=A+{adr} | NVZC"""
    carry_in = get_flag(mem_map, FLAG.CAR)
    value = get_byte(mem_map, low_byte) + mem_map.a + carry_in
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER, FLAG.CAR))
    mem_map.a = value

def op_75(mem_map):
    """adc zpx | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_75: not implemented")

def op_61(mem_map):
    """adc izx | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_61: not implemented")

def op_71(mem_map):
    """adc izy | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_71: not implemented")

def op_6d(mem_map):
    """adc abs | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_6d: not implemented")

def op_7d(mem_map):
    """adc abx | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_7d: not implemented")

def op_79(mem_map):
    """adc aby | A:=A+{adr} | NVZC"""
    mem_map.dispatch("op_79: not implemented")

def op_ca(mem_map):
    """dex imp | X:=X-1 | NZ"""
    value = mem_map.x - 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.x = value

def op_88(mem_map):
    """dey imp | Y:=Y-1 | NZ"""
    value = mem_map.y - 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.y = value

def op_e6(mem_map, low_byte):
    """inc zp | {adr}:={adr}+1 | NZ"""
    value = get_byte(mem_map, low_byte) + 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    set_byte(mem_map, value, low_byte)

def op_e8(mem_map):
    """inx imp | X:=X+1 | NZ"""
    value = mem_map.x + 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.x = value

def op_c8(mem_map):
    """iny imp | Y:=Y+1 | NZ"""
    value = mem_map.y + 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.y = value

def op_0a(mem_map):
    """asl imp | {adr}:={adr}*2 | NZC"""
    value = mem_map.a << 1
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER, FLAG.CAR))
    mem_map.a = value

def op_2a(mem_map):
    """rol imp | {adr}:={adr}*2+C | NZC"""
    carry_in = get_flag(mem_map, FLAG.CAR)
    value = (mem_map.a << 1) + carry_in
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER, FLAG.CAR))
    mem_map.a = value

# --------------------- Move commands ----------------------

def op_a9(mem_map, low_byte):
    """lda imm | A:={adr} | NZ"""
    value = low_byte
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_a5(mem_map, low_byte):
    """lda zp | A:={adr} | NZ"""
    value = get_byte(mem_map, low_byte)
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_a1(mem_map, low_byte):
    """lda izx | A:={adr} | NZ | TODO handle crossing page boundries"""
    index = low_byte + mem_map.x
    low_byte = get_byte(mem_map, index)
    high_byte = get_byte(mem_map, index + 1)
    value = get_byte(mem_map, low_byte, high_byte)
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_85(mem_map, low_byte):
    """sta zp | {adr}:=A | none"""
    value = mem_map.a
    set_byte(mem_map, value, low_byte)

def op_8d(mem_map, low_byte, high_byte):
    """sta abs | {adr}:=A | none"""
    value = mem_map.a
    set_byte(mem_map, value, low_byte, high_byte)

def op_a2(mem_map, low_byte):
    """ldx imm | X:={adr} | NZ"""
    value = low_byte
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.x = value

def op_86(mem_map, low_byte):
    """stx zp | {adr}:=X | none"""
    value = mem_map.x
    set_byte(mem_map, value, low_byte)

def op_a0(mem_map, low_byte):
    """ldy imm | Y:={adr} | NZ"""
    value = low_byte
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.y = value

def op_a4(mem_map, low_byte):
    """ldy zp | Y:={adr} | NZ"""
    value = get_byte(mem_map, low_byte)
    mem_map.y = value

def op_8c(mem_map, low_byte, high_byte):
    """sty abs | {adr}:=Y | none"""
    value = mem_map.y
    set_byte(mem_map, value, low_byte, high_byte)

def op_aa(mem_map):
    """tax imp | X:=A | NZ"""
    value = mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.x = value

def op_8a(mem_map):
    """txa imp | A:=X | NZ"""
    value = mem_map.x
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_a8(mem_map):
    """tay imp | Y:=A | NZ"""
    value = mem_map.a
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.y = value

def op_98(mem_map):
    """tya imp | A:=Y | NZ"""
    value = mem_map.y
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_ba(mem_map):
    """tsx imp | X:=S | NZ"""
    value = mem_map.sp
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.x = value

def op_9a(mem_map):
    """txs imp | S:=X | none"""
    mem_map.sp = mem_map.x

def op_68(mem_map):
    """pla imp | A:=+(S) | NZ"""
    value = pull(mem_map)
    update_flags(mem_map, value, (FLAG.NEG, FLAG.ZER))
    mem_map.a = value

def op_48(mem_map):
    """pha imp | (S)-:=A | none"""
    value = mem_map.a
    push(mem_map, value)

def op_28(mem_map):
    """plp imp | P:=+(S) | NVDIZC"""
    value = (pull(mem_map) & 0b11001111) | (mem_map.sr & 0b00110000)
    mem_map.sr = value

def op_08(mem_map):
    """php imp | (S)-:=P | none"""
    value = mem_map.sr | 0b00110000
    push(mem_map, value)

# ------------------- Jump / Flag commands -------------------
def op_d0(mem_map, low_byte):
    """bne rel | branch on Z=0 | none"""
    zero_in = get_flag(mem_map, FLAG.ZER)
    if not zero_in:
        mem_map.pc += twos_comp(low_byte)

def op_00(mem_map):
    """brk imp | (S)-:=PC,P PC:=($FFFE) | B:=1 I:=1 | TODO ?"""
    set_flag(mem_map, FLAG.INT, True)
    set_flag(mem_map, FLAG.BRK, True)

def op_20(mem_map, low_byte, high_byte):
    """jsr abs | (S)-:=PC PC:={adr} | none"""
    return_low_byte = mem_map.pc & 0xFF
    return_high_byte = (mem_map.pc & 0xFF00) >> 8
    push(mem_map, return_high_byte)
    push(mem_map, return_low_byte)
    address = low_byte + (high_byte << 8)
    mem_map.pc = address
    mem_map.increment_pc = False

def op_60(mem_map): #  none
    """rts imp | PC:=+(S) | none"""
    low_byte = pull(mem_map)
    high_byte = pull(mem_map)
    address = low_byte + (high_byte << 8)
    mem_map.pc = address

def op_4c(mem_map, low_byte, high_byte): #  none
    """jmp abs | PC:={adr} | none"""
    address = low_byte + (high_byte << 8)
    mem_map.pc = address
    mem_map.increment_pc = False

def op_24(mem_map, low_byte):
    """bit zp | N:=b7 V:=b6 Z:=A&{adr} | NVZ"""
    mem_map.dispatch("op_24: not implemented")

def op_2c(mem_map, low_byte, high_byte):
    """bit abs | N:=b7 V:=b6 Z:=A&{adr} | NVZ"""
    mem_map.dispatch("op_2c: not implemented")

def op_18(mem_map): # clc imp c=0
    """clc imp | C:=0 | C:=0"""
    set_flag(mem_map, FLAG.CAR, False)

def op_38(mem_map):
    """sec imp | C:=1 | C:=1"""
    set_flag(mem_map, FLAG.CAR, True)

def op_d8(mem_map): # cld imp d=0
    """cld imp | D:=0 | D:=0"""
    set_flag(mem_map, FLAG.DEC, False)

def op_f8(mem_map): # sed imp d=1
    """sed imp | D:=1 | D:=1"""
    set_flag(mem_map, FLAG.DEC, True)

def op_58(mem_map): # cli imp i=0
    """cli imp | I:=0 | I:=0"""
    set_flag(mem_map, FLAG.INT, False)

def op_78(mem_map): # sei imp i=1
    """sei imp | I:=1 | I:=1"""
    set_flag(mem_map, FLAG.INT, True)

def op_b8(mem_map): # clv imp v=0
    """clv imp | I:=1 | I:=1"""
    set_flag(mem_map, FLAG.OVR, True)

def op_ea(mem_map): # nop imp none
    """nop imp | no effect | none"""
    pass

# ---------------- not implemented ----------------


def op_e9(mem_map):
    """ |  | """
    mem_map.dispatch("op_e9: not implemented")

def op_e5(mem_map):
    """ |  | """
    mem_map.dispatch("op_e5: not implemented")

def op_f5(mem_map):
    """ |  | """
    mem_map.dispatch("op_f5: not implemented")

def op_ed(mem_map):
    """ |  | """
    mem_map.dispatch("op_ed: not implemented")

def op_fd(mem_map):
    """ |  | """
    mem_map.dispatch("op_fd: not implemented")

def op_f9(mem_map):
    """ |  | """
    mem_map.dispatch("op_f9: not implemented")

def op_e1(mem_map):
    """ |  | """
    mem_map.dispatch("op_e1: not implemented")

def op_f1(mem_map):
    """ |  | """
    mem_map.dispatch("op_f1: not implemented")

def op_c9(mem_map, low_byte):
    """cmp imm | A-{adr} | NVC"""
    mem_map.dispatch("op_c9: not implemented")

def op_c5(mem_map, low_byte):
    """cmp zp | A-{adr} | NVC"""
    mem_map.dispatch("op_c5: not implemented")

def op_d5(mem_map):
    """ |  | """
    mem_map.dispatch("op_d5: not implemented")

def op_c1(mem_map):
    """ |  | """
    mem_map.dispatch("op_c1: not implemented")

def op_d1(mem_map):
    """ |  | """
    mem_map.dispatch("op_d1: not implemented")

def op_cd(mem_map):
    """ |  | """
    mem_map.dispatch("op_cd: not implemented")

def op_dd(mem_map):
    """ |  | """
    mem_map.dispatch("op_dd: not implemented")

def op_d9(mem_map):
    """ |  | """
    mem_map.dispatch("op_d9: not implemented")

def op_e0(mem_map):
    """ |  | """
    mem_map.dispatch("op_e0: not implemented")

def op_e4(mem_map):
    """ |  | """
    mem_map.dispatch("op_e4: not implemented")

def op_ec(mem_map):
    """ |  | """
    mem_map.dispatch("op_ec: not implemented")

def op_c0(mem_map):
    """ |  | """
    mem_map.dispatch("op_c0: not implemented")

def op_c4(mem_map):
    """ |  | """
    mem_map.dispatch("op_c4: not implemented")

def op_cc(mem_map):
    """ |  | """
    mem_map.dispatch("op_cc: not implemented")

def op_c6(mem_map):
    """ |  | """
    mem_map.dispatch("op_c6: not implemented")

def op_d6(mem_map):
    """ |  | """
    mem_map.dispatch("op_d6: not implemented")

def op_ce(mem_map):
    """ |  | """
    mem_map.dispatch("op_ce: not implemented")

def op_de(mem_map):
    """ |  | """
    mem_map.dispatch("op_de: not implemented")

def op_f6(mem_map):
    """ |  | """
    mem_map.dispatch("op_f6: not implemented")

def op_ee(mem_map):
    """ |  | """
    mem_map.dispatch("op_ee: not implemented")

def op_fe(mem_map):
    """ |  | """
    mem_map.dispatch("op_fe: not implemented")

def op_06(mem_map):
    """ |  | """
    mem_map.dispatch("op_06: not implemented")

def op_16(mem_map):
    """ |  | """
    mem_map.dispatch("op_16: not implemented")

def op_0e(mem_map):
    """ |  | """
    mem_map.dispatch("op_0e: not implemented")

def op_1e(mem_map):
    """ |  | """
    mem_map.dispatch("op_1e: not implemented")

def op_26(mem_map):
    """ |  | """
    mem_map.dispatch("op_26: not implemented")

def op_36(mem_map):
    """ |  | """
    mem_map.dispatch("op_36: not implemented")

def op_2e(mem_map):
    """ |  | """
    mem_map.dispatch("op_2e: not implemented")

def op_3e(mem_map):
    """ |  | """
    mem_map.dispatch("op_3e: not implemented")

def op_4a(mem_map):
    """ |  | """
    mem_map.dispatch("op_4a: not implemented")

def op_46(mem_map):
    """ |  | """
    mem_map.dispatch("op_46: not implemented")

def op_56(mem_map):
    """ |  | """
    mem_map.dispatch("op_56: not implemented")

def op_4e(mem_map):
    """ |  | """
    mem_map.dispatch("op_4e: not implemented")

def op_5e(mem_map):
    """ |  | """
    mem_map.dispatch("op_5e: not implemented")

def op_66(mem_map):
    """ |  | """
    mem_map.dispatch("op_66: not implemented")

def op_76(mem_map):
    """ |  | """
    mem_map.dispatch("op_76: not implemented")

def op_6e(mem_map):
    """ |  | """
    mem_map.dispatch("op_6e: not implemented")

def op_7e(mem_map):
    """ |  | """
    mem_map.dispatch("op_7e: not implemented")

def op_6a(mem_map):
    """ |  | """
    mem_map.dispatch("op_6a: not implemented")

def op_b5(mem_map):
    """ |  | """
    mem_map.dispatch("op_b5: not implemented")

def op_b1(mem_map):
    """ |  | """
    mem_map.dispatch("op_b1: not implemented")

def op_ad(mem_map):
    """ |  | """
    mem_map.dispatch("op_ad: not implemented")

def op_bd(mem_map):
    """ |  | """
    mem_map.dispatch("op_bd: not implemented")

def op_b9(mem_map):
    """ |  | """
    mem_map.dispatch("op_b9: not implemented")

def op_95(mem_map):
    """ |  | """
    mem_map.dispatch("op_95: not implemented")

def op_9d(mem_map):
    """ |  | """
    mem_map.dispatch("op_9d: not implemented")

def op_99(mem_map):
    """ |  | """
    mem_map.dispatch("op_99: not implemented")

def op_81(mem_map):
    """ |  | """
    mem_map.dispatch("op_81: not implemented")

def op_91(mem_map):
    """ |  | """
    mem_map.dispatch("op_91: not implemented")

def op_a6(mem_map):
    """ |  | """
    mem_map.dispatch("op_a6: not implemented")

def op_b6(mem_map):
    """ |  | """
    mem_map.dispatch("op_b6: not implemented")

def op_ae(mem_map):
    """ |  | """
    mem_map.dispatch("op_ae: not implemented")

def op_be(mem_map):
    """ |  | """
    mem_map.dispatch("op_be: not implemented")

def op_96(mem_map):
    """ |  | """
    mem_map.dispatch("op_96: not implemented")

def op_8e(mem_map):
    """ |  | """
    mem_map.dispatch("op_8e: not implemented")

def op_b4(mem_map):
    """ |  | """
    mem_map.dispatch("op_b4: not implemented")

def op_ac(mem_map):
    """ |  | """
    mem_map.dispatch("op_ac: not implemented")

def op_bc(mem_map):
    """ |  | """
    mem_map.dispatch("op_bc: not implemented")

def op_84(mem_map):
    """ |  | """
    mem_map.dispatch("op_84: not implemented")

def op_94(mem_map):
    """ |  | """
    mem_map.dispatch("op_94: not implemented")

def op_10(mem_map):
    """ |  | """
    mem_map.dispatch("op_10: not implemented")

def op_30(mem_map):
    """ |  | """
    mem_map.dispatch("op_30: not implemented")

def op_50(mem_map):
    """ |  | """
    mem_map.dispatch("op_50: not implemented")

def op_70(mem_map):
    """ |  | """
    mem_map.dispatch("op_70: not implemented")

def op_90(mem_map):
    """ |  | """
    mem_map.dispatch("op_90: not implemented")

def op_b0(mem_map):
    """ |  | """
    mem_map.dispatch("op_b0: not implemented")

def op_f0(mem_map, low_byte):
    """beq rel | branch on Z=1 | none"""
    mem_map.dispatch("op_f0: not implemented")

def op_40(mem_map):
    """ |  | """
    mem_map.dispatch("op_40: not implemented")

def op_6c(mem_map):
    """ |  | """
    mem_map.dispatch("op_6c: not implemented")

# ---------------------------------------------------------------------
# ------------------------- lookup tables -----------------------------
# ---------------------------------------------------------------------

class FLAG(object):
    """processor flags"""
    NEG = 128  # NEGATIVE
    OVR = 64   # OVERFLOW
    UND = 32   # UNUSED
    BRK = 16   # BREAK
    DEC = 8    # DECIMAL
    INT = 4    # INTERRUPT
    ZER = 2    # ZERO
    CAR = 1    # CARRY

"""opcode: {(name, mode), func, length}"""
op_table = {
    0x09: {'name': 'ora', 'mode': 'imm', 'func': op_09, 'len': 2},
    0x05: {'name': 'ora', 'mode': 'zp', 'func': op_05, 'len': 2},
    0x15: {'name': 'ora', 'mode': 'zpx', 'func': op_15, 'len': 2},
    0x01: {'name': 'ora', 'mode': 'izx', 'func': op_01, 'len': 2},
    0x11: {'name': 'ora', 'mode': 'izy', 'func': op_11, 'len': 2},
    0x0d: {'name': 'ora', 'mode': 'abs', 'func': op_0d, 'len': 3},
    0x1d: {'name': 'ora', 'mode': 'abx', 'func': op_1d, 'len': 3},
    0x19: {'name': 'ora', 'mode': 'aby', 'func': op_19, 'len': 3},
    0x29: {'name': 'and', 'mode': 'imm', 'func': op_29, 'len': 2},
    0x25: {'name': 'and', 'mode': 'zp', 'func': op_25, 'len': 2},
    0x35: {'name': 'and', 'mode': 'zpx', 'func': op_35, 'len': 2},
    0x21: {'name': 'and', 'mode': 'izx', 'func': op_21, 'len': 2},
    0x31: {'name': 'and', 'mode': 'izy', 'func': op_31, 'len': 2},
    0x2d: {'name': 'and', 'mode': 'abs', 'func': op_2d, 'len': 3},
    0x3d: {'name': 'and', 'mode': 'abx', 'func': op_3d, 'len': 3},
    0x39: {'name': 'and', 'mode': 'aby', 'func': op_39, 'len': 3},
    0x49: {'name': 'eor', 'mode': 'imm', 'func': op_49, 'len': 2},
    0x45: {'name': 'eor', 'mode': 'zp', 'func': op_45, 'len': 2},
    0x55: {'name': 'eor', 'mode': 'zpx', 'func': op_55, 'len': 2},
    0x41: {'name': 'eor', 'mode': 'izx', 'func': op_41, 'len': 2},
    0x51: {'name': 'eor', 'mode': 'izy', 'func': op_51, 'len': 2},
    0x4d: {'name': 'eor', 'mode': 'abs', 'func': op_4d, 'len': 3},
    0x5d: {'name': 'eor', 'mode': 'abx', 'func': op_5d, 'len': 3},
    0x59: {'name': 'eor', 'mode': 'aby', 'func': op_59, 'len': 3},
    0x69: {'name': 'adc', 'mode': 'imm', 'func': op_69, 'len': 2},
    0x65: {'name': 'adc', 'mode': 'zp', 'func': op_65, 'len': 2},
    0x75: {'name': 'adc', 'mode': 'zpx', 'func': op_75, 'len': 2},
    0x61: {'name': 'adc', 'mode': 'izx', 'func': op_61, 'len': 2},
    0x71: {'name': 'adc', 'mode': 'izy', 'func': op_71, 'len': 2},
    0x6d: {'name': 'adc', 'mode': 'abs', 'func': op_6d, 'len': 3},
    0x7d: {'name': 'adc', 'mode': 'abx', 'func': op_7d, 'len': 3},
    0x79: {'name': 'adc', 'mode': 'aby', 'func': op_79, 'len': 3},
    0xe9: {'name': 'sbc', 'mode': 'imm', 'func': op_e9, 'len': 2},
    0xe5: {'name': 'sbc', 'mode': 'zp', 'func': op_e5, 'len': 2},
    0xf5: {'name': 'sbc', 'mode': 'zpx', 'func': op_f5, 'len': 2},
    0xed: {'name': 'sbc', 'mode': 'abs', 'func': op_ed, 'len': 3},
    0xfd: {'name': 'sbc', 'mode': 'abx', 'func': op_fd, 'len': 3},
    0xf9: {'name': 'sbc', 'mode': 'aby', 'func': op_f9, 'len': 3},
    0xe1: {'name': 'sbc', 'mode': 'izx', 'func': op_e1, 'len': 2},
    0xf1: {'name': 'sbc', 'mode': 'izy', 'func': op_f1, 'len': 2},
    0xc9: {'name': 'cmp', 'mode': 'imm', 'func': op_c9, 'len': 2},
    0xc5: {'name': 'cmp', 'mode': 'zp', 'func': op_c5, 'len': 2},
    0xd5: {'name': 'cmp', 'mode': 'zpx', 'func': op_d5, 'len': 2},
    0xc1: {'name': 'cmp', 'mode': 'izx', 'func': op_c1, 'len': 2},
    0xd1: {'name': 'cmp', 'mode': 'izy', 'func': op_d1, 'len': 2},
    0xcd: {'name': 'cmp', 'mode': 'abs', 'func': op_cd, 'len': 3},
    0xdd: {'name': 'cmp', 'mode': 'abx', 'func': op_dd, 'len': 3},
    0xd9: {'name': 'cmp', 'mode': 'aby', 'func': op_d9, 'len': 3},
    0xe0: {'name': 'cpx', 'mode': 'imm', 'func': op_e0, 'len': 2},
    0xe4: {'name': 'cpx', 'mode': 'zp', 'func': op_e4, 'len': 2},
    0xec: {'name': 'cpx', 'mode': 'abs', 'func': op_ec, 'len': 3},
    0xc0: {'name': 'cpy', 'mode': 'imm', 'func': op_c0, 'len': 2},
    0xc4: {'name': 'cpy', 'mode': 'zp', 'func': op_c4, 'len': 2},
    0xcc: {'name': 'cpy', 'mode': 'abs', 'func': op_cc, 'len': 3},
    0xc6: {'name': 'dec', 'mode': 'zp', 'func': op_c6, 'len': 2},
    0xd6: {'name': 'dec', 'mode': 'zpx', 'func': op_d6, 'len': 2},
    0xce: {'name': 'dec', 'mode': 'abs', 'func': op_ce, 'len': 3},
    0xde: {'name': 'dec', 'mode': 'abx', 'func': op_de, 'len': 3},
    0xca: {'name': 'dex', 'mode': 'imp', 'func': op_ca, 'len': 1},
    0x88: {'name': 'dey', 'mode': 'imp', 'func': op_88, 'len': 1},
    0xe6: {'name': 'inc', 'mode': 'zp', 'func': op_e6, 'len': 2},
    0xf6: {'name': 'inc', 'mode': 'zpx', 'func': op_f6, 'len': 2},
    0xee: {'name': 'inc', 'mode': 'abs', 'func': op_ee, 'len': 3},
    0xfe: {'name': 'inc', 'mode': 'abx', 'func': op_fe, 'len': 3},
    0xe8: {'name': 'inx', 'mode': 'imp', 'func': op_e8, 'len': 1},
    0xc8: {'name': 'iny', 'mode': 'imp', 'func': op_c8, 'len': 1},
    0x0a: {'name': 'asl', 'mode': 'imp', 'func': op_0a, 'len': 1},
    0x06: {'name': 'asl', 'mode': 'zp', 'func': op_06, 'len': 2},
    0x16: {'name': 'asl', 'mode': 'zpx', 'func': op_16, 'len': 2},
    0x0e: {'name': 'asl', 'mode': 'abs', 'func': op_0e, 'len': 3},
    0x1e: {'name': 'asl', 'mode': 'abx', 'func': op_1e, 'len': 3},
    0x26: {'name': 'rol', 'mode': 'zp', 'func': op_26, 'len': 2},
    0x36: {'name': 'rol', 'mode': 'zpx', 'func': op_36, 'len': 2},
    0x2e: {'name': 'rol', 'mode': 'abs', 'func': op_2e, 'len': 3},
    0x3e: {'name': 'rol', 'mode': 'abx', 'func': op_3e, 'len': 3},
    0x2a: {'name': 'rol', 'mode': 'imp', 'func': op_2a, 'len': 1},
    0x4a: {'name': 'lsr', 'mode': 'imp', 'func': op_4a, 'len': 1},
    0x46: {'name': 'lsr', 'mode': 'zp', 'func': op_46, 'len': 2},
    0x56: {'name': 'lsr', 'mode': 'zpx', 'func': op_56, 'len': 2},
    0x4e: {'name': 'lsr', 'mode': 'abs', 'func': op_4e, 'len': 3},
    0x5e: {'name': 'lsr', 'mode': 'abx', 'func': op_5e, 'len': 3},
    0x66: {'name': 'ror', 'mode': 'zp', 'func': op_66, 'len': 2},
    0x76: {'name': 'ror', 'mode': 'zpx', 'func': op_76, 'len': 2},
    0x6e: {'name': 'ror', 'mode': 'abs', 'func': op_6e, 'len': 3},
    0x7e: {'name': 'ror', 'mode': 'abx', 'func': op_7e, 'len': 3},
    0x6a: {'name': 'ror', 'mode': 'imp', 'func': op_6a, 'len': 1},
    0xa9: {'name': 'lda', 'mode': 'imm', 'func': op_a9, 'len': 2},
    0xa5: {'name': 'lda', 'mode': 'zp', 'func': op_a5, 'len': 2},
    0xb5: {'name': 'lda', 'mode': 'zpx', 'func': op_b5, 'len': 2},
    0xa1: {'name': 'lda', 'mode': 'izx', 'func': op_a1, 'len': 2},
    0xb1: {'name': 'lda', 'mode': 'izy', 'func': op_b1, 'len': 2},
    0xad: {'name': 'lda', 'mode': 'abs', 'func': op_ad, 'len': 3},
    0xbd: {'name': 'lda', 'mode': 'abx', 'func': op_bd, 'len': 3},
    0xb9: {'name': 'lda', 'mode': 'aby', 'func': op_b9, 'len': 3},
    0x85: {'name': 'sta', 'mode': 'zp', 'func': op_85, 'len': 2},
    0x95: {'name': 'sta', 'mode': 'zpx', 'func': op_95, 'len': 2},
    0x8d: {'name': 'sta', 'mode': 'abs', 'func': op_8d, 'len': 3},
    0x9d: {'name': 'sta', 'mode': 'abx', 'func': op_9d, 'len': 3},
    0x99: {'name': 'sta', 'mode': 'aby', 'func': op_99, 'len': 3},
    0x81: {'name': 'sta', 'mode': 'izx', 'func': op_81, 'len': 2},
    0x91: {'name': 'sta', 'mode': 'izy', 'func': op_91, 'len': 2},
    0xa2: {'name': 'ldx', 'mode': 'imm', 'func': op_a2, 'len': 2},
    0xa6: {'name': 'ldx', 'mode': 'zp', 'func': op_a6, 'len': 2},
    0xb6: {'name': 'ldx', 'mode': 'zpy', 'func': op_b6, 'len': 2},
    0xae: {'name': 'ldx', 'mode': 'abs', 'func': op_ae, 'len': 3},
    0xbe: {'name': 'ldx', 'mode': 'aby', 'func': op_be, 'len': 3},
    0x86: {'name': 'stx', 'mode': 'zp', 'func': op_86, 'len': 2},
    0x96: {'name': 'stx', 'mode': 'zpy', 'func': op_96, 'len': 2},
    0x8e: {'name': 'stx', 'mode': 'abs', 'func': op_8e, 'len': 3},
    0xa0: {'name': 'ldy', 'mode': 'imm', 'func': op_a0, 'len': 2},
    0xa4: {'name': 'ldy', 'mode': 'zp', 'func': op_a4, 'len': 2},
    0xb4: {'name': 'ldy', 'mode': 'zpx', 'func': op_b4, 'len': 2},
    0xac: {'name': 'ldy', 'mode': 'abs', 'func': op_ac, 'len': 3},
    0xbc: {'name': 'ldy', 'mode': 'abx', 'func': op_bc, 'len': 3},
    0x84: {'name': 'sty', 'mode': 'zp', 'func': op_84, 'len': 2},
    0x94: {'name': 'sty', 'mode': 'zpx', 'func': op_94, 'len': 2},
    0x8c: {'name': 'sty', 'mode': 'abs', 'func': op_8c, 'len': 3},
    0xaa: {'name': 'tax', 'mode': 'imp', 'func': op_aa, 'len': 1},
    0x8a: {'name': 'txa', 'mode': 'imp', 'func': op_8a, 'len': 1},
    0xa8: {'name': 'tay', 'mode': 'imp', 'func': op_a8, 'len': 1},
    0x98: {'name': 'tya', 'mode': 'imp', 'func': op_98, 'len': 1},
    0xba: {'name': 'tsx', 'mode': 'imp', 'func': op_ba, 'len': 1},
    0x9a: {'name': 'txs', 'mode': 'imp', 'func': op_9a, 'len': 1},
    0x68: {'name': 'pla', 'mode': 'imp', 'func': op_68, 'len': 1},
    0x48: {'name': 'pha', 'mode': 'imp', 'func': op_48, 'len': 1},
    0x28: {'name': 'plp', 'mode': 'imp', 'func': op_28, 'len': 1},
    0x08: {'name': 'php', 'mode': 'imp', 'func': op_08, 'len': 1},
    0x10: {'name': 'bpl', 'mode': 'rel', 'func': op_10, 'len': 2},
    0x30: {'name': 'bmi', 'mode': 'rel', 'func': op_30, 'len': 2},
    0x50: {'name': 'bvc', 'mode': 'rel', 'func': op_50, 'len': 2},
    0x70: {'name': 'bvs', 'mode': 'rel', 'func': op_70, 'len': 2},
    0x90: {'name': 'bcc', 'mode': 'rel', 'func': op_90, 'len': 2},
    0xb0: {'name': 'bcs', 'mode': 'rel', 'func': op_b0, 'len': 2},
    0xd0: {'name': 'bne', 'mode': 'rel', 'func': op_d0, 'len': 2},
    0xf0: {'name': 'beq', 'mode': 'rel', 'func': op_f0, 'len': 2},
    0x00: {'name': 'brk', 'mode': 'imp', 'func': op_00, 'len': 1},
    0x40: {'name': 'rti', 'mode': 'imp', 'func': op_40, 'len': 1},
    0x20: {'name': 'jsr', 'mode': 'abs', 'func': op_20, 'len': 3},
    0x60: {'name': 'rts', 'mode': 'imp', 'func': op_60, 'len': 1},
    0x4c: {'name': 'jmp', 'mode': 'abs', 'func': op_4c, 'len': 3},
    0x6c: {'name': 'jmp', 'mode': 'ind', 'func': op_6c, 'len': 3},
    0x24: {'name': 'bit', 'mode': 'zp', 'func': op_24, 'len': 2},
    0x2c: {'name': 'bit', 'mode': 'abs', 'func': op_2c, 'len': 3},
    0x18: {'name': 'clc', 'mode': 'imp', 'func': op_18, 'len': 1},
    0x38: {'name': 'sec', 'mode': 'imp', 'func': op_38, 'len': 1},
    0xd8: {'name': 'cld', 'mode': 'imp', 'func': op_d8, 'len': 1},
    0xf8: {'name': 'sed', 'mode': 'imp', 'func': op_f8, 'len': 1},
    0x58: {'name': 'cli', 'mode': 'imp', 'func': op_58, 'len': 1},
    0x78: {'name': 'sei', 'mode': 'imp', 'func': op_78, 'len': 1},
    0xb8: {'name': 'clv', 'mode': 'imp', 'func': op_b8, 'len': 1},
    0xea: {'name': 'nop', 'mode': 'imp', 'func': op_ea, 'len': 1},
}

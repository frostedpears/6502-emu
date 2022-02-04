import os
import sys
sys.path.append(f"{os.path.dirname('.')}")

import emu6502 as emu
import parse6502 as parser
from testlist import tests

def run_all(show_details=True):
    for i in range(0, len(tests)):
        run_test(i, show_details)

def run_test(index, show_details=True):
    e = emu.Emu6502()
    test = get_test(index)
    result = TestResult(test)
    result.name = f"[{index}], \"{test.name}\""

    e.write_list(test.prog_bytes, test.prog_start)
    e.run_range(test.prog_start, test.prog_end)

    result.mem_bytes = e.get_range(test.out_start, test.out_end)
    result.mem_axy = [e.x_mem['a'], e.x_mem['x'], e.x_mem['y']]
    result.mem_flags = e.get_flags_byte()

    result.mem_pass = result.mem_bytes == test.out_bytes
    result.axy_pass = result.mem_axy == test.out_axy
    result.flag_pass = result.mem_flags == test.out_flags

    print_result_header(result)
    if show_details:
        print_result_detailed(result)

def get_test(index):
    return TestUnit(tests[index])

class CTEXT:
    FAIL = '\033[31mFAIL\033[m'
    PASS = '\033[32mPASS\033[m'

def print_result_header(result):
    print(f"{CTEXT.PASS if result.all_pass() else CTEXT.FAIL} {result.name}")

def print_result_detailed(result):
    test = result.test
    print(f"Mem  : {CTEXT.PASS if result.mem_pass else CTEXT.FAIL}")
    if not result.mem_pass:
        print(f"  Emu Mem  : {parser.byte_list_to_hex_str(result.mem_bytes)}")
        print(f"  Expected : {parser.byte_list_to_hex_str(test.out_bytes)}")

    print(f"AXY  : {CTEXT.PASS if result.axy_pass else CTEXT.FAIL}")
    if not result.axy_pass:
        print(f"  Emu AXY  : {parser.byte_list_to_hex_str(result.mem_axy)}")
        print(f"  Expected : {parser.byte_list_to_hex_str(test.out_axy)}")

    print(f"Flags: {CTEXT.PASS if result.flag_pass else CTEXT.FAIL}")
    if not result.flag_pass:
        print(f"             {' '.join('NV-BDIZC')}")
        print(f"  Emu Flags: {' '.join('{:08b}'.format(result.mem_flags))}")
        print(f"  Expected : {' '.join('{:08b}'.format(test.out_flags))}")
    print(f"--------------------------------")


class TestUnit():
    def __init__(self, test_dict):
        self.name = test_dict['name']
        self.prog_start = test_dict['prog_start']
        self.prog_len = test_dict['prog_len']
        self.prog_end = self.prog_start + self.prog_len
        self.prog_bytes = parser.hex_to_byte_list(test_dict['prog_hex'])
        
        self.out_start = test_dict['out_start']
        self.out_len = test_dict['out_len']
        self.out_end = self.out_start + self.out_len
        self.out_bytes = parser.hex_to_byte_list(test_dict['out_hex'])
        self.out_flags = test_dict['out_flags']
        self.out_axy = test_dict['out_reg']


class TestResult():
    def __init__(self, test):
        self.test = test
        self.name = test.name
        self.mem_pass = False
        self.axy_pass = False
        self.flag_pass = False

        self.mem_bytes = None
        self.mem_axy = None
        self.mem_flags = None
    
    def all_pass(self):
        return self.mem_pass and self.axy_pass and self.flag_pass

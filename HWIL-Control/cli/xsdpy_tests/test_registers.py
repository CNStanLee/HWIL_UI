#######################################################################
# Copyright (c) 2023 Xilinx, Inc.  All rights reserved.
#
# This   document  contains  proprietary information  which   is
# protected by  copyright. All rights  are reserved. No  part of
# this  document may be photocopied, reproduced or translated to
# another  program  language  without  prior written  consent of
# XILINX Inc., San Jose, CA. 95124
#
# Xilinx, Inc.
# XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS" AS A
# COURTESY TO YOU.  BY PROVIDING THIS DESIGN, CODE, OR INFORMATION AS
# ONE POSSIBLE   IMPLEMENTATION OF THIS FEATURE, APPLICATION OR
# STANDARD, XILINX IS MAKING NO REPRESENTATION THAT THIS IMPLEMENTATION
# IS FREE FROM ANY CLAIMS OF INFRINGEMENT, AND YOU ARE RESPONSIBLE
# FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE FOR YOUR IMPLEMENTATION.
# XILINX EXPRESSLY DISCLAIMS ANY WARRANTY WHATSOEVER WITH RESPECT TO
# THE ADEQUACY OF THE IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO
# ANY WARRANTIES OR REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE
# FROM CLAIMS OF INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE.
#
#######################################################################
import time

import xsdpy_tests as t
sleep_time = 0.2

class RegisterTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" REGISTERS ")

    def test(self):
        self.test_read_registers()
        self.test_write_registers()

    def test_read_registers(self):
        self.test_rrd()
        self.test_rrd_regs()
        self.test_rrd_reg_path()
        self.test_rrd_reg_definitions()
        self.test_rrd_reg_format_result()
        self.test_rrd_reg_no_bits()
        self.test_rrd_reg_nvlist()
        self.test_rrd_reg_access_mode()

    def test_rrd(self):
        t.test_option(" test_rrd ")
        self.test_rrd_apu()
        self.test_rrd_a9_0()
        self.test_rrd_a9_1()
        self.test_rrd_fpga()

    def test_rrd_regs(self):
        t.test_option(" test_rrd_regs ")
        self.test_rrd_apu_axihp0()
        self.test_rrd_apu_devcfg()
        self.test_rrd_a9_0_r0()
        self.test_rrd_a9_1_usr()
        self.test_rrd_a9_0_cpsr()
        self.test_rrd_a9_0_mpcore()
        self.test_rrd_error_msg()

    def test_rrd_reg_path(self):
        t.test_option(" test_rrd_reg_path ")
        self.test_rrd_apu_swdt_mode()
        self.test_rrd_a9_0_usr_r8()
        self.test_rrd_a9_0_mpcore_icdipr()
        self.test_rrd_a9_0_mpcore_icdipr_ipr95()
        self.test_rrd_a9_0_mpcore_icciar()

    def test_rrd_reg_definitions(self):
        t.test_option(" test_rrd_reg_definitions ")
        self.test_rrd_apu_defs()
        self.test_rrd_a9_0_defs()
        self.test_rrd_a9_0_cpsr_defs()
        self.test_rrd_a9_0_usr_defs()
        self.test_rrd_a9_0_usr_r8_defs()
        self.test_rrd_a9_0_mpcore_defs()

    def test_rrd_reg_format_result(self):
        t.test_option(" test_rrd_reg_format_result ")
        self.test_rrd_apu_format_result()
        self.test_rrd_a9_0_format_result()
        self.test_rrd_a9_0_cpsr_format_result()
        self.test_rrd_a9_0_usr_format_result()
        self.test_rrd_a9_0_usr_r8_format_result()
        self.test_rrd_a9_0_mpcore_format_result()

    def test_rrd_reg_no_bits(self):
        t.test_option(" test_rrd_reg_no_bits ")
        self.test_rrd_apu_swdt_mode_no_bits()
        self.test_rrd_a9_0_cpsr_no_bits()

    def test_rrd_reg_nvlist(self):
        t.test_option(" test_rrd_reg_nvlist ")
        self.test_rrd_apu_nvlist()
        self.test_rrd_a9_0_nvlist()
        self.test_rrd_a9_0_cpsr_nvlist()
        self.test_rrd_a9_0_usr_nvlist()
        self.test_rrd_a9_0_usr_r8_nvlist()
        self.test_rrd_a9_0_mpcore_nvlist()

    def test_rrd_reg_access_mode(self):
        t.test_option(" test_rrd_reg_access_mode ")
        self.test_rrd_apu_access_mode()
        self.test_rrd_a9_0_access_mode_pa()
        self.test_rrd_a9_0_access_mode_r()

    def test_rrd_apu(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Registers")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read Cortex-A9#0 Registers")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_1(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read Cortex-A9#1 Registers")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.rrd()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_fpga(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read FPGA Registers")
        try:
            ta = self.session.targets("--set", filter="name !~ A*")
            ta.rrd()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_axihp0(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU 'axi_hp0'")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd("axi_hp0")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_devcfg(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU 'devcfg'")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd("devcfg")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_r0(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'r0'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd("r0")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_1_usr(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#1 'usr'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.rrd("usr")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_cpsr(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'cpsr'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd("cpsr")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'mpcore'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd("mpcore")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_swdt_mode(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU 'swdt mode'")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd("swdt mode")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_r8(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'usr r8'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd("usr r8")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_icdipr(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'mpcore icdipr'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore icdipr')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_icdipr_ipr95(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'mpcore icdipr ipr95'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore icdipr ipr95')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_icciar(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 'mpcore icciar'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore icciar')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Register Definitions")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd('--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Definitions")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_cpsr_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Definitions 'cpsr'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('cpsr', '--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Definitions 'usr'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('usr', '--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_r8_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Definitions 'usr r8'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('usr r8', '--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Definitions 'mpcore'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore', '--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Register Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_cpsr_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'cpsr' Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('cpsr', '--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'usr' Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('usr', '--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_r8_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'usr r8' Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('usr r8', '--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_format_result(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'mpcore' Format Result")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore', '--format_result')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_swdt_mode_no_bits(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Register 'swdt mode' with no_bits")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            print(":: with bits ::")
            print("")
            ta.rrd('swdt mode')
            print(":: with no-bits ::")
            ta.rrd('swdt mode', '--no_bits')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_cpsr_no_bits(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'cpsr' with no_bits")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(":: with bits ::")
            ta.rrd('cpsr')
            print(":: with no-bits ::")
            ta.rrd('cpsr', '--no_bits')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Registers Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            print(ta.rrd('--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Registers Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(ta.rrd('--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_cpsr_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'cpsr' Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(ta.rrd('cpsr', '--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'usr' Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(ta.rrd('usr', '--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_usr_r8_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'usr r8' Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(ta.rrd('usr r8', '--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_mpcore_nvlist(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'mpcore' Name-Value list")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print(ta.rrd('mpcore', '--nvlist'))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_apu_access_mode(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read APU Register with access mode")
        try:
            ta = self.session.targets("--set", filter="name == APU")
            ta.rrd('mpcore', access_mode='PA')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_access_mode_r(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'mpcore' with access mode R")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore', access_mode='R')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_a9_0_access_mode_pa(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read A9#0 Register 'mpcore' with access mode PA")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore', access_mode='PA')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_rrd_error_msg(self):
        time.sleep(sleep_time)
        t.test_option(" test_rrd_error_msg ")
        t.test_name("TEST: Read A9#0 Register 'mpcore icciar cpuid'")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('mpcore icciar cpuid')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_registers(self):
        time.sleep(sleep_time)
        t.test_option(" test_write_registers ")
        self.test_write_r0()
        self.test_write_cpsr()
        self.test_write_cpsr_m()
        self.test_write_usr_r12()

    def test_write_r0(self):
        t.test_name("TEST: Writing n reading the register 'r0'")
        value = 0x5555aaaa
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rwr('r0', value)
            time.sleep(sleep_time)
            val = ta.rrd('r0', '--nvlist')
            if val['r0'] == value:
                print("Read and write values match -", hex(val['r0']))
            else:
                print(f"Mismatch - write value - {value}, read value {hex(val['r0'])}")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_cpsr(self):
        t.test_name("TEST: Writing n reading the register 'cpsr'")
        value = 0x200001d0
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rwr('cpsr', value)
            time.sleep(sleep_time)
            val = ta.rrd('cpsr', '--nvlist')
            if val['cpsr'] == value:
                print("Read and write values match -", hex(val['cpsr']))
            else:
                print(f"Mismatch - write value - {value}, read value {hex(val['cpsr'])}")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_cpsr_m(self):
        t.test_name("TEST: Writing n reading the register 'cpsr' bit 'm'")
        value = 0x13
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            print("CPSR (before write) -")
            ta.rrd('cpsr')
            ta.rwr('cpsr m', value)
            print("CPSR (after write) -")
            ta.rrd('cpsr')
            time.sleep(sleep_time)
            val = ta.rrd('cpsr m', '--nvlist')
            if val['m'] == value:
                print("Read and write values match -", hex(val['m']))
            else:
                print(f"Mismatch - write value - {value}, read value {hex(val['m'])}")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_usr_r12(self):
        t.test_name("TEST: Writing n reading the register 'usr r12'")
        value = 0xa5a5a5a5
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rwr('usr r12', value)
            time.sleep(sleep_time)
            val = ta.rrd('usr r12', '--nvlist')
            if val['r12'] == value:
                print("Read and write values match -", hex(val['r12']))
            else:
                print(f"Mismatch - write value - {value}, read value {hex(val['r12'])}")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_option_errors(self):
        time.sleep(sleep_time)
        t.test_option(" test_option_errors ")
        t.test_name("TEST: Conflicting args")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.rrd('--nvlist', '--defs', '--format_result')
        except Exception as inst:
            print('!!Error!!', inst)
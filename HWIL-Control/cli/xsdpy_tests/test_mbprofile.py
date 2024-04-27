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
import os
import time

import xsdpy_tests as t


class MbProfileTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" MBProfile ")

    def test(self):
        self.error_tests()
        self.test_mbprofile_normal_flow()
        self.test_mbprofile_normal_flow_with_disassemble()
        self.test_mbtrace()

    def error_tests(self):
        url = "TCP:xhdbfarmrkb8:3121"
        s = self.session
        s.connect(url=url)
        t.try_function(lambda: s.mbprofile(low='low', high='high'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--start'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--stop'), '', sleep=0.1, error=1)
        s.ta(3)
        s.jtag_targets()
        t.try_function(lambda: s.mbprofile(low='low', high='high'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--start'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--stop'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--start', low='low', high='high'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--stop', low='low', high='high'), '', sleep=0.1, error=1)
        s.dow('xsdpy_tests/elfs/mbprofile/hello_lmb.elf')
        t.try_function(lambda: s.mbprofile('--count_instr', low='low', high='high'), '', sleep=0.1, error=0)
        t.try_function(lambda: s.mbprofile('--stop'), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--stop', out="xsdpy_tests/elfs/mbprofile/gmon_inst.out"), '', sleep=0.1, error=1)
        t.try_function(lambda: s.mbprofile('--start'), '', sleep=0.1, error=0)
        t.try_function(lambda: s.mbprofile('--stop'), '', sleep=0.1, error=0)

    def test_mbprofile_normal_flow(self):
        url = "TCP:xhdbfarmrkb8:3121"
        s = self.session
        s.connect(url=url)
        # s.ta()
        # s.fpga(file='xsdpy_tests/elfs/mbprofile/work/mb_prof/design_1_wrapper.bit')
        # time.sleep(1)
        s.ta(3)
        s.jtag_targets()
        s.dow('xsdpy_tests/elfs/mbprofile/hello_lmb.elf')
        # s.bpadd(addr='&_exit')
        s.mbprofile('--count_instr', low='low', high='high')
        # s.mbprofile(low='low', high='high')
        s.mbprofile('--start')
        s.con()
        time.sleep(2)
        s.stop()
        s.mbprofile('--stop', out="xsdpy_tests/elfs/mbprofile/gmon_inst.out")

    def test_mbprofile_normal_flow_with_disassemble(self):
        url = "TCP:xhdbfarmrkb8:3121"
        s = self.session
        s.connect(url=url)
        # s.ta()
        # s.fpga(file='xsdpy_tests/elfs/mbprofile/design_1_wrapper.bit')
        # time.sleep(1)
        s.ta(3)
        s.jtag_targets()
        s.dow('xsdpy_tests/elfs/mbprofile/hello_lmb.elf')
        # s.bpadd(addr='&_exit')
        s.mbprofile(low='low', high='high')
        s.mbprofile('--start')
        s.con()
        time.sleep(2)
        s.stop()
        s.mbprofile('--stop', out="xsdpy_tests/elfs/mbprofile/gmon_inst_1.out")

    def test_mbtrace(self):
        url = "TCP:xhdbfarmrka17:3121"
        s = self.session
        s.connect(url=url)
        # s.ta(1)
        # s.fpga(file='xsdpy_tests/elfs/mbprofile/design_1_wrapper.bit')
        time.sleep(1)
        s.ta(3)
        s.jtag_targets()
        s.dow('xsdpy_tests/elfs/mbprofile/hello_lmb.elf')
        # s.bpadd('main')
        s.bpadd(2508)
        s.bplist()
        # s.mbtrace('--start')
        s.mbtrace('--start', '--halt', level='full')
        s.nxt()
        # s.mbtrace('-f', '--stop', out="xsdpy_tests/elfs/mbprofile/gmon_trace.txt")
        s.mbtrace('-f', '--con', out="xsdpy_tests/elfs/mbprofile/gmon_trace.txt")
        time.sleep(1)
        # s.mbtrace('-f', '--stop', out="xsdpy_tests/elfs/mbprofile/gmon_trace.txt")
        print('End of test')

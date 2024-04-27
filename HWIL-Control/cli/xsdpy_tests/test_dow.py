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
import subprocess
from subprocess import PIPE


class DowTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" DOW ")

    def test(self):
        self.test_dow_elf()
        self.test_dow_verify()
        self.test_fpga()
        self.test_dow_elf_session_object()
        self.test_dow_verify_session_object()
        self.test_fpga_session_object()

    def test_dow_elf_session_object(self):
        t.test_option(" test_dow_elf")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: download elf")
        try:
            self.session.dow('xsdpy_tests/elfs/zynq/core0zynq.elf',auto_stop=True)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download elf with clear bss option and relocate_sections")
        try:
            self.session.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-c', relocate_sections=0x30000000)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download data file")
        try:
            self.session.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_fpga(self):
        t.test_option(" test_fpga")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: configure fpga")
        try:
            tgt.fpga(file='xsdpy_tests/elfs/zynq/zc702.bit')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: wbstar_status")
        try:
            tgt.fpga('--wbstar_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: cor1_status")
        try:
            tgt.fpga('--cor1_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: cor0_status")
        try:
            tgt.fpga('--cor0_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: timer_status")
        try:
            tgt.fpga('--timer_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: boot_status")
        try:
            tgt.fpga('--boot_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: ir_status")
        try:
            tgt.fpga('--ir_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: config_status")
        try:
            tgt.fpga('--config_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: state")
        try:
            tgt.fpga('--state')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_dow_elf(self):
        t.test_option(" test_dow_elf")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: download elf")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf',auto_stop=True)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download elf with clear bss option and relocate_sections")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-c', relocate_sections=0x30000000)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download data file")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_dow_verify(self):
        t.test_option(" test_dow_verify")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download elf and verify")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            tgt.verify('xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download data file and verify")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            tgt.verify('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_dow_verify_session_object(self):
        t.test_option(" test_dow_verify")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download elf and verify")
        try:
            self.session.dow('xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.verify('xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download data file and verify")
        try:
            self.session.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.verify('xsdpy_tests/elfs/zynq/core0zynq.elf', '-d', addr=0x10000000)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_fpga_session_object(self):
        t.test_option(" test_fpga")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: configure fpga")
        try:
            self.session.fpga(file='xsdpy_tests/elfs/zynq/zc702.bit')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: wbstar_status")
        try:
            self.session.fpga('--wbstar_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: cor1_status")
        try:
            self.session.fpga('--cor1_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: cor0_status")
        try:
            self.session.fpga('--cor0_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: timer_status")
        try:
            self.session.fpga('--timer_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: boot_status")
        try:
            self.session.fpga('--boot_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: ir_status")
        try:
            self.session.fpga('--ir_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: config_status")
        try:
            self.session.fpga('--config_status')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: state")
        try:
            self.session.fpga('--state')
        except Exception as inst:
            print('!!Error!!', inst)
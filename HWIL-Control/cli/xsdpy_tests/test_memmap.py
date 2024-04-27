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
import xsdpy_tests as t


class MemmapTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" MEMMAP ")

    def test(self):
        self.test_memmap()
        self.test_osa()

    def test_memmap(self):
        t.test_option(" test_memmap")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: download elf")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-c', relocate_sections=0x20000000)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Add memmap region 0xFC000000 size 0x1000")
        try:
            tgt.memmap(addr=0xFC000000, size=0x1000, flags=3)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memmap list")
        try:
            tgt.memmap('-l')
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: clear memmap region 0xFC000000 size 0x1000")
        try:
            tgt.memmap('-c', addr=0xFC000000)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            tgt.memmap('-l')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_osa(self):
        t.test_option(" test_osa")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: download elf")
        try:
            tgt.dow('xsdpy_tests/elfs/zynq/core0zynq.elf', '-c', relocate_sections=0x20000000)
        except Exception as inst:
            print('!!Error!!', inst)
        tgt.memmap('-l')
        t.test_name("TEST: enable osa to the symbol file")
        try:
            tgt.osa('--fast_step', file='xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)
        tgt.memmap('-l')
        t.test_name("TEST: disable osa to the symbol file")
        try:
            tgt.osa('--disable', file='xsdpy_tests/elfs/zynq/core0zynq.elf')
        except Exception as inst:
            print('!!Error!!', inst)
        tgt.memmap('-l')

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


class ProfileTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" Profile ")

    def test(self):
        # self.error_tests()
        self.test_normal_flow()

    def error_tests(self):
        url = "TCP:xhdbfarmrke9:3121"
        s = self.session
        s.connect(url=url)
        s.ta(2)
        t.try_function(lambda: s.profile(out="tests/data/gmon_inst.out"), '', sleep=0.1, error=1)
        t.try_function(lambda: s.profile(freq=10000), '', sleep=0.1, error=1)
        t.try_function(lambda: s.profile(freq=10000, addr=0x30000000), '', sleep=0.1, error=0)
        t.try_function(lambda: s.profile(freq=10000, addr=0x30000000), '', sleep=0.1, error=0)
        t.try_function(lambda: s.profile(out="tests/data/gmon_inst.out"), '', sleep=0.1, error=1)  # no dow
        s.dow('xsdpy_tests/elfs/zynq/zynq_prof.elf')
        s.con()
        time.sleep(1)
        s.stop()
        t.try_function(lambda: s.profile(out="tests/data/gmon_inst.out"), '', sleep=0.1, error=0)
        t.try_function(lambda: s.profile(freq=10000, addr=0x30000000), '', sleep=0.1, error=0)
        s.dow('xsdpy_tests/elfs/zynq/zynq_prof.elf')
        s.con()
        time.sleep(1)
        s.stop()
        t.try_function(lambda: s.profile(out="tests/data/gmon_inst.out"), '', sleep=0.1, error=0)
        t.try_function(lambda: s.profile(out="tests/data/gmon_inst.out"), '', sleep=0.1, error=1)

    def test_normal_flow(self):
        url = "TCP:xhdbfarmrke9:3121"
        s = self.session
        s.connect(url=url)
        s.ta(2)
        s.profile(freq=10000, addr=0x30000000)
        s.dow('xsdpy_tests/elfs/zynq/zynq_prof.elf')
        s.con()
        time.sleep(1)
        s.stop()
        s.profile(out="tests/data/gmon_inst.out")

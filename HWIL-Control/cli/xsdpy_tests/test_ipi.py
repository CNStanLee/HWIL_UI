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




class IpiTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" IPI ")

    def test(self):
        # s.device_program('xsdpy_tests/elfs/versal/vck190.pdi')
        self.test_pmc()
        self.test_plm()
        self.error_tests()

    def error_tests(self):
        s = self.session
        s.ta(1)
        t.try_function(lambda: s.pmc('generic', [0x10241, 0x1c000000], 7, response_size=1), '', sleep=0.1, error=1)
        t.try_function(lambda: s.pmc('generic', [0x10241, 0x1c000000, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2], response_size=1), '', sleep=0.1, error=1)
        t.try_function(lambda: s.pmc('get_board', [0xffff0000]), '', sleep=0.1, error=1)
        t.try_function(lambda: s.pmc('adsf', [0xffff0000]), '', sleep=0.1, error=1)
        t.try_function(lambda: s.plm_set_log_level(5), '', sleep=0.1, error=1)

    def test_pmc(self):
        s = self.session
        s.ta(1)
        print(s.pmc('generic', [0x10241, 0x1c000000], response_size=1))
        print(s.pmc('get_board', [0xffff0000, 0x100]))
        print(s.pmc(cmd='generic', data=[0x1030115, 0xffff0000, 0x100], response_size=2))

    def test_plm(self):
        s = self.session
        s.ta(1)
        s.plm_set_log_level(4)
        s.plm_set_debug_log(0x0, 0x4000)
        s.plm_copy_debug_log(0x0)
        s.plm_log(0x0, 0x4000)
        f = open('xsdpy_tests/data/plm.log', 'w')
        s.plm_log(0x0, 0x4000, handle=f)
        f.close()


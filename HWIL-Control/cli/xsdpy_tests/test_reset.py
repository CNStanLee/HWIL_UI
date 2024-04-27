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


class ResetTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" Reset Tests")

    def test(self):
        self.test_reset_on_zynq()
        self.test_error_reset_on_zynq()

    def test_error_reset_on_zynq(self):
        s = self.session
        for i in range(1, 5):
            s.target(i)
            t.try_function(lambda: s.rst(type='coasdres'), f'target = {i}, type=coasdres', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--start', type='dap'), f'target = {i}, --start, type=dap', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--stop', type='dap'), f'target = {i}, --stop, type=dap', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--start', type='srst'), f'target = {i}, --start, type=srst', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--stop', type='srst'), f'target = {i}, --stop, type=srst', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--start', type='por'), f'target = {i}, --start, type=por', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--stop', type='por'), f'target = {i}, --stop, type=por', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--start', type='ps'), f'target = {i}, --start, type=ps', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--stop', type='ps'), f'target = {i}, --stop, type=ps', sleep=0.1, error=1)
            t.try_function(lambda: s.rst(endianness='le', type='dap'), f'target = {i}, endianness=le, type=dap', sleep=0.1, error=1)
            t.try_function(lambda: s.rst(code_endianness='le', type='dap'), f'target = {i}, code_endianness=le, type=dap', sleep=0.1, error=1)
            t.try_function(lambda: s.rst(isa='ARM', type='srst'), f'target = {i}, isa=ARM, type=srst', sleep=0.1, error=1)
            t.try_function(lambda: s.rst(isasdfa='ARM', type='srst'), f'target = {i}, isasdfa=ARM, type=srst', sleep=0.1, error=1)
            t.try_function(lambda: s.rst('--stop', isa='ASRM', type='cores'), f'target = {i}, --stop, isa=ASRM, type=cores', sleep=0, error=1)

    def test_reset_on_zynq(self):
        s = self.session
        for i in range(1, 5):
            s.target(i)
            t.try_function(lambda: s.rst('--stop', endianness='le', type='cores'), f'target = {i} --stop, endianness=le, type=cores', sleep=0.5, error=1 if i == 4 else 0)
            t.try_function(lambda: s.rst('--start', type='cores'), f'target = {i} --start, type=cores', sleep=0.5, error=1 if i == 4 else 0)
            t.try_function(lambda: s.rst('--stop', isa='ARM', type='cores'), f'target = {i} --stop, isa=ARM, type=cores', sleep=0.5, error=1 if i == 4 else 0)
            t.try_function(lambda: s.rst(type='ps'), f'target = {i} type=ps', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='srst'), f'target = {i} type=srst', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='por'), f'target = {i} type=por', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='dap'), f'target = {i} type=dap', sleep=0.5, error=1 if i == 4 else 0)
            t.try_function(lambda: s.rst(type='proc'), f'target = {i} type=proc', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='system'), f'target = {i} type=system', sleep=0.5, error=1 if i == 4 else 0)
            t.try_function(lambda: s.rst(type='pl-srst'), f'target = {i} type=pl-srst', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='pl-por'), f'target = {i} type=pl-por', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='pmc-por'), f'target = {i} type=pmc-por', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='pmc-srst'), f'target = {i} type=pmc-srst', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='ps-por'), f'target = {i} type=ps-por', sleep=0.5, error=1)
            t.try_function(lambda: s.rst(type='ps-srst'), f'target = {i} type=ps-srst', sleep=0.5, error=1)

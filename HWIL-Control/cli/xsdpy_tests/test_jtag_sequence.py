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


class JtagSequenceTests(object):
    def __init__(self, session, url):
        self.session = session
        self.url = url
        t.test_group(" JTAG SEQUENCE")

    def test(self):
        self.test_jtag_sequence_cmds()

    def test_jtag_sequence_cmds(self):
        global index
        t.test_option(" test_jtag_sequence_cmds ")
        t.test_name("TEST: Jtag Sequence commands 1")
        s = self.session
        jt3 = s.jtag_targets(3)
        jseq = jt3.sequence()
        jseq.state("RESET")
        jseq.delay(100)
        jseq.atomic()
        # jseq.get_pin('TDI')
        # jseq.set_pin('TDI', 0)
        # jseq.get_pin('TDI')
        # jseq.set_pin('TDI', 1)
        # jseq.get_pin('TDI')
        jseq.drshift(capture=True, state="IDLE", tdi=0, bit_len=2)
        print(jseq.run())
        jseq.clear()
        del jseq

        t.test_name("TEST: Jtag Sequence commands 2")
        jseq = jt3.sequence()
        jseq.state("RESET")
        jseq.delay(100)
        jseq.atomic()
        # jseq.get_pin('TDI')
        # jseq.set_pin('TDI', 0)
        # jseq.get_pin('TDI')
        # jseq.set_pin('TDI', 1)
        # jseq.get_pin('TDI')
        jseq.irshift(register='bypass', state="IRUPDATE")
        jseq.irshift(tdi=0, bit_len=256)
        jseq.drshift(False, state="DRUPDATE", bit_len=8, data=0b01010010)
        jseq.drshift(state="DRUPDATE", bit_len=8, data='01010010')
        jseq.drshift(state="DRUPDATE", bit_len=32, data=0xAABBCCDD)
        jseq.drshift(state="DRUPDATE", bit_len=32, data=5543453)
        jseq.drshift(state='IDLE', tdi=6, bit_len=2)
        print(jseq.run('--single', '--binary'))
        jseq.clear()
        del jseq

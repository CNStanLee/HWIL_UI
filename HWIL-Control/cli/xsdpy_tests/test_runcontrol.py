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


class RunControlTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" RUN CONTROL ")

    def test(self):
        self.test_stop_cores()
        self.test_resume_cores()
        self.test_stop_container()
        self.test_resume_container()
        self.test_step()
        self.test_stpi()
        self.test_stpout()
        self.test_nxt()
        self.test_nxti()
        self.test_disassembly()

    def test_disassembly(self):
        t.test_option(" test_disassembly")
        tgt = self.session.targets(id=2)
        try:
            tgt.dis(0x00100000)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            tgt.dis(0x00100000, 5)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_stop_cores(self):
        t.test_option(" test_stop_cores")
        t.test_name("TEST: Stop target A9-0 from Target object")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.stop()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Stop target A9-1 from Session object")
        try:
            self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            self.session.stop()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_resume_cores(self):
        t.test_option(" test_resume_cores")
        t.test_name("TEST: Resume target A9-0 from session object")
        try:
            self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            self.session.con()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Resume target A9-1 from target object")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.con()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_stop_container(self):
        t.test_option(" test_stop_container ")
        t.test_name("TEST: Stop targets under APU")
        try:
            self.session.targets("--set", filter="name == APU")
            self.session.stop()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_resume_container(self):
        t.test_option(" test_resume_container ")
        t.test_name("TEST: Resume targets under APU")
        try:
            self.session.targets("--set", filter="name == APU")
            self.session.con()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_step(self):
        t.test_option(" test_step_in ")
        ta = self.session.targets("--set", filter="name == APU")
        ta.stop()
        t.test_name("TEST: Step in once for A9#0")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            ta.stp(1)
            self.session.targets()

        t.test_name("TEST: Step in twice for A9#1")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.stp(2)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_stpi(self):
        t.test_option(" test_step_instruction ")
        ta = self.session.targets("--set", filter="name == APU")
        ta.stop()
        t.test_name("TEST: Step instruction for A9#0")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.stpi(1)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_stpout(self):
        t.test_option(" test_step_out ")
        t.test_name("TEST: Step out for A9#1")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.stpout()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_nxt(self):
        t.test_option(" test_next ")
        t.test_name("TEST: Step Over (Next line) for A9#1")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
            ta.nxt()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_nxti(self):
        t.test_option(" test_next_instruction ")
        t.test_name("TEST: Step Over (Next line) instruction for A9#0")
        try:
            ta = self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #0")
            ta.nxti()
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

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


class BreakpointTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" BREAKPOINTS ")

    def test(self):
        self.breakpoints_test_using_bp_obj()
        self.breakpoints_test_using_tgt_obj()
        self.breakpoints_test_using_session_obj()
        self.breakpoints_test_with_ct_ios()

    def breakpoints_test_using_bp_obj(self):
        t.test_option(" breakpoints_test_using_bp_obj")
        try:
            t1 = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        # try:
        t1.bplist()
        # except Exception as inst:
        #    print('!!Error!!', inst)
        t.test_name("TEST: Add a breakpoint at main")
        try:
            b1 = t1.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: List of breakpoints")
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Breakpoint status at main")
        try:
            print(b1.status())
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Disable breakpoint at main")
        try:
            b1.disable()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Breakpoint status at main")
        try:
            b1.status()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Enable breakpoint at main")
        try:
            b1.enable()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Breakpoint status at main")
        try:
            b1.status()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Remove breakpoint at main")
        try:
            b1.remove()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: List of breakpoints")
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)

    def breakpoints_test_using_tgt_obj(self):
        t.test_option(" breakpoints_test_using_tgt_obj")
        try:
            t1 = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Add four breakpoints at main and verify list")
        try:
            t1.bpadd(addr='main', type='hw', mode=2)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bpadd(addr='main', type='sw', mode=3)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Disable [1,2] breakpoints and verify list")
        try:
            t1.bpdisable(bp_ids=[1, 2])
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Enable [1,2] breakpoints and verify list")
        try:
            t1.bpenable(bp_ids=[1, 2])
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Disable 1st breakpoint and verify list")
        try:
            t1.bpdisable(bp_ids=1)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Enable 1st breakpoint and verify list")
        try:
            t1.bpenable(bp_ids=1)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bpstatus(bp_id=3)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Remove [1] breakpoints and verify list")
        # try:
        #     t1.bpremove(bp_ids=[1])
        # except Exception as inst:
        #     print('!!Error!!', inst)
        # try:
        #     t1.bplist()
        # except Exception as inst:
        #     print('!!Error!!', inst)
        # t.test_name("TEST: Remove 2nd breakpoint and verify list")
        # try:
        #     t1.bpremove(bp_ids=2)
        # except Exception as inst:
        #     print('!!Error!!', inst)
        # try:
        #     t1.bplist()
        # except Exception as inst:
        #     print('!!Error!!', inst)
        t.test_name("TEST: Remove \"-all\" breakpoints and verify list")
        try:
            t1.bpremove('--all')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)

    def breakpoints_test_using_session_obj(self):
        t.test_option(" breakpoints_test_using_session_obj")
        try:
            t1 = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Add four breakpoints at main and verify list")
        try:
            self.session.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bpadd(addr='main')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Disable [5,6] breakpoints and verify list")
        try:
            self.session.bpdisable(bp_ids=[5, 6])
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Enable [5, 6] breakpoints and verify list")
        try:
            self.session.bpenable(bp_ids=[5, 6])
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Disable 5th breakpoint and verify list")
        try:
            self.session.bpdisable(bp_ids=5)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Enable 5th breakpoint and verify list")
        try:
            self.session.bpenable(bp_ids=5)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Remove [5] breakpoints and verify list")
        try:
            self.session.bpremove(bp_ids=[5])
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Remove 6th breakpoint and verify list")
        try:
            self.session.bpremove(bp_ids=6)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Remove \"-all\" breakpoints and verify list")
        try:
            self.session.bpremove('--all')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.bplist()
        except Exception as inst:
            print('!!Error!!', inst)

    def breakpoints_test_with_ct_ios(self):
        try:
            t1 = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: Add breakpoint with ct_input 0 and ct_output 8")
        try:
            t1.bpadd(ct_input=0, ct_output=8, skip_on_step=1)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            t1.bplist()
        except Exception as inst:
            print('!!Error!!', inst)

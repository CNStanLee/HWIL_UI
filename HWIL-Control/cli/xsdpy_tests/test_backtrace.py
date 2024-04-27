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


class StackTraceTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" STACKTRACE ")

    def test(self):
        self.test_stacktrace()

    def test_stacktrace(self):
        t.test_option(" test_stacktrace ")
        try:
            self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.stop()
        try:
            self.session.targets()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: stacktrace without max-frames option")
        try:
            self.session.backtrace()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: stacktrace with max-frames option")
        try:
            self.session.backtrace(5)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.targets(id=3)
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.targets()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: stacktrace with target that is not running elf")
        try:
            self.session.backtrace()
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        # t.test_name("TEST: stacktrace with target that doesnot has state")
        # self.session.targets(id=1)
        # self.session.targets()
        # self.session.backtrace()

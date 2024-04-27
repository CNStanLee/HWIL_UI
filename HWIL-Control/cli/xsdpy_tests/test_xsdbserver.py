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




class XsdbserverTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" XSDBSERVER ")

    def test(self):
        self.func_test()
        # self.error_tests()

    def error_tests(self):
        s = self.session
        s.ta(1)
        t.try_function(lambda: s.xsdbserver_version(), '', sleep=0.1, error=1)
        t.try_function(lambda: s.xsdbserver_stop(), '', sleep=0.1, error=1)
        t.try_function(lambda: s.xsdbserver_disconnect(), '', sleep=0.1, error=1)
        t.try_function(lambda: s.xsdbserver_start(), '', sleep=1, error=0)
        t.try_function(lambda: s.xsdbserver_disconnect(), '', sleep=0.1, error=1)
        t.try_function(lambda: s.xsdbserver_start(), '', sleep=0.1, error=1)
        t.try_function(lambda: s.xsdbserver_stop(), '', sleep=0.1, error=0)

    def func_test(self):
        s = self.session
        s.xsdbserver_start()
        time.sleep(30)
        s.xsdbserver_version()
        s.xsdbserver_disconnect()
        time.sleep(5)
        s.xsdbserver_stop()
        time.sleep(5)
        s.xsdbserver_start()
        while True:
            time.sleep(1)
        # s.xsdbserver_stop()


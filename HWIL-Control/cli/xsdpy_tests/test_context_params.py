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
sleep_time = 0.2

class ContextParamsTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" CONTEXT PARAMETERS ")

    def test(self):
        self.test_context_params()
        self.test_read_context_params()
        self.test_write_context_params()

    def test_context_params(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read context parameters")
        try:
            self.session.configparams()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_read_context_params(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read context parameters xvc-timeout")
        try:
            self.session.configparams('xvc-timeout')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params(self):
        self.test_write_context_params_integer()
        self.test_write_context_params_integer_error()
        self.test_write_context_params_boolean()
        self.test_write_context_params_boolean_error()
        self.test_write_context_params_string()
        self.test_write_context_params_string_error()

    def test_write_context_params_integer(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters integer xvc-timeout")
        try:
            self.session.configparams('xvc-timeout', 288)
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('xvc-timeout')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params_integer_error(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters integer xvc-timeout error")
        try:
            self.session.configparams('xvc-timeout', 'avc')
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('xvc-timeout')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params_boolean(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters boolean debug-poll-enable")
        try:
            self.session.configparams('debug-poll-enable', True)
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('debug-poll-enable')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params_boolean_error(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters boolean debug-poll-enable error")
        try:
            self.session.configparams('debug-poll-enable', 288)
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('debug-poll-enable')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params_string(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters string xvc-capabilities")
        try:
            self.session.configparams('xvc-capabilities', 'control')
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('xvc-capabilities')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_context_params_string_error(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write context parameters string xvc-capabilities error")
        try:
            self.session.configparams('xvc-capabilities', '12345')
        except Exception as inst:
            print('!!Error!!', inst)

        try:
            self.session.configparams('xvc-capabilities')
        except Exception as inst:
            print('!!Error!!', inst)
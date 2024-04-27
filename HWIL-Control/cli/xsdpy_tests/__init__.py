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
import sys
import time

import xsdb
from . import test_targets, test_tfile, test_jtag_targets, test_stapl, test_breakpoints, test_streams, test_mbprofile, \
    test_profile, test_runcontrol, test_connections, test_backtrace, test_memory, test_dow, test_reset, \
    test_memmap, test_device_cmds, test_jtag_sequence, test_registers, test_variables, test_expressions, \
    test_context_params, test_ipi, test_xsdbserver


def test_group(test):
    print("\n\n<********************************************************************>")
    print("\t\t\t", test)
    print("<********************************************************************> ")


def test_option(test):
    print("\n----------------------------------------------------------------------")
    print(test)
    print("----------------------------------------------------------------------")


def test_name(test):
    print("\n ----- " + test + " ----- ")
    time.sleep(0.3)


def try_function(function, desc=None, sleep=0, error=0):
    if desc is not None:
        test_name(desc)
    if error == 1:
        print('\n--Error Expected--')
        try:
            ret = function()
            if ret is not None:
                print(ret)
            raise Exception('Error expected but test is successful') from None
        except Exception as inst:
            if inst.args[0] == 'Error expected but test is successful':
                raise Exception('!!Error!!', inst) from None
            print('!!Error!!', inst)
    else:
        try:
            ret = function()
            if ret is not None:
                print(ret)
        except Exception as inst:
            raise Exception('Error not expected but got : ', inst) from None
    if sleep:
        time.sleep(sleep)


def run_test_set1(s, chan, url):
    t = test_connections.ConnectionsTests(s, chan, url)
    t.test()
    tgt = test_targets.TargetTests(s, url)
    tgt.test()
    rc = test_runcontrol.RunControlTests(s)
    rc.test()
    bt = test_backtrace.StackTraceTests(s)
    bt.test()
    mem = test_memory.MemoryTests(s)
    mem.test()
    bp = test_breakpoints.BreakpointTests(s)
    bp.test()
    reg = test_registers.RegisterTests(s)
    reg.test()
    var = test_variables.VariableTests(s)
    var.test()
    exp = test_expressions.ExpressionTests(s)
    exp.test()
    cp = test_context_params.ContextParamsTests(s)
    cp.test()


def run_test_dow(s):
    dow = test_dow.DowTests(s)
    dow.test()
    mm = test_memmap.MemmapTests(s)
    mm.test()


def run_test_stfile(s):
    tf = test_tfile.TFileTests(s)
    tf.test()


def run_test_jtag_targets_on_sim(s, chan, url):
    # In case of simulation environment, Connect to local host,
    # create Versal virtual targets using below stapl commands(remove comment for the first two commented code lines).
    # st = s.stapl()
    # st.config(out="xsdpy_tests/data/pystapl.stapl", scan_chain=[{'name': 'xcvc1902'}, {'name': 'xcvm1802'}])
    dc = test_device_cmds.DeviceCommandsTests(s)
    dc.test()
    jt = test_jtag_targets.JtagTargetTests(s, url)
    jt.test()
    jts = test_jtag_sequence.JtagSequenceTests(s, url)
    jts.test()
    sys.exit()


def run_test_stapl_on_sim(s):
    # Connect to local host, create Versal virtual targets using stapl commands
    stapl = test_stapl.StaplTests(s)
    stapl.test()


def run_streams_tests(s):
    streams = test_streams.StreamsTests(s)
    streams.test()
    while True:
        time.sleep(1)


def run_mbprofile_tests(s):
    mb = test_mbprofile.MbProfileTests(s)
    mb.test()


def run_profile_tests(s):
    p = test_profile.ProfileTests(s)
    p.test()


def run_ipi_tests(s):
    i = test_ipi.IpiTests(s)
    i.test()


def run_reset_tests(s):
    # r = test_reset.ResetTests(s)
    # r.test()
    print('pass')


def run_xsdbserver_tests(s):
    r = test_xsdbserver.XsdbserverTests(s)
    r.test()
    print('Pass')


def run_tests(s, chan, url):
    # run_test_set1(s, chan, url)
    # run_test_dow(s)
    # run_test_stfile(s)
    # run_test_jtag_targets_on_sim(s, chan, url)
    # run_test_stapl_on_sim(s)
    # run_streams_tests(s)
    # run_reset_tests(s)
    # run_mbprofile_tests(s)
    # run_profile_tests(s)
    # run_ipi_tests(s)
    # run_xsdbserver_tests(s)
    print("\n\nTESTS DONE")

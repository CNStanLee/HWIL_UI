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

import xsdpy_tests as t


class StaplTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" STAPL ")

    def test(self):
        # Run one test at a time
        # self.test_stapl_with_file_input()
        self.test_stapl_with_file_descriptor_input()

    def test_stapl_with_file_descriptor_input(self):
        t.test_option(" test_stapl")
        try:
            st = self.session.stapl()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("Remove stapl file. Ignore error if already removed")
        try:
            os.remove("tests/data/pystapl.stapl")
        except Exception as inst:
            print('!!Error!!', inst)

        handle = open("tests/data/pystapl.stapl", "w+b")
        t.test_option("config stapl devices")
        st.config('-c', handle=handle, part=['xcvc1902', 'xcvm1802'])

        t.test_option("select target")
        try:
            self.session.targets(2)
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.targets()

        t.test_option("select jtag target")
        try:
            self.session.jtag_targets('-s', filter='name == xcvc1902')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_option("start stapl")
        try:
            st.start()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("device program")
        try:
            self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("select target")
        try:
            self.session.targets(4)
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.targets()

        t.test_option("select jtag target")
        try:
            self.session.jtag_targets('-s', filter='name == xcvm1802')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_option("start stapl")
        try:
            st.start()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("device program")
        try:
            self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("stop stapl")
        try:
            st.stop()
        except Exception as inst:
            print('!!Error!!', inst)
        handle.close()
        exit()

    def test_stapl_with_file_input(self):
        t.test_option(" test_stapl")
        try:
            st = self.session.stapl()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("Remove stapl file. Ignore error if already removed")
        try:
            os.remove("tests/data/pystapl.stapl")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("config stapl devices")
        st.config(out="tests/data/pystapl.stapl", scan_chain=[{'name': 'xcvc1902'}, {'name': 'xcvm1802'}])

        t.test_option("select target")
        try:
            self.session.targets(2)
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.targets()

        t.test_option("select jtag target")
        try:
            self.session.jtag_targets('-s', filter='name == xcvc1902')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_option("start stapl")
        try:
            st.start()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("device program")
        try:
            self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("select target")
        try:
            self.session.targets(4)
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.targets()

        t.test_option("select jtag target")
        try:
            self.session.jtag_targets('-s', filter='name == xcvm1802')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_option("start stapl")
        try:
            st.start()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("device program")
        try:
            self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_option("stop stapl")
        try:
            st.stop()
        except Exception as inst:
            print('!!Error!!', inst)
        exit()


    # def configtest(self, **kwargs):
    #     exec_in_dispatch_thread(self.__add_target, 'target000')
    #     device_list = kwargs.get('devices')
    #     for device in device_list:
    #         exec_in_dispatch_thread(self.__add_device, "jsn-XNC-target000", device, 0, 0, 0, 0)
    #     exec_in_dispatch_thread(self.__add_target, 'target001')
    #     device_list = kwargs.get('devices')
    #     for device in device_list:
    #         exec_in_dispatch_thread(self.__add_device, "jsn-XNC-target001", device, 0, 0, 0, 0)
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


class JtagTargetTests(object):
    def __init__(self, session, url):
        self.session = session
        self.url = url
        t.test_group(" JTAG TARGETS ")

    def test(self):
        self.test_jtag_targets_no_active_connection()
        self.test_jtag_targets()
        self.test_jtag_targets_id()
        self.test_jtag_targets_id_error()
        self.test_jtag_targets_multiple_filters()
        self.test_jtag_targets_filter()
        self.test_jtag_targets_filter_set_name()
        self.test_jtag_targets_properties()
        self.test_jtag_targets_close_open_port()
        self.test_jtag_commands()
        self.test_jtag_commands_session_object()

    def test_jtag_targets(self):
        global index
        t.test_option(" test_jtag_targets ")
        t.test_name("TEST: JTAG Targets list")
        self.session.jtag_targets()

    def test_jtag_targets_id(self):
        t.test_option(" test_jtag_targets id ")
        t.test_name("TEST: JTAG Targets id 2")
        try:
            self.session.jtag_targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.jtag_targets()

        t.test_name("TEST: JTAG Targets id 8")
        try:
            self.session.jtag_targets(8)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.jtag_targets()

    def test_jtag_targets_id_error(self):
        t.test_option(" test_jtag_targets_id_error ")
        t.test_name("TEST: JTAG Targets id error")
        try:
            self.session.jtag_targets("id=3", id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.jtag_targets()

    def test_jtag_targets_filter(self):
        t.test_option(" test_jtag_targets_filter ")
        self.session.jtag_targets()
        t.test_name("TEST: JTAG Targets name filter with == : 'name == xcvc1902'")
        try:
            self.session.jtag_targets(filter="name == xcvc1902")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_name("TEST: JTAG Targets name filter with =~ : 'name !~ ARM*'")
        try:
            self.session.jtag_targets(filter="name !~ arm*")
            self.session.jtag_targets('-n', filter="name !~ XCVC*")
            self.session.jtag_targets(filter="level != 1")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

    def test_jtag_targets_filter_set_name(self):
        t.test_option(" test_jtag_targets_filter_set_name ")
        t.test_name("TEST: JTAG Targets option set and name filter with == : 'name == xcvc1902'")
        try:
            self.session.jtag_targets('-s', filter="name == xcvc1902")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.jtag_targets()

    def test_jtag_targets_properties(self):
        t.test_option(" test_jtag_targets_properties ")
        t.test_name("TEST: JTAG Targets properties'")
        try:
            print(self.session.jtag_targets('-t'))
            print(self.session.jtag_targets('-t', id=3))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_jtag_targets_no_active_connection(self):
        t.test_option(" test_jtag_targets_no_active_connection ")
        t.test_name("TEST: JTAG Targets when no active connection")
        try:
            self.session.disconnect(self.session.curchan)
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)
            self.session.connect(url=self.url)
            # create stapl targets again in case of virtual tgts

    def test_jtag_targets_close_open_port(self):
        t.test_option(" test_jtag_targets_close_open_port ")
        try:
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: close jtag port")
        try:
            self.session.jtag_targets('-c')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            self.session.targets('-s', filter='name == DAP')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.targets()
        time.sleep(0.5)
        t.test_name("TEST: open  jtag port")
        try:
            self.session.jtag_targets('-o')
        except Exception as inst:
            print('!!Error!!', inst)
        time.sleep(0.2)

    def test_jtag_commands(self):
        t.test_option(" test_jtag_commands ")
        t.test_name("TEST: Select jtag target")
        try:
            self.session.jtag_targets()
            jt = self.session.jtag_targets(1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: jtag lock")
        try:
            jt.lock(100)
        except Exception as inst:
            print('!!Error!!', inst)
        time.sleep(0.2)
        t.test_name("TEST: jtag unlock")
        try:
            jt.unlock()
        except Exception as inst:
            print('!!Error!!', inst)
        # t.test_name("TEST: claim jtag")
        # try:
        #     jt.claim()
        # except Exception as inst:
        #     print('!!Error!!', inst)
        # time.sleep(0.2)
        # t.test_name("TEST: disclaim jtag")
        # try:
        #     jt.disclaim()
        # except Exception as inst:
        #     print('!!Error!!', inst)

        t.test_name("TEST: print jtag skew")
        try:
            print(jt.skew())
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag frequency")
        try:
            freq = jt.frequency()
            print(freq)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print supported jtag frequencies")
        try:
            print(jt.frequency('-l'))
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: set jtag freq")
        try:
            print(jt.frequency(freq))
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag servers")
        try:
            jt.servers()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag servers with format option")
        try:
            jt.servers('-f')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: open jtag server")
        try:
            jt.servers(open='xilinx-xvc:localhost:10200')
        except Exception as inst:
            print('!!Error!!', inst)
        time.sleep(0.2)
        t.test_name("TEST: get jtag targets")
        try:
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: get jtag servers")
        try:
            jt.servers()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: close jtag server")
        try:
            jt.servers(close='xilinx-xvc:localhost:10200')
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: get jtag targets")
        try:
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: jtag device properties")
        try:
            print(jt.device_properties(0x6ba00477))
        except Exception as inst:
            print('!!Error!!', inst)

        # t.test_name("TEST: set jtag device properties")
        # try:
        #     props = {'idcode': 0x6ba00477, 'irlen': 4}
        #     jt.device_properties(props=props)
        # except Exception as inst:
        #     print('!!Error!!', inst)

        t.test_name("TEST: jtag device properties")
        try:
            print(jt.device_properties(0x6ba00477))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_jtag_commands_session_object(self):
        time.sleep(2)
        t.test_option(" test_jtag_commands_session_object ")
        t.test_name("TEST: Select jtag target")
        try:
            self.session.jtag_targets()
            self.session.jtag_targets(1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: jtag lock")
        try:
            self.session.lock(100)
        except Exception as inst:
            print('!!Error!!', inst)
        time.sleep(0.2)
        t.test_name("TEST: jtag unlock")
        try:
            self.session.unlock()
        except Exception as inst:
            print('!!Error!!', inst)
        # t.test_name("TEST: claim jtag")
        # try:
        #     jt.claim()
        # except Exception as inst:
        #     print('!!Error!!', inst)
        # time.sleep(0.2)
        # t.test_name("TEST: disclaim jtag")
        # try:
        #     jt.disclaim()
        # except Exception as inst:
        #     print('!!Error!!', inst)

        t.test_name("TEST: print jtag skew")
        try:
            print(self.session.skew())
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag frequency")
        try:
            freq = self.session.frequency()
            print(freq)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print supported jtag frequencies")
        try:
            print(self.session.frequency('-l'))
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: set jtag freq")
        try:
            print(self.session.frequency(freq))
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag servers")
        try:
            self.session.servers()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: print jtag servers with format option")
        try:
            self.session.servers('-f')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: open jtag server")
        try:
            self.session.servers(open='xilinx-xvc:localhost:10200')
        except Exception as inst:
            print('!!Error!!', inst)
        time.sleep(0.2)
        t.test_name("TEST: get jtag targets")
        try:
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: close jtag server")
        try:
            self.session.servers(close='xilinx-xvc:localhost:10200')
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: get jtag targets")
        try:
            self.session.jtag_targets()
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: jtag device properties")
        try:
            print(self.session.device_properties(0x6ba00477))
        except Exception as inst:
            print('!!Error!!', inst)

        # t.test_name("TEST: set jtag device properties")
        # try:
        #     props = {'idcode': 0x6ba00477, 'irlen': 4}
        #     jt.device_properties(props=props)
        # except Exception as inst:
        #     print('!!Error!!', inst)

        t.test_name("TEST: jtag device properties")
        try:
            print(self.session.device_properties(0x6ba00477))
        except Exception as inst:
            print('!!Error!!', inst)

    def test_jtag_targets_multiple_filters(self):
        t.test_option(" test_jtag_targets_multiple_filters ")
        t.test_name("TEST: Targets name filter with == : (idcode == 4ba00477)")
        try:
            self.session.jtag_targets(filter='(idcode == 4ba00477)')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_name("TEST: Targets name filter with == : (name == arm_dap) and (level == 1)")
        try:
            self.session.jtag_targets(filter='(name == arm_dap) and (level == 1)')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_name("TEST: Targets name filter with == : (name == arm_dap) and (level == 1) and (idcode == 4ba00477)")
        try:
            ta = self.session.jtag_targets(filter="(name == arm_dap) and (level == 1) and (idcode == 4ba00477)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

        t.test_name("TEST: Targets name filter with == : (name =~ *m_d*) and ((level == 2) or (idcode == 4ba00477))")
        try:
            ta = self.session.jtag_targets(filter="(name =~ *m_d*) and ((level == 2) or (idcode == 4ba00477))")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()
        t.test_name("TEST: Targets name filter with == : ((node_id == 2) or (node_id == 3))")
        try:
            ta = self.session.jtag_targets('-s', filter="(((node_id == 2) or (node_id == 3)) and ((name =~ *m_d*) or (level == 2 )))")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.jtag_targets()

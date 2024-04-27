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


class TargetTests(object):
    def __init__(self, session, url):
        self.session = session
        self.url = url
        t.test_group(" TARGETS ")

    def test(self):
        self.test_targets_no_active_connection()
        self.test_targets()
        self.test_targets_id()
        self.test_targets_id_error()
        self.test_targets_filter()
        self.test_targets_filter_set_name()
        self.test_targets_filter_set_parent()
        self.test_targets_multiple_filters()
        self.test_targets_properties()

    def test_targets(self):
        global index
        t.test_option(" test_targets ")
        t.test_name("TEST: Targets list")
        self.session.targets()

    def test_targets_id(self):
        t.test_option(" test_targets_id ")
        t.test_name("TEST: Targets id 2")
        try:
            self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets id 8")
        try:
            self.session.targets(id=8)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets id 15")
        try:
            self.session.targets(id=15)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_targets_id_error(self):
        t.test_option(" test_targets_id_error ")
        t.test_name("TEST: Targets id error")
        try:
            self.session.targets("id=3", id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_targets_filter(self):
        t.test_option(" test_targets_filter ")
        t.test_name("TEST: Targets name filter with == : 'name == ARM Cortex-A9 MPCore #1'")
        try:
            self.session.targets(filter="name == ARM Cortex-A9 MPCore #1")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: Targets name filter with =~ : 'name =~ ARM*'")
        try:
            self.session.targets(filter="name =~ ARM*")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: Targets name filter with != : 'parent != APU'")
        try:
            self.session.targets(filter="parent != APU")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_targets_filter_set_name(self):
        t.test_option(" test_targets_filter_set_name ")
        t.test_name("TEST: Targets option set and name filter with == : 'name == ARM Cortex-A9 MPCore #1'")
        try:
            self.session.targets("--set", filter="name == ARM Cortex-A9 MPCore #1")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and name filter with =~ : 'name =~ *A9*0'")
        try:
            self.session.targets("--set", filter="name =~ *A9*0")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and name filter with !~ : 'name !~ *A9*0'")
        try:
            self.session.targets("--set", filter="name !~ *A9*0")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and name filter with != : 'name != *A9*0'")
        try:
            self.session.targets("--set", filter="name != *A9*0")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and name filter with =~ : 'name =~ MicroBlaze*'")
        try:
            self.session.targets("--set", filter="name =~ MicroBlaze*")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_targets_filter_set_parent(self):
        t.test_option(" test_targets_filter_set_parent ")
        t.test_name("TEST: Targets option set and parent filter with == : 'parent == APU'")
        try:
            self.session.targets("--set", filter="parent == APU")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and parent filter with != : 'parent != APU'")
        try:
            self.session.targets("--set", filter="parent != APU")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

        t.test_name("TEST: Targets option set and parent filter with =~ : 'parent =~ APU'")
        try:
            self.session.targets("--set", filter="parent =~ APU")
        except Exception as inst:
            print('!!Error!!', inst)
        else:
            self.session.targets()

    def test_targets_properties(self):
        t.test_option(" test_targets_properties ")
        t.test_name("TEST: Targets properties'")
        try:
            props = self.session.targets("--target_properties")
            print(props)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_targets_no_active_connection(self):
        t.test_option(" test_targets_no_active_connection ")
        t.test_name("TEST: Targets when no active connection")
        try:
            self.session.disconnect(self.session.curchan)
            self.session.targets()
        except Exception as inst:
            print('!!Error!!', inst)
            self.session.connect(url=self.url)

    def test_targets_multiple_filters(self):
        t.test_option(" test_targets_multiple_filters ")

        t.test_name("TEST: Targets name filter with == : name == ARM Cortex-A9 MPCore #1")
        try:
            self.session.targets("--set", filter='(name == ARM Cortex-A9 MPCore #1) and (target_id == 3)')
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : (name =~ *A9*0) and (parent == APU)")
        try:
            ta = self.session.targets("--set", filter="(name =~ *A9*0) and (parent == APU)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : (name =~ *A9*0) and (parent == APU) and (target_id == 2)")
        try:
            ta = self.session.targets("--set", filter="(name =~ *A9*0) and (parent == APU) and (target_id == 2)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : (name =~ *A9*1) and (state_reason == None)")
        try:
            ta = self.session.targets("--set", filter="(name =~ *A9*1) and (state_reason == None)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : (target_id == 3) and ((name =~ *A9*0) or (name =~ *A9*1))")
        try:
            ta = self.session.targets("--set", filter="(target_id == 3) and ((name =~ *A9*0) or (name =~ *A9*1))")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name(
            "TEST: Targets name filter with == : ((target_id == 3) or (target_id == 2)) and ((name =~ *A9*0) or (name =~ *A9*1))")
        try:
            ta = self.session.targets("--set",
                           filter="((target_id == 3) or (target_id == 2)) and ((name =~ *A9*0) or (name =~ *A9*1))")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : ((target_id == 3) or (target_id == 2)) and (name =~ *A9*0)")
        try:
            ta = self.session.targets("--set", filter="((target_id == 3) or (target_id == 2)) and (name =~ *A9*0)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name(
            "TEST: Targets name filter with == : ((name =~ *A9*0) or (name =~ *A9*1)) and (parent == APU) and ((target_id == 2) or (target_id == 3))")
        try:
            ta = self.session.targets("--set",
                           filter="((name =~ *A9*0) or (name =~ *A9*1)) and (parent == APU) and ((target_id==2) or (target_id==3))")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name(
            "TEST: Targets name filter with == : (parent == APU) and ((name =~ *A9*0) or (name =~ *A9*1)) and (target_id == 3)")
        try:
            ta = self.session.targets("--set",
                           filter="(parent == APU) and ((name =~ *A9*0) or (name =~ *A9*1)) and (target_id == 3)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

        t.test_name("TEST: Targets name filter with == : (state_reason == Breakpoint)")
        try:
            ta = self.session.targets("--set", filter="(state_reason == Breakpoint)")
        except Exception as inst:
            print('!!Error!!', inst)
        self.session.ta()

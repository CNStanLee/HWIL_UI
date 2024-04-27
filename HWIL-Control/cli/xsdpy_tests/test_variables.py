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

class VariableTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" VARIABLES ")
        self.ta = self.session.targets(2)
        time.sleep(0.5)
        self.session.dow('xsdpy_tests/elfs/zynq/variables_test.elf')
        time.sleep(0.5)
        self.ta.bpadd(file='helloworld.c', line=88)
        time.sleep(0.5)
        self.session.con()
        time.sleep(0.5)

    def test(self):
        self.test_read_variables()
        self.test_write_variables()

    def test_read_variables(self):
        self.test_locals()
        self.test_locals_int()
        self.test_locals_char()
        self.test_locals_float()
        self.test_locals_double()
        self.test_locals_struct()
        self.test_locals_array()
        self.test_locals_enum()
        self.test_locals_pointer()

    def test_locals(self):
        t.test_option(" test_locals ")
        self.test_locals_vars()
        self.test_locals_name()
        self.test_locals_defs()
        self.test_locals_dict()

    def test_locals_int(self):
        t.test_option(" test_locals_int ")
        self.test_locals_int_name()
        self.test_locals_int_defs()
        self.test_locals_int_dict()

    def test_locals_char(self):
        t.test_option(" test_locals_char ")
        self.test_locals_char_name()
        self.test_locals_char_defs()
        self.test_locals_char_dict()

    def test_locals_float(self):
        t.test_option(" test_locals_float ")
        self.test_locals_float_name()
        self.test_locals_float_defs()
        self.test_locals_float_dict()

    def test_locals_double(self):
        t.test_option(" test_locals_double ")
        self.test_locals_double_name()
        self.test_locals_double_defs()
        self.test_locals_double_dict()

    def test_locals_struct(self):
        t.test_option(" test_locals_struct ")
        self.test_locals_struct_name()
        self.test_locals_struct_defs()
        self.test_locals_struct_dict()

    def test_locals_array(self):
        t.test_option(" test_locals_array ")
        self.test_locals_array_name()
        self.test_locals_array_defs()
        self.test_locals_array_dict()

    def test_locals_enum(self):
        t.test_option(" test_locals_enum ")
        self.test_locals_enum_name()
        self.test_locals_enum_defs()
        self.test_locals_enum_dict()

    def test_locals_pointer(self):
        t.test_option(" test_locals_pointer ")
        self.test_locals_pointer_name()
        self.test_locals_pointer_name_value()
        self.test_locals_pointer_defs()
        self.test_locals_pointer_dict()

    def test_locals_vars(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local variables")
        try:
            #self.session.locals()
            self.ta.locals()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local variable l_int_a")
        try:
            self.session.locals(name='l_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local defs")
        try:
            self.session.locals('--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local dict")
        try:
            self.session.locals('--dict')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_int_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local int l_int_b")
        try:
            self.session.locals(name='l_int_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_int_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local int l_int_c defs")
        try:
            self.session.locals('--defs', name='l_int_c')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_int_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local int l_int_d dict")
        try:
            self.session.locals('--dict', name='l_int_d')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_char_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local char l_char_b")
        try:
            self.session.locals(name='l_char_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_char_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_char_b defs")
        try:
            self.session.locals('--defs', name='l_char_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_char_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_char_b dict")
        try:
            self.session.locals('--dict', name='l_char_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_float_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_float_b")
        try:
            self.session.locals(name='l_float_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_float_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_float_b defs")
        try:
            self.session.locals('--defs', name='l_float_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_float_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_float_b dict")
        try:
            self.session.locals('--dict', name='l_float_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_double_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local double l_double_b")
        try:
            self.session.locals(name='l_double_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_double_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local double l_double_b defs")
        try:
            self.session.locals('--defs', name='l_double_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_double_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local double dict")
        try:
            self.session.locals('--dict', name='l_double_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_struct_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_struct_b")
        try:
            self.session.locals(name='l_struct_b')
            self.session.locals(name='l_struct_b.x')
            self.session.locals(name='l_struct_b.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_struct_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_struct_c dict")
        try:
            self.session.locals('--dict', name='l_struct_c')
            self.session.locals('--dict', name='l_struct_c.x')
            self.session.locals('--dict', name='l_struct_c.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_struct_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_struct_b defs")
        try:
            self.session.locals('--defs', name='l_struct_b')
            self.session.locals('--defs', name='l_struct_b.x')
            self.session.locals('--defs', name='l_struct_b.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_array_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_array_b")
        try:
            self.session.locals(name='l_array_b')
            self.session.locals(name='l_array_b[0]')
            self.session.locals(name='l_array_b[1]')
            self.session.locals(name='l_array_b[2]')
            self.session.locals(name='l_array_b[3]')
            self.session.locals(name='l_array_b[4]')
            self.session.locals(name='l_array_b[5]')
            self.session.locals(name='l_array_b[6]')
            self.session.locals(name='l_array_b[7]')
            self.session.locals(name='l_array_b[8]')
            self.session.locals(name='l_array_b[9]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_array_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_array_b defs")
        try:
            self.session.locals('--defs', name='l_array_b')
            self.session.locals('--defs', name='l_array_b[0]')
            self.session.locals('--defs', name='l_array_b[1]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_array_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local array l_array_b defs")
        try:
            self.session.locals('--dict', name='l_array_b')
            self.session.locals('--dict', name='l_array_b[7]')
            self.session.locals('--dict', name='l_array_b[6]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_array_out_of_index(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local array l_array_b out of index")
        try:
            self.session.locals(name='l_array_b[11]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_enum_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_enum_b")
        try:
            self.session.locals('--dict', name='l_enum_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_enum_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_enum_b defs")
        try:
            self.session.locals('--defs', name='l_enum_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_enum_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_enum_b dict")
        try:
            self.session.locals('--dict', name='l_enum_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_pointer_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local l_ptr_b")
        try:
            self.session.locals(name='l_ptr_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_pointer_name_value(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local pointer l_ptr_b value")
        try:
            self.session.locals(name='*l_ptr_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_pointer_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local pointer l_ptr_b")
        try:
            self.session.locals('--defs', name='l_ptr_b')
            self.session.locals('--defs', name='*l_ptr_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_pointer_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read local pointer l_ptr_b")
        try:
            self.session.locals('--dict', name='l_ptr_b')
            self.session.locals('--dict', name='*l_ptr_b')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_write_variables(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local variables")
        self.test_locals_write_int()
        self.test_locals_write_char()
        self.test_locals_write_float()
        self.test_locals_write_double()
        self.test_locals_write_struct()
        self.test_locals_write_array()
        self.test_locals_array_out_of_index()
        self.test_locals_write_enum()
        self.test_locals_write_pointer()
        self.test_locals_write_pointer_value()
        time.sleep(sleep_time)
        self.session.locals()

    def test_locals_write_int(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local int l_int_b")
        try:
            self.session.locals(name='l_int_b', val=815)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_char(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local char l_char_b")
        try:
            self.session.locals(name='l_char_b', val='x')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_float(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local float l_float_b")
        try:
            self.session.locals(name='l_float_b', val=98.564)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_double(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local l_double_b")
        try:
            self.session.locals(name='l_double_b', val=7342.344534534)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_struct(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local struct l_struct_b")
        try:
            self.session.locals(name='l_struct_b.x', val=56)
            self.session.locals(name='l_struct_b.y', val=344.3423)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_array(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local array l_array_b")
        try:
            self.session.locals(name='l_array_b[0]', val=11)
            self.session.locals(name='l_array_b[1]', val=22)
            self.session.locals(name='l_array_b[2]', val=33)
            self.session.locals(name='l_array_b[3]', val=44)
            self.session.locals(name='l_array_b[4]', val=55)
            self.session.locals(name='l_array_b[5]', val=66)
            self.session.locals(name='l_array_b[6]', val=77)
            self.session.locals(name='l_array_b[7]', val=88)
            self.session.locals(name='l_array_b[8]', val=99)
            self.session.locals(name='l_array_b[9]', val=1010)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_array_out_of_index(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local array l_array_b out of index")
        try:
            self.session.locals(name='l_array_b[11]', val=1111)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_enum(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local enum l_enum_b")
        try:
            self.session.locals('--dict', name='l_enum_b', val=5)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_pointer(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local pointer l_ptr_b")
        try:
            self.session.locals(name='l_ptr_b', val=43434)
        except Exception as inst:
            print('!!Error!!', inst)

    def test_locals_write_pointer_value(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Write local pointer l_ptr_b value")
        try:
            self.session.locals(name='*l_ptr_b',val=445)
        except Exception as inst:
            print('!!Error!!', inst)


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

class ExpressionTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" EXPRESSIONS ")
        self.ta = self.session.targets(2)
        #self.session.dow()

    def test(self):
        self.test_read_global_vars()
        self.test_write_global_vars()
        self.test_add_expression()
        self.test_remove_expression()
        self.test_read_expressions()

    def test_read_global_vars(self):
        self.test_expr()
        self.test_expr_int()
        self.test_expr_char()
        self.test_expr_float()
        self.test_expr_double()
        self.test_expr_struct()
        self.test_expr_array()
        self.test_expr_enum()
        self.test_expr_pointer()

    def test_expr(self):
        t.test_option(" test_expr ")
        self.test_expr_vars()
        self.test_expr_name()
        self.test_expr_defs()
        self.test_expr_dict()

    def test_expr_int(self):
        t.test_option(" test_expr_int ")
        self.test_expr_int_name()
        self.test_expr_int_defs()
        self.test_expr_int_dict()

    def test_expr_char(self):
        t.test_option(" test_expr_char ")
        self.test_expr_char_name()
        self.test_expr_char_defs()
        self.test_expr_char_dict()

    def test_expr_float(self):
        t.test_option(" test_expr_float ")
        self.test_expr_float_name()
        self.test_expr_float_defs()
        self.test_expr_float_dict()

    def test_expr_double(self):
        t.test_option(" test_expr_double ")
        self.test_expr_double_name()
        self.test_expr_double_defs()
        self.test_expr_double_dict()

    def test_expr_struct(self):
        t.test_option(" test_expr_struct ")
        self.test_expr_struct_name()
        self.test_expr_struct_defs()
        self.test_expr_struct_dict()

    def test_expr_array(self):
        t.test_option(" test_expr_array ")
        self.test_expr_array_name()
        self.test_expr_array_defs()
        self.test_expr_array_dict()

    def test_expr_enum(self):
        t.test_option(" test_expr_enum ")
        self.test_expr_enum_name()
        self.test_expr_enum_defs()
        self.test_expr_enum_dict()

    def test_expr_pointer(self):
        self.test_expr_pointer_name()
        self.test_expr_pointer_name_value()
        self.test_expr_pointer_defs()
        self.test_expr_pointer_dict()

    def test_expr_vars(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global variables with nothing added to auto expression list")
        try:
            self.ta.print()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global variable g_int_a")
        try:
            self.session.print(expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global defs with nothing added to auto expression list")
        try:
            self.session.print('--defs')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global dict with nothing added to auto expression list")
        try:
            self.session.print('--dict')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_int_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_int_a")
        try:
            self.session.print(expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_int_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_int_a defs")
        try:
            self.session.print('--defs', expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_int_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global int g_int_a dict")
        try:
            self.session.print('--dict', expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_char_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_char_a")
        try:
            self.session.print(expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_char_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_char_a defs")
        try:
            self.session.print('--defs', expr='g_char_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_char_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global char g_char_a dict")
        try:
            self.session.print('--dict', expr='g_char_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_float_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_float_a")
        try:
            self.session.print(expr='g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_float_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_float_a defs")
        try:
            self.session.print('--defs', expr=' g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_float_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_float_a dict")
        try:
            self.session.print('--dict', expr='g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_double_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_double_a")
        try:
            self.session.print(expr='g_double_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_double_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_double_a defs")
        try:
            self.session.print('--defs', expr='g_double_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_double_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_double_a dict")
        try:
            self.session.print('--dict', expr='g_double_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_struct_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_struct_a")
        try:
            self.session.print(expr='g_struct_a')
            self.session.print(expr='g_struct_a.x')
            self.session.print(expr='g_struct_a.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_struct_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_struct_a dict")
        try:
            self.session.print('--dict', expr='g_struct_a')
            self.session.print('--dict', expr='g_struct_a.x')
            self.session.print('--dict', expr='g_struct_a.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_struct_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_struct_a defs")
        try:
            self.session.print('--defs', expr='g_struct_a')
            self.session.print('--defs', expr='g_struct_a.x')
            self.session.print('--defs', expr='g_struct_a.y')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_array_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_array_a")
        try:
            self.session.print(expr='g_array_a')
            self.session.print(expr='g_array_a[0]')
            self.session.print(expr='g_array_a[1]')
            self.session.print(expr='g_array_a[2]')
            self.session.print(expr='g_array_a[3]')
            self.session.print(expr='g_array_a[4]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_array_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global array g_array_a defs")
        try:
            self.session.print('--defs', expr='g_array_a')
            self.session.print('--defs', expr='g_array_a[0]')
            self.session.print('--defs', expr='g_array_a[1]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_array_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global array g_array_a defs")
        try:
            self.session.print('--dict', expr='g_array_a')
            self.session.print('--dict', expr='g_array_a[2]')
            self.session.print('--dict', expr='g_array_a[3]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_array_out_of_index(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global array g_array_a out of index")
        try:
            self.session.print(expr='g_array_a[11]')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_enum_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_enum_a")
        try:
            self.session.print('--dict', expr='g_enum_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_enum_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_enum_a defs")
        try:
            self.session.print('--defs', expr='g_enum_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_enum_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_enum_a dict")
        try:
            self.session.print('--dict', expr='g_enum_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_pointer_name(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_ptr_a")
        try:
            self.session.print(expr='g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_pointer_name_value(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global pointer g_ptr_a value")
        try:
            self.session.print(expr='*g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_pointer_defs(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global g_ptr_a")
        try:
            self.session.print('--defs', expr='g_ptr_a')
            self.session.print('--defs', expr='*g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_expr_pointer_dict(self):
        time.sleep(sleep_time)
        t.test_name("TEST: Read global pointer g_ptr_a")
        try:
            self.session.print('--dict', expr='g_ptr_a')
            self.session.print('--dict', expr='*g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

    def test_add_expression(self):
        t.test_option(" test_add_expression ")
        time.sleep(sleep_time)
        t.test_name("TEST: Read add g_ptr_a")
        try:
            self.session.print('--add', expr='g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Read add g_double_a")
        try:
            self.session.print('--add', expr='g_double_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Read add g_int_a")
        try:
            self.session.print('--add', expr='g_int_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Read add g_float_a")
        try:
            self.session.print('--add', expr='g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Read add g_array_a")
        try:
            self.session.print('--add', expr='g_array_a[4]')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Printing local auto variables:")
        try:
            self.session.print()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_remove_expression(self):
        t.test_option(" test_remove_expression ")
        time.sleep(sleep_time)
        t.test_name("TEST: Read remove g_ptr_a")
        try:
            self.session.print('--remove', expr='g_ptr_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Read remove g_double_a")
        try:
            self.session.print('--remove', expr='g_double_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Printing local auto variables:")
        try:
            self.session.print()
        except Exception as inst:
            print('!!Error!!', inst)

    def test_read_expressions(self):
        time.sleep(sleep_time)
        t.test_option(" test_read_expressions ")
        t.test_name("TEST: Expression g_int_a + g_float_a")
        try:
            self.session.print('--add', expr='g_int_a + g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Expression g_double_a + g_float_a")
        try:
            self.session.print('--add', expr='g_double_a + g_float_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Expression g_array_a[1] + g_array_a[2]")
        try:
            self.session.print('--add', expr='g_array_a[1] + g_array_a[2]')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Expression l_int_a + l_int_b")
        try:
            self.session.print('--add', expr='l_int_a + l_int_b')
        except Exception as inst:
            print('!!Error!!', inst)


    def test_write_global_vars(self):
        t.test_option(" test_write_global_vars ")

        time.sleep(sleep_time)
        t.test_name("TEST: Write global variable g_int_a")
        try:
            self.session.print('--add', expr='g_int_a', val=9919)
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Write global variable g_int_a")
        try:
            self.session.print('--add', expr='g_array_a')
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Write global variable g_float_a")
        try:
            self.session.print('--add', expr='g_float_a', val=794)
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Write global variable g_struct_a.x")
        try:
            self.session.print('--add', expr='g_struct_a.x', val=111)
            self.session.print('--add', expr='g_struct_a.y', val=1212)
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Write global variable g_array_a")
        try:
            self.session.print('--add', expr='g_array_a[0]', val=5555)
            self.session.print('--add', expr='g_array_a[1]', val=4444)
            self.session.print('--add', expr='g_array_a[2]', val=3333)
            self.session.print('--add', expr='g_array_a[3]', val=2222)
            self.session.print('--add', expr='g_array_a[4]', val=1111)
        except Exception as inst:
            print('!!Error!!', inst)

        time.sleep(sleep_time)
        t.test_name("TEST: Printing global auto variables:")
        try:
            self.session.print()
        except Exception as inst:
            print('!!Error!!', inst)
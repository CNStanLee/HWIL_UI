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
import threading
import time
from subprocess import Popen

import xsdpy_tests as t

testdir = os.path.dirname(os.path.realpath(__file__))


class StreamsTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" STREAMS TEST")

    def test(self):
        # Write a test application that prints a test data every one second.
        # also get the integer as input
        # while (1){
        #   sleep(1);
        #   xil_printf("value of x = %d \n", x);
        #   scanf("%d", & k);
        #   xil_printf("test = %d \n", k);
        # }

        # NOTES: Run one tests in the below list at a time
        self.test_set_1()
        self.test_jtag_terminal_external_socket_and_hyperterminal()
        self.session_test_jtag_terminal_hyperterminal_and_external_socket()
        self.test_read_jtag_uart_vs_jtag_terminal()
        self.jtag_terminal_with_more_targets()
        self.error_conditions_test_readjtaguart()
        print('Completed all tests')

    def test_set_1(self):
        t.test_option('test_read_jtag_uart')
        self.test_read_jtag_uart()

        t.test_option('session_test_read_jtag_uart')
        self.session_test_read_jtag_uart()

        t.test_option('test_read_jtag_uart_filehandler')
        self.test_read_jtag_uart_filehandler()

        t.test_option('session_test_read_jtag_uart_filehandler')
        self.session_test_read_jtag_uart_filehandler()

        t.test_option('read_jtag_uart_error_tests')
        self.read_jtag_uart_error_tests()

        t.test_option('test_jtag_terminal')
        self.test_jtag_terminal()

        t.test_option('session_test_jtag_terminal')
        self.session_test_jtag_terminal()

        t.test_option('test_jtag_terminal_external_socket')
        self.test_jtag_terminal_external_socket()

        t.test_option('session_test_jtag_terminal_external_socket')
        self.session_test_jtag_terminal_external_socket()
        time.sleep(2)

    def test_read_jtag_uart(self):
        s = self.session
        t.test_name("")
        tg = s.target(2)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=0, error=0)
        tg2 = s.target(3)
        t.try_function(lambda: tg2.readjtaguart(), 'readjtaguart for target 3', sleep=2, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=0, error=0)
        t.try_function(lambda: tg2.readjtaguart('--stop'), 'readjtaguart stop for target 3', sleep=1, error=0)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=2, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def session_test_read_jtag_uart(self):
        s = self.session
        s.target(2)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 3', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 3', sleep=2, error=0)
        s.target(2)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 2', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def test_read_jtag_uart_filehandler(self):
        s = self.session
        tg = s.target(2)
        t.try_function(lambda: tg.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=0)
        tg2 = s.target(3)
        t.try_function(lambda: tg2.readjtaguart(file=testdir + '/data/streams2.log', mode='w'),
                       'readjtaguart with filehandle for target 3', sleep=2, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 3', sleep=1,
                       error=0)
        t.try_function(lambda: tg2.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=0)
        t.try_function(lambda: tg.readjtaguart(file=testdir + '/data/streams.log', mode='a'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def session_test_read_jtag_uart_filehandler(self):
        s = self.session
        s.target(2)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=0, error=0)
        s.target(3)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams2.log', mode='w'),
                       'readjtaguart with filehandle for target 3', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 3', sleep=0,
                       error=0)
        s.target(2)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=2,
                       error=0)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='a'),
                       'readjtaguart stop with filehandle for target 2', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def read_jtag_uart_error_tests(self):
        s = self.session
        tg = s.target(2)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=0, error=0)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2 again', sleep=0, error=1)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=0, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2 again', sleep=1, error=1)
        self.check_hanging_streams_threads()
        print('Done')

    def test_jtag_terminal(self):
        k = 0
        while k < 2:
            k += 1
            s = self.session
            tg = s.target(2)
            t.try_function(lambda: tg.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
            tg2 = s.target(3)
            t.try_function(lambda: tg2.jtagterminal(), 'jtagterminal for target 3', sleep=2, error=0)
            t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=0, error=0)
            t.try_function(lambda: tg2.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def session_test_jtag_terminal(self):
        s = self.session
        s.target(2)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def test_jtag_terminal_external_socket(self):
        s = self.session
        tg = s.target(2)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=0, error=0)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=0, error=1)
        t.try_function(lambda: tg.jtagterminal(), 'jtagterminal with socket for target 2', sleep=0, error=1)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=2,
                       error=0)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=0, error=0)

        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=2, error=1)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=2,
                       error=0)
        tg = s.target(3)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 3', sleep=2, error=0)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop with socket for target 3', sleep=2,
                       error=0)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 3', sleep=2, error=0)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop with socket for target 3', sleep=1,
                       error=0)
        s = self.session
        t1 = s.target(2)
        t2 = s.target(3)
        i = 0
        while i < 2:
            i += 1
            print(t1.jtagterminal('--socket'))
            print(t2.jtagterminal('--socket'))
            time.sleep(2)

            t.try_function(lambda: t1.jtagterminal('--stop'), 'stopping jtagterm', sleep=0.1, error=0)
            t.try_function(lambda: t2.jtagterminal('--stop'), 'stopping jtagterm', sleep=0.1, error=0)

        i = 0
        while i < 2:
            i += 1
            port = t1.jtagterminal('--socket')
            port2 = t2.jtagterminal('--socket')
            terminal_script = testdir + '/test_streams_client.py'
            Popen([f'python {terminal_script} {port}'], shell=True)
            Popen([f'python {terminal_script} {port2}'], shell=True)

            time.sleep(5)
            t.try_function(lambda: t1.jtagterminal('--stop'), 'stopping jtagterm', sleep=0, error=0)
            t.try_function(lambda: t2.jtagterminal('--stop'), 'stopping jtagterm', sleep=1, error=0)

        self.check_hanging_streams_threads()
        print('Done')

    def session_test_jtag_terminal_external_socket(self):
        s = self.session
        s.target(2)
        i = 0
        while i < 2:
            i += 1
            s.target(2)
            t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=2,
                           error=0)
            t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=2,
                           error=0)
            t.test_name("jtagterminal with socket for target 2")
            port = s.jtagterminal('--socket')
            terminal_script = testdir + '/test_streams_client.py'
            Popen([f'python {terminal_script} {port}'], shell=True)
            time.sleep(2)
            t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=1,
                           error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def test_jtag_terminal_external_socket_and_hyperterminal(self):
        t.test_option('test_jtag_terminal_external_socket_and_hyperterminal')
        s = self.session
        tg = s.target(2)
        t.try_function(lambda: tg.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=1, error=0)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=1,
                       error=0)
        t.try_function(lambda: tg.jtagterminal(), 'jtagterminal for target 2', sleep=3, error=0)
        t.try_function(lambda: tg.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=0, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def session_test_jtag_terminal_hyperterminal_and_external_socket(self):
        t.test_option('session_test_jtag_terminal_hyperterminal_and_external_socket')
        s = self.session
        s.target(2)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=2, error=0)
        t.test_name("jtagterminal with socket for target 2")
        port = s.jtagterminal('--socket')
        terminal_script = testdir + '/test_streams_client.py'
        Popen([f'python {terminal_script} {port}'], shell=True)
        time.sleep(2)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal with socket for target 2', sleep=1, error=0)

        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=2, error=0)
        t.test_name("jtagterminal with socket for target 3")
        port = s.jtagterminal('--socket')
        terminal_script = testdir + '/test_streams_client.py'
        Popen([f'python {terminal_script} {port}'], shell=True)
        time.sleep(2)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal with socket for target 2', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def test_read_jtag_uart_vs_jtag_terminal(self):
        t.test_option('test_read_jtag_uart_vs_jtag_terminal')
        s = self.session
        s.target(2)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 2', sleep=2, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=2, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 2', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=2, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def jtag_terminal_with_more_targets(self):
        t.test_option('jtag_terminal_with_more_targets')
        s = self.session
        s.target(2)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=0, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=3, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=0, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=0, error=1)

        s.target(2)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=2, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=2, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=0, error=0)
        s.target(2)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=0, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def error_conditions_test_readjtaguart(self):
        t.test_option('error_conditions_test_readjtaguart')
        s = self.session
        tg = s.target(2)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=1, error=0)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=1, error=1)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=1, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=1, error=1)
        t.try_function(lambda: tg.readjtaguart(), 'readjtaguart for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=3, error=0)
        t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal socket for target 3', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 3', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 3', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)
        t.try_function(lambda: tg.readjtaguart('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)

        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 3', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 3', sleep=1, error=0)

        s.target(2)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=0)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart  for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=0)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal with socket for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop with socket for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=0)

        s.target(2)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal  for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 3', sleep=1, error=0)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams2.log', mode='w'),
                       'readjtaguart with filehandle for target 3', sleep=1, error=1)
        s.target(2)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=1)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)

        s.target(2)
        t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal socket for target 2', sleep=1, error=0)
        s.target(3)
        t.try_function(lambda: s.jtagterminal('--socket'), 'jtagterminal socket for target 3', sleep=1, error=0)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams2.log', mode='w'),
                       'readjtaguart with filehandle for target 3', sleep=1, error=1)
        s.target(2)
        t.try_function(lambda: s.readjtaguart(file=testdir + '/data/streams.log', mode='w'),
                       'readjtaguart with filehandle for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=1)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart for target 2', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 2', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=1)

        s.target(3)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart('--stop'), 'readjtaguart stop with filehandle for target 2', sleep=1,
                       error=1)
        t.try_function(lambda: s.jtagterminal(), 'jtagterminal  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.readjtaguart(), 'readjtaguart  for target 3', sleep=1, error=1)
        t.try_function(lambda: s.jtagterminal('--stop'), 'jtagterminal stop for target 2', sleep=1, error=0)
        self.check_hanging_streams_threads()
        print('Done')

    def check_hanging_streams_threads(self):
        time.sleep(2)
        for th in threading.enumerate():
            th_name = th.name
            if th_name.startswith('stream_sock_thread_'):
                raise Exception('There are some hanging threads')

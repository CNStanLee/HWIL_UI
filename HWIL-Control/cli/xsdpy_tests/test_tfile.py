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
import subprocess
from subprocess import PIPE

from tcf.services.filesystem import *


class TFileTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" TFILE ")

    def test(self):
        self.test_tfile()

    def test_tfile(self):
        t.test_option(" test_tfile")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        tfile = self.session.tfile()
        tfile.ls('/tmp')
        try:
            tfile.remove('/tmp/rigel.txt')
        except Exception as inst:
            print('!!Error!!', inst)
        try:
            tfile.remove('/tmp/rigel1.txt')
        except Exception as inst:
            print('!!Error!!', inst)
        handle = tfile.open('/tmp/tfile_test.txt', flags=0x0F)
        tfile.write(handle, 'hi, this is a test string')
        print(tfile.read(handle, size=5))
        fstat = tfile.fstat(handle)
        print(fstat)
        tfile.close(handle)

        tfile.rename('/tmp/tfile_test.txt', '/tmp/rigel.txt')
        lstat = tfile.lstat('/tmp/rigel.txt')
        print(lstat)
        stat = tfile.stat('/tmp/rigel.txt')
        print(stat)

        stat.permissions = 65535
        tfile.setstat('/tmp/rigel.txt', stat)
        stat = tfile.stat('/tmp/rigel.txt')
        print(stat)

        print(tfile.realpath('/tmp/../tmp/rigel.txt'))
        tfile.symlink('/tmp/rigel1.txt', '/tmp/rigel.txt')
        print(tfile.readlink('/tmp/rigel1.txt'))
        tfile.copy('/tmp/rigel.txt', '/tmp/rigel2.txt')
        tfile.remove('/tmp/rigel.txt')

        tfile.mkdir('/tmp/new')
        tfile.rmdir('/tmp/new')

        print(tfile.roots())
        f = tfile.opendir('/tmp')
        print(tfile.readdir(f))

        print(tfile.user())

    def test_tfile_bkup(self):
        t.test_option(" test_tfile")
        try:
            tgt = self.session.targets(id=2)
        except Exception as inst:
            print('!!Error!!', inst)
        tfile = self.session.tfile()
        tfile.ls('/home/rpalla/Desktop/tcl_files')
        handle = tfile.open('/home/rpalla/Desktop/tcl_files/tfile_test.txt', flags=0x0F)
        tfile.write(handle, 'hi, this is a test string')
        print(tfile.read(handle, size=5))
        fstat = tfile.fstat(handle)
        print(fstat)
        tfile.close(handle)

        tfile.rename('/home/rpalla/Desktop/tcl_files/tfile_test.txt', '/home/rpalla/Desktop/tcl_files/rigel.txt')
        lstat = tfile.lstat('/home/rpalla/Desktop/tcl_files/rigel.txt')
        print(lstat)
        stat = tfile.stat('/home/rpalla/Desktop/tcl_files/rigel.txt')
        print(stat)

        stat.permissions = 65535
        tfile.setstat('/home/rpalla/Desktop/tcl_files/rigel.txt', stat)
        stat = tfile.stat('/home/rpalla/Desktop/tcl_files/rigel.txt')
        print(stat)

        print(tfile.realpath('/home/rpalla/../rpalla/Desktop/tcl_files/rigel.txt'))
        tfile.symlink('/home/rpalla/Desktop/tcl_files/rigel1.txt', '/home/rpalla/Desktop/tcl_files/rigel.txt')
        print(tfile.readlink('/home/rpalla/Desktop/tcl_files/rigel1.txt'))
        tfile.copy('/home/rpalla/Desktop/tcl_files/rigel.txt', '/home/rpalla/Desktop/tcl_files/rigel2.txt')
        tfile.remove('/home/rpalla/Desktop/tcl_files/rigel.txt')

        tfile.mkdir('/home/rpalla/Desktop/tcl_files/new')
        tfile.rmdir('/home/rpalla/Desktop/tcl_files/new')

        print(tfile.roots())
        f = tfile.opendir('/home/rpalla/Desktop/tcl_files/')
        print(tfile.readdir(f))

        print(tfile.user())

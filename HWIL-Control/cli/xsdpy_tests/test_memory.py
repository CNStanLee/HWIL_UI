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
import subprocess
from subprocess import PIPE


class MemoryTests(object):
    def __init__(self, session):
        self.session = session
        t.test_group(" MEMORY ")
        cmd = 'id | awk -F\'=\' \'{print $2}\' | awk -F\' \' \'{print $1}\' | awk -F\'(\' \'{print $2}\' | awk ' \
              '-F\')\' \'{print $1}\' '
        p = subprocess.run([cmd], shell=True, stdout=PIPE, stderr=PIPE)
        self.username = str(p.stdout.decode().split("\n")[0])

    def test(self):
        self.test_memory_read_commands()
        self.test_memory_write_commands()
        self.test_memory_read_commands_from_session_object()
        self.test_memory_write_commands_from_session_object()

    def test_memory_read_commands(self):
        t.test_option(" test_memory_read_commands")
        try:
            tgt = self.session.targets(id=1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 words from address 0x00100000")
        try:
            tgt.mrd(0x00100000, word_size=4, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 half words from address 0x00100000")
        try:
            tgt.mrd(0x00100000, word_size=2, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 bytes from address 0x00100000")
        try:
            tgt.mrd(0x00100000, word_size=1, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 double words from address 0x00100000")
        try:
            tgt.mrd(0x00100000, word_size=8, size=10)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read 20 double words from address 0x00100000 and write to the file "
                    "xsdpy_tests/data/mrd.bin")
        try:
            tgt.mrd(0x00100000, '-b', word_size=8, size=20, file="xsdpy_tests/data/mrd.bin")
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 words from address 0x00100002 with force mem accesses option")
        try:
            tgt.mrd(0x00100002, '-f', word_size=4, size=10)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read one word from Zynq address space APR, location 0x100")
        try:
            tgt.mrd(0x100, address_space="APR")
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read one word from Zynq address space AP1, location 0x80090088")
        try:
            tgt.mrd(0x80090088, address_space="AP1")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read 20 words from location 0x100000 and return as list")
        x = None
        try:
            x = tgt.mrd(0x100000, '-v', word_size=4, size=20)
        except Exception as inst:
            print('!!Error!!', inst)
        if not isinstance(x, str):
            if x is not None:
                print('[{}]'.format(', '.join(hex(z) for z in x)))

    def test_memory_write_commands(self):
        t.test_option(" test_memory_write_commands")
        try:
            tgt = self.session.targets(id=1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory write 10 words to location 0x100000")
        try:
            tgt.mwr(0x00100000, word_size=4, size=10, words=[0x01, 0x02, 0x03])
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: fill 5 words with [0x0E]")
        try:
            tgt.mwr(0x00100000, word_size=4, size=5, words=[0x0E])
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: fill 5 words with 0x0F")
        try:
            tgt.mwr(0x00100000, word_size=4, size=5, words=0x0F)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory write 1 words to location 0x100000")
        try:
            tgt.mwr(0x00100000, word_size=4, words=0x04)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory write 5 words to file xsdpy_tests/data/mrd.bin")
        try:
            tgt.mwr(0x00100000, '-b', word_size=4, size = 5, file="xsdpy_tests/data/mrd.bin")
        except Exception as inst:
            print('!!Error!!', inst)

    def test_memory_read_commands_from_session_object(self):
        t.test_option(" test_memory_read_commands_from_session_object")
        try:
            tgt = self.session.targets(id=1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 words from address 0x00100000")
        try:
            self.session.mrd(0x00100000, word_size=4, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 half words from address 0x00100000")
        try:
            self.session.mrd(0x00100000, word_size=2, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 bytes from address 0x00100000")
        try:
            self.session.mrd(0x00100000, word_size=1, size=10)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 double words from address 0x00100000")
        try:
            self.session.mrd(0x00100000, word_size=8, size=10)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read 20 double words from address 0x00100000 and write to the file "
                    "xsdpy_tests/data/mrd.bin")
        try:
            self.session.mrd(0x00100000, '-b', word_size=8, size=20, file="xsdpy_tests/data/mrd.bin")
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read 10 words from address 0x00100002 with force mem accesses option")
        try:
            self.session.mrd(0x00100002, '-f', word_size=4, size=10)
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read one word from Zynq address space APR, location 0x100")
        try:
            self.session.mrd(0x100, address_space="APR")
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory read one word from Zynq address space AP1, location 0x80090088")
        try:
            self.session.mrd(0x80090088, address_space="AP1")
        except Exception as inst:
            print('!!Error!!', inst)

        t.test_name("TEST: memory read 20 words from location 0x100000 and return as list")
        x = None
        try:
            x = self.session.mrd(0x100000, '-v', word_size=4, size=20)
        except Exception as inst:
            print('!!Error!!', inst)
        if not isinstance(x, str):
            if x is not None:
                print('[{}]'.format(', '.join(hex(z) for z in x)))

    def test_memory_write_commands_from_session_object(self):
        t.test_option(" test_memory_write_commands_from_session_object")
        try:
            tgt = self.session.targets(id=1)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory write 20 words to location 0x100000")
        try:
            self.session.mwr(0x00100000, word_size=4, size=10, words=[0x04, 0x02, 0x07])
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory write 1 words to location 0x100000")
        try:
            self.session.mwr(0x00100000, word_size=4, words=0x04)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory fill with word 0x04 to 10 locations from 0x100000")
        try:
            self.session.mwr(0x00100000, word_size=4, size=10, words=0x04)
        except Exception as inst:
            print('!!Error!!', inst)
        t.test_name("TEST: memory write 5 words to file xsdpy_tests/data/mrd.bin")
        try:
            self.session.mwr(0x00100000, '-b', word_size=4, size=5, file="xsdpy_tests/data/mrd.bin")
        except Exception as inst:
            print('!!Error!!', inst)

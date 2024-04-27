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

#url = "TCP:xhdbfarmrke9:3121"


class ConnectionsTests(object):
    def __init__(self, session, chan, url):
        self.session = session
        self.chan = chan
        self.url = url
        t.test_group(" CONNECTIONS ")

    def test(self):
        self.test_connections()

    def test_connections(self):
        t.test_option(" test_connections ")
        t.test_name("TEST: connect command with -new")
        try:
            chan = self.session.connect('--new', url=self.url)
        except Exception as inst:
            print(inst)
        t.test_name("TEST: list of connections")
        try:
            self.session.connect('--list')
        except Exception as inst:
            print(inst)
        t.test_name("TEST: disconnect command")
        try:
            self.session.disconnect(chan)
        except Exception as inst:
            print(inst)
        t.test_name("TEST: list of connections")
        try:
            self.session.connect('--list')
        except Exception as inst:
            print(inst)
        t.test_name("TEST: connect to existing channel")
        try:
            self.session.connect(url=self.url)
        except Exception as inst:
            print(inst)
        t.test_name("TEST: list of connections")
        try:
            self.session.connect('--list')
        except Exception as inst:
            print(inst)

    def test_auto_start(self):
        pass

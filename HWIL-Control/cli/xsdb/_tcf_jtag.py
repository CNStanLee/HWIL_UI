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

import base64
from tcf.services import jtag as jtag_service
from tcf.services import jtagcable as jtag_cable_service
from xsdb._utils import *


class TcfJtag(object):
    def __init__(self, session):
        self.session = session
        self.js = protocol.invokeAndWait(session._curchan_obj.getRemoteService, jtag_service.NAME)
        self.jc = protocol.invokeAndWait(session._curchan_obj.getRemoteService, jtag_cable_service.NAME)

    def jtag_sequence(self, ctx, params, cmds, data, sync):
        class __DoneHWCommand(jtag_service.DoneHWCommand):
            def __init__(self, sync):
                self.sync = sync

            def doneHW(self, token, error, args):
                if error:
                    self.sync.done(error=error, result=None)
                else:
                    if args is not None:
                        self.sync.done(error=None, result=base64.b64decode(args))
                    else:
                        self.sync.done(error=None, result=args)

        self.js.sequence(ctx, params, cmds, data, __DoneHWCommand(sync))

    class __DoneHWCommand(jtag_service.DoneHWCommand):
        def __init__(self, sync):
            self.__sync = sync

        def doneHW(self, token, error, args):
            if self.__sync is not None:
                self.__sync.done(error=error, result=args)

    def jtag_lock(self, ctx, timeout, sync=None):
        self.js.lock(ctx, timeout, self.__DoneHWCommand(sync))

    def jtag_unlock(self, ctx, sync=None):
        self.js.unlock(ctx, self.__DoneHWCommand(sync))

    def jtag_claim(self, ctx, mask, sync=None):
        self.js.claim(ctx, mask, self.__DoneHWCommand(sync))

    def jtag_disclaim(self, ctx, mask, sync=None):
        self.js.disclaim(ctx, mask, self.__DoneHWCommand(sync))

    def jtag_get_option(self, ctx, key, sync=None):
        self.js.get_option(ctx, key, self.__DoneHWCommand(sync))

    def jtag_set_option(self, ctx, key, value, sync=None):
        self.js.set_option(ctx, key, value, self.__DoneHWCommand(sync))

    def jtagcable_server_ctx(self, ctx, sync=None):
        self.jc.getServerContext(ctx, self.__DoneHWCommand(sync))

    def jtagcable_open_server(self, serverid, params, sync=None):
        self.jc.openServer(serverid, params, self.__DoneHWCommand(sync))

    def jtagcable_close_server(self, serverid, sync=None):
        self.jc.closeServer(serverid, self.__DoneHWCommand(sync))

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

from tcf.services import xilinxreset as xr
from xsdb._utils import *


class TcfReset(object):
    def __init__(self, session):
        self.session = session
        self.cp = protocol.invokeAndWait(session._curchan_obj.getRemoteService, xr.NAME)

    class __DoneHWCommand(xr.DoneHWCommand):
        def __init__(self, sync):
            self.sync = sync

        def doneHW(self, token, error, args):
            self.sync.done(error=None if error is None else error['Format'], result=args)

    def rst_cmd(self, ctx, type, params, sync):
        self.cp.reset(ctx, type, params, self.__DoneHWCommand(sync))

    def rst_capabilities(self, ctx, sync):
        self.cp.getCapabilities(ctx, self.__DoneHWCommand(sync))
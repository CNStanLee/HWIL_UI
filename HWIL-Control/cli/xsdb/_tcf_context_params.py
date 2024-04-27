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

from tcf.services import contextparams as ctxparams_service
from xsdb._utils import *


class TcfContextParams(object):
    def __init__(self, chan, session):
        self.session = session
        self.channel = chan
        self.cp = protocol.invokeAndWait(session._curchan_obj.getRemoteService, ctxparams_service.NAME)

    class __DoneHWCommand(ctxparams_service.DoneHWCommand):
        def __init__(self, sync):
            self.sync = sync

        def doneHW(self, token, error, args):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error, result=args)

    def get_definitions(self, sync):
        self.cp.getDefinitions(self.__DoneHWCommand(sync))

    def get_values(self, param_name, sync):
        self.cp.getValues(param_name, self.__DoneHWCommand(sync))

    def get(self, ctx, param_name, sync):
        self.cp.get(ctx, param_name, self.__DoneHWCommand(sync))

    def set(self, ctx, param_name, param_value, sync):
        self.cp.set(ctx, param_name, param_value, self.__DoneHWCommand(sync))

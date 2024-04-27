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

from tcf.services import svf as svf_service
from xsdb._utils import *


class TcfSVF(object):
    def __init__(self, session):
        self.svfs = protocol.invokeAndWait(session._curchan_obj.getRemoteService, svf_service.NAME)

    class __DoneHWCommand(svf_service.DoneHWCommand):
        def __init__(self, sync):
            self.sync = sync

        def doneHW(self, token, error, args):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error, result=args)

    def add_device(self, target_ctx, name, idcode, irlen, idcode2, mask, sync):
        self.svfs.add_device(target_ctx, name, idcode, irlen, idcode2, mask, self.__DoneHWCommand(sync))

    def add_target(self, name, sync):
        self.svfs.add_target(name, self.__DoneHWCommand(sync))
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

from tcf.services import disassembly as disassembly_srv


#################################################################################################
# TcfNodeDisassembly -
#   * disassemble commands for a memory context in disassembly service
#################################################################################################


class TcfNodeDisassembly(object):
    def __init__(self, __tcf_node_exec_ctx, channel, id: str):
        self.id = id
        self.channel = channel
        self.node = __tcf_node_exec_ctx

    def disassemble(self, addr, size, params, sync):
        dis = self.channel.getRemoteService(disassembly_srv.NAME)

        class DoneDisassemble(disassembly_srv.DoneDisassemble):
            def __init__(self, sync):
                self.__sync = sync

            def doneDisassemble(self, token, error, disassembly):
                if self.__sync is not None:
                    self.__sync.done(error=error, result=disassembly)

        dis.disassemble(self.id, addr, size, params, DoneDisassemble(sync))


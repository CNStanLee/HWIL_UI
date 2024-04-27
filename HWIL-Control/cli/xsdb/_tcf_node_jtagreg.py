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

from tcf.util import cache
from tcf.services import xicom as xicom_service, DoneHWCommand


#################################################################################################
# TcfNodeJtagReg -
#   * get jtag reg
#################################################################################################


class TcfNodeJtagReg(object):
    def __init__(self, channel, ctx_id: str):
        self.ctx_id = ctx_id
        self.channel = channel
        self.__get_jtagreg_list = self.JtagRegGetList(self, channel, ctx_id)
        self.get_jtagreg_def = {}

    class JtagRegGetList(cache.DataCache):
        def __init__(self, node, channel, context_id):
            super().__init__(channel)
            self.node = node
            self.__context_id = context_id
            self.__channel = channel

        def startDataRetrieval(self):
            xs = self.__channel.getRemoteService(xicom_service.NAME)
            data = self

            class DoneHWCommand(xicom_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    for reg in args:
                        regdef = data.node.JtagRegGetDef(data.node.channel, reg)
                        data.node.get_jtagreg_def.update({reg: regdef})
                    data.set(token, error, args)

            data._command = xs.jtag_reg_list(self.__context_id, DoneHWCommand())

    class JtagRegGetDef(cache.DataCache):
        def __init__(self, channel, context_id):
            super().__init__(channel)
            self.__context_id = context_id
            self.__channel = channel

        def startDataRetrieval(self):
            xs = self.__channel.getRemoteService(xicom_service.NAME)
            data = self

            class DoneHWCommand(xicom_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    data.set(token, error, args)

            data._command = xs.jtag_reg_def(self.__context_id, DoneHWCommand())

    def jtag_reg_get(self, ctx, reg_ctx, slr, sync):
        xs = self.channel.getRemoteService(xicom_service.NAME)

        class DoneHWCommand(xicom_service.DoneHWCommand):
            def __init__(self, sync):
                self.sync = sync

            def doneHW(self, token, error, val):
                self.sync.done(error=error, result=base64.b64decode(val))

        xs.jtag_reg_get(ctx, reg_ctx, slr, DoneHWCommand(sync))

    def get_jtag_reg_list(self):
        return self.__get_jtagreg_list

    def get_jtag_reg_def(self, reg_id):
        if reg_id not in self.get_jtagreg_def.keys():
            raise Exception(f'No Register id {reg_id} in the list') from None
        return self.get_jtagreg_def[reg_id]

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

from tcf.services import xicom as xicom_service
from xsdb._utils import *


class TcfXicom(object):
    def __init__(self, session):
        self.session = session
        self.xs = protocol.invokeAndWait(session._curchan_obj.getRemoteService, xicom_service.NAME)

    class __DoneHWCommand(xicom_service.DoneHWCommand):
        def __init__(self, sync):
            self.sync = sync

        def doneHW(self, token, error, args):
            self.sync.done(error=error, result=args)

    def xicom_get_bitfile_props(self, ctx, size, data, sync):
        self.xs.get_bit_file_properties(ctx, size, data, self.__DoneHWCommand(sync))

    def xicom_config_prog(self, ctx, sync):
        self.xs.config_prog(ctx, self.__DoneHWCommand(sync))

    def xicom_config_reset(self, ctx, props, sync):
        self.xs.config_reset(ctx, props, self.__DoneHWCommand(sync))

    def xicom_config_begin(self, ctx, props, sync):
        self.xs.config_begin(ctx, props, self.__DoneHWCommand(sync))

    def xicom_config_end(self, ctx, props, sync):
        self.xs.config_end(ctx, props, self.__DoneHWCommand(sync))

    def xicom_config_start(self, ctx, sync):
        self.xs.config_start(ctx, self.__DoneHWCommand(sync))

    def xicom_get_config_status(self, ctx, sync):
        self.xs.get_config_status(ctx, self.__DoneHWCommand(sync))

    def xicom_get_ir_status(self, ctx, sync):
        self.xs.get_ir_status(ctx, self.__DoneHWCommand(sync))

    def xicom_get_boot_status(self, ctx, sync):
        self.xs.get_boot_status(ctx, self.__DoneHWCommand(sync))

    def xicom_get_timer_status(self, ctx, sync):
        self.xs.get_timer_reg(ctx, self.__DoneHWCommand(sync))

    def xicom_get_cor0_status(self, ctx, sync):
        self.xs.get_cor0_reg(ctx, self.__DoneHWCommand(sync))

    def xicom_get_cor1_status(self, ctx, sync):
        self.xs.get_cor1_reg(ctx, self.__DoneHWCommand(sync))

    def xicom_get_wbstar_status(self, ctx, sync):
        self.xs.get_wbstar(ctx, self.__DoneHWCommand(sync))

    def xicom_cancel(self, ctx, sync):
        self.xs.cancel(ctx, self.__DoneHWCommand(sync))

    def xicom_secure_debug(self, ctx, data, sync):
        self.xs.secure_debug(ctx, data, self.__DoneHWCommand(sync))

    def xicom_config_in(self, ctx, start_pos, total_bytes, data_bytes, data, callback=None,
                          callback_arg=None):

        class DoneHWCommand(xicom_service.DoneHWCommand):
            def __init__(self, callback, callback_arg, data_bytes):
                self.__callback = callback
                self.__callback_arg = callback_arg
                self.__data_bytes = data_bytes

            def doneHW(self, token, error, args):
                if self.__callback is not None:
                    self.__callback(self.__callback_arg, self.__data_bytes, args,
                                    error if isinstance(error, OSError) else
                                    error.getAttributes()['Format'] if error else None, token.id)

        return self.xs.config_in(ctx, start_pos, total_bytes, data_bytes, data, DoneHWCommand(callback, callback_arg,
                                                                                         data_bytes))

    def xicom_config_data(self, ctx, data, datalen, callback=None, callback_arg=None):

        class DoneHWCommand(xicom_service.DoneHWCommand):
            def __init__(self, callback, callback_arg, datalen):
                self.__callback = callback
                self.__callback_arg = callback_arg
                self.__datalen = datalen

            def doneHW(self, token, error, args):
                if self.__callback is not None:
                    self.__callback(self.__callback_arg, self.__datalen, error, token.id)

        return self.xs.config_data(ctx, data, DoneHWCommand(callback, callback_arg, datalen))
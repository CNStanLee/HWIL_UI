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

from tcf import protocol
from tcf.util import cache
from tcf.services import jtagdevice as jtagdevice_service


#################################################################################################
# TcfNodeJtagDevice -
#   * set and get commands for a jtag device service
#################################################################################################


class TcfNodeJtagDevice(object):
    def __init__(self, __tcf_node_exec_ctx, channel, jtag_device_id: int = 0):
        self.channel = channel
        self.node = __tcf_node_exec_ctx
        self.__jtagdevice_properties = self.JtagDeviceProperties(channel, jtag_device_id)

    class JtagDeviceProperties(cache.DataCache):
        def __init__(self, channel, jtag_device_id):
            super().__init__(channel)
            self.__channel = channel
            self.__jtag_device_id = jtag_device_id

        def startDataRetrieval(self):
            js = self.__channel.getRemoteService(jtagdevice_service.NAME)
            data = self

            class DoneHWCommand(jtagdevice_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    data.set(token, error, args)

            data._command = js.get_properties(self.__jtag_device_id, DoneHWCommand())

    class __DoneHWCommand(jtagdevice_service.DoneHWCommand):
        def __init__(self, sync):
            self.__sync = sync

        def doneHW(self, token, error, args):
            if self.__sync is not None:
                self.__sync.done(error=error, result=args)

    def jtag_devices(self, sync=None):
        js = self.channel.getRemoteService(jtagdevice_service.NAME)
        js.get_devices(self.__DoneHWCommand(sync))

    def get_jtag_devices_properties(self, id, sync=None):
        js = self.channel.getRemoteService(jtagdevice_service.NAME)
        js.get_properties(id, self.__DoneHWCommand(sync))

    def set_jtag_devices_properties(self, props, sync=None):
        js = self.channel.getRemoteService(jtagdevice_service.NAME)
        js.set_properties(props, self.__DoneHWCommand(sync))

    def get_jtagdevice_properties(self):
        return self.__jtagdevice_properties

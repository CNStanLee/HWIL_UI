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

from tcf.util import cache
from tcf.services import jtagcable as jtagcable_service


#################################################################################################
# TcfNodeJtagCable -
#   * set and get commands for a jtag cable service
#################################################################################################


class TcfNodeJtagCable(object):
    def __init__(self, channel, port_id: str):
        self.channel = channel
        self.__jtag_cable_context = self.JtagCableContext(channel, port_id)
        self.__jtag_cable_server_descriptions = self.JtagCableServerDescriptions(channel)
        self.__jtag_cable_open_servers = self.JtagCableOpenServers(self, channel)
        self.jtag_cable_port_descriptions = {}

    class JtagCableContext(cache.DataCache):
        def __init__(self, channel, port_id):
            super().__init__(channel)
            self.__channel = channel
            self.__port_id = port_id

        def startDataRetrieval(self):
            jc = self.__channel.getRemoteService(jtagcable_service.NAME)
            data = self

            class DoneHWCommand(jtagcable_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    data.set(token, error, args)

            data._command = jc.getContext(self.__port_id, DoneHWCommand())

    class JtagCableServerDescriptions(cache.DataCache):
        def __init__(self, channel):
            super().__init__(channel)
            self._channel = channel

        def startDataRetrieval(self):
            jc = self._channel.getRemoteService(jtagcable_service.NAME)
            data = self

            class DoneHWCommand(jtagcable_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    data.set(token, error, args)

            data._command = jc.getServerDescriptions(DoneHWCommand())

    class JtagCablePortDescriptions(cache.DataCache):
        def __init__(self, channel, serverid):
            super().__init__(channel)
            self._channel = channel
            self._serverid = serverid

        def startDataRetrieval(self):
            jc = self._channel.getRemoteService(jtagcable_service.NAME)
            data = self

            class DoneHWCommand(jtagcable_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    data.set(token, error, args)

            data._command = jc.getPortDescriptions(self._serverid, DoneHWCommand())

    class JtagCableOpenServers(cache.DataCache):
        def __init__(self, node, channel):
            super().__init__(channel)
            self.node = node
            self.__channel = channel

        def startDataRetrieval(self):
            jc = self.__channel.getRemoteService(jtagcable_service.NAME)
            data = self

            class DoneHWCommand(jtagcable_service.DoneHWCommand):
                def doneHW(self, token, error, open_servers):
                    for server in open_servers:
                        server_desc = data.node.JtagCablePortDescriptions(data.node.channel, server)
                        data.node.jtag_cable_port_descriptions.update({server: server_desc})
                    data.set(token, error, open_servers)

            data._command = jc.getOpenServers(DoneHWCommand())


    class DoneHWCommand(jtagcable_service.DoneHWCommand):
        def __init__(self, sync):
            self.__sync = sync

        def doneHW(self, token, error, args):
            if self.__sync is not None:
                self.__sync.done(error=error, result=args)

    def openport(self, ctx, sync=None):
        jc = self.channel.getRemoteService(jtagcable_service.NAME)
        jc.openPort(ctx, self.DoneHWCommand(sync))

    def closeport(self, ctx, sync=None):
        jc = self.channel.getRemoteService(jtagcable_service.NAME)
        jc.closePort(ctx, self.DoneHWCommand(sync))

    def get_jtag_cable_context(self):
        return self.__jtag_cable_context

    def get_jtag_cable_server_descriptions(self):
        return self.__jtag_cable_server_descriptions

    def set_jtag_cable_server_descriptions(self, node):
        self.__jtag_cable_server_descriptions = node

    def get_jtag_cable_open_servers(self):
        return self.__jtag_cable_open_servers

    def set_jtag_cable_open_servers(self, node):
        self.__jtag_cable_open_servers = node

    def on_jtag_cable_context_changed(self, context):
        self.__jtag_cable_context.reset(context)

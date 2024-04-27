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

from tcf.services import jtag as jtag_service
from tcf.util import cache

from xsdb import _tcf_jtag_children_exec_context
from xsdb._tcf_node import TcfNode
from ._tcf_node_jtagcable import TcfNodeJtagCable

#################################################################################################
# TcfJtagContextState -
#   * Creates TcfCache for getting jtag children, context, properties.
#################################################################################################


class TcfJtagNodeExecContext(TcfNode):
    def __init__(self, parent: TcfNode, ctx_id: str):
        super().__init__(parent.channel, parent.info)
        self.id = ctx_id
        self.parent = parent
        self.channel = parent.channel
        self.__children_exec = _tcf_jtag_children_exec_context.TcfJtagChildrenExecContext(self)
        self.__context = self.JtagCtxTcfData(self.channel, self.id)
        self.__capabilities = self.JtagCapabilitiesTcfData(self.channel, self.id)
        self.__jtag_device_node = None
        self.__jtag_device_properties_data = {}
        if parent.parent == '':
            self.__jtag_cable_node = TcfNodeJtagCable(self.channel, self.id)
            self.__jtag_cable_context_data = {}
        else:
            self.__jtag_cable_node = None
            self.__jtag_cable_context_data = None
        self.__context_data = {}
        self.__props = {}

    class JtagCtxTcfData(cache.DataCache):
        def __init__(self, channel, ctx_id):
            super().__init__(channel)
            self.__id = ctx_id

        def startDataRetrieval(self):
            js = self._channel.getRemoteService(jtag_service.NAME)
            ctx = self

            class DoneHWCommand(jtag_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    ctx.set(token, error, args)

            ctx._command = js.get_context(self.__id, DoneHWCommand())
            return False

    class JtagCapabilitiesTcfData(cache.DataCache):
        def __init__(self, channel, ctx_id):
            super().__init__(channel)
            self.__id = ctx_id

        def startDataRetrieval(self):
            js = self._channel.getRemoteService(jtag_service.NAME)
            ctx = self

            class DoneHWCommand(jtag_service.DoneHWCommand):
                def doneHW(self, token, error, args):
                    ctx.set(token, error, args)

            ctx._command = js.get_capabilities(self.__id, DoneHWCommand())
            return False

    def get_children(self):
        return self.__children_exec

    def get_context(self):
        return self.__context

    def get_capabilities(self):
        return self.__capabilities

    def get_context_data(self):
        return self.__context_data

    def set_context_data(self, data):
        self.__context_data = data

    def set_jtag_device_node(self, node):
        self.__jtag_device_node = node

    def get_jtag_device_node(self):
        return self.__jtag_device_node

    def get_properties_data(self):
        return self.__jtag_device_properties_data

    def set_properties_data(self, data):
        self.__jtag_device_properties_data = data

    def get_jtag_cable_node(self):
        return self.__jtag_cable_node

    def set_jtag_cable_node(self, node):
        self.__jtag_cable_node = node

    def get_jtag_cable_context_data(self):
        return self.__jtag_cable_context_data

    def set_jtag_cable_context_data(self, data):
        self.__jtag_cable_context_data = data

    def set_props(self, props):
        self.__props = props

    def get_props(self,):
        return self.__props

    def dispose(self):
        assert not self.is_disposed()
        super().dispose()

    def on_jtag_context_added(self, context):
        assert not self.is_disposed()
        self.__children_exec.on_jtag_context_added(context)

    def on_jtag_context_removed(self, context):
        assert not self.is_disposed()
        self.dispose()

    def on_jtag_context_changed(self, context):
        assert not self.is_disposed()
        self.__context.reset(context)

    def on_jtag_cable_context_changed(self, context):
        assert not self.is_disposed()
        self.__jtag_cable_node.get_jtag_cable_context().reset(context)

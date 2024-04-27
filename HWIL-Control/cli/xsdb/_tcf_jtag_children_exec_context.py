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

import xsdb
from tcf.services import jtag as jtag_service
from xsdb import _logger
from xsdb._tcf_children import TcfChildren
from xsdb._tcf_node import TcfNode


#################################################################################################
# TcfJtagChildrenExecContext -
#   * Sends command to get the Jtag Children
#   * Gets the list of children
#   * Creates a node for each context
#   * Updates the list of nodes
#################################################################################################

class TcfJtagChildrenExecContext(TcfChildren):
    def __init__(self, node: TcfNode):
        super().__init__(node)
        self.__jtag_children = self.JtagChildrenTcfChildren(node)

    # ---------------------------------------------------------------------------------------------
    # ---- JtagChildrenTcfChildren -----------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class JtagChildrenTcfChildren(TcfChildren):
        def __init__(self, node):
            super().__init__(node)
            self.__node = node

        def startDataRetrieval(self):
            js = self.node.channel.getRemoteService(jtag_service.NAME)
            children = self

            class DoneHWCommand(jtag_service.DoneHWCommand):
                def doneHW(self,  token, error, args):
                    data = {}
                    if children._command is token and error is None:
                        _logger.debug(' [R] {0:3s} [Jtag getChildren] ---- {1}'.format(token.id, args))
                        for context_id in args:
                            if context_id in children.node.info.get_nodes().keys():
                                n = children.node.info.get_node(context_id)
                            else:
                                n = xsdb._tcf_jtag_node_exec_context.\
                                    TcfJtagNodeExecContext(children.node, context_id)
                            assert n.parent.id == children.node.id
                            data.update({context_id: n})
                            children.node.info.update_nodes(data)
                    children.set(token, error, data)

            children._command = js.get_children(self.node.id, DoneHWCommand())
            _logger.debug(' [C] {0:3s} [Jtag getChildren] ---- {1}'.format(children._command.id, self.node.id))
            return False

    # ---------------------------------------------------------------------------------------------
    # StartDataRetrieval
    # ---------------------------------------------------------------------------------------------
    def startDataRetrieval(self):
        pending = None
        if not self.__jtag_children.validate():
            pending = self.__jtag_children
        if pending is not None:
            pending.wait(self)
            return False
        error = self.__jtag_children.getError()
        data = {'jtag_children': {}}
        m1 = self.__jtag_children.getData()
        if m1 is not None:
            data['jtag_children'].update(m1)
        self.set(None, error, data)
        return True

    def on_jtag_context_added(self, context):
        self.reset()
        self.__jtag_children.reset()
        data = {}
        context_id = context.props['ID']
        if context_id in self.node.info.get_nodes().keys():
            n = self.node.info.get_node(context_id)
        else:
            n = xsdb._tcf_jtag_node_exec_context.TcfJtagNodeExecContext(self.node, context_id)
        data.update({context_id: n})
        self.node.info.update_nodes(data)
        if isinstance(context.service, jtag_service.JtagService):
            n.get_context().reset(context)
            n.set_context_data(context)

    def on_jtag_cable_context_added(self, context):
        self.reset()
        self.__jtag_children.reset()
        data = {}
        context_id = context['ID']
        if context_id in self.node.info.get_nodes().keys():
            n = self.node.info.get_node(context_id)
        else:
            n = xsdb._tcf_jtag_node_exec_context.TcfJtagNodeExecContext(self.node, context_id)
        data.update({context_id: n})
        self.node.info.update_nodes(data)
        n.get_jtag_cable_node().get_jtag_cable_context().reset(context)
        n.set_jtag_cable_context_data(context)
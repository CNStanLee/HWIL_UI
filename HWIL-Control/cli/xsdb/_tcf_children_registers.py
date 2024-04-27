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

#import xsdb
from xsdb._tcf_children import TcfChildren
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_register import TcfNodeRegister
from tcf.services import registers as reg_service
from xsdb import _logger

#################################################################################################
# TcfChildrenRegisters -
#   * Sends command to get the Register children
#   * Creates a Register node for each register child
#################################################################################################

class TcfChildrenRegisters(TcfChildren):
    def __init__(self, node: TcfNode):
        super().__init__(node)
        self.__node = node

    def startDataRetrieval(self):
        reg = self.node.channel.getRemoteService(reg_service.NAME)
        if reg is None:
            self.set(None, None, {})
            return True
        reg_children = self

        class DoneGetChildren(reg_service.DoneGetChildren):
            def doneGetChildren(self, token, error, context_ids):
                data = None
                if reg_children._command is token and error is None:
                    data = {}
                    _logger.debug(' [R] {0:3s} [Registers getChildren] ---- {1}'.format(token.id, context_ids))
                    for context_id in context_ids:
                        if context_id in reg_children.node.info.get_nodes().keys():
                            n = reg_children.node.info.get_node(context_id)
                        else:
                            n = TcfNodeRegister(reg_children.node, context_id)
                        data.update({context_id: n})
                        reg_children.node.info.update_nodes(data)
                        reg_children.node.set_reg_children_data(data)
                reg_children.set(token, error, data)
        reg_children._command = reg.getChildren(self.node.id, DoneGetChildren())
        _logger.debug(' [C] {0:3s} [Registers getChildren] ---- {1}'.format(reg_children._command.id, self.node.id))
        return False

    def on_register_context_changed(self):
        nodes = self.__node.info.get_nodes().values()
        for node in nodes:
            if isinstance(node, TcfNodeRegister):
                node.on_register_context_changed()
        self.reset()

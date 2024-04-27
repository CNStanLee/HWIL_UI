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

from tcf.services import memory as mem_service
from tcf.services import runcontrol as rc_service

import xsdb
from xsdb import _logger
from xsdb._logger import *
from xsdb._tcf_node import TcfNode
from xsdb._tcf_children import TcfChildren


#################################################################################################
# TcfChildrenExecContext -
#   * Sends command to get the Memory and Run Control Children
#   * Gets the list of children
#   * Creates a node for each context
#   * Updates the list of nodes
#################################################################################################

class TcfChildrenExecContext(TcfChildren):
    def __init__(self, node: TcfNode):
        super().__init__(node)
        self.__mem_children = self.MemChildrenTcfChildren(node)
        self.__run_children = self.RunChildrenTcfChildren(node)

    # ---------------------------------------------------------------------------------------------
    # ---- MemChildrenTcfChildren -----------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class MemChildrenTcfChildren(TcfChildren):
        def __init__(self, node):
            super().__init__(node)
            self.__node = node

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            mem = self.node.channel.getRemoteService(mem_service.NAME)
            mem_children = self

            class DoneGetChildren(mem_service.DoneGetChildren):
                def doneGetChildren(self, token, error, context_ids):
                    data = {}
                    if mem_children._command is token and error is None:
                        _logger.debug(' [R] {0:3s} [Memory getChildren] ---- {1}'.format(token.id, context_ids))
                        for context_id in context_ids:
                            if context_id in mem_children.node.info.get_nodes().keys():
                                n = mem_children.node.info.get_node(context_id)
                            else:
                                n = xsdb._tcf_node_exec_context.TcfNodeExecContext(mem_children.node, context_id)
                            assert n.parent == mem_children.node
                            data.update({context_id: n})
                            mem_children.node.info.update_nodes(data)
                    mem_children.set(token, error, data)

            mem_children._command = mem.getChildren(self.node.id, DoneGetChildren())
            _logger.debug(' [C] {0:3s} [Memory getChildren] ---- {1}'.format(mem_children._command.id, self.node.id))
            return False

    # ---------------------------------------------------------------------------------------------
    # ---- RunChildrenTcfChildren -----------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RunChildrenTcfChildren(TcfChildren):
        def __init__(self, node):
            super().__init__(node)
            self.__node = node

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            run = self.node.channel.getRemoteService(rc_service.NAME)
            run_children = self

            class DoneGetChildren(rc_service.DoneGetChildren):
                def doneGetChildren(self, token, error, context_ids):
                    data = {}
                    if run_children._command is token and error is None:
                        _logger.debug(' [R] {0:3s} [RunControl getChildren] ---- {1}'.format(token.id, context_ids))
                        for context_id in context_ids:
                            if context_id in run_children.node.info.get_nodes().keys():
                                n = run_children.node.info.get_node(context_id)
                            else:
                                n = xsdb._tcf_node_exec_context.TcfNodeExecContext(run_children.node, context_id)
                            assert n.parent == run_children.node
                            data.update({context_id: n})
                            run_children.node.info.update_nodes(data)
                    run_children.set(token, error, data)

            run_children._command = run.getChildren(self.node.id, DoneGetChildren())
            _logger.debug(' [C] {0:3s} [RunControl getChildren] ---- {1}'.format(run_children._command.id, self.node.id))
            return False

    # ---------------------------------------------------------------------------------------------
    # StartDataRetrieval
    # ---------------------------------------------------------------------------------------------
    def startDataRetrieval(self):
        pending = None
        if not self.__mem_children.validate():
            pending = self.__mem_children
        if not self.__run_children.validate():
            pending = self.__run_children
        if pending is not None:
            pending.wait(self)
            return False
        error = self.__mem_children.getError()
        if error is None:
            error = self.__run_children.getError()
        data = {'children': {}, 'mem_children': {}}
        m1 = self.__mem_children.getData()
        m2 = self.__run_children.getData()
        if m1 is not None:
            data['children'].update(m1)
            data['mem_children'].update(m1)
        if m2 is not None:
            data['children'].update(m2)

        self.set(None, error, data)
        return True

    # ---------------------------------------------------------------------------------------------
    # onContextAdded
    # ---------------------------------------------------------------------------------------------
    def on_context_added(self, context):
        self.reset()
        self.__mem_children.reset()
        self.__run_children.reset()
        data = {}
        context_id = context.getID()
        if context_id in self.node.info.get_nodes().keys():
            n = self.node.info.get_node(context_id)
        else:
            n = xsdb._tcf_node_exec_context.TcfNodeExecContext(self.node, context_id)
        data.update({context_id: n})
        self.node.info.update_nodes(data)
        if isinstance(context.service, rc_service.RunControlService):
            n.get_run_context().reset(context)
            n.set_run_context_data(context)
        if isinstance(context.service, mem_service.MemoryService):
            n.get_memory_context().reset(context)
            n.mem_context_data = context

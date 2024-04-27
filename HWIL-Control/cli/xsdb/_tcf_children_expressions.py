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

from xsdb._tcf_children import TcfChildren
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_expression import TcfNodeExpression
from tcf.services import expressions as exp_service
from xsdb import _logger


#################################################################################################
# TcfChildrenLocalVariables -
#################################################################################################
class TcfChildrenExpressions(TcfChildren):
    def __init__(self, node: TcfNode):
        super().__init__(node)
        self._node = node

    def startDataRetrieval(self):
        exps = self.node.channel.getRemoteService(exp_service.NAME)
        if exps is None :
            self.set(None, None, {})
            return True
        exps_children = self

        class DoneGetChildren(exp_service.DoneGetChildren):
            def doneGetChildren(self, token, error, contexts):
                data = None
                if exps_children._command is token and error is None:
                    cnt = 0
                    data = {}
                    _logger.debug(' [R] {0:3s} [Expressions getChildren] ---- {1}'.format(token.id, contexts))
                    for id in contexts:
                        if id in exps_children.node.info.get_nodes().keys():
                            n = exps_children.node.info.get_node(id)
                        else:
                            n = TcfNodeExpression(exps_children.node, id)

                        data.update({id: n})
                        exps_children.node.info.update_nodes(data)
                        #exps_children.node.set_exps_children_data(data)
                exps_children.set(token, error, data)

        exps_children._command = exps.getChildren(self._node.id, DoneGetChildren())
        _logger.debug(' [C] {0:3s} [Expressions getChildren] ---- {1}'.format(exps_children._command.id, self.node.id))
        return False

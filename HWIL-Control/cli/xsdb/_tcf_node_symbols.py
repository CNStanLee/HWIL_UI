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

from tcf.services import symbols as sym_service
from tcf.util import cache
from . import _logger
from xsdb._tcf_node import TcfNode
from xsdb._tcf_children import TcfChildren


#################################################################################################
# TcfFindSymbol -
#   * Creates TcfCache for getting symbol_id using address from tcf-symbol service.
# TCFNodeSymbol -
#   * Creates TcfCache for getting data from tcf-symbol service.
#################################################################################################


class TcfFindSymbol(object):
    def __init__(self, channel, context_id, address):
        self.id = address
        self.channel = channel
        self.symbol_id = None
        self.__find_symbol = self.SymbolFindByAddressData(channel, context_id, address)

    class SymbolFindByAddressData(cache.DataCache):
        def __init__(self, channel, context_id, address):
            super().__init__(channel)
            self.__context_id = context_id
            self.__address = address
            self.__channel = channel

        def startDataRetrieval(self):
            sym = self.__channel.getRemoteService(sym_service.NAME)
            sym_data = self

            class DoneFind(sym_service.DoneFind):
                def doneFind(self, token, error, symbol_ids):
                    sym_data.set(token, error, symbol_ids)

            sym_data._command = sym.findByAddr(self.__context_id, self.__address, DoneFind())
            return False

    def find_symbol_id(self):
        return self.__find_symbol


class TcfNodeSymbol(TcfNode):
    def __init__(self, parent: TcfNode, ctx_id: str):
        super().__init__(parent.channel, parent.info, ctx_id)
        self.id = ctx_id
        self.parent = parent
        self.channel = parent.channel
        self.__context = self.SymbolCtxTcfData(self)
        self.__children = self.SymbolChildrenTcfData(self)
        self.__context_data = None
        self.__children_data = None

    # ---------------------------------------------------------------------------------------------
    # ---- SymbolCtxTcfData -----------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class SymbolCtxTcfData(cache.DataCache):
        def __init__(self, outer_node_ctx):
            super().__init__(outer_node_ctx.channel)
            self.__node = outer_node_ctx
            self.__id = outer_node_ctx.id

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            sym = self._channel.getRemoteService(sym_service.NAME)
            sym_ctx = self

            class DoneGetContext(sym_service.DoneGetContext):
                def __init__(self, node):
                    self.__node = node

                def doneGetContext(self, token, error, context):
                    _logger.debug(' [R] {0:3s} [Symbols getContext] ---- {1}'.format(token.id, context))
                    self.__node.set_context_data(context)
                    sym_ctx.set(token, error, context)

            sym_ctx._command = sym.getContext(self.__id, DoneGetContext(self.__node))
            _logger.debug(' [C] {0:3s} [Symbols getContext] ---- {1}'.format(sym_ctx._command.id, self.__id))
            return False

    # ---------------------------------------------------------------------------------------------
    # ---- SymbolChildrenTcfData ------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class SymbolChildrenTcfData(TcfChildren):
        def __init__(self, node: TcfNode):
            super().__init__(node)
            self.__node = node

        def startDataRetrieval(self):
            sym = self.node.channel.getRemoteService(sym_service.NAME)
            sym_ctx = self

            class DoneGetChildren(sym_service.DoneGetChildren):
                def __init__(self, node):
                    self.__node = node

                def doneGetChildren(self, token, error, context_ids):
                    data = None
                    if sym_ctx._command is token and error is None:
                        data = {}
                        _logger.debug(' [R] {0:3s} [Symbols getChildren] ---- {1}'.format(token.id, context_ids))
                        for context_id in context_ids:
                            if context_id in sym_ctx.node.info.get_nodes().keys():
                                n = sym_ctx.node.info.get_node(context_id)
                            else:
                                n = TcfNodeSymbol(sym_ctx.node, context_id)
                            data.update({context_id: n})
                            sym_ctx.node.info.update_nodes(data)
                            sym_ctx.node.set_children_data(data)
                        sym_ctx.set(token, error, data)

            sym_ctx._command = sym.getChildren(self.__node.id, DoneGetChildren(self.__node))
            _logger.debug(' [C] {0:3s} [Symbols getChildren] ---- {1}'.format(sym_ctx._command.id, self.__node.id))
            return False

    def get_context(self):
        return self.__context

    def set_context_data(self, data):
        self.__context_data = data

    def get_context_data(self):
        return self.__context_data

    def get_children(self):
        return self.__children

    def set_children_data(self, data):
        self.__children_data = data

    def set_ctx_id(self, id):
        self.id = id
        self.__context = self.SymbolCtxTcfData(self)

    def get_ctx_id(self):
        return self.id

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
from tcf.services import expressions as exp_service

import xsdb
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_symbols import TcfNodeSymbol
from . import _logger


class TcfNodeExpression(TcfNode):
    def __init__(self, parent: TcfNode, var_id: str, exp_string: str):
        if var_id is not None:
            id = var_id
        else:
            id = 'Expr'
        super().__init__(parent.channel, parent.info, var_id)
        self.id = id
        self.parent = parent
        self.channel = parent.channel
        #self.__children = xsdb._tcf_children_registers.TcfChildrenRegisters(self)
        self.__context = self.ExpressionCtxTcfData(self)
        self.__context_data = {}
        self.__symbol_context = None
        self.__type_context = None
        self.__base_type_context = None

    # ---------------------------------------------------------------------------------------------
    # ---- ExpressionCtxTcfData -------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class ExpressionCtxTcfData(cache.DataCache):
        def __init__(self, outer_node_ctx):
            super().__init__(outer_node_ctx.channel)
            self.__node = outer_node_ctx
            self.__id = outer_node_ctx.id

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            exps = self._channel.getRemoteService(exp_service.NAME)
            exp_ctx = self

            class DoneGetContext(exp_service.DoneGetContext):
                def __init__(self, node):
                    self.__node = node

                def doneGetContext(self, token, error, context):
                    _logger.debug(' [R] {0:3s} [Expressions getContext] ---- {1}'.format(token.id, context))
                    self.__node.set_context_data(context)
                    exp_ctx.set(token, error, context)

            exp_ctx._command = exps.getContext(self.__id, DoneGetContext(self.__node))
            _logger.debug(' [C] {0:3s} [Expressions getContext] ---- {1}'.format(exp_ctx._command.id, self.__id))
            return False

    def evaluate(self, sync=None):
        exps = self.channel.getRemoteService(exp_service.NAME)

        class DoneEvaluate(exp_service.DoneEvaluate):
            def __init__(self, sync):
                self.__sync = sync

            def doneEvaluate(self, token, error, value):
                _logger.debug(' [R] {0:3s} [Expressions evaluate] ---- {1}'.format(token.id, value))
                if self.__sync is not None:
                    if error:
                        #self.__sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'],
                        #                 result=None)
                        self.__sync.done(error=None, result=error.getAttributes().get('Format', None))
                    else:
                        self.__sync.done(error=None, result=value)

        _command = exps.evaluate(self.id, DoneEvaluate(sync))
        _logger.debug(' [C] {0:3s} [Expressions evaluate] ---- {1}'.format(_command.id, self.id))
        return False

    def create(self, expression, sync=None):
        exps = self.channel.getRemoteService(exp_service.NAME)

        class DoneCreate(exp_service.DoneCreate):
            def __init__(self, sync):
                self.__sync = sync

            def doneCreate(self, token, error, context):
                _logger.debug(' [R] {0:3s} [Expressions create] ---- {1}'.format(token.id, context))
                if self.__sync is not None:
                    if error:
                        self.__sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'],
                                         result=None)
                    else:
                        self.__sync.done(error=None, result=context)

        _command = exps.create(self.parent.id, None, expression, DoneCreate(sync))
        _logger.debug(' [C] {0:3s} [Expressions create] ---- {1}'.format(_command.id, expression))
        return False

    def assign(self, value, sync=None):
        exps = self.channel.getRemoteService(exp_service.NAME)

        class DoneAssign(exp_service.DoneAssign):
            def __init__(self, sync):
                self.__sync = sync

            def doneAssign(self, token, error):
                _logger.debug(' [R] {0:3s} [Expressions assign] ---- '.format(token.id))
                if self.__sync is not None:
                    if error:
                        self.__sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'],
                                         result=None)
                    else:
                        self.__sync.done(error=None, result=None)

        _command = exps.assign(self.id, value, DoneAssign(sync))
        _logger.debug(' [C] {0:3s} [Expressions assign] ---- {1}'.format(_command.id, self.id, value))
        return False

    def get_context(self):
        return self.__context

    def set_context_data(self, data):
        self.__context_data = data

    def get_symbol_context(self, sym_id):
        if sym_id in self.info.get_nodes().keys():
            self.__symbol_context = self.info.get_node(sym_id)
        else:
            self.__symbol_context = TcfNodeSymbol(self, sym_id)
        self.info.update_nodes({sym_id: self.__symbol_context})
        return self.__symbol_context

    def get_type_context(self, type_id):
        if type_id in self.info.get_nodes().keys():
            self.__type_context = self.info.get_node(type_id)
        else:
            self.__type_context = TcfNodeSymbol(self, type_id)
        self.info.update_nodes({type_id: self.__type_context})
        return self.__type_context

    def get_base_type_context(self, type_id):
        if type_id in self.info.get_nodes().keys():
            self.__base_type_context = self.info.get_node(type_id)
        else:
            self.__base_type_context = TcfNodeSymbol(self, type_id)
        self.info.update_nodes({type_id: self.__base_type_context})
        return self.__base_type_context
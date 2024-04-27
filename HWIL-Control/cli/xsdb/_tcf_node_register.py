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
from tcf.services import registers as reg_service

import xsdb
from xsdb._tcf_node import TcfNode
#from xsdb._tcf_children_registers import TcfChildrenRegisters
from . import _logger

class TcfNodeRegister(TcfNode):
    def __init__(self, parent: TcfNode, ctx_id: str):
        super().__init__(parent.channel, parent.info, ctx_id)
        self.id = ctx_id
        self.parent = parent
        self.channel = parent.channel
        self.__children = xsdb._tcf_children_registers.TcfChildrenRegisters(self)
        self.__context = self.RegCtxTcfData(self)
        self.__context_data = {}
        self.__children_data = {}
        self.__value = None
        self.__value = {'value': None, 'error': None}
    # ---------------------------------------------------------------------------------------------
    # ---- RegCtxTcfData --------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RegCtxTcfData(cache.DataCache):
        def __init__(self, outer_node_ctx):
            super().__init__(outer_node_ctx.channel)
            self.__node = outer_node_ctx
            self.__id = outer_node_ctx.id

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            reg = self._channel.getRemoteService(reg_service.NAME)
            reg_ctx = self

            class DoneGetContext(reg_service.DoneGetContext):
                def __init__(self, node):
                    self.__node = node

                def doneGetContext(self, token, error, context):
                    _logger.debug(' [R] {0:3s} [Registers getContext] ---- {1}'.format(token.id, context))
                    self.__node.set_context_data(context)
                    reg_ctx.set(token, error, context)

            reg_ctx._command = reg.getContext(self.__id, DoneGetContext(self.__node))
            _logger.debug(' [C] {0:3s} [Registers getContext] ---- {1}'.format(reg_ctx._command.id, self.__id))
            return False

    # ---------------------------------------------------------------------------------------------
    # def read_reg(self):
    #     ctx = self.__context.getData()
    #
    #     class DoneGet(reg_service.DoneGetContext):
    #         def __init__(self, node):
    #             self.__node = node
    #
    #         def doneGet(self, token, error, value):
    #             if error is not None:
    #                 raise Exception(f"{error.getAttributes()['Format']}") from None
    #             else:
    #                 endianness = "big" if ctx.isBigEndian() else "little"
    #                 val = int.from_bytes(bytes(value), endianness)
    #                 self.__node.set_reg_value(val)
    #                 _logger.debug(' [R] {0:3s} [Register get] ---- {1}'.format(token.id, hex(val)))
    #
    #     token = ctx.get(DoneGet(self))
    #     _logger.debug(' [C] {0:3s} [Registers get] ---- {1}'.format(token.id, ctx.getName()))
    #     return True

    # ---------------------------------------------------------------------------------------------
    def read_register(self, sync):
        ctx = self.__context.getData()

        class DoneGet(reg_service.DoneGet):
            def __init__(self, node, sync):
                self.__node = node
                self.sync = sync

            def doneGet(self, token, error, value):
                if error is not None:
                    self.__node.set_reg_value(None, error)
                    _logger.debug(' [R] {0:3s} [Register get] ---- {1}'.format(token.id, error))
                    self.sync.done(error=None, result=error.getAttributes()['Format'])
                else:
                    endianness = "big" if ctx.isBigEndian() else "little"
                    val = int.from_bytes(bytes(value), endianness)
                    self.__node.set_reg_value(val, error)
                    _logger.debug(' [R] {0:3s} [Register get] ---- {1}'.format(token.id, hex(val)))
                    self.sync.done(error=None, result=None)

        token = ctx.get(DoneGet(self, sync))
        _logger.debug(' [C] {0:3s} [Registers get] ---- {1}'.format(token.id, ctx.getName()))
        return True

    # ---------------------------------------------------------------------------------------------
    def write_register(self, val, sync):
        ctx = self.__context.getData()

        class DoneSet(reg_service.DoneSet):
            def __init__(self, node, sync):
                self.__node = node
                self.sync = sync

            def doneSet(self, token, error):
                _logger.debug(' [R] {0:3s} [Register set] ---- {1}'.format(token.id, error))
                if error is not None:
                    error = error.getAttributes()['Format']
                self.sync.done(error=error, result=None)

        token = ctx.set(val, DoneSet(self, sync))
        _logger.debug(' [C] {0:3s} [Registers set] ---- {1} - {2}'.format(token.id, ctx.getName(), val))
        return True

    def get_reg_children(self):
        return self.__children

    def get_context(self):
        return self.__context

    def get_values(self):
        return self.__value

    def set_context_data(self, data):
        self.__context_data = data

    def get_context_data(self):
        return self.__context_data

    def set_reg_children_data(self, data):
        self.__children_data = data

    def get_reg_children_data(self):
        return self.__children_data

    def set_reg_value(self, value, error):
        self.__value['value'] = value
        self.__value['error'] = error

    def get_reg_value(self):
        return self.__value.get('value', None)

    def get_reg_error(self):
        error = self.__value.get('error', None)
        if error is not None:
            return error.getAttributes().get('Format')

    # ---------------------------------------------------------------------------------------------
    # ---- Events ---------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    def on_register_context_changed(self):
        self.__children.reset()
        self.__children_data = {}
        self.__context.reset()
        self.__context_data = {}

# ---------------------------------------------------------------------------------------------
def read_multiple_registers(node_list, sync):
    pending = []

    def on_done():
        sync.done(error=None, result=None)

    class DoneGet(reg_service.DoneGet):
        def __init__(self, node):
            self.__node = node
            self.__ctx = node.get_context_data()

        def doneGet(self, token, error, value):
            pending.remove(token)
            if error is not None:
                self.__node.set_reg_value(None, error)
                _logger.debug(' [R] {0:3s} [Register get] ---- {1}'.format(token.id, error))
            else:
                endianness = "big" if self.__ctx.isBigEndian() else "little"
                val = int.from_bytes(bytes(value), endianness)
                self.__node.set_reg_value(val, error)
                _logger.debug(' [R] {0:3s} [Register get] ---- {1}'.format(token.id, hex(val)))
            if not pending:
                on_done()

    for node in node_list:
        token = node.get_context().getData().get(DoneGet(node))
        pending.append(token)
        _logger.debug(' [C] {0:3s} [Registers get] ---- {1}'.format(token.id, node.get_context_data().getName()))

    return True

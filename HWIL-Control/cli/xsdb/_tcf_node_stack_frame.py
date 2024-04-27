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

from tcf.services import stacktrace as stacktrace_service
from tcf.util import cache

from xsdb._tcf_node_line_numbers import TcfNodeLineNumber
from xsdb._tcf_node_symbols import TcfNodeSymbol, TcfFindSymbol


#################################################################################################
# TcfNodeStackFrame -
#   * Creates TcfCache for getting stacktrace children, context data.
#################################################################################################

class TcfNodeStackFrame(object):
    def __init__(self, __tcf_node_exec_ctx, channel, id: str):
        self.id = id
        self.channel = channel
        self.__tcf_node_exec_ctx = __tcf_node_exec_ctx
        self.stacktrace_children_data = []
        self.stacktrace_context_data = []
        self.__stacktrace_children = self.StackTraceChildrenTcfData(self, channel, id)
        self.__stacktrace_context = self.StackTraceContextTcfData(self, channel, id)
        self.__stacktrace_children_range = self.StackTraceChildrenRangeTcfData(self, channel, id, 10)
        self.__max_frames = -1
        self.__prev_max_frames = -2
        self.__line_number_node_list = []
        self.__symbol_node_list = []
        self.__symbols = []
        self.__stacktrace_data = {'data': {}, 'error': ''}

    class StackTraceChildrenTcfData(cache.DataCache):
        def __init__(self, __tcf_node_exec_ctx, channel, id):
            super().__init__(channel)
            self.__tcf_node_exec_ctx = __tcf_node_exec_ctx
            self.__id = id
            self.__channel = channel

        def startDataRetrieval(self):
            st = self.__channel.getRemoteService(stacktrace_service.NAME)
            st_child = self

            class DoneGetChildren(stacktrace_service.DoneGetChildren):
                def doneGetChildren(self, token, error, context_ids):
                    st_child.set(token, error, context_ids)
                    return True

            st_child._command = st.getChildren(self.__id, DoneGetChildren())
            return False

    class StackTraceChildrenRangeTcfData(cache.DataCache):
        def __init__(self, __tcf_node_exec_ctx, channel, id, max_frames):
            super().__init__(channel)
            self.__tcf_node_exec_ctx = __tcf_node_exec_ctx
            self.__id = id
            self.__channel = channel
            self.__max_frames = max_frames

        def startDataRetrieval(self):
            st = self.__channel.getRemoteService(stacktrace_service.NAME)
            st_children_range = self

            class DoneGetChildren(stacktrace_service.DoneGetChildren):
                def doneGetChildren(self, token, error, context_ids):
                    st_children_range.set(token, error, context_ids)
                    return True

            st_children_range._command = st.getChildrenRange(self.__id, 0, self.__max_frames, DoneGetChildren())
            return False

    class StackTraceContextTcfData(cache.DataCache):
        def __init__(self, node, channel, id):
            super().__init__(channel)
            self.__id = id
            self.__node = node
            self.__line_node = None
            self.__symbol_node = None
            self.__channel = channel

        def startDataRetrieval(self):
            st = self.__channel.getRemoteService(stacktrace_service.NAME)
            st_ctx = self
            node = self.__node

            class DoneGetContext(stacktrace_service.DoneGetContext):
                def doneGetContext(self, token, error, context):
                    st_ctx.set(token, error, context)
                    return True

            st_ctx._command = st.getContext(node.stacktrace_children_data, DoneGetContext())
            return False

    def invalidate_stacktrace(self):
        if self.__class__.__name__ == 'TcfNodeStackFrame':
            node = self
        else:
            node = self.__stacktrace
        node.__prev_max_frames = node.__max_frames
        del node.__line_number_node_list
        del node.__symbol_node_list
        del node.__symbols
        node.__line_number_node_list = []
        node.__symbol_node_list = []
        node.__symbols = []
        node.__stacktrace_children.reset()
        node.__stacktrace_children_range.reset()
        node.__stacktrace_context.reset()

    def get_stacktrace_context(self, run):
        done = True
        self.__max_frames = run.arg
        if self.__prev_max_frames != self.__max_frames:
            if not (self.__max_frames != -1 and self.__prev_max_frames > self.__max_frames):
                self.invalidate_stacktrace()

        if self.__max_frames == -1:
            c = self.__stacktrace_children
            if not c.validate(run):
                return None
            if c.getError() is not None:
                self.__stacktrace_data['error'] = c.getError()
                return self.__stacktrace_data
            self.stacktrace_children_data = c.getData()
        else:
            if self.__stacktrace_children_range.isValid() is None or self.__stacktrace_children_range.isValid() is False:
                del self.__stacktrace_children_range
                self.__stacktrace_children_range = self.StackTraceChildrenRangeTcfData(self,
                                                                                       self.channel, self.id,
                                                                                       self.__max_frames)
            c = self.__stacktrace_children_range
            if not c.validate(run):
                return None
            if c.getError() is not None:
                self.__stacktrace_data['error'] = c.getError()
                return self.__stacktrace_data
            self.stacktrace_children_data = c.getData()

        c = self.__stacktrace_context
        if not c.validate(run):
            return None
        if c.getError() is not None:
            self.__stacktrace_data['error'] = c.getError()
            return self.__stacktrace_data
        self.stacktrace_context_data = c.getData()

        for st_context in reversed(self.stacktrace_context_data):
            if not hasattr(st_context, 'line_node'):
                pid = st_context.getProcessID()
                ip = st_context.getInstructionAddress()
                if ip is not None:
                    iph = ipl = ip
                    if st_context.isTopFrame() is True:
                        iph = iph + 1
                    elif ipl > 0:
                        ipl = ipl - 1
                    ln_node = TcfNodeLineNumber(self.channel, '', pid, ipl, iph)
                    st_context.line_node = ln_node
                    self.__line_number_node_list.append(ln_node)

                    sym = TcfFindSymbol(self.channel, pid, ip)
                    st_context.sym = sym
                    self.__symbols.append(sym)

                    sym_node = TcfNodeSymbol(self.__tcf_node_exec_ctx, '')
                    st_context.symbol_node = sym_node
                    self.__symbol_node_list.append(sym_node)

        for line_node in self.__line_number_node_list:
            c = line_node.map_to_source
            if not c.validate(run):
                done = False
            else:
                if c.getError() is not None:
                    self.__stacktrace_data['error'] = c.getError()
                    return self.__stacktrace_data
                line_node.map_to_source_data = c.getData()
        if done is False:
            return None

        for sym in self.__symbols:
            c = sym.find_symbol_id()
            if not c.validate(run):
                done = False
            else:
                if c.getError() is not None:
                    if c.getError().attrs['Format'] == 'Symbol not found':
                        continue
                    else:
                        self.__stacktrace_data['error'] = c.getError()
                        return self.__stacktrace_data
                sym.symbol_id = c.getData()
        if done is False:
            return None

        for i, symbol_node in enumerate(self.__symbol_node_list):
            symbol = self.__symbols[i].symbol_id
            if symbol is not None:
                if symbol_node.get_ctx_id() == '':
                    symbol_node.set_ctx_id(symbol)
                c = symbol_node.get_context()
                if not c.validate(run):
                    done = False
                else:
                    if c.getError() is not None:
                        self.__stacktrace_data['error'] = c.getError()
                        return self.__stacktrace_data
        if done is False:
            return None
        if self.__max_frames == -1:
            self.stacktrace_context_data = list(reversed(self.stacktrace_context_data))
        self.__stacktrace_data['data'] = self.stacktrace_context_data
        return self.__stacktrace_data

    def get_stack_children(self):
        return self.__stacktrace_children
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

from tcf import errors
from tcf.services import memory as mem_service
from tcf.services import runcontrol as rc_service
from tcf.util import cache

from xsdb import _tcf_children_exec_context
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_stack_frame import TcfNodeStackFrame
from xsdb._tcf_node_memory import MemCtxTcfData
from xsdb._tcf_node_memmap import TcfNodeMemoryMap
from xsdb._tcf_node_disassembly import TcfNodeDisassembly
from xsdb._tcf_children_registers import TcfChildrenRegisters
from xsdb._tcf_children_local_variables import TcfChildrenLocalVariables
from xsdb._utils import *
from . import _logger


#################################################################################################
# TcfNodeExecContext -
#   * Creates TcfCache for getting children, context, run state, stack trace etc.
#   * This is created for each context to get all its info.
#   * Resume and Stop commands for the RunControl service.
#   * Handles various RunControl events.
#################################################################################################

class TcfContextState(object):
    def __init__(self, suspended, pc, reason, states):
        self.is_suspended = suspended
        self.suspend_pc = pc
        self.suspend_reason = reason
        self.state_data = states


class TcfNodeExecContext(TcfNode):
    def __init__(self, parent: TcfNode, ctx_id: str):
        super().__init__(parent.channel, parent.info)
        self.id = ctx_id
        self.parent = parent
        self.channel = parent.channel
        self.__children_exec = _tcf_children_exec_context.TcfChildrenExecContext(self)
        self.__mem_context = MemCtxTcfData(self.channel, self.id)
        self.__run_context = self.RunCtxTcfData(self.channel, self.id)
        self.__run_state = self.RunStateTcfData(self)
        self.__stacktrace = TcfNodeStackFrame(self, self.channel, self.id)
        self.__mem_map = TcfNodeMemoryMap(self, self.channel, self.id)
        self.__disassembly = TcfNodeDisassembly(self, self.channel, self.id)
        self.__jtagreg = None
        self.__jtagdevice = None
        self.__children_regs = TcfChildrenRegisters(self)
        self.__children_local_variables = TcfChildrenLocalVariables(self)
        self.__run_context_data = {}
        self.mem_context_data = None
        self.__run_state_data = None
        self.__reg_children_data = {}

    # ---------------------------------------------------------------------------------------------
    # ---- RunCtxTcfData --------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RunCtxTcfData(cache.DataCache):
        def __init__(self, channel, ctx_id):
            super().__init__(channel)
            self.__id = ctx_id

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            run = self._channel.getRemoteService(rc_service.NAME)
            run_ctx = self

            class DoneGetContext(rc_service.DoneGetContext):
                def doneGetContext(self, token, error, context):
                    _logger.debug(' [R] {0:3s} [RunControl getContext] ---- {1}'.format(token.id, context))
                    run_ctx.set(token, error, context)

            run_ctx._command = run.getContext(self.__id, DoneGetContext())
            _logger.debug(' [C] {0:3s} [RunControl getContext] ---- {1}'.format(run_ctx._command.id, self.__id))
            return False

    # ---------------------------------------------------------------------------------------------
    # ---- RunStateTcfData ------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RunStateTcfData(cache.DataCache):
        def __init__(self, outer_node_ctx):
            super().__init__(outer_node_ctx.channel)
            self.__tcf_node_exec_ctx = outer_node_ctx
            self.__id = outer_node_ctx.id

        # -----------------------------------------------------------------------------------------
        def startDataRetrieval(self):
            run_state = self

            class DoneGetState(rc_service.DoneGetState):
                def doneGetState(self, token, error, suspended, pc, reason, states):
                    state = TcfContextState(suspended, pc, reason, states)
                    _logger.debug(
                        ' [R] {0:3s} [RunControl getState] ---- {1} {2} {3} {4}'.format(token.id, suspended, states,
                                                                                        hex(pc), reason))
                    run_state.set(token, error, state)

            if not self.__tcf_node_exec_ctx.get_run_context().validate(self):
                return False
            ctx = self.__tcf_node_exec_ctx.get_run_context().getData()
            if ctx is None or not ctx.hasState():
                # Should we call set on state cache here?
                run_state.set(None, None, None)
                return True
            run_state._command = ctx.getState(DoneGetState())
            _logger.debug(' [C] {0:3s} [RunControl getState] ---- {1}'.format(run_state._command.id, self.__id))
            return False

    # ---------------------------------------------------------------------------------------------
    def resume(self, mode: int, count: int, sync):
        class DoneResume(rc_service.DoneCommand):
            def __init__(self, sync):
                self.sync = sync

            def doneCommand(self, token, error):
                _logger.debug(' [R] {0:3s} [RunControl resume] ---- '.format(token.id))
                if error:
                    if error.getErrorCode() == errors.TCF_ERROR_ALREADY_RUNNING:
                        print(error.getAttributes()['Format'])
                        self.sync.done(error=None, result=error.getAttributes()['Format'])
                    else:
                        self.sync.done(error=error.getAttributes()['Format'], result=None)
                else:
                    self.sync.done(error=None, result=None)

        if self.__run_context.isValid():
            ctx = self.__run_context.getData()
            command = ctx.resume(mode, count, None, DoneResume(sync))
            _logger.debug(' [C] {0:3s} [RunControl resume] ---- {1}'.format(command.id, self.id))
        return True

    # ---------------------------------------------------------------------------------------------
    def stop(self, sync):
        class DoneSuspend(rc_service.DoneCommand):
            def __init__(self, sync):
                self.sync = sync

            def doneCommand(self, token, error):
                _logger.debug(' [R] {0:3s} [RunControl suspend] ---- '.format(token.id))
                if error:
                    if error.getErrorCode() == errors.TCF_ERROR_ALREADY_STOPPED:
                        print(error.getAttributes()['Format'])
                        self.sync.done(error=None, result=error.getAttributes()['Format'])
                    else:
                        self.sync.done(error=error.getAttributes()['Format'], result=None)
                else:
                    self.sync.done(error=None, result=None)

        if self.__run_context.isValid():
            ctx = self.__run_context.getData()
            command = ctx.suspend(DoneSuspend(sync))
            _logger.debug(' [C] {0:3s} [RunControl suspend] ---- {1}'.format(command.id, self.id))
        return True

    # ---------------------------------------------------------------------------------------------
    def get_children(self):
        return self.__children_exec

    # ---------------------------------------------------------------------------------------------
    def get_reg_children(self):
        return self.__children_regs

    # ---------------------------------------------------------------------------------------------
    def get_memory_context(self):
        return self.__mem_context

    # ---------------------------------------------------------------------------------------------
    def get_run_context(self):
        return self.__run_context

    # ---------------------------------------------------------------------------------------------
    def get_run_state(self):
        return self.__run_state

    # ---------------------------------------------------------------------------------------------
    def get_stack_trace(self):
        return self.__stacktrace

    # ---------------------------------------------------------------------------------------------
    def set_run_context_data(self, data):
        self.__run_context_data = data

    # ---------------------------------------------------------------------------------------------
    def get_run_context_data(self):
        return self.__run_context_data

    # ---------------------------------------------------------------------------------------------
    def set_run_state_data(self, data):
        self.__run_state_data = data

    # ---------------------------------------------------------------------------------------------
    def get_run_state_data(self):
        return self.__run_state_data

    # ---------------------------------------------------------------------------------------------
    def set_reg_children_data(self, data):
        self.__reg_children_data = data

    # ---------------------------------------------------------------------------------------------
    def get_reg_children_data(self):
        return self.__reg_children_data

    # ---------------------------------------------------------------------------------------------
    def get_memmap_node(self):
        return self.__mem_map

    # ---------------------------------------------------------------------------------------------
    def get_jtag_device_node(self):
        return self.__jtagdevice

    def set_jtag_device_node(self, node):
        self.__jtagdevice = node

    # ---------------------------------------------------------------------------------------------
    def get_jtag_reg_node(self):
        return self.__jtagreg

    def set_jtag_reg_node(self, node):
        self.__jtagreg = node

    # ---------------------------------------------------------------------------------------------
    def get_disassembly_node(self):
        return self.__disassembly

    # ---------------------------------------------------------------------------------------------
    def get_local_variables_node(self):
        return self.__children_local_variables

    # ---------------------------------------------------------------------------------------------
    def dispose(self):
        assert not self.is_disposed()
        super().dispose()

    # ---------------------------------------------------------------------------------------------
    # ---- Events ---------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------

    def on_context_added(self, context):
        assert not self.is_disposed()
        self.__children_exec.on_context_added(context)

    # ---------------------------------------------------------------------------------------------
    def on_context_removed(self):
        assert not self.is_disposed()
        self.dispose()
        # Todo on context removed

    # ---------------------------------------------------------------------------------------------
    def on_run_context_changed(self, context):
        assert not self.is_disposed()
        self.__run_context.reset(context)
        # Todo on context changed
        # Reset other dependent caches like stacktrace, register children etc.
        self.__children_regs.reset()
        self.__children_exec.reset()
        self.__stacktrace.invalidate_stacktrace()
        # self.children_register.reset()

    # ---------------------------------------------------------------------------------------------
    def on_container_resumed(self):
        assert not self.is_disposed()
        if self.__run_context.isValid():
            ctx = self.__run_context.getData()
            if ctx is not None and ctx.hasState() is False:
                return
        self.on_context_resumed()

    # ---------------------------------------------------------------------------------------------
    def on_container_suspended(self):
        assert not self.is_disposed()
        if self.__run_context.isValid():
            ctx = self.__run_context.getData()
            if ctx is not None and not ctx.hasState():
                return
        self.on_context_suspended(None, None, None)

    # ---------------------------------------------------------------------------------------------
    def on_context_resumed(self):
        assert not self.is_disposed()
        self.__run_state.reset()
        self.__stacktrace.invalidate_stacktrace()
        # invalidate expressions

    # ---------------------------------------------------------------------------------------------
    def on_context_suspended(self, pc, reason, state):
        assert not self.is_disposed()
        if pc is not None:
            s = TcfContextState(True, pc, reason, state)
            self.__run_state.reset(s)
        else:
            self.__run_state.reset()
        self.__stacktrace.invalidate_stacktrace()
        # self.children_stack.onSuspended(func_call)
        # self.children_exps.onSuspended(func_call)
        # self.children_regs.onSuspended(func_call)

    # ---------------------------------------------------------------------------------------------
    def on_context_state_changed(self):
        assert not self.is_disposed()
        self.__run_state.reset()

    # ---------------------------------------------------------------------------------------------
    def on_mem_context_changed(self, context):
        assert not self.is_disposed()
        self.__mem_context.reset(context)

    # ---------------------------------------------------------------------------------------------
    def on_memory_changed(self, address, size):
        assert not self.is_disposed()
        # self.children_stack.onMemoryChanged()
        # self.children_exps.onMemoryChanged()

    # ---------------------------------------------------------------------------------------------
    def on_memmap_changed(self):
        assert not self.is_disposed()
        self.__stacktrace.invalidate_stacktrace()

    # ---------------------------------------------------------------------------------------------
    def on_register_context_changed(self):
        self.__children_regs.on_register_context_changed()

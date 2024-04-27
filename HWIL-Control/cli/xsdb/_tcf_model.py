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

import time

import tcf
from tcf.services import memory as mem_service
from tcf.services import runcontrol as rc_service
from tcf.services import breakpoints as bp_service
from tcf.services import memorymap as memmap_service
from tcf.services import jtag as jtag_service
from tcf.services import jtagdevice as jtagdevice_service
from tcf.services import jtagcable as jtagcable_service
from tcf.services import stapl as stapl_service
from tcf.services import registers as reg_service

import xsdb
from xsdb._utils import *
from xsdb import _logger
from xsdb import _target
from xsdb._tcf_node_exec_context import TcfNodeExecContext, TcfContextState
from xsdb._tcf_jtag_node_exec_context import TcfJtagNodeExecContext
from xsdb._tcf_node_jtagcable import TcfNodeJtagCable
from xsdb._tcf_node_launch import TcfNodeLaunch
from xsdb._tcf_node_info import TcfNodeInfo
from xsdb._tcf_node_register import TcfNodeRegister


#################################################################################################
# TCF Model -
#   * Creates the listeners for different events like Run Control, Memory, Breakpoints etc.
#   * Handles events from different services.
#   * Creates a launch/root node for extracting the top level children.
#   * Updates the list of nodes
#################################################################################################


class TcfModel(object):
    def __init__(self, tcf_channel, session):
        # self.context_map = {}
        self.launch_node = None
        self.session = session
        self.__channel = tcf_channel
        self.__mem_listener = self.MemoryListener(self)
        self.__run_listener = self.RunControlListener(self)
        self.__breakpoint_listener = self.BreakPointListener(self)
        self.__memmap_listener = self.MemoryMapListener(self)
        self.__jtag_listener = self.JtagListener(self)
        self.__jtag_device_listener = self.JtagDeviceListener(self)
        self.__jtag_cable_listener = self.JtagCableListener(self)
        self.__stapl_listener = self.StaplListener(self)
        self.__reg_listener = self.RegistersListener(self)
        self.__info = TcfNodeInfo()

    class JtagDeviceListener(jtagdevice_service.JtagDeviceListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def devicesChanged(self):
            _logger.debug(f' [E] JtagDevice Event devicesChanged')
            self.__tcf_model.launch_node.on_jtag_devices_changed()

    class JtagCableListener(jtagcable_service.JtagCableListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def contextAdded(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] JtagCable Event contextAdded {context}')
                self.__tcf_model.launch_node.on_jtag_cable_context_added(context)
            self.__tcf_model.launch_node.on_jtag_context_added_or_removed()

        def contextChanged(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] JtagCable Event contextChanged {context}')
                ctx_id = context['ID']
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfJtagNodeExecContext):
                    node.on_jtag_cable_context_changed(context)

        def contextRemoved(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] JtagCable Event contextRemoved {context}')
                if isinstance(context, dict):
                    context = context["ID"]
                node = self.__tcf_model.get_node(context)
                if isinstance(node, TcfJtagNodeExecContext):
                    node.on_jtag_context_removed(context)
            self.__tcf_model.launch_node.on_jtag_context_added_or_removed()

        def serverAdded(self, servers):
            for server in servers:
                _logger.debug(f' [E] JtagCable Event serverAdded {server}')
            self.__tcf_model.launch_node.on_jtag_cable_server_added_or_removed()

        def serverRemoved(self, servers):
            for server in servers:
                _logger.debug(f' [E] JtagCable Event serverRemoved {server}')
            self.__tcf_model.launch_node.on_jtag_cable_server_added_or_removed()

    class StaplListener(stapl_service.StaplListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def staplData(self, size, data):
            _logger.debug(f' [E] Stapl Event staplData {data}')
            self.__tcf_model.session._stapl_node.on_stapl_data_event(size, data)

        def staplNotes(self, size, data):
            _logger.debug(f' [E] Stapl Event staplNotes {data}')
            self.__tcf_model.session._stapl_node.on_stapl_notes_event(size, data)

    class JtagListener(jtag_service.JtagListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def contextAdded(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] Jtag Event contextAdded {context}')
                ctx_id = context.props['ParentID']
                if ctx_id == '':
                    self.__tcf_model.launch_node.on_jtag_context_added(context)
                else:
                    node = self.__tcf_model.get_node(ctx_id)
                    if isinstance(node, TcfJtagNodeExecContext):
                        node.on_jtag_context_added(context)
            self.__tcf_model.launch_node.on_jtag_context_added_or_removed()

        def contextChanged(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] Jtag Event contextChanged {context}')
                ctx_id = context.props['ID']
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfJtagNodeExecContext):
                    node.on_jtag_context_changed(context)

        def contextRemoved(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] Jtag Event contextRemoved {context}')
                node = self.__tcf_model.get_node(context)
                if isinstance(node, TcfJtagNodeExecContext):
                    node.on_jtag_context_removed(context)
            self.__tcf_model.launch_node.on_jtag_context_added_or_removed()

    # ---------------------------------------------------------------------------------------------
    # ---- Memory Service Events ------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class MemoryListener(mem_service.MemoryListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        # -----------------------------------------------------------------------------------------
        def contextAdded(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] Memory Event contextAdded {context.getID()}')
                ctx_id = context.getParentID()
                if ctx_id is None:
                    self.__tcf_model.launch_node.on_context_added(context)
                else:
                    node = self.__tcf_model.get_node(ctx_id)
                    node.on_context_added(context)
            self.__tcf_model.launch_node.on_context_added_or_removed()

        # -----------------------------------------------------------------------------------------
        def contextChanged(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] Memory Event contextChanged {context.getID()}')
                ctx_id = context.getID()
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_mem_context_changed(context)

        # -----------------------------------------------------------------------------------------
        def contextRemoved(self, context_ids):
            for ctx_id in context_ids:
                _logger.debug(f' [E] Memory Event contextRemoved {ctx_id}')
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_context_removed()
            self.__tcf_model.launch_node.on_context_added_or_removed()

        # -----------------------------------------------------------------------------------------
        def memoryChanged(self, context_id, address, size):
            _logger.debug(f' [E] Event memoryChanged {context_id}, address {address}, size {size}')
            node = self.__tcf_model.get_node(context_id)
            if isinstance(node, TcfNodeExecContext):
                node.on_memory_changed(address, size)

    # ---------------------------------------------------------------------------------------------
    # ---- RunControl Service Events --------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RunControlListener(rc_service.RunControlListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        # -----------------------------------------------------------------------------------------
        def contextAdded(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] RunControl Event contextAdded {context.getID()}')
                ctx_id = context.getParentID()
                if ctx_id is None:
                    self.__tcf_model.launch_node.on_context_added(context)
                else:
                    node = self.__tcf_model.get_node(ctx_id)
                    if isinstance(node, TcfNodeExecContext):
                        node.on_context_added(context)
            self.__tcf_model.launch_node.on_context_added_or_removed()

        # -----------------------------------------------------------------------------------------
        def contextChanged(self, contexts):
            for context in contexts:
                _logger.debug(f' [E] RunControl Event contextChanged {context.getID()}')
                ctx_id = context.getID()
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_run_context_changed(context)

        # -----------------------------------------------------------------------------------------
        def contextRemoved(self, context_ids):
            for ctx_id in context_ids:
                _logger.debug(f' [E] RunControl Event contextRemoved {ctx_id}')
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_context_removed()
            self.__tcf_model.launch_node.on_context_added_or_removed()

        # -----------------------------------------------------------------------------------------

        def print_state_info(self, ctx_id, ctx_state=None):
            node = self.__tcf_model.get_node(ctx_id)
            exec_as_runnable(self.__tcf_model.session._get_targets)
            exec_as_runnable(self.__tcf_model.session.get_target_state, node)
            if self.__tcf_model.session.get_silent_mode() >= 2:
                return
            target_name = self.__tcf_model.get_target_name(ctx_id)
            target_id = self.__tcf_model.get_target_id(ctx_id)
            if target_name is not None and target_id is not None:
                if ctx_state is not None and node.get_run_state_data().is_suspended:
                    pc = node.get_run_state_data().suspend_pc
                    reason = node.get_run_state_data().suspend_reason
                    result = 'Info: ' + target_name + ' (target ' + str(target_id) + ') Stopped at ' + str(
                        hex(pc)) + ' (' + reason + ')'
                    result += self.__tcf_model.get_source_line_info(ctx_id)
                    print(result)
                else:
                    print(f'Info: ' + target_name + ' (target ' + str(target_id) + ') Running')

        def containerResumed(self, context_ids):
            _logger.debug(f' [E] RunControl Event containerResumed {context_ids}')
            for ctx_id in context_ids:
                node = self.__tcf_model.get_node(ctx_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_container_resumed()
                if node.get_run_context().isValid():
                    self.__tcf_model.session.deferred_queue.put(lambda: self.print_state_info(ctx_id, None))

        def containerSuspended(self, context_id, pc, reason, state, suspended_ids):
            _logger.debug(f' [E] RunControl Event containerSuspended {suspended_ids}')
            ctx_state = TcfContextState(True, pc, reason, state)
            for sus_id in suspended_ids:
                node = self.__tcf_model.get_node(sus_id)
                if isinstance(node, TcfNodeExecContext):
                    node.on_container_suspended()
                if node.get_run_context().isValid():
                    self.__tcf_model.session.deferred_queue.put(lambda: self.print_state_info(sus_id, ctx_state))
                    # TO-DO without sleep, the deferred thread prints the same target and status
                    time.sleep(0.001)
            ctx_node = self.__tcf_model.get_node(context_id)
            if isinstance(ctx_node, TcfNodeExecContext):
                ctx_node.on_context_suspended(pc, reason, state)

        def contextResumed(self, context_id):
            _logger.debug(f' [E] RunControl Event contextResumed {context_id}')
            node = self.__tcf_model.get_node(context_id)
            if isinstance(node, TcfNodeExecContext):
                node.on_context_resumed()
                if node.get_run_context().isValid():
                    self.__tcf_model.session.deferred_queue.put(lambda: self.print_state_info(context_id, None))

        def contextSuspended(self, context_id, pc, reason, state):
            _logger.debug(f' [E] RunControl Event contextSuspended {context_id}')
            ctx_state = TcfContextState(True, pc, reason, state)
            node = self.__tcf_model.get_node(context_id)
            if isinstance(node, TcfNodeExecContext):
                node.on_context_suspended(pc, reason, state)
                if node.get_run_context().isValid():
                    self.__tcf_model.session.deferred_queue.put(lambda: self.print_state_info(context_id, ctx_state))

        # -----------------------------------------------------------------------------------------
        def contextStateChanged(self, context_id):
            _logger.debug(f' [E] RunControl Event contextStateChanged {context_id}')
            node = self.__tcf_model.get_node(context_id)
            if isinstance(node, TcfNodeExecContext):
                node.on_context_state_changed()

    # ---------------------------------------------------------------------------------------------
    # ---- Breakpoint Events ------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class BreakPointListener(bp_service.BreakpointsListener):
        def __init__(self, tcf_model):
            self.tcf_model = tcf_model

        def breakpointStatusChanged(self, bp_id, status):
            id = None
            for k, bp in self.tcf_model.session._bptable.items():
                if bp.id == bp_id:
                    id = k
                    break
            if id is None:
                return
            if bp.show_status is False:
                return
            bp.show_status = False
            bp.on_breakpoint_event_status_changed(id, status)

    # ---------------------------------------------------------------------------------------------
    # ---- MemMap Events ------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class MemoryMapListener(memmap_service.MemoryMapListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def changed(self, context_id):
            _logger.debug(f' [E] MemoryMap Event changed {context_id}')
            node = self.__tcf_model.get_node(context_id)
            if node is not None:
                node.on_memmap_changed()

    # ---------------------------------------------------------------------------------------------
    # ---- Register Events ------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RegistersListener(reg_service.RegistersListener):
        def __init__(self, tcf_model):
            self.__tcf_model = tcf_model

        def contextChanged(self):
            _logger.debug(f' [E] Register Event contextChanged')
            regnodes = []
            nodes = self.__tcf_model.get_nodes().values()
            for node in nodes:
                if isinstance(node, TcfNodeExecContext):
                    node.on_register_context_changed()
                if isinstance(node, TcfNodeRegister):
                    if not node.is_disposed():
                        regnodes.append(node)

            for regnode in regnodes:
                if not regnode.is_disposed():
                    regnode.dispose()

        def registerChanged(self, contextID):
            _logger.debug(f' [E] Register Event registerChanged {contextID}')

    # ---------------------------------------------------------------------------------------------
    def on_connected(self):
        self.launch_node = TcfNodeLaunch(self.__channel, self.__info, self.session)
        _services = sorted(protocol.invokeAndWait(self.session._curchan_obj.getRemoteServices))
        if mem_service.NAME in _services:
            __mem = self.__channel.getRemoteService(mem_service.NAME)
            __mem.addListener(self.__mem_listener)
        if rc_service.NAME in _services:
            __run = self.__channel.getRemoteService(rc_service.NAME)
            __run.addListener(self.__run_listener)
        if bp_service.NAME in _services:
            __bp = self.__channel.getRemoteService(bp_service.NAME)
            __bp.addListener(self.__breakpoint_listener)
        if memmap_service.NAME in _services:
            __mm = self.__channel.getRemoteService(memmap_service.NAME)
            __mm.addListener(self.__memmap_listener)
        if jtag_service.NAME in _services:
            __jl = self.__channel.getRemoteService(jtag_service.NAME)
            __jl.addListener(self.__jtag_listener)
        if jtagdevice_service.NAME in _services:
            __jdl = self.__channel.getRemoteService(jtagdevice_service.NAME)
            __jdl.addListener(self.__jtag_device_listener)
        if jtagcable_service.NAME in _services:
            __jcl = self.__channel.getRemoteService(jtagcable_service.NAME)
            __jcl.addListener(self.__jtag_cable_listener)
        if stapl_service.NAME in _services:
            __sl = self.__channel.getRemoteService(stapl_service.NAME)
            __sl.addListener(self.__stapl_listener)
        if reg_service.NAME in _services:
            __reg = self.__channel.getRemoteService(reg_service.NAME)
            __reg.addListener(self.__reg_listener)
        return

    # ---------------------------------------------------------------------------------------------
    def get_channel(self):
        return self.__channel

    # ---------------------------------------------------------------------------------------------
    def get_launch_node(self):
        return self.__launch_node

    # ---------------------------------------------------------------------------------------------
    def get_nodes(self):
        return self.__info.get_nodes()

    # ---------------------------------------------------------------------------------------------
    def get_node(self, context_id):
        return self.__info.get_node(context_id)

    # ---------------------------------------------------------------------------------------------
    def get_target_name(self, context_id):
        node = self.__info.get_node(context_id)
        if node is not None:
            return node.get_run_context_data().getName()

    # ---------------------------------------------------------------------------------------------
    def get_target_id(self, context_id):
        node = self.__info.get_node(context_id)
        if node is not None:
            return node.target_id

    def read_line_from_file(self, file, line_num):
        with open(file) as fp:
            for i, line in enumerate(fp):
                if i == line_num-1:
                    return line
            raise Exception(f"Cannot read line {line_num} from file {file}") from None


    def get_source_line_info(self, ctx_id):
        result = ''
        if not self.session.get_source_line_view():
            return result
        node = self.session.current_node
        tgt = self.session._get_target_obj(ctx_id)
        if tgt is not None:
            sc = exec_as_runnable(tgt.get_stack_trace, 1)
            if sc is not None:
                if sc[0].line_node is not None:
                    if sc[0].line_node.map_to_source_data is not None:
                        filename = sc[0].line_node.map_to_source_data[0].file
                        directory = sc[0].line_node.map_to_source_data[0].directory
                        linenum = sc[0].line_node.map_to_source_data[0].start_line
                        funcname = sc[0].symbol_node.get_context_data().getName()
                        result += '\n' + funcname + '() at ' + filename + ': ' + str(linenum)
                        file_line = self.read_line_from_file(directory + '/' + filename, linenum)
                        result +=  '\n' + str(linenum) + ': ' + file_line.strip()
        return result



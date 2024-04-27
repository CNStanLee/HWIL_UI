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
from xsdb import _xsdb

import argparse
import json
import math
import ntpath
import os
import platform
import socket
import time
from subprocess import Popen

from tcf.errors import ErrorReport
from elftools.elf import descriptions
from tcf.services import disassembly as dis
from tcf.services import memorymap as mm
from tcf.services.memory import *
from tcf.services import expressions as exp_service
from tcf.services import symbols as sym_service
from tcf.services import registers as reg_service

from xsdb import _breakpoint
from xsdb._gprof import Gprof
from xsdb._mbprofiler import MbProfiler
from xsdb._mbtrace import MbTrace
from xsdb._tcf_streams import *
from xsdb._tcf_reset import TcfReset
from xsdb._tcf_jtag import TcfJtag
from xsdb._tcf_xicom import TcfXicom
from xsdb._breakpoint import bp_get_ids, bp_get_properties, get_bp_status
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_memory import TcfNodeMemory
from xsdb._tcf_node_exec_context import TcfNodeExecContext
from xsdb._tcf_children_registers import TcfChildrenRegisters
from xsdb._tcf_node_jtagdevice import TcfNodeJtagDevice
from xsdb._tcf_node_jtagreg import TcfNodeJtagReg
from xsdb._tcf_node_expression import TcfNodeExpression
from xsdb._tcf_node_symbols import TcfNodeSymbol
from xsdb._elf import ElfParse
from xsdb._utils import *
import xsdb._xsdb


class Target(object):
    __bool_values = {0: 0, 1: 1, True: 1, False: 0}

    def __init__(self, chan, id, node: TcfNodeExecContext, session):
        self.chan = chan
        self.ctx = node.id
        self.name = node.get_run_context_data().getName()
        self.id = id
        self.node = node
        self.session = session

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(Target) if callable(getattr(Target, method)) if
                              not method.startswith('_')]
            for method in public_methods:
                if is_ss(method, name):
                    matches.append(method)
            if len(matches) == 0:
                raise NameError(f"Unknown attribute '{name}'") from None
            if len(matches) > 1:
                raise NameError(f"Ambiguous attribute '{name}': {matches}") from None
            return getattr(self, matches[0])(*args, **kwargs)

        return unknown

    def __select_target_tcl(self, weak=False):
        if self.__class__.__name__ == 'Target':
            _xsdb.cmd(f'targets {self.id}')
            self.session.targets(self.id)
        else:
            if self.curtarget is None:
                if weak is False:
                    raise Exception(f"Invalid target, select a target using targets function") from None
                else:
                    return
            _xsdb.cmd(f'targets {self.curtarget.id}')
            self.targets(self.curtarget.id)

    def loadhw(self, *args, hw=None, mem_ranges=None):
        """
loadhw:
    Load a Vivado HW design, and set the memory map for the current
    target. If the current target is a parent for a group of
    processors, memory map is set for all its child processors.
    If current target is a processor, memory map is set for all the
    child processors of it's parent. This command returns the HW
    design object.

Prototype:
    target.loadhw(*args, hw, mem_ranges)

Optional Arguments:
    mem_ranges
        List of memory ranges from which the memory map should be set.
        Memory map is not set for the addresses outside these ranges.
        If this option is not specified, then memory map is set for all
        the addresses in the hardware design.

Options:
    --regs
        Add registers to memory map.

    --list
        Return a list of open designs for the targets.

Returns:
    Design object
        If the HW design is loaded and memory map is set successfully.
    Exception:
        Failed to open hw design.

Examples:
    session.targets(filter='name =~ "xc7z045"')
    target.loadhw(hw=design.xsa)
        Load the HW design named design.hdf and set memory map for all
        the child processors for which xc7z045 is the parent.

Interactive mode examples:
    loadhw -hw 'zc702.xsa' -mem_ranges [[0x40000000, 0xbfffffff]] -r

        """
        parser = argparse.ArgumentParser(description='loadhw options')
        parser.add_argument('-l', '--list', action='store_true', help='List open hw designs')
        parser.add_argument('-r', '--regs', action='store_true', help='Add registers to memory map')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.list:
            if parsed_args.regs or hw is not None or mem_ranges is not None:
                raise Exception(f"--list cannot be used with other args") from None
            print(_xsdb.cmd('loadhw -list'))
        else:
            if hw is None:
                raise Exception(f"HW design is needed to set memory map") from None
            c = f'loadhw -hw {hw}'
            if mem_ranges is not None:
                c += ' -mem-ranges [list'
                for range in mem_ranges:
                    if len(range) != 2:
                        raise Exception(f"Invalid mem range: must be (start, end)") from None
                    c += ' {'
                    c += f'{range[0]} {range[1]}'
                    c += '}'
                c += ' ]'
            if parsed_args.regs:
                c += ' -regs'
            self.__select_target_tcl()
            _xsdb.cmd(c)

    add_function_metadata('loadhw', 'Set memory map from Vivado design', 'memorymap', 'Target')

    def unloadhw(self):
        """
unloadhw:
    Close the Vivado HW design which was opened during loadhw command,
    and clear the memory map for the current target.
    If the current target is a parent for a group of processors, memory
    map is cleared for all its child processors. If the current target
    is a processor, memory map is cleared for all the child processors
    of it's parent. This command does not clear memory map explicitly
    set by users.

Prototype:
    target.unloadhw()

Returns:
    None

Examples:
    target.unloadhw()

Interactive mode examples:
    unloadhw
        """
        self.__select_target_tcl()
        _xsdb.cmd('unloadhw')

    add_function_metadata('unloadhw', 'Clear memory map set from Vivado design', 'memorymap', 'Target')

    def __select_target(self, weak=False):
        if self.__class__.__name__ == 'Target':
            return self.ctx
        else:
            if self.curtarget is None:
                if weak is False:
                    raise Exception("Invalid target, select a target using targets function.") from None
                else:
                    return
            return self.curtarget.ctx

    def __get_current_node(self):
        if self.__class__.__name__ == 'Target':
            return self.node
        else:
            return self.current_node

    def __get_current_channel(self):
        if self.__class__.__name__ == 'Target':
            return self.node.channel
        else:
            return self.model.launch_node.channel

    def get_stack_trace(self, run):
        n = self.__get_current_node()
        if not n.get_run_state().validate(run):
            return False
        run_state_data = n.get_run_state().getData()
        if run_state_data is None:
            run.sync.done(error="Target doesn't have stack trace", result=None)
            return True
        elif run_state_data.is_suspended is False:
            run.sync.done(error="Target is in running state", result=None)
            return True
        else:
            st_node = n.get_stack_trace()

        c = st_node.get_stacktrace_context(run)
        if c is None:
            return False
        else:
            if c.get('error') == '':
                run.sync.done(error=None, result=c.get('data'))
            else:
                run.sync.done(error=c.get('error').getAttributes()['Format'], result=None)
        return True

    def __get_mem_ctx(self, run):
        node = run.arg
        if not node.get_memory_context().validate(run):
            return False
        else:
            if node.get_memory_context().getError() is not None:
                run.sync.done(error=node.get_memory_context().getError().getAttributes()['Format'], result=None)
            else:
                node.mem_context_data = node.get_memory_context().getData()
                run.sync.done(error=None, result=node.mem_context_data)

    def __get_run_ctx(self, run):
        node = run.arg
        if not node.get_run_context().validate(run):
            return False
        else:
            if node.get_run_context().getError() is not None:
                run.sync.done(error=node.get_run_context().getError().getAttributes()['Format'], result=None)
            else:
                run.sync.done(error=None, result=node.get_run_context().getData())

    def __get_run_state(self, run):
        node = run.arg
        if not node.get_run_state().validate(run):
            return False
        else:
            if node.get_run_state().getError() is not None:
                run.sync.done(error=node.get_run_state().getError().getAttributes()['Format'], result=None)
            else:
                run.sync.done(error=None, result=node.get_run_state().getData())

    def __get_jtag_device_properties(self, run):
        node = run.arg
        if not node.get_jtag_device_node().get_jtagdevice_properties().validate(run):
            return False
        else:
            error = node.get_jtag_device_node().get_jtagdevice_properties().getError()
            if error is not None:
                run.sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'],
                              result=None)
            else:
                run.sync.done(error=None, result=node.get_jtag_device_node().get_jtagdevice_properties().getData())

    def __get_memory_tgt(self, id):
        if id in self.session._mem_targets.keys():
            mem_node = self.session._mem_targets.get(id)
        else:
            mem_node = TcfNodeMemory(self.__get_current_channel(), id)
            self.session._mem_targets[id] = mem_node
        exec_as_runnable(self.__get_mem_ctx, mem_node)
        return mem_node

    def __download_data_callback(self, argvar, size, buf, offset, error, token):
        argvar['cmds'].remove(token)
        if error is not None:
            argvar['err'] = error
            argvar.get('synq').done()
            return
        ts = round(time.time() * 1000)
        current_bytes = argvar.get('current_bytes') + size
        argvar['current_bytes'] = current_bytes
        progress_delta_ms = (ts - argvar.get('progress_time'))
        complete = int((100 * current_bytes) / argvar.get('total_bytes'))
        remaining_bytes = argvar.get('total_bytes') - current_bytes
        if progress_delta_ms > 500 or remaining_bytes == 0:
            argvar['progress_time'] = ts
            total_time = ts - argvar.get('start_time')
            throughput = current_bytes / (total_time / 1000.0)
            if remaining_bytes == 0:
                eta = '{0:02d}{1}{2:02d}'.format(int(total_time / 1000 / 60), ':', int(total_time / 1000 % 60))
            elif total_time > 3000 and throughput > 0:
                remaining_time = int(remaining_bytes / throughput)
                eta = '{0:02d}{1}{2:02d}'.format(int(remaining_time / 60), ':', int(remaining_time % 60))
            else:
                eta = '??:?? ETA'
            str_info = '{0}{1}{2:.2f}{3}{4:.2f}{5}{6}'.format(complete, '%    ', current_bytes / 1048676, 'MB    ',
                                                              throughput / 1048676, 'MB/s    ', eta)
            if not self.session.get_silent_mode():
                print(str_info, end='\r')

        if len(argvar['cmds']) == 0 and complete == 100:
            argvar.get('synq').done()

    def __download_data(self, argvar, mem_node):
        size = argvar.get('chunksize')
        mode = argvar.get('mode')
        while argvar.get('curpos') != argvar['endpos']:
            if argvar['err'] is not None:
                return
            offset = argvar['offset'] + argvar.get('curpos')
            addr = argvar['address'] + argvar.get('curpos')

            if argvar['endpos'] != 0 and size > argvar['endpos'] - argvar.get('curpos'):
                size = argvar['endpos'] - argvar.get('curpos')
            bindata = argvar['f'].read_at(offset, size) if argvar['data'] == 0 else argvar['f'].read(size)

            argvar['cmds'].add((protocol.invokeAndWait(mem_node.mem_write, addr, 0, bindata, 0, size,
                                                       mode, self.__download_data_callback, argvar)).id)

            argvar['curpos'] += size

    def __dow_clear_data(self, argvar, ph, mem_node):
        while True:
            addr = argvar['address'] + ph.get('p_filesz') + argvar.get('curpos')
            size = (ph.get('p_memsz') - ph.get('p_filesz')) - argvar.get('curpos')
            if size == 0 or argvar['err'] is not None:
                return
            if size > argvar.get('chunksize'):
                size = argvar.get('chunksize')
            argvar['cmds'].add((protocol.invokeAndWait(mem_node.mem_fill, addr, 0, [0],
                                                       size, argvar.get('mode'),
                                                       self.__download_data_callback, argvar)).id)
            argvar['curpos'] += size

    def __verify_callback(self, argvar, size, data, offset, error, token):
        argvar['cmds'].remove(token)
        if error is not None or argvar['err'] is not None:
            if error is not None:
                argvar['err'] = error
            argvar.get('synq').done()
            return
        ts = round(time.time() * 1000)
        fdata = list(argvar['f'].read_at(offset, size) if argvar['data'] == 0 else argvar['f'].read(size))
        if fdata != data:
            if len(fdata) != len(data):
                addr = argvar['addr']
                argvar['err'] = f'elf verify failed at address {hex(addr)}'
                return
            for i in range(0, len(fdata)):
                if fdata[i] != data[i]:
                    addr = argvar['addr'] + offset + i
                    argvar['err'] = f'elf verify failed at address {hex(addr)}'
                    return

        current_bytes = argvar.get('current_bytes') + size
        argvar['current_bytes'] = current_bytes
        progress_delta_ms = (ts - argvar.get('progress_time'))
        complete = int((100 * current_bytes) / argvar.get('total_bytes'))
        remaining_bytes = argvar.get('total_bytes') - current_bytes
        if progress_delta_ms > 500 or remaining_bytes == 0:
            argvar['progress_time'] = ts
            total_time = ts - argvar.get('start_time')
            throughput = current_bytes / (total_time / 1000.0)
            if remaining_bytes == 0:
                eta = '{0:02d}{1}{2:02d}'.format(int(total_time / 1000 / 60), ':', int(total_time / 1000 % 60))
            elif total_time > 3000 and throughput > 0:
                remaining_time = int(remaining_bytes / throughput)
                eta = '{0:02d}{1}{2:02d}'.format(int(remaining_time / 60), ':', int(remaining_time % 60))
            else:
                eta = '??:?? ETA'
            str_info = '{0}{1}{2:.2f}{3}{4:.2f}{5}{6}'.format(complete, '%    ', current_bytes / 1048676, 'MB    ',
                                                              throughput / 1048676, 'MB/s    ', eta)
            if not self.session.get_silent_mode():
                print(str_info, end='\r')

        if len(argvar['cmds']) == 0 and complete == 100:
            argvar.get('synq').done()

    def __bpmodify(self, action: str, ids: List[int] or int or str):
        bp_ids = []
        bp_status = list()
        ret = None
        if isinstance(ids, str):
            if ids == '--all':
                bp_ids = list(self.session._bptable.keys())
            else:
                ids = check_int(ids)
                bp_ids.append(ids)
        elif isinstance(ids, int):
            bp_ids.append(ids)
        else:
            bp_ids = ids.copy()
        for id in bp_ids:
            if id in self.session._bptable.keys():
                bp_obj = self.session._bptable[id]
                if action == 'status':
                    res_dict = dict()
                    ret, out_dict = getattr(bp_obj, action)()
                    for key, value in out_dict.items():
                        if 'Error' in value:
                            res_dict = {'target': key, 'Error': value['Error']}
                        else:
                            res_dict = {'target': key, 'location': bp_obj.location,
                                         'HitCount': value['HitCount'], 'Size': value['Size'],
                                         'BreakpointType': value['BreakpointType']}
                        bp_status.append(res_dict)
                    print('\n' + ret)
                else:
                    ret = getattr(bp_obj, action)()
            else:
                raise Exception(f'No Breakpoint with id: {id}.') from None
        if action == 'status':
            return bp_status
        else:
            return ret

    def __update_memory_map(self):
        map_table = []
        for maps in self.session._memmaptable.values():
            map_table += maps
        exec_in_dispatch_thread(self.__get_current_node().get_memmap_node().set, map_table)

    def __resume(self, mode: int = 0, count: int = 1):
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        if isinstance(node, TcfNodeExecContext):
            exec_in_dispatch_thread(node.resume, mode, count)
        # TODO : else case

    def __get_fpga_target(self):
        fpgas = []
        nodes = self.session.model.get_nodes()
        for ctx, ctx_node in nodes.items():
            if ctx_node.__class__.__name__ == 'TcfNodeExecContext':
                if ctx == '':
                    continue
                else:
                    rc = exec_as_runnable(self.__get_run_ctx, ctx_node).getProperties()
                    if 'JtagDeviceID' in rc.keys():
                        if ctx_node.get_jtag_device_node() is None:
                            ctx_node.set_jtag_device_node(TcfNodeJtagDevice(ctx_node, self.__get_current_channel(),
                                                                            rc.get('JtagDeviceID')))
                        if 'reg.jprogram' in exec_as_runnable(self.__get_jtag_device_properties, ctx_node):
                            fpgas.append(self.session.get_context_target_map()[ctx])
        fpgas.sort()
        if len(fpgas) == 0:
            raise Exception('No supported FPGA device found.') from None
        elif len(fpgas) > 1:
            raise Exception(f'Multiple FPGA devices found, use targets command to select one of: {fpgas}.') from None
        else:
            return fpgas[0]

    def __get_program_device(self):
        devices = []
        nodes = self.session.model.get_nodes()
        for ctx, ctx_node in nodes.items():
            if ctx_node.__class__.__name__ == 'TcfNodeExecContext':
                if ctx == '':
                    continue
                else:
                    rc = exec_as_runnable(self.__get_run_ctx, ctx_node).getProperties()
                    if 'JtagDeviceID' in rc.keys():
                        if ctx_node.get_jtag_device_node() is None:
                            ctx_node.set_jtag_device_node(TcfNodeJtagDevice(ctx_node, self.__get_current_channel(),
                                                                            rc.get('JtagDeviceID')))
                        if 'reg.jconfig' in exec_as_runnable(self.__get_jtag_device_properties, ctx_node):
                            devices.append(self.session.get_context_target_map()[ctx])
        devices.sort()
        if len(devices) == 0:
            raise Exception('No supported device found.') from None
        elif len(devices) > 1:
            raise Exception(f'Multiple devices found, use targets command to select one of: {devices}.') from None
        else:
            return devices[0]

    def __download_fpga_callback(self, argvar, data_bytes, ret, error, token):
        argvar['cmds'].remove(token)
        if error is not None:
            argvar['err'] = error
            argvar.get('synq').done()
            return
        ts = round(time.time() * 1000)
        current_bytes = argvar.get('current_bytes') + data_bytes
        argvar['current_bytes'] = current_bytes
        progress_delta_ms = (ts - argvar.get('progress_time'))
        complete = int((100 * current_bytes) / argvar.get('total_bytes'))
        remaining_bytes = argvar.get('total_bytes') - current_bytes
        if progress_delta_ms > 500 or remaining_bytes == 0:
            argvar['progress_time'] = ts
            total_time = ts - argvar.get('start_time')
            throughput = current_bytes / (total_time / 1000.0)
            if remaining_bytes == 0:
                eta = '{0:02d}{1}{2:02d}'.format(int(total_time / 1000 / 60), ':', int(total_time / 1000 % 60))
            elif total_time > 3000 and throughput > 0:
                remaining_time = int(remaining_bytes / throughput)
                eta = '{0:02d}{1}{2:02d}'.format(int(remaining_time / 60), ':', int(remaining_time % 60))
            else:
                eta = '??:?? ETA'
            str_info = '{0}{1}{2:.2f}{3}{4:.2f}{5}{6}'.format(complete, '%    ', current_bytes / 1048676, 'MB    ',
                                                              throughput / 1048676, 'MB/s    ', eta)
            if not self.session.get_silent_mode():
                print(str_info, end='\r')

        if len(argvar['cmds']) == 0 and complete == 100:
            argvar.get('synq').done()

    def __download_device_callback(self, argvar, datalen, error, token):
        argvar['cmds'].remove(token)
        if error is not None:
            argvar['err'] = error
            argvar.get('synq').done()
            return
        ts = round(time.time() * 1000)
        current_bytes = argvar.get('current_bytes') + datalen
        argvar['current_bytes'] = current_bytes
        progress_delta_ms = (ts - argvar.get('progress_time'))
        complete = int((100 * current_bytes) / argvar.get('total_bytes'))
        remaining_bytes = argvar.get('total_bytes') - current_bytes
        if progress_delta_ms > 500 or remaining_bytes == 0:
            argvar['progress_time'] = ts
            total_time = ts - argvar.get('start_time')
            throughput = current_bytes / (total_time / 1000.0)
            if remaining_bytes == 0:
                eta = '{0:02d}{1}{2:02d}'.format(int(total_time / 1000 / 60), ':', int(total_time / 1000 % 60))
            elif total_time > 3000 and throughput > 0:
                remaining_time = int(remaining_bytes / throughput)
                eta = '{0:02d}{1}{2:02d}'.format(int(remaining_time / 60), ':', int(remaining_time % 60))
            else:
                eta = '??:?? ETA'
            str_info = '{0}{1}{2:.2f}{3}{4:.2f}{5}{6}'.format(complete, '%    ', current_bytes / 1048676, 'MB    ',
                                                              throughput / 1048676, 'MB/s    ', eta)
            if not self.session.get_silent_mode():
                print(str_info, end='\r')

        if len(argvar['cmds']) == 0 and complete == 100:
            argvar.get('synq').done()

    def __get_jtag_ctx(self):
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        jt = exec_as_runnable(self.session.model.launch_node.jtag_targets)
        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()

        if 'DAP' in rc['Name']:
            ctx = rc['JtagNodeID']
            jc = jt[ctx]['context']
            parent = jt[jc['ParentID']]
            children = parent['children']
            index = list(children.keys()).index(ctx)
            jtag_device_id = rc['JtagDeviceID']
            if jtag_device_id == 1268778103:
                index = index - 1
            elif jtag_device_id == 1537213559 or jtag_device_id == 1805649015:
                index = index + 1
            else:
                index = -1

            if 0 <= index < len(children):
                ctx2 = list(children.keys())[index]
                jp = jt[ctx2]['properties']
                if 'reg.jconfig' not in jp:
                    raise Exception(f'Unknown jtag_ctx {ctx2}.') from None
                jtag_ctx = ctx2
            else:
                raise Exception(f'Unknown jtag_device_id {jtag_device_id}.') from None

        elif len(rc) and 'DpcTargetID' in rc:
            if 'DpcDriverName' in rc and rc['DpcDriverName'] == 'dpc-jtag':
                raise Exception('JTAG-based DPC target incompatible.') from None
            jtag_ctx = rc['DpcTargetID']

        else:
            if 'JtagDeviceID' in rc.keys():
                if node.get_jtag_device_node() is None:
                    node.set_jtag_device_node(TcfNodeJtagDevice(node, self.__get_current_channel(),
                                                                rc.get('JtagDeviceID')))
                dp = exec_as_runnable(self.__get_jtag_device_properties, node)
                if 'reg.jconfig' not in dp:
                    device = self.__get_program_device()
                else:
                    device = self.session.get_context_target_map()[node.id]
            else:
                device = self.__get_program_device()
            ctx = self.session.model.launch_node.get_target_context_map()[device]
            node = self.session.model.get_nodes()[ctx]
            jtag_ctx = exec_as_runnable(self.__get_run_ctx, node).getProperties()['JtagNodeID']

        return jtag_ctx

    def __get_jtag_reg_list(self, run):
        node = run.arg
        if not node.get_jtag_reg_node().get_jtag_reg_list().validate(run):
            return False
        else:
            error = node.get_jtag_reg_node().get_jtag_reg_list().getError()
            if error is not None:
                run.sync.done(error=error, result=None)
            else:
                run.sync.done(error=None, result=node.get_jtag_reg_node().get_jtag_reg_list().getData())

    def __get_jtag_reg_def(self, run):
        node = run.arg[0]
        reg_id = run.arg[1]
        reg_def_node = node.get_jtag_reg_node().get_jtag_reg_def(reg_id)
        if not reg_def_node.validate(run):
            return False
        else:
            error = reg_def_node.getError()
            if error is not None:
                run.sync.done(error=error, result=None)
            else:
                run.sync.done(error=None, result=reg_def_node.getData())

    @staticmethod
    def _get_registers(run, reg_node: TcfChildrenRegisters):
        done = True
        # Get Register children
        if not reg_node.validate(run):
            return False
        else:
            if reg_node.getError() is not None:
                run.sync.done(error=reg_node.getAttributes()['Format'], result=None)
            data = reg_node.getData()

            # Get contexts for the above register children
            for ctx, node in data.items():
                if not node.get_context().validate(run):
                    done = False
                else:
                    if node.get_context().getError() is not None:
                        run.sync.done(error=node.get_context().getAttributes()['Format'], result=None)

                # Get next level register children of the above children
                if not node.get_reg_children().validate(run):
                    done = False
                else:
                    done = True
            if done is False:
                return False

            return True

    def __get_registers(self, run):
        ctx_node = run.arg
        info = ctx_node.info
        reg_dict = {}
        ret_data = self._get_registers(run, ctx_node.get_reg_children())
        if ret_data is False:
            return False
        else:
            regs = ctx_node.get_reg_children()
            for reg in regs.getData():
                reg_node = info.get_node(reg)
                reg_dict[reg_node.id] = {}
                reg_dict[reg_node.id] = reg_node
            run.sync.done(error=None, result=reg_dict)
            return True

    def __print_name_value_list(self, nvlist, level, flags):
        reg_val = ""
        has_children = 0
        name_max = 0
        value_max = 0
        format_data = flags.get('format_result')

        for name, regdata in nvlist.items():
            if regdata.get('children', None):
                has_children = 1
            value = regdata.get('value')
            name_len = len(name)
            value_len = len(value)
            if name_len > name_max:
                name_max = name_len
            if value_len > value_max:
                value_max = value_len

        print_list = 1 if has_children else 0
        sep_max = 2 if value_max > 0 else 0
        indent = level * 3

        if (format_data == 1) or print_list or ((80 - indent) / (name_max + sep_max + value_max + 2) <= 1):
            for name, regdata in nvlist.items():
                value = regdata.get('value')
                if len(nvlist) == 1:
                    if value == 'N/A' and regdata.get('error', None):
                        value = regdata.get('error')
                name_len = len(name)
                value_len = len(value)

                if value_len > 0:
                    if format_data == 1:
                        sep = "\t"
                        if value != "N/A":
                            value = "0x" + value
                    else:
                        sep = ": "
                elif sep_max > 0:
                    if format_data == 1:
                        sep = "\t"
                    else:
                        sep = "  "
                else:
                    sep = ""

                addr = regdata.get('addr', None)
                if (format_data == 1) and (addr is not None):
                    reg_val += "".rjust(indent) + "".rjust(name_max - name_len) + name + sep + "0x" + format(addr,
                                                                                                             "0x") + sep + value + "\n"
                else:
                    reg_val += "".rjust(indent) + "".rjust(name_max - name_len) + name + sep + value + "\n"
                reg_val += self.__print_name_value_list(regdata.get('children', {}), level + 1, flags)
        else:
            pos = 0
            for name, regdata in nvlist.items():
                value = regdata.get('value')
                if len(nvlist) == 1:
                    if value == 'N/A' and regdata.get('error', None):
                        value = regdata.get('error')
                name_len = len(name)
                value_len = len(value)
                if value_len > 0:
                    sep = ": "
                elif sep_max > 0:
                    sep = "  "
                else:
                    sep = ""

                if pos > 0 and (pos + name_max + sep_max + value_max + 2 >= 80):
                    pos = 0
                    reg_val += '\n'
                if pos == 0:
                    reg_val += "".rjust(indent)
                    pos += indent
                if pos != 0:
                    reg_val += "  "
                    pos += 2

                reg_val += "".rjust(name_max - name_len) + name + sep + value.ljust(value_max)
                pos += (name_max + sep_max + value_max)

            if pos > 0:
                reg_val += '\n'
        return reg_val

    @staticmethod
    def __get_reg_def(reg):
        desc = reg.getDescription()
        value = desc if desc is not None else ""
        props = ""
        if reg.isReadable() is True:
            props += "R"
            if reg.isReadOnce() is True:
                props += "O"

        if reg.isWriteable() is True:
            props += "W"
            if reg.isWriteOnce() is True:
                props += "O"

        if reg.isVolatile() is True:
            props += "V"

        if props != "":
            if value != "":
                value += " "
            value += "(" + props + ")"

        return value

    def __get_bit_fields_list(self, bit_fields):
        main_list = []
        main_list.append([])
        j = 0
        for i in range(len(bit_fields) - 1):
            main_list[j].append(bit_fields[i])
            if bit_fields[i] + 1 != bit_fields[i + 1]:
                j += 1
                main_list.append([])
                if i == len(bit_fields) - 2:
                    main_list[j].append(bit_fields[i + 1])
            else:
                if i == len(bit_fields) - 2:
                    main_list[j].append(bit_fields[i + 1])
        return main_list

    def __print_regs(self, data, ctxs, flags):
        nvlist = {}
        opt_defs = flags.get("defs", None)
        opt_parent = flags.get("parent", None)
        opt_no_bits = flags.get("no_bits", None)
        opt_nvlist = flags.get("nvlist", None)

        for ctx in ctxs.values():
            value = ""
            error_string = ""
            name = ctx.get_context_data().getName()

            addr = ctx.get_context_data().getMemoryAddress()
            if addr is not None:
                nvlist[name] = {}
                nvlist[name]['addr'] = addr
            bit_fields = ctx.get_context_data().getBitNumbers()

            # for -defs - displaying reg defns
            if opt_defs == 1:
                if bit_fields:
                    parent_ctx = ctx.get_context_data().getParentID()
                    parent = data[parent_ctx].get_context_data()
                    parent_name = parent.getName()
                    if opt_parent == 1 and parent_name not in nvlist.keys():
                        nvlist[parent_name] = {}
                        nvlist[parent_name]['value'] = self.__get_reg_def(parent)
                        children = {}
                    value = self.__get_reg_def(ctx.get_context_data())
                    if opt_parent == 1:
                        children[name] = {}
                        children[name]['value'] = value
                        nvlist[parent_name]['children'] = children
                        continue
                else:
                    value = self.__get_reg_def(ctx.get_context_data())

            # Displaying values
            elif ctx.get_reg_value() is not None or bit_fields:
                bits = ""
                # if bit_fields present, display parent first and then child bits
                if bit_fields:
                    bits = bit_fields
                    parent_ctx = ctx.get_context_data().getParentID()
                    parent = data[parent_ctx].get_context_data()
                    parent_node = data[parent_ctx]
                    parent_name = parent.getName()
                    value = "N/A"
                    if parent_node.get_reg_value() is not None:
                        value = parent_node.get_reg_value()
                    elif parent_node.get_reg_error() is not None:
                        error_string = parent_node.get_reg_error()
                else:
                    value = "N/A"
                    if ctx.get_reg_value() is not None:
                        if ctx.get_context_data().getSize() == 1:
                            value = format(ctx.get_reg_value(), "02x")
                        elif ctx.get_context_data().getSize() == 2:
                            value = format(ctx.get_reg_value(), "04x")
                        else:
                            value = format(ctx.get_reg_value(), "08x")

                if bits != "":
                    if opt_parent == 1 and parent_name not in nvlist.keys():
                        children = {}
                        nvlist[parent_name] = {}
                        nvlist[parent_name]['value'] = format(value, "0x") if value != "N/A" else value
                        if error_string != "":
                            nvlist[parent_name]['error'] = ctx.get_reg_error()
                        if addr is not None:
                            nvlist[parent_name]['addr'] = addr

                    if opt_no_bits == 1 and opt_parent == 1:
                        continue

                    if value != "N/A":
                        if len(bits) == 1:
                            bit_value = 1 << bits[0]
                            if opt_parent == 1:
                                name += " (Bits [" + str(bits[0]) + "])"
                            value = (value & bit_value) >> bits[0]
                        else:
                            bit_value = 0
                            bf_list = self.__get_bit_fields_list(bits)
                            act_val = 0
                            shift = 0
                            index = 0
                            if opt_parent == 1:
                                name += " (Bits ["
                            for bf in bf_list:
                                if opt_parent == 1:
                                    name += str(bf[-1]) + ":" + str(bf[0])
                                    if index < len(bf_list) - 1:
                                        name += ","
                                for b in bf:
                                    bit_value = (1 << b) | bit_value
                                temp_value = (value & bit_value) >> bf[0]
                                bit_value = 0
                                act_val |= (temp_value << index * shift)
                                shift = len(bf)
                                index += 1
                            if opt_parent == 1:
                                name += "])"
                            value = act_val
                        if value != "N/A" and value != "":
                            value = format(value, "0x")

                    if opt_parent == 1:
                        children[name] = {}
                        children[name]['value'] = value
                        if error_string != "":
                            children[name]['error'] = error_string
                        nvlist[parent_name]['children'] = children
                        continue
            elif ctx.get_reg_error() is not None:
                value = 'N/A'
                if name not in nvlist.keys():
                    nvlist[name] = {}
                    nvlist[name]['error'] = ctx.get_reg_error()
            else:
                value = ""

            if name not in nvlist.keys():
                nvlist[name] = {}
            nvlist[name]['value'] = value
            if error_string != "":
                value = 'N/A'
                nvlist[name]['error'] = error_string
        if opt_nvlist == 1:
            nvdict = {}
            for name, regdata in nvlist.items():
                if regdata['value'] != "" and regdata['value'] != "N/A":
                    nvdict[name] = int(regdata['value'], 16)
                else:
                    nvdict[name] = regdata['value']
            return nvdict
        ret_val = self.__print_name_value_list(nvlist, 0, flags)
        return ret_val

    @staticmethod
    def __read_registers(data):
        # Read one register at a time - send command and wait for response for each register
        # for node in data.values():
        #     if node.get_context_data().isReadable():
        #         exec_in_dispatch_thread(node.read_reg)

        # Read a group of registers at a time - send command for all regs at once and wait for all responses
        node_list = []
        for node in data.values():
            if node.get_context_data().isReadable():
                node_list.append(node)
        if len(node_list):
            exec_in_dispatch_thread(xsdb._tcf_node_register.read_multiple_registers, node_list)

    def __get_next_level_children(self, data, reg_path):
        reg_match = 0
        node_match = None
        temp_data = {}
        leaf_reg = reg_path[-1]
        if data:
            for reg in reg_path:
                leaf_reg = reg
                for ctx, node in data.items():
                    name = node.get_context_data().getName()
                    if name == reg:
                        child_data = exec_as_runnable(self.__get_registers, node)
                        if len(child_data) != 0:
                            temp_data.update(child_data)
                        reg_match = 1
                        node_match = node
                data.update(temp_data)

        if reg_match == 0:
            raise Exception("No register match: ", leaf_reg)
        return data, node_match

    @staticmethod
    def __get_access_mode_targets(run, node):
        done = True
        children_context = {}
        if node.get_run_context_data().hasState():
            children = node.get_children()
            if not children.validate(run):
                return None
            else:
                if node.get_children().getError() is not None:
                    run.sync.done(error=children.getAttributes()['Format'], result=None)
                data = children.getData()

                for ctx, child_node in data['children'].items():
                    child_node_ctx = child_node.get_run_context()
                    if not child_node_ctx.validate(run):
                        done = False
                    else:
                        if child_node_ctx.getError() is not None:
                            run.sync.done(error=child_node_ctx.getAttributes()['Format'], result=None)
                        ctx_data = child_node_ctx.getData()
                        children_context[ctx_data.getName()] = child_node

                if done is False:
                    return None

        return children_context

    @staticmethod
    def __get_access_modes(run):
        node = run.arg
        done = True
        children_context = {}
        if node.get_run_context_data().hasState():
            children = node.get_children()
            if not children.validate(run):
                return False
            else:
                if node.get_children().getError() is not None:
                    run.sync.done(error=children.getAttributes()['Format'], result=None)
                data = children.getData()

                for ctx, child_node in data['children'].items():
                    child_node_ctx = child_node.get_run_context()
                    if not child_node_ctx.validate(run):
                        done = False
                    else:
                        if child_node_ctx.getError() is not None:
                            run.sync.done(error=child_node_ctx.getAttributes()['Format'], result=None)
                        ctx_data = child_node_ctx.getData()
                        children_context[ctx_data.getName()] = child_node

                if done is False:
                    return False

        run.sync.done(error=None, result=children_context)
        return True

    def __get_target_microblaze_props(self, ctx):
        nodes = self.session.model.get_nodes()
        ctx_node = nodes[ctx]
        params = dict()
        rc = exec_as_runnable(self.__get_run_ctx, ctx_node).getProperties()
        if 'HasState' in rc:
            if 'XMDCPort' in rc:
                params['MBCore'] = rc['XMDCPort']
            if 'ParentID' in rc:
                parentid = rc['ParentID']
                parent_node = nodes[parentid]
                rc = exec_as_runnable(self.__get_run_ctx, parent_node).getProperties()
            else:
                rc = dict()
        if 'MDMConfig' in rc:
            params['MDMConfig'] = rc['MDMConfig']
        if 'MDMAddr' in rc:
            params['MDMAddr'] = rc['MDMAddr']
            if 'ParentID' in rc:
                params['MemID'] = rc['ParentID']
        if 'JtagGroup' in rc:
            if 'JtagChain' in rc:
                params['JtagChain'] = rc['JtagChain']
            jtaggroup_node = nodes[rc['JtagGroup']]
            rc = exec_as_runnable(self.__get_run_ctx, jtaggroup_node).getProperties()
            if 'JtagNodeID' in rc:
                params['JtagNodeID'] = rc['JtagNodeID']
        return params

    def __ipi(self, ipi: int = 5, args=None, **kwargs):
        if args is None:
            args = []
        response_list = kwargs.pop('response_list') if 'response_list' in kwargs else None
        response_size = kwargs.pop('response_size') if 'response_size' in kwargs else None
        timeout = kwargs.pop('timeout') if 'timeout' in kwargs else 1000
        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        rc = exec_as_runnable(get_cache_data, node.get_run_context()).getProperties()
        while 'ParentID' in rc and rc['ParentID'] != '':
            parent_node = node.info.get_node(rc['ParentID'])
            rc = exec_as_runnable(get_cache_data, parent_node.get_run_context()).getProperties()

        device = ''
        if rc['Name'].startswith('Versal'):
            idcode = rc['JtagDeviceID']
            if idcode == 0x4ba06477:
                device = 'versalnet'
            elif idcode == 0x6ba00477:
                device = 'versal'
        elif rc['Name'].startswith('DPC'):
            idcode = rc['DpcDeviceID']
            if idcode & 0x0fffffff in (0x04d80093, 0x04d81093, 0x04d82093):
                device = 'versalnet'
            elif idcode & 0x0fe00fff == 0x04c00093:
                device = 'versal'

        if device == 'versalnet':
            ipi0_trig = 0xeb330000
            ipi0_obs = 0xeb330004
            ipi0_pmc_buf = 0xeb3f0440
            ipi0_pmc_resp = 0xeb3f0460
        elif device == 'versal':
            ipi0_trig = 0xff330000
            ipi0_obs = 0xff330004
            ipi0_pmc_buf = 0xff3f0440
            ipi0_pmc_resp = 0xff3f0460
        else:
            raise Exception('selected target is not a versal target') from None

        pmccmds = self.session.pmccmds
        if response_list is not None or response_size is not None:
            val = self.session.mrd(ipi0_obs + (0x10000 * ipi), '-f', '-v')
            if val & 0x02 != 0:
                raise Exception('previous ipi request is pending') from None
            if len(args) > 8:
                raise Exception('ipi buffer overflow, max buffer size is 8') from None

        self.session.mwr(ipi0_pmc_buf + (ipi * 0x200), '-f', words=args)
        self.session.mwr(ipi0_trig + (ipi * 0x10000), '-f', words=0x02)

        is_reset = 0
        for name, data in pmccmds.items():
            if name == 'reset_assert' and data['cmd'] == args[0]:
                is_reset = 1
                break

        # Check for ACK only if the command is not reset_assert
        if response_list is not None and response_size is not None:
            if is_reset == 0:
                start = round(time.time() * 1000)
                while (self.session.mrd(ipi0_obs + (ipi * 0x10000), '-f', '-v') & 0x02) != 0:
                    end = round(time.time() * 1000)
                    if end - start > timeout:
                        raise Exception("timeout waiting for request to be acknowledged") from None

        result = ''
        if response_list is not None:
            count = len(response_list)
            values = self.session.mrd(ipi0_pmc_resp + (ipi * 0x200), '-v', size=count)
            for i in range(0, count):
                result = result + '{0:30s} : {1:s}'.format(response_list[i], hex(values[i])) + '\n'
        elif response_size is not None:
            result = self.session.mrd(ipi0_pmc_resp + (ipi * 0x200), '-v', size=response_size)
        return result

    def __check_if_plm_log_supported(self):
        features_cmd = 0x010100
        ret = self.session.pmc('generic', [features_cmd, 19], response_size=2)
        if ret[0] != 0 or ret[1] != 0:
            raise Exception('event logging is not supported by this version of PLM') from None

    def __init_pmc_commands(self):
        pmccmds = self.session.pmccmds

        # PLM commands
        pmccmds['features'] = {'cmd': 0x1010100, 'args': ['api-id'], 'resp': ['status']}
        pmccmds['get_device_id'] = {'cmd': 0x1000112, 'args': [], 'resp': ['status', 'idcode', 'ext-idcode']}
        pmccmds['get_board'] = {'cmd': 0x1030115, 'args': ['addr', 'max-size'], 'resp': ['status', 'response-length']}

        # PM commands
        pmccmds['request_device'] = {'cmd': 0x04020D, 'args': ['node-id', 'capabilities', 'qos', 'ack-type'],
                                     'resp': ['cmd_status']}
        pmccmds['release_device'] = {'cmd': 0x01020E, 'args': ['node-id'], 'resp': ['cmd_status']}
        pmccmds['set_requirement'] = {'cmd': 0x04020F, 'args': ['node-id', 'capabilities', 'qos', 'ack-type'],
                                      'resp': ['cmd_status']}
        pmccmds['self_suspend'] = {'cmd': 0x050207, 'args': ['node-id', 'wakeup-latency', 'power-state', 'resume-addr'],
                                   'resp': ['cmd_status']}
        pmccmds['request_suspend'] = {'cmd': 0x040206,
                                      'args': ['subsystem-id', 'ack-type', 'wakeup-latency', 'power-state'],
                                      'resp': ['cmd_status']}
        pmccmds['request_wakeup'] = {'cmd': 0x04020A, 'args': ['node-id', 'resume-addr', 'ack-type'],
                                     'resp': ['cmd_status']}
        pmccmds['abort_suspend'] = {'cmd': 0x020209, 'args': ['abort-reason', 'node-id'], 'resp': ['cmd_status']}
        pmccmds['setup_wakeup_source'] = {'cmd': 0x03020B, 'args': ['subsystem-id', 'node-id', 'flag'],
                                          'resp': ['cmd_status']}
        pmccmds['get_device_status'] = {'cmd': 0x010203, 'args': ['node-id'],
                                        'resp': ['cmd_status', 'status', 'requirement', 'usage']}
        pmccmds['device_ioctl'] = {'cmd': 0x020222, 'args': ['node-id', 'ioctl-id'], 'resp': ['cmd_status']}
        pmccmds['set_max_latency'] = {'cmd': 0x020210, 'args': ['node-id', 'latency'], 'resp': ['cmd_status']}

        pmccmds['reset_assert'] = {'cmd': 0x020211, 'args': ['node-id', 'flag'], 'resp': ['cmd_status']}
        pmccmds['reset_get_state'] = {'cmd': 0x010212, 'args': ['node-id'], 'resp': ['cmd_status', 'reset-state']}

        pmccmds['pin_control_request'] = {'cmd': 0x01021C, 'args': ['node-id'], 'resp': ['cmd_status']}
        pmccmds['pin_control_release'] = {'cmd': 0x01021D, 'args': ['node-id'], 'resp': ['cmd_status']}
        pmccmds['pin_get_fuction'] = {'cmd': 0x01021E, 'args': ['node-id'], 'resp': ['cmd_status', 'function-id']}
        pmccmds['pin_set_fuction'] = {'cmd': 0x02021F, 'args': ['node-id', 'function-id'], 'resp': ['cmd_status']}
        pmccmds['pin_get_config_param'] = {'cmd': 0x020220, 'args': ['node-id', 'param-id'],
                                           'resp': ['cmd_status', 'param-value']}
        pmccmds['pin_set_config_param'] = {'cmd': 0x030221, 'args': ['node-id', 'param-id', 'param-value'],
                                           'resp': ['cmd_status']}

        pmccmds['clock_enable'] = {'cmd': 0x010224, 'args': ['node-id'], 'resp': ['cmd_status']}
        pmccmds['clock_disable'] = {'cmd': 0x010225, 'args': ['node-id'], 'resp': ['cmd_status']}
        pmccmds['clock_get_state'] = {'cmd': 0x010226, 'args': ['node-id'], 'resp': ['cmd_status', 'state']}
        pmccmds['clock_set_divider'] = {'cmd': 0x020227, 'args': ['node-id', 'divider'], 'resp': ['cmd_status']}
        pmccmds['clock_get_divider'] = {'cmd': 0x010228, 'args': ['node-id'], 'resp': ['cmd_status', 'divider']}
        pmccmds['clock_set_parent'] = {'cmd': 0x01022B, 'args': ['node-id', 'parent-index'], 'resp': ['cmd_status']}
        pmccmds['clock_get_parent'] = {'cmd': 0x01022C, 'args': ['node-id'], 'resp': ['cmd_status', 'parent-index']}

        pmccmds['pll_set_param'] = {'cmd': 0x030230, 'args': ['node-id', 'param-id', 'param-value'],
                                    'resp': ['cmd_status']}
        pmccmds['pll_set_param'] = {'cmd': 0x020231, 'args': ['node-id', 'param-id'],
                                    'resp': ['cmd_status', 'param-value']}
        pmccmds['pll_set_mode'] = {'cmd': 0x020232, 'args': ['node-id', 'pll-mode'], 'resp': ['cmd_status']}
        pmccmds['pll_get_mode'] = {'cmd': 0x010232, 'args': ['node-id'], 'resp': ['cmd_status', 'pll-mode']}

        pmccmds['force_power_down'] = {'cmd': 0x020208, 'args': ['node-id', 'ack-type'], 'resp': ['cmd_status']}
        pmccmds['system_shutdown'] = {'cmd': 0x02020C, 'args': ['shutdown-type', 'sub-type'], 'resp': ['cmd_status']}

        # Generic command to allow users to trigger any other commands
        pmccmds['generic'] = dict()

    def __get_elf_text_addrs(self, elf):
        f = ElfParse()
        f.open(elf)
        sec_info = f.get_section_header()
        for esh in sec_info:
            if esh['sh_name'] == '.text':
                res = {'low_addr': esh['sh_addr'], 'high_addr': esh['sh_size'] + esh['sh_addr']}
                return res

    def __get_regs(self, node, reg_path):
        parent = node
        data = {}
        for name in reg_path:
            regs = exec_as_runnable(self.__get_registers, parent)
            data.update(regs)
            for ctx, child_node in regs.items():
                reg = child_node.get_context_data()
                if reg.getName() == name:
                    parent = child_node
                    break
        return data

    def __get_expr_type(self, data, id):
        type = ''
        classtype = data.get('Context').get('Class', None)

        if classtype is None:
            return 'N/A'
        elif classtype == sym_service.TypeClass.pointer:
            btype = data.get('BaseType', None)
            if btype is not None:
                type = btype.get('Name', '')
            if type == '':
                btype = data.get('BaseTypeID', None)
                if btype is not None:
                    type = btype.get('Name', '')
            type += ' *'
        elif classtype == sym_service.TypeClass.array:
            btype = data.get('BaseType', None)
            if btype is not None:
                type = btype.get('Name')
            if type == '':
                btype = data.get('BaseTypeID', None)
                if btype is not None:
                    type = btype.get('Name')
            typeclass = data.get('BaseType', None)
            if typeclass is not None:
                typeclass = typeclass.get('TypeClass')
            if typeclass == sym_service.TypeClass.pointer:
                type += ' *'
            type += '[' + str(data.get('Type').get('Length')) + ']'
        else:
            type = data.get('Type').get('Name')
            if type == '':
                type = data.get('TypeID').get('Name')
            if type == '' and classtype == sym_service.TypeClass.composite:
                type = '<Structure>'
        return type

    def __get_expr_value(self, exprs, id, endianness, array_index, read_one_var):
        classtype = exprs.get(id).get('Context').get('Class')

        if classtype == sym_service.TypeClass.array:
            value = exprs.get(id).get('BaseType').get('Name')
            if value == '':
                value = exprs.get(id).get('BaseTypeID').get('Name')
            if exprs.get(id).get('BaseType').get('TypeClass') == sym_service.TypeClass.pointer:
                value += '*'
            # Reading array elements
            if array_index is not None:
                size = exprs.get(id).get('Symbol').get('Size')
                length = exprs.get(id).get('Symbol').get('Length')
                element_size = int(size / length)
                lower_bound = exprs.get(id).get('Symbol').get('LowerBound')
                upper_bound = exprs.get(id).get('Symbol').get('UpperBound')
                if array_index < lower_bound or array_index > upper_bound:
                    raise Exception(
                        f"array {exprs.get(id).get('Symbol').get('Name')} index {array_index} out of bound") from None
                bin = exprs.get(id).get('Value').getValue()
                value = int.from_bytes(bytes(bin[array_index * element_size:array_index * element_size + element_size]),
                                       endianness)
            else:
                value += '[' + str(exprs.get(id).get('Type').get('Length')) + ']'
            return value
        elif classtype == sym_service.TypeClass.composite:
            value = exprs.get(id).get('Type').get('Name')
            if value == '':
                value = '<Structure>'
                return value
        else:
            if exprs.get(id).get('Type') is not None:
                datatype = exprs.get(id).get('Type').get('Name')
            else:
                prop = exprs.get(id).get('Value').getProperties().get('Class', None)
                if prop is not None:
                    if prop == sym_service.TypeClass.cardinal or prop == sym_service.TypeClass.integer:
                        datatype = 'int'
                    else:
                        datatype = 'float'
            value = 'N/A'
            if exprs.get(id).get('Value'):
                if isinstance(exprs.get(id).get('Value'), exp_service.Value):
                    bin = exprs.get(id).get('Value').getValue()
                    if datatype == 'float' or datatype == 'double':
                        value = struct.unpack(datatype[0], bin)[0]
                    else:
                        value = int.from_bytes(bytes(bin), endianness, signed=True)
                else:
                    if read_one_var:
                        value = exprs.get(id).get('Value')
        return value

    def __get_child_variables(self, exprs, id_list, parent):
        id_list.append(parent)
        children = exprs[parent].get('Children', None)
        for child in children:
            self.__get_child_variables(exprs, id_list, child)

    @staticmethod
    def __exp_is_array(name):
        if name.find('[') != -1:
            return True
        return False

    def __process_expressions(self, exprs, endianness, locals, args):
        maxlen = 0
        maxlevel = 0
        result = ''
        parent = ''
        dict_result = {}
        id_list = []
        names = []
        array_index = None
        a_name = args['name']
        if a_name is not None:
            if locals:
                if self.__exp_is_array(a_name):
                    names.append(a_name.split('[')[0])
                    array_index = int(a_name[a_name.index('[') + 1: a_name.index(']')])
                else:
                    names = a_name.split('.')
            else:
                names.append(a_name)
            root = names[0]
            for id, data in exprs.items():
                var_name = id
                if data.get('Name', None):
                    var_name = data.get('Name')
                if data.get('Symbol', None):
                    var_name = data.get('Symbol').get('Name', '')
                if var_name == root:
                    parent = id
                    break
            if parent == '':
                raise Exception("No variable match ", a_name) from None

            if len(names) != 1:
                for name in names:
                    if name == exprs[parent].get('Symbol').get('Name', ''):
                        continue
                    match = False
                    if exprs[parent].get('Children', None):
                        for child in exprs[parent].get('Children'):
                            var_name = child
                            if exprs[child].get('Symbol', None):
                                var_name = exprs[child].get('Symbol').get('Name', '')
                            if var_name == name:
                                parent = child
                                match = True
                                break
                    if not match:
                        raise Exception("No variable match ", name) from None

            self.__get_child_variables(exprs, id_list, parent)

        for id, data in exprs.items():
            name = id
            if not locals:
                name = data.get('Name', name)
            if data.get('Symbol', None):
                name = data.get('Symbol').get('Name', '')
            name_len = len(name)
            if len(name) > maxlen:
                maxlen = len(name)
            level = data.get('level', None)
            if level > maxlevel:
                maxlevel = level

        if maxlen < 8:
            maxlen = 8
        length = maxlen + (maxlevel * 3) + 2

        if not args['dict'] and args['defs']:
            result += 'Name'.ljust(length) + 'Type'.ljust(maxlen) + 'Address'.ljust(20) + 'Size'.ljust(10) \
                      + 'Flags'.ljust(10)
            result += '\n' + '========'.ljust(length) + '========'.ljust(maxlen) + '==========='.ljust(20) \
                      + '===='.ljust(10) + '======'.ljust(10)
        start_level = -1
        hier_name = ''

        # Reading value of the variable
        if args['value'] is None:
            for id, data in exprs.items():
                name = id
                if id_list and id not in id_list:
                    continue
                if data.get('Symbol', None):
                    name = data.get('Symbol').get('Name', '')
                level = data.get('level', None)
                if start_level == -1 or start_level > level:
                    start_level = level

                indent = (level - start_level) * 3
                length = maxlen - indent + (maxlevel * 3) + 2
                if not args['dict'] and result != '':
                    result += '\n'
                if level == 0:
                    hier_name = ''

                if args['defs']:
                    flags = data.get('Context', None).get('CanAssign', None)
                    if flags == 1:
                        flags = 'RW'
                    elif flags == 0:
                        flags = 'R'
                    else:
                        flags = 'N/A'

                    addr = 'N/A'
                    value = data.get('Value', None)
                    if value is not None:
                        if isinstance(value, exp_service.Value):
                            if value.getAddress() is not None:
                                addr = hex(value.getAddress())

                    size = data.get('Type', None).get('Size', None)
                    if size == '':
                        size = data.get('Context', None).get('Size', None)

                    type = self.__get_expr_type(data, id)

                    if args['dict']:
                        if not locals:
                            name = data.get('Name', name)
                        if hier_name == '':
                            hier_name = name
                        else:
                            hier_name = '.'.join(hier_name.split('.')[0:level])
                            hier_name += '.' + name
                        dict_result.update({hier_name: {'type': type, 'addr': addr, 'size': size, 'flags': flags}})
                    else:
                        if not locals:
                            name = data.get('Name', name)
                        result += ''.rjust(indent) + name.ljust(length) + type.ljust(maxlen) + addr.ljust(20) + str(
                            size).ljust(10) + flags.ljust(10)
                else:
                    read_one_var = len(id_list)
                    value = self.__get_expr_value(exprs, id, endianness, array_index, read_one_var)
                    if args['dict']:
                        if not locals:
                            name = data.get('Name', name)
                        if hier_name == '':
                            hier_name = name
                        else:
                            hier_name = '.'.join(hier_name.split('.')[0:level])
                            hier_name += '.' + name
                        dict_result.update({hier_name: value})
                    else:
                        if not locals:
                            name = data.get('Name', name)
                        if array_index is not None:
                            name = a_name
                        result += "".rjust(indent) + name.ljust(length) + ': ' + str(value)

            if args['dict']:
                return dict_result
            else:
                return result

        # Writing value to the variable
        else:
            if len(id_list) > 1:
                raise Exception(
                    'Cannot modify the value of a complex data type. Specify a child element to be modified') from None

            for id, data in exprs.items():
                if id_list and id not in id_list:
                    continue
                if data.get('Context', None):
                    if data.get('Context').get('CanAssign', None) != 1:
                        raise Exception('Expression cannot be modified') from None
                classtype = data.get('Context').get('Class', None)
                if classtype == sym_service.TypeClass.array:
                    size = int(data.get('Symbol').get('Size') / data.get('Symbol').get('Length'))
                    if data.get('BaseType', None):
                        if data.get('BaseType').get('TypeClass', None):
                            classtype = data.get('BaseType').get('TypeClass')
                    ctx = None
                    a_elem_id = None
                    if data.get('Context', None):
                        if data.get('Context').get('Expression', None):
                            ctx = data.get('Context').get('Expression')
                            elem_id = ctx + '[' + str(array_index) + ']'
                            node = self.__get_current_node().info.get_node(data.get('Context').get('ID'))
                            elem_exp = exec_in_dispatch_thread(node.create, elem_id)
                            a_elem_id = elem_exp.getID()
                            if elem_id in node.info.get_nodes().keys():
                                n = node.info.get_node(a_elem_id)
                            else:
                                n = TcfNodeExpression(node, a_elem_id, None)
                                node.info.update_nodes({a_elem_id: n})
                    id = a_elem_id
                else:
                    size = data.get('Context').get('Size', None)
                if classtype == sym_service.TypeClass.integer or classtype == sym_service.TypeClass.cardinal:
                    if isinstance(args['value'], float) or isinstance(args['value'], str):
                        raise Exception(f"Expected integer value, got {args['value']}") from None
                if classtype == sym_service.TypeClass.real:
                    if size == 8:
                        value = bytearray(struct.pack('d', args['value']))
                    else:
                        value = bytearray(struct.pack('f', args['value']))
                else:
                    value = args['value'].to_bytes(size, endianness)
                exec_in_dispatch_thread(self.__get_current_node().info.get_node(id).assign, value)

    def __get_expression_children(self, run):
        node = run.arg
        if not node.validate(run):
            return False
        else:
            if node.getError() is not None:
                run.sync.done(error=node.getError().getAttributes()['Format'], result=None)
            data = node.getData()
            run.sync.done(error=None, result=data)
            return True

    def __get_expression_and_symbol_contexts(self, run):
        node = run.arg
        if not node.get_context().validate(run):
            return False
        else:
            if node.get_context().getError() is not None:
                run.sync.done(error=node.get_context().getError(), result=None)
            sc = node.get_context().getData()
            run.sync.done(error=None, result=sc)
            return True

    def __get_symbol_node(self, node: TcfNode, id: str):
        if id in node.info.get_nodes().keys():
            ret_node = node.info.get_node(id)
        else:
            ret_node = TcfNodeSymbol(node, id)
        node.info.update_nodes({id: ret_node})
        return ret_node

    def __get_variable_expressions(self, node, exprs, parent='', sctx='', level=0):
        chan = self.__get_current_channel()
        ctx = node.id
        expr_table = self.session._expr_table
        type_ctx = None
        type_node = None

        # Get expression context of the expression node
        exp_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, node)

        # Get symbol ID and get its context
        sym_id = exp_ctx.getSymbolID()
        if sym_id is not None:
            sym_node = node.get_symbol_context(sym_id)
            sym_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, sym_node)
        else:
            sym_ctx = sctx

        # Get type ID and get its context
        type = exp_ctx.getTypeID()
        if type is not None:
            type_node = node.get_type_context(type)
            type_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, type_node)

        exprs.update({ctx: {'Context': exp_ctx.getProperties(), 'Symbol': sym_ctx.getProperties(),
                            'Type': type_ctx.getProperties(), 'Parent': parent, 'Children': "", 'level': level}})

        if type_ctx.getTypeClass() == sym_service.TypeClass.array:
            # If array type variable, get the datatype of the elements in it
            base_type_id = type_ctx.getBaseTypeID()
            if base_type_id is not None:
                base_type_node = node.get_type_context(base_type_id)
                base_type_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, base_type_node)
                exprs[ctx].update({'BaseType': base_type_ctx.getProperties()})
                base_type_id_in_base_type_ctx = base_type_ctx.getBaseTypeID()
                if base_type_id_in_base_type_ctx is not None:
                    base_type_node_in_base_type_ctx = node.get_base_type_context(base_type_id_in_base_type_ctx)
                    base_type_id_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts,
                                                        base_type_node_in_base_type_ctx)
                    exprs[ctx].update({'BaseTypeID': base_type_id_ctx.getProperties()})

        elif type_ctx.getTypeClass() == sym_service.TypeClass.composite:
            # If structure type variable, get the children of this expression - members
            children = exec_as_runnable(self.__get_expression_children, type_node.get_children())
            child_id_list = []
            for child in children:
                child_sym_node = self.__get_symbol_node(node, child)
                child_sym_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, child_sym_node)
                child_id = exp_ctx.getExpression() + '.${' + child + '}'

                if expr_table.get(chan).get(node.parent.id).get(child_id, None) is None:
                    child_exp = exec_in_dispatch_thread(node.create, child_id)
                    expr_id = child_exp.getID()
                    n = TcfNodeExpression(node, expr_id, None)
                    node.info.update_nodes({expr_id: n})
                    expr_table[chan][node.parent.id].update({child_id: {'data': child_exp.getProperties()}})
                else:
                    expr_id = expr_table[chan][node.parent.id][child_id]['data']['ID']
                    if expr_id in node.info.get_nodes().keys():
                        n = node.info.get_node(expr_id)
                child_id_list.append(expr_id)
                exprs[ctx].update({'Children': child_id_list})
                self.__get_variable_expressions(n, exprs, node.id, child_sym_ctx, level + 1)

    def __get_expressions(self, node, exprs, parent='', sctx='', level=0):
        chan = self.__get_current_channel()
        ctx = node.id
        exp_name = ''
        type_ctx = None
        sym_ctx = None
        type_ctx_props = None
        sym_ctx_props = None
        expr_table = self.session._expr_table

        # TODO - set local and autoexpr
        # Get the expression context of the expression node
        exp_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, node)

        # Get the symbol ID and its symbol context
        sym_id = exp_ctx.getSymbolID()
        if sym_id is not None:
            sym_node = self.__get_symbol_node(node, sym_id)
            sym_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, sym_node)
        else:
            sym_ctx = sctx
            if sym_ctx != '' and sym_ctx is not None:
                exp_name = sym_ctx.getName()

        # Get the type ID and its context
        type = exp_ctx.getTypeID()
        if type is not None:
            type_node = self.__get_symbol_node(node, type)
            type_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, type_node)
        if type_ctx is not None:
            type_ctx_props = type_ctx.getProperties()
        if sym_ctx is not None and sym_ctx != '':
            sym_ctx_props = sym_ctx.getProperties()

        if exp_name == '':
            exp_name = exp_ctx.getExpression()
        exprs.update({ctx: {'Name': exp_name, 'Context': exp_ctx.getProperties(), 'Symbol': sym_ctx_props,
                            'Type': type_ctx_props, 'Parent': parent, 'Children': "", 'level': level}})

        if type_ctx is not None:
            # If array, get the data type of its members
            if type_ctx.getTypeClass() == sym_service.TypeClass.array:
                base_type_id = type_ctx.getBaseTypeID()
                if base_type_id is not None:
                    base_type_node = self.__get_symbol_node(node, base_type_id)
                    base_type_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, base_type_node)
                    exprs[ctx].update({'BaseType': base_type_ctx.getProperties()})

                    base_type_id_in_base_type_ctx = base_type_ctx.getBaseTypeID()
                    if base_type_id_in_base_type_ctx is not None:
                        base_type_node_in_base_type_ctx = self.__get_symbol_node(node, base_type_id_in_base_type_ctx)
                        base_type_id_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts,
                                                            base_type_node_in_base_type_ctx)
                        exprs[ctx].update({'BaseTypeID': base_type_id_ctx.getProperties()})

            # If structure, get the member expressions and their contexts
            elif type_ctx.getTypeClass() == sym_service.TypeClass.composite:
                children = exec_as_runnable(self.__get_expression_children, type_node.get_children())
                child_id_list = []

                for child in children:
                    child_sym_node = self.__get_symbol_node(node, child)
                    child_sym_ctx = exec_as_runnable(self.__get_expression_and_symbol_contexts, child_sym_node)
                    child_id = exp_ctx.getExpression() + '.${' + child + '}'

                    if expr_table.get(chan).get(node.parent.id).get(child_id, None) is None:
                        child_exp = exec_in_dispatch_thread(node.create, child_id)
                        expr_id = child_exp.getID()
                        n = TcfNodeExpression(node, expr_id, None)
                        node.info.update_nodes({expr_id: n})
                        expr_table[chan][node.parent.id].update({child_id: {'data': child_exp.getProperties()}})
                    else:
                        expr_id = expr_table[chan][node.parent.id][child_id]['data']['ID']
                        if expr_id in node.info.get_nodes().keys():
                            n = node.info.get_node(expr_id)
                    child_id_list.append(expr_id)
                    exprs[ctx].update({'Children': child_id_list})
                    self.__get_expressions(n, exprs, node.id, child_sym_ctx, level + 1)

    def __stop_jtag_uart(self, ctx, terminal=1, socket_exit=0):
        if ctx not in self.session.stream_table.keys():
            raise Exception('Jtag Uart connection doesnot exists.') from None
        ctx_stream_table = self.session.stream_table[ctx]
        if 'connected' not in ctx_stream_table or ctx_stream_table['connected'] == 0:
            if 'ext_socket' in ctx_stream_table and ctx_stream_table['ext_socket'] == 1:
                port = self.session.stream_table['meta']['port']
                if terminal == 1:
                    terminal_script = os.path.dirname(os.path.realpath(__file__)) + '/jtag_uart_terminal.py'
                    Popen([f'python {terminal_script} {port} 2'], shell=True)
                    time.sleep(0.2)
                    return
                else:
                    raise Exception(f'Use \'jtagterminal\' command to stop jtag uart reads') from None
            else:
                raise Exception('Jtag Uart connection doesnot exists.') from None

        if terminal == 1:
            if 'jtagterminal_cmd' not in ctx_stream_table or ctx_stream_table['jtagterminal_cmd'] == 0:
                raise Exception('Use \'readjtaguart\' command to stop jtag uart reads.') from None
            ctx_stream_table['connected'] = ctx_stream_table['jtagterminal_cmd'] = 0
            if socket_exit == 0:
                if 'terminal_socket' in ctx_stream_table and not ctx_stream_table['terminal_socket']._closed:
                    ctx_stream_table['terminal_socket'].send('xsdb_exit'.encode())
            exec_in_dispatch_thread(streams_disconnect, self, ctx_stream_table['RXStreamID'])
        else:
            if 'readjtaguart_cmd' not in ctx_stream_table or ctx_stream_table['readjtaguart_cmd'] == 0:
                raise Exception('Use \'jtagterminal\' command to stop jtag uart reads.') from None
            ctx_stream_table['connected'] = ctx_stream_table['readjtaguart'] = 0
            if ctx_stream_table['handle'] is not None:
                ctx_stream_table['handle'].close()
        exec_in_dispatch_thread(streams_disconnect, self, ctx_stream_table['TXStreamID'])
        print("Stopping Jtag Uart reads.")
        self.session.stream_table.pop(ctx)

    def __stream_sock_thread(self, ctx_stream_table, stream_table):
        ctx_stream_table['terminal_socket'] = stream_table['server'].accept()[0]
        ctx_stream_table['connected'] = ctx_stream_table['jtagterminal_cmd'] = 1
        protocol.invokeAndWait(streams_read, self, ctx_stream_table['TXStreamID'], self.__stream_reader_callback)
        while True:
            if ctx_stream_table['terminal_socket']._closed is False:
                ctx_stream_table['terminal_socket'].settimeout(1)
                try:
                    data = ctx_stream_table['terminal_socket'].recv(4096)
                except Exception:
                    if 'connected' in ctx_stream_table.keys() and ctx_stream_table['connected'] == 0:
                        data = ''.encode()
                    else:
                        continue
                if data.decode() == '':
                    return
                if 'connected' in ctx_stream_table.keys() and ctx_stream_table['connected'] == 1:
                    if data.decode() == "terminal_exit\n":
                        self.__stop_jtag_uart(ctx_stream_table['ctx'], socket_exit=1)
                        return
                    protocol.invokeLater(streams_write, self, ctx_stream_table['RXStreamID'], data)
            else:
                break

    def __stream_reader_callback(self, TXStreamID, error, lost_size, data, eos):
        if error:
            if isinstance(error, ErrorReport) and error.getAttributes()['Format'] == 'Command canceled':
                return
            raise Exception(f'{error}') from None
        if eos:
            return
        ctx = None
        for context, stream_info in self.session.stream_table.items():
            if 'TXStreamID' in stream_info and stream_info['TXStreamID'] == TXStreamID:
                ctx = context
                break
        if ctx is None:
            raise Exception("No target context to read stream data") from None

        ctx_stream_table = self.session.stream_table[ctx]
        if 'terminal_socket' in ctx_stream_table and not ctx_stream_table['terminal_socket']._closed:
            try:
                ctx_stream_table['terminal_socket'].send(data)
            except Exception as inst:
                if isinstance(inst, OSError) and inst.strerror == 'Broken pipe':
                    self.session.deferred_queue.put(lambda: self.__stop_jtag_uart(ctx, socket_exit=1))
                    return
                else:
                    raise Exception(inst) from None
        elif 'handle' in ctx_stream_table.keys() and ctx_stream_table['handle'] is not None:
            if ctx_stream_table['handle'].closed:
                return
            self.session.deferred_queue.put(lambda: ctx_stream_table['handle'].write(data.decode()))
        else:
            self.session.deferred_queue.put(lambda: print(data.decode()))
        if 'connected' in ctx_stream_table.keys() and ctx_stream_table['connected'] == 1:
            streams_read(self, TXStreamID, self.__stream_reader_callback)

    def __wait_for_run_state(self, node, state, timeout):
        start = round(time.time() * 1000)
        end = start
        targets = dict()
        targets.update({node.id: node})
        targets.update(self._get_all_children_of_the_node(node))
        while end - start < timeout:
            found_state = 0
            match_state = 0
            for child, child_node in targets.items():
                rs = exec_as_runnable(get_cache_data, child_node.get_run_state())
                if rs is not None:
                    found_state += 1
                    if rs.is_suspended == state:
                        match_state += 1
            if found_state > 0 and found_state == match_state:
                break
            time.sleep(0.001)
            end = round(time.time() * 1000)

    def _get_all_children_of_the_node(self, node):
        child_data = exec_as_runnable(get_cache_data, node.get_children())
        children = child_data['children'] if 'children' in child_data else None
        if children is not None:
            for child, child_node in children.copy().items():
                children.update(self._get_all_children_of_the_node(child_node))
        return children

    def __get_register_context(self, reg):
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        if reg is None:
            reg = ""
        reg_path = reg.split(" ")

        parent = node
        reg_ctx = None
        data = {}
        for name in reg_path:
            match = 0
            regs = exec_as_runnable(self.__get_registers, parent)
            data.update(regs)
            for ctx, child_node in regs.items():
                reg_ctx = child_node.get_context_data()
                if reg_ctx.getName() == name:
                    parent = child_node
                    match = 1
                    break
            if match == 0:
                raise Exception(f"No register match: {name} ") from None
        return reg_ctx

    def __write_gprof_hist_data(self, f, data):
        gprof = self.session.gprof
        profile_config = self.session.profile_config
        endian = 'little' if gprof.get_prof_endianness() == 0 else 'big'
        ngsecs = data['ngmonsecs']
        lowpc = data['sec0']['lowpc']
        secnr = f'sec{ngsecs - 1}'
        highpc = data[secnr]['highpc']
        countsize = int((highpc - lowpc) / 16)
        GMON_TAG_TIME_HIST = 0
        f.write(to_bytes(GMON_TAG_TIME_HIST, 1, endian))
        f.write(to_bytes(lowpc, 4, endian))
        f.write(to_bytes(highpc, 4, endian))
        f.write(to_bytes(countsize, 4, endian))
        f.write(to_bytes(profile_config['sampfreq'], 4, endian))
        f.write('seconds'.encode())
        for i in range(0, 2):
            f.write(to_bytes(0, 4, endian))
        f.write('s'.encode())
        # Write actual histogram data
        secidx = 0
        while True:
            secnr = f'sec{secidx}'
            kcountsize = data[secnr]['kcountsize']
            gmonhist = data[secnr]['gmonhist']
            for histidx in range(0, kcountsize * 2):
                count = gmonhist[histidx]
                f.write(to_bytes(count, 1, endian))
            countsize = countsize - kcountsize
            secidx += 1
            if secidx == ngsecs:
                break
            # current section's lowpc - last section's highpc
            d_lowpc = data[secnr]['lowpc']
            lastsecnr = f'sec{ngsecs - 1}'
            d_highpc = data[lastsecnr]['highpc']
            d_kcountsize = int((d_highpc - d_lowpc) / 16)
            for i in range(0, d_kcountsize * 2):
                f.write(to_bytes(0, 4, endian))
            countsize = countsize - d_kcountsize
            while kcountsize != 0:
                f.write(to_bytes(0, 1, endian))
                kcountsize = kcountsize - 1

    def __write_gprof_cg_data(self, f, data):
        gprof = self.session.gprof
        endian = 'little' if gprof.get_prof_endianness() == 0 else 'big'
        GMON_TAG_CG_ARC = 1
        ngsecs = data['ngmonsecs']
        for secidx in range(0, ngsecs):
            secnr = f'sec{secidx}'
            tosz = data[secnr]['tosz']
            cgdata = data[secnr]['cgdata']
            for i in range(0, tosz):
                f.write(to_bytes(GMON_TAG_CG_ARC, 1, endian))
                f.write(to_bytes(cgdata[i]['raw_frompc'], 4, endian))
                f.write(to_bytes(cgdata[i]['raw_selfpc'], 4, endian))
                f.write(to_bytes(cgdata[i]['raw_count'], 4, endian))

    def __read_cg_from_target(self, profdata: dict):
        ngsecs = profdata['ngmonsecs']
        for i in range(0, ngsecs):
            name = f'sec{i}'
            value = profdata[name]['gmondata']
            g_start, g_hist, g_histsz, g_cg_from, g_cg_fromsz, g_cg_to, g_cg_tosz, g_lowpc, g_highpc, g_textsz = \
                [value[k] for k in range(0, 10)]
            if g_cg_fromsz <= 0 or g_cg_tosz <= 0 or g_cg_tosz > 0x1000000:
                raise Exception('Profiling Data Memory Corrupted !!!\n'
                                'Ensure program does not overwrite profiling data memory') from None
            profdata['frombin'] = self.mrd(g_cg_from, '-v', size=g_cg_fromsz * 8)
            profdata['tobin'] = self.mrd(g_cg_to, '-v', size=g_cg_tosz * 12)

        # Read the cg data for each section
        for i in range(0, ngsecs):
            name = f'sec{i}'
            value = profdata[name]['gmondata']
            g_start, g_hist, g_histsz, g_cg_from, g_cg_fromsz, g_cg_to, g_cg_tosz, g_lowpc, g_highpc, g_textsz = \
                [value[k] for k in range(0, 10)]
            cgfunclist = list()
            frombin = profdata['frombin']
            tobin = profdata['tobin']
            profdata.pop('frombin')
            profdata.pop('tobin')
            for frmidx in range(0, g_cg_fromsz):
                frompc = frombin[2 * frmidx]
                toidx = frombin[(2 * frmidx) + 1]
                while toidx != 0xFFFF:
                    toidx = g_cg_tosz - toidx - 1
                    selfpc = tobin[3 * toidx]
                    rawcnt = tobin[(3 * toidx) + 1]
                    if rawcnt < 0:
                        raise Exception('Invalid Profiling Data on Target') from None
                    cgfunclist.append({'raw_frompc': frompc, 'raw_selfpc': selfpc, 'raw_count': rawcnt})
                    toidx = tobin[(3 * toidx) + 2]
            profdata[name]['fromsz'] = g_cg_fromsz
            profdata[name]['tosz'] = g_cg_tosz
            profdata[name]['cgdata'] = cgfunclist
        return profdata

    def __read_hist_from_target(self):
        gprof = self.session.gprof
        profile_config = self.session.profile_config
        profaddrs = gprof.get_prof_addresses()
        profdata = dict()

        paramlist = ['cpufreq', 'sampfreq', 'binsize', 'ngmonsecs', 'gmonparam']
        for parameter in paramlist:
            profdata[parameter] = self.mrd(profaddrs[parameter], '-v', size=1)

        cpufrqelf = gprof.get_prof_cpufreq()
        sampfrqconf = profile_config['sampfreq']
        ngsecself = gprof.get_no_of_gmon_sections()
        scratchaddr = profile_config['scratchaddr']
        if cpufrqelf != profdata['cpufreq'] or sampfrqconf != profdata['sampfreq'] or profdata['binsize'] != 4 or \
                ngsecself != profdata['ngmonsecs'] or scratchaddr != profdata['gmonparam']:
            raise Exception('Profiling Data Memory Corrupted') from None

        # Read the gmon structure from memory
        gmondatasize = gprof.get_gmonparam_offsets()['GPARAM_SIZE']
        for i in range(0, ngsecself):
            profdata[f'sec{i}'] = dict()
            profdata[f'sec{i}']['gmondata'] = self.mrd(scratchaddr + (i * gmondatasize), '-v',
                                                       size=int(gmondatasize / 4))

        # Validate the values from gmon structure
        # Read the histogram data for each section
        gmonarray = gprof.get_gmonparamstruct()
        ngsecs = profdata['ngmonsecs']
        for i in range(0, ngsecs):
            name = f'sec{i}'
            value = profdata[name]['gmondata']
            g_start, g_hist, g_histsz, g_cg_from, g_cg_fromsz, g_cg_to, g_cg_tosz, g_lowpc, g_highpc, g_textsz = \
                [value[k] for k in range(0, 10)]
            gmonsec = gmonarray[i]
            profdata[name]['kcountsize'] = g_histsz
            profdata[name]['lowpc'] = g_lowpc
            profdata[name]['highpc'] = g_highpc
            profdata[name]['textsize'] = g_highpc - g_lowpc
            profdata[name]['section_name'] = gmonsec['secname']

            # Compare lowpc/highpc values, to check if data is not corrupted
            if g_lowpc != gmonsec['lowpc'] or g_highpc != gmonsec['highpc']:
                raise Exception('Profiling Data Memory Corrupted') from None
            nbytes = g_histsz * 2
            profdata[f'sec{i}']['gmonhist'] = self.mrd(g_hist, '-v', word_size=1, size=nbytes)
        return profdata

    def __write_prof_output(self, filename):
        gprof = self.session.gprof
        endian = 'little' if gprof.get_prof_endianness() == 0 else 'big'
        data = self.__read_hist_from_target()
        data = self.__read_cg_from_target(data)
        outfile = filename if filename != '' else 'gmon.out'
        f = open(outfile, 'wb')
        f.write('gmon'.encode())
        # Trailing space
        for i in range(0, 3):
            f.write(to_bytes(0, 4, endian))
        # Version
        f.write(to_bytes(1, 4))
        self.__write_gprof_hist_data(f, data)
        self.__write_gprof_cg_data(f, data)
        f.close()

    def __parse_ipxact(self, ctx, buf, sync):
        class __DoneCommand(reg_service.DoneParseIpxact):
            def __init__(self, sync):
                self.sync = sync

            def doneparseIpxact(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result=None)

        reg = protocol.invokeAndWait(self.session._curchan_obj.getRemoteService, reg_service.NAME)
        reg.parseIpxact(ctx, buf, __DoneCommand(sync))

    def __level2mode(self, level):
        if level == 'full':
            return 0
        if level == 'flow':
            return 1
        if level == 'event':
            return 2
        if level == 'cycles':
            return 3
        raise Exception(f'Unknown level {level}. set level to one of (full, flow, event, cycles)') from None

    def __slave_slr_map(self, slr, addr, length):
        slr_cnt = 3
        if slr < 0 or slr > slr_cnt:
            raise Exception(f'invalid slr number: should be from 0 to {slr_cnt}') from None
        if addr < 0xf0000000 or addr >= 0xf8000000 or (addr + length) >= 0xf8000000:
            raise Exception('address out of range, valid range 0xf0000000-0xf7ffffff') from None
        if slr == 0:
            return addr
        elif slr == 1:
            return addr + 0x108000000 - 0xf0000000
        elif slr == 2:
            return addr + 0x110000000 - 0xf0000000
        elif slr == 3:
            return addr + 0x118000000 - 0xf0000000

    def state(self):
        """
state:
    Return the current state of target.

Prototype:
    st = target.state()

Returns:
    Current state of target.

Examples:
    target.state()

Interactive mode examples:
    state
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None
        rs = exec_as_runnable(self.__get_run_state, node)
        if rs is None:
            raise Exception("State error. Invalid Context") from None
        if rs.is_suspended is False:
            info = 'Running'
        else:
            info = 'Stopped'
            if rs.suspend_reason is not None:
                info += f': ({rs.suspend_reason})'
        return info

    add_function_metadata('state', 'Return the current state of target', 'runcontrol', 'Target')

    def con(self, *args, addr=None, timeout=0):
        """
con:
    Resume execution of active target.

Prototype:
    target.con(*args, addr = <address>, timeout = <timeout_sec>)

Optional Arguments:
    addr = <address>
        Resume execution from address specified by <address>.

    timeout = <timeout_sec>
        Timeout value in seconds.

    -b or --block
        Block until the target stops or a timeout is reached.

Returns:
    None
        Target resumed successfully.
    Exception
        Error resuming target.

Examples:
    target.con(addr = 0x100000)
        Resume execution of the active target from address 0x100000.
    target.con('-b', timeout=3)
        Blocks the console until the target stops or a timeout is reached.
Interactive mode examples:
    con
    con -b -timeout 3
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='con')
        parser.add_argument('-b', '--block', action='store_true', help='block until stopped')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if addr is not None:
            check_int(addr)
            self.rwr('pc', addr)

        self.__resume(0, 1)
        if parsed_args.block is True:
            status = 0
            rs = exec_as_runnable(self.__get_run_state, node)
            if rs.is_suspended is True:
                return
            while status == 0:
                time.sleep(1)
                rs = exec_as_runnable(self.__get_run_state, node)
                if rs.is_suspended is True:
                    break
                if timeout:
                    timeout = timeout - 1
                    if timeout == 0:
                        raise Exception('timeout: target has not halted') from None

    add_function_metadata('con', 'Resume active target', 'runcontrol', 'Target')

    def stp(self, count=1):
        """
stp:
    Step into a line of source code.

Prototype:
    target.stp(count = <stp_count>)

Optional Arguments:
    count = <stp_count>
        Resume execution of the active target until control reaches
        instruction that belongs to different line of source code.
        If a function is called, stop at first line of the function
        code. Error is returned if line number information not
        available. If <count> is greater than 1, repeat <count> times.
        Step count is 1. (Default)

Returns:
    None
        If the target has single stepped.
    Exception
        Target is already running or cannot be resumed.

Examples:
    target.stp(count = 2)

Interactive mode examples:
    stp -count 2
        """

        self.__resume(4, count)

    add_function_metadata('stp', 'Step into a line of source code', 'runcontrol', 'Target')

    def nxt(self, count=1):
        """
nxt:
    Step over a line of source code.

Prototype:
    target.nxt(count = <nxt_count>)

Optional Arguments:
    count = <nxt_count>
        If <count> is greater than 1, repeat <count> times.
        Step count is 1. (Default)

Returns:
    None
        If the target has stepped to the next source line.
    Exception
        Target is already running or cannot be resumed.

Examples:
    target.nxt(count = 2)

Interactive mode examples:
    nxt -count 2
        """

        self.__resume(3, count)

    add_function_metadata('nxt', 'Step over a line of source code', 'runcontrol', 'Target')

    def stpi(self, count=1):
        """
stpi:
    Step into a line of source code.

Prototype:
    target.stp(count = <stp_count>)

Optional Arguments:
    count = <stp_count>
        Resume execution of the active target until control reaches
        instruction that belongs to different line of source code.
        If a function is called, stop at first line of the function
        code. Error is returned if line number information not
        available. If <count> is greater than 1, repeat <count> times.
        Step count is 1. (Default)

Returns:
    None
        If the target has single stepped.
    Exception
        Target is already running or cannot be resumed.

Examples:
    target.stp(count = 2)

Interactive mode examples:
    stp -count 2
        """

        self.__resume(2, count)

    add_function_metadata('stpi', 'Execute a machine instruction', 'runcontrol', 'Target')

    def nxti(self, count=1):
        """
nxti:
    Step over a machine instruction.

Prototype:
    target.nxti(count = <nixt_count>)

Optional Arguments:
    count = <nxt_count>
        If <count> is greater than 1, repeat <count> times.
        Step count is 1. (Default)

Returns:
    None
        If the target has stepped to the next machine instruction.
    Exception
        Target is already running or cannot be resumed.

Examples:
    target.nxti(count = 2)

Interactive mode examples:
    nxti
        """

        self.__resume(1, count)

    add_function_metadata('nxti', 'Step over a machine instruction', 'runcontrol', 'Target')

    def stpout(self, count=1):
        """
stpout:
    Step out from current function.

Prototype:
    target.stpout(count = <stp_count>)

Optional Arguments:
    count = <stp_count>
        If <count> is greater than 1, repeat <count> times.
        Step count is 1. (Default)

Returns:
    None
        If the target has stepped out of the current function.
    Exception
        Target is already running or cannot be resumed.

Examples:
    target.stpout(count = 2)

Interactive mode examples:
    stpout
        """

        self.__resume(5, count)

    add_function_metadata('stpout', 'Step-out from current function', 'runcontrol', 'Target')

    def stop(self):
        """
stop:
    Suspend execution of active target.

Prototype:
    target.stop()

Returns:
    None
        Target stopped successfully.
    Exception
        Error stopping target or target already stopped.

Examples:
    target.stop()

Interactive mode examples:
    stop
        """
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        if isinstance(node, TcfNodeExecContext):
            exec_in_dispatch_thread(node.stop)
        time.sleep(0.2)

    add_function_metadata('stop', 'Stop active target', 'runcontrol', 'Target')

    def mrd(self, *args, address: int = None, size=1, word_size: int = 4, **kwargs):
        """
mrd:
    Read data values from the active target's memory address
    specified by <address>.

Prototype:
    words = target.mrd(address = <mem_addr>, size = <num_words>,
            word_size = <word_size>)

Required Arguments:
    address = <mem_addr>
        Memory address to read from.

Optional Arguments:
    word_size = <word_size>
        <word_size> can be one of the values below:
        1  = Bytes accesses
        2  = Half-word accesses
        4  = Word accesses
        8  = Double-word accesses
        Default word_size is 4.
        Address is aligned to word-size before reading memory, if the
        '--unaligned_access' option is not used.

    size = <num_words>
        Number of words to be accessed

    --force or -f
        Overwrite access protection. By default accesses to reserved and
        invalid address ranges are blocked.

    --unaligned_access or -u
        The memory address is not aligned to the access size before performing
        a read operation. Support for unaligned accesses is target
        architecture dependent. If this option is not specified, addresses
        are automatically aligned to access size.

    --value or -v
        Return a list of values, instead of displaying the result on the
        console.

    --bin or -b
        Return data read from the target in binary format.

    file = <file-name>
        Write binary data read from the target to <file-name>.

    address_space = <name>
        Access specified memory space instead default memory space of
        current target.
        For Arm DAP targets, address spaces DPR, APR and AP<n> can be
        used to access DP registers, AP registers, and MEM-AP
        addresses respectively.
        The APR address range is 0x0 - 0xfffc, where the higher eight bits
        select an AP and the lower eight bits are the register address for
        that AP.

Returns:
    Memory addresses and data in requested format, else exception.

Examples:
    tgt.mrd(address = '0x1', size = '3', word_size = 1)
        Read 3 bytes at address 0x1.
    tgt.mrd(0x00100000, word_size=4, size=10)
        Read 10 words from address 0x00100000.
    tgt.mrd(0x00100000, '-b', word_size=8, size=20, file="mrd.bin")
        Read 20 double words from address 0x00100000 to the file mrd.bin.
    tgt.mrd(0x80090088, address_space="AP1")
        Read address 0x80090088 on DAP APB-AP.
        AP 1 selects the APB-AP.
        0x80090088 on APB-AP corresponds to DBGDSCR of Cortex-A9#0, on Zynq.
    x = tgt.mrd(0x100000, '-v', word_size=4, size=20)
        Read 20 words at 0x100000 and return a list of values.

Interactive mode examples:
    mrd 0x00100000 -word_size 8 -size 20
    mrd 0x80090088 -address_space AP1
        """

        parser = argparse.ArgumentParser(description='mrd')
        parser.add_argument('-f', '--force', action='store_true', help='Overwrite access protection')
        parser.add_argument('-u', '--unaligned_access', action='store_true', help='do not align address to access size')
        parser.add_argument('-v', '--value', action='store_true', help='Return list of values')
        parser.add_argument('-b', '--bin', action='store_true', help='Read binary data and store it in a file')
        parser.add_argument('address', nargs='?', type=int, help='Memory address')
        parser.add_argument('size', nargs='?', type=int, help='Num words')
        parser.add_argument('word_size', nargs='?', type=int, help='Word size')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.address is None and address is None:
            raise Exception("Address value not specified.") from None
        elif parsed_args.address is not None:
            address = parsed_args.address

        if parsed_args.word_size is not None:
            word_size = parsed_args.word_size
        if parsed_args.size is not None:
            size = parsed_args.size
        word_size = check_int(word_size)
        size = check_int(size)
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        if node.mem_context_data is None:
            raise Exception("Target does not support memory access.") from None

        node = self.__get_memory_tgt(node.id)

        if word_size not in [1, 2, 4, 8]:
            raise Exception(f"Illegal access size \'{word_size}\' : must be [1, 2, 4, 8].") from None

        num_bytes = word_size * size
        mode = MODE_VERIFY | MODE_CONTINUEONERROR

        if parsed_args.force or self.session._force_mem_accesses != 0:
            mode = mode | MODE_BYPASS_ADDR_CHECK

        if parsed_args.unaligned_access is False:
            address = address & ~(word_size - 1)

        endianness = 'little' if node.mem_context_data.isBigEndian() is False else 'big'

        address_space = kwargs.pop('address_space', None)
        file = kwargs.pop('file', None)
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if address_space is not None:
            AddressSpaces = node.mem_context_data.getProperties()["AddressSpaces"]
            if address_space in AddressSpaces.keys():
                if AddressSpaces.get(address_space) in self.session._mem_targets.keys():
                    node = self.session._mem_targets.get(AddressSpaces.get(address_space))
                else:
                    node = TcfNodeMemory(self.__get_current_channel(), AddressSpaces.get(address_space))
                    self.session._mem_targets[AddressSpaces.get(address_space)] = node
                exec_as_runnable(self.__get_mem_ctx, node)
            else:
                raise Exception(f"Unknown or ambiguous address space {address_space}. "
                                f"Must be one of {list(AddressSpaces.keys())}") from None

        buf_list = []
        exec_in_dispatch_thread(node.mem_read, address, 0, buf_list, 0, num_bytes, mode)

        if parsed_args.bin is True:
            if file is None:
                raise Exception("Filepath is not specified.") from None
            else:
                with open(file, 'wb') as f:
                    f.write(bytearray(buf_list))
        elif parsed_args.value is True:
            retbuf_list = []
            for i in range(0, len(buf_list), word_size):
                retbuf_list.append(int.from_bytes(buf_list[i:i + word_size], byteorder=endianness, signed=False))
            if len(retbuf_list) == 1:
                return retbuf_list[0]
            else:
                return retbuf_list
        else:
            mdinfo = ''
            for i in range(0, len(buf_list), word_size):
                mdinfo = mdinfo + \
                         '{0}{1}{2}{3}'.format('{0:{1}X}'.format(address, 2 * 4),
                                               " :  ",
                                               '{0:0{1}X}'.format(int.from_bytes(buf_list[i:i + word_size],
                                                                                 byteorder=endianness,
                                                                                 signed=False), 2 * word_size),
                                               '\n')
                address = address + word_size
            print(mdinfo)

    add_function_metadata('mrd', 'Memory read', 'memory', 'Target')

    def mwr(self, *args, address: int = None, size: int = None, word_size: int = 4, words: list or int = None,
            **kwargs):
        """
mwr:
    Write data values on the active target's memory address
    specified by <address>.

Prototype:
    target.mrd(address = <mem_addr>, size = <num_words>,
                words = <int_list or int>, word_size = <word_size>)

Required Arguments:
    address = <mem_addr>
        Memory address to read from.
    words = <int_list or int>
        Words to be written on the specified address.

Optional Arguments:
    word_size = <word_size>
        <word_size> can be one of the values below:
        1 = Bytes accesses
        2 = Half-word accesses
        4 = Word accesses
        8 = Double-word accesses
        Default word_size is 4.
         Address will be aligned to access-size before writing to memory, if
        the '--unaligned_access' option is not used.

    size = <num_words>
        Number of words to be accessed.
        When words are supplied as input data, the default size is 1.
        If a binary file is supplied as input data, the default size is the
        length of the file.

    --force or -f
        Overwrite access protection. By default accesses to reserved and
        invalid address ranges are blocked.

    --bypass_cache_synq
        Do not flush/invalidate CPU caches during memory write. Without this
        option, the debugger flushes/invalidates caches to make sure caches are
        in sync.

    --bin or b
        Read binary data from a file and write it to the target address space.

    file = <file-name>
        File from which binary data is read, to write to the target address
        space.

    address_space  = <name>
        Access specified memory space instead default memory space of
        current target.
        For Arm DAP targets, address spaces DPR, APR, and AP<n> can be
        used to access DP registers, AP registers, and MEM-AP
        addresses respectively.
        The APR address range is 0x0 - 0xfffc, where the higher eight bits
        select an AP and the lower eight bits are the register address for
        that AP.

    --unaligned_accesses or -u
        Memory address is not aligned to access size before performing
        a write operation. Support for unaligned accesses is target
        architecture dependent. If this option is not specified, addresses
        are automatically aligned to access size.

Returns:
    None
        Memory write successful.
    Exception
        Failed to write.

Examples:
    tgt.mwr(0x00100000, word_size=4, size=3, words=[0x01, 0x02, 0x03])
        Write three words from the list of values to address 0x00100000.
    tgt.mwr(0x00100000, word_size=4, size=10, words=[0x01, 0x02, 0x03])
        Write three words from the list of values to address 0x00100000
        and fill the last word from the list at the remaining seven
        address locations.
    tgt.mwr(0x00100000, '-b', word_size=4, size = 5, file="mwr.bin")
        Read 5 words from binary file mwr.bin and write the data at
        target address 0x00100000.
    tgt.mwr(0x80090088, address_space="AP1",words=[0x03186003])
        Write 0x03186003 to address 0x80090088 on DAP APB-AP.
        AP 1 selects the APB-AP.
        0x80090088 on APB-AP corresponds to DBGDSCR of Cortex-A9#0, on Zynq.

Interactive mode examples:
    mwr 0x00100000 -word_size 4 -size 10 -words [0x01, 0x02, 0x03]
        """

        parser = argparse.ArgumentParser(description='mwr')
        parser.add_argument('-f', '--force', action='store_true', help='Overwrite access protection')
        parser.add_argument('-u', '--unaligned_access', action='store_true', help='do not align address to access size')
        parser.add_argument('-v', '--bypass_cache_synq', action='store_true', help='bypass_cache_synq mode')
        parser.add_argument('-b', '--bin', action='store_true', help='Read binary data and store it in a file')
        parser.add_argument('address', nargs='?', type=int, help='Memory address')
        parser.add_argument('size', nargs='?', type=int, help='Num words')
        parser.add_argument('word_size', nargs='?', type=int, help='Word size')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.address is None and address is None:
            raise Exception("Address value not specified.") from None
        elif parsed_args.address is not None:
            address = parsed_args.address

        if words is None and parsed_args.bin is False:
            raise Exception("\'words\' not specified.") from None

        if parsed_args.word_size is not None:
            word_size = parsed_args.word_size

        # if size is not specified, len(file) must be written in case of binfile specified else 1 byte
        size_specified = True
        if parsed_args.size is None and size is None:
            size_specified = False
            size = 1
        if parsed_args.size is not None:
            size = parsed_args.size

        word_size = check_int(word_size)
        size = check_int(size)

        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        if node.mem_context_data is None:
            raise Exception("Target does not support memory access.") from None

        if words is None and parsed_args.bin is False:
            raise Exception("No data to write. Specify words or binary file.") from None

        node = self.__get_memory_tgt(node.id)

        if word_size not in [1, 2, 4, 8]:
            raise Exception(f"Illegal access size \'{word_size}\' : must be [1, 2, 4, 8].") from None

        mode = MODE_VERIFY | MODE_CONTINUEONERROR
        if parsed_args.force is True or self.session._force_mem_accesses != 0:
            mode = mode | MODE_BYPASS_ADDR_CHECK
        if parsed_args.bypass_cache_synq is True:
            mode = mode | MODE_BYPASS_CACHE_SYNC

        if parsed_args.unaligned_access is False:
            address = address & ~(word_size - 1)

        endianness = 'little' if node.mem_context_data.isBigEndian() is False else 'big'

        address_space = kwargs.pop('address_space', None)
        file = kwargs.pop('file', None)
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if address_space is not None:
            AddressSpaces = node.mem_context_data.getProperties()["AddressSpaces"]
            if address_space in AddressSpaces.keys():
                if AddressSpaces.get(address_space) in self.session._mem_targets.keys():
                    node = self.session._mem_targets.get(AddressSpaces.get(address_space))
                else:
                    node = TcfNodeMemory(self.__get_current_channel(), AddressSpaces.get(address_space))
                    self.session._mem_targets[AddressSpaces.get(address_space)] = node
                exec_as_runnable(self.__get_mem_ctx, node)
            else:
                raise Exception(f"Unknown or ambiguous address space {address_space}. "
                                f"Must be one of {list(AddressSpaces.keys())}") from None

        fill_data = None
        buf_list = []
        mwr_len = 0
        if parsed_args.bin is True:
            if file is None:
                raise Exception("\'file\' not specified.") from None
            else:
                with open(file, "rb") as f:
                    buf_list = f.read(os.path.getsize(file) if size_specified is False else (size * word_size))
                    mwr_len = len(buf_list)
                    word_size = 1
        else:
            if isinstance(words, list):
                size = max(size, len(words))
                len_of_words = len(words)
                if (len_of_words == 1 and size > 1) or len_of_words < size:
                    if len_of_words < size and len_of_words != 1:
                        mwr_len = len_of_words
                    fill_data = list(words[len_of_words - 1].to_bytes(word_size, endianness))
                else:
                    mwr_len = size
            else:
                fill_data = list(words.to_bytes(word_size, endianness))

        num_bytes = 0
        if mwr_len:
            num_bytes = word_size * mwr_len
            if parsed_args.bin is False:
                for i in range(0, mwr_len):
                    buf_list.append(list(words[i].to_bytes(word_size, endianness)))
                buf_list = flatten(buf_list)

            exec_in_dispatch_thread(node.mem_write, address, 0, buf_list, 0, num_bytes, mode)

        if fill_data is not None:
            exec_in_dispatch_thread(node.mem_fill, address + num_bytes,
                                    0, fill_data, (size - mwr_len) * word_size, mode)

    add_function_metadata('mwr', 'Memory write', 'memory', 'Target')

    def mask_write(self, address: int = None, mask: int = None, words: int = None):
        """
mask_write:
    Read, modify and write an address.

Note:
    This is an helper command for initializing the PS through
    ps*_init.tcl and is not recommended for external usage

Prototype:
    target.mask_write(addr = <address>, mask = <mask_bits>,
                      data = <data>)

Optional Arguments:
    addr = <address>
        Address to read and modify from.

    mask = <mask_bits>
        Mask for bits to be cleared.

    count = <num>
        Number of instructions to be disassembled.
        count is 1. (Default)

Returns:
    None
        Successfully modified and written.
    Exception
        Memory address cannot be accessed.
        """

        # TODO: error handling in case of write-only
        address = address & ~0x3
        curvalue = self.mrd(address, '-v')
        newval = ((curvalue[0] & ~mask) | (words & mask))
        self.mwr(address, words=[newval])

    add_function_metadata('mask_write', 'Read, modify and write an address', 'memory', 'Target')

    def mask_poll(self, address: int = None, mask: int = None, expected: int = None, sleep: int = 10,
                  timeout: int = 100):
        """
mask_poll:
    Read an address and poll the bit specified by mask.

Note:
    This is an helper command for initializing the PS through
    ps*_init.tcl and is not recommended for external usage

Prototype:
    target.mask_poll(addr = <address>, mask = <mask_bits>,
                      expected = <value>, sleep = <sleep_time>,
                      timeout = <iterations>)

Required Arguments:
    addr = <address>
        Address to poll bits from.

    mask = <mask_bits>
        Mask to poll the bits.

Optional Arguments:
    expected = <value>
        If expected-value is specified, then compare the bit(s) against
        the expected value.

    sleep = <sleep_time>
        A time delay specified by sleep is added between two successive
        poll cycles.
        Sleep time is 10ms. (Default)

    timeout = <iterations>
        Timeout iterations.
        Timeout is 100 iterations. (Default)

Returns:
    None
        Successfully polled the bits.
    Exception
        Memory address cannot be accessed.
        """

        count = 1
        while count < timeout:
            curval = self.mrd(address, '-v')
            maskedval = curval[0] & mask
            if expected is None:
                if maskedval != 0:
                    return
            else:
                if maskedval == expected:
                    return
                if sleep:
                    time.sleep(sleep / 1000)
            count = count + 1
        raise Exception(f"Timeout Reached.Mask poll failed at ADDRESS: {address} MASK: {mask}") from None

    add_function_metadata('mask_poll', 'Read an address and poll the bit specified by mask', 'memory', 'Target')

    def init_ps(self, init_data: list = None):
        """
init_ps:
    Initialize PS by running initalization sequence specified by init_data..

Note:
    This is an helper command for initializing the PS through
    ps*_init.py and is not recommended for external usage

Prototype:
    init_ps <init_data>

Required Arguments:
    init_ps
       The init_data contains mask_write, mask_poll and mask_delay commands in
        meta data format. mask_delay adds delay in milli seconds

Returns:
    None
        Successfully polled the bits.
    Exception
        Memory address cannot be accessed.
        """
        s = self.session
        saved_mode = s._force_mem_accesses
        s._force_mem_accesses = 1
        for cmd in init_data:
            cmddata = cmd.split()
            if cmddata[0] == "mask_write":
                self.mask_write(address=int(cmddata[1], 0), mask=int(cmddata[2], 0), words=int(cmddata[3], 0))
            elif cmddata[0] == "mask_poll":
                self.mask_poll(address=int(cmddata[1], 0), mask=int(cmddata[2], 0), expected=int(cmddata[3], 0))
            elif cmddata[0] == "mask_delay":
                time.sleep(int(cmddata[1]) / 1000)
            else:
                raise Exception("Wrong command in the init_data. Must be mask_write, mask_poll, mask_delay.") from None
        s._force_mem_accesses = saved_mode

    add_function_metadata('init_ps', 'initialize PS', 'memory', 'Target')

    def backtrace(self, maxframes=10):
        """
backtrace:
    Print stack trace for current target. Target must be stopped.
    Use debug information for best result. 'bt' is the alias for
    backtrace and can be used interchangeably.

Prototype:
    target.backtrace(maxframes = <num_frames>)

Optional Arguments:
    maxframes = <num_frames>
        Maximum number of frames in stack trace.
        Use -1 for all the frames. Maximum frames is 10. (Default)

Returns:
    Stack trace, else exception.

Examples:
    target.backtrace(maxframes = 5)
    target.bt(maxframes = 5)
    target.bt()
    target.bt(maxframes = -1)

Interactive mode examples:
    bt -maxframes 5
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        maxframes = check_int(maxframes)
        if maxframes == 0:
            return
        elif maxframes > 0:
            maxframes = maxframes - 1
        else:
            maxframes = -1

        cache_data = exec_as_runnable(self.get_stack_trace, maxframes)
        frames = len(cache_data) if maxframes == -1 else min(maxframes + 1, len(cache_data))

        st_info = ''
        for i in range(0, frames):
            node = cache_data[i]
            index = node.getIndex()
            ip = node.getInstructionAddress()
            fun_name = ''
            if ip is not None:
                offset = ''
                file = ''
                start_line = ''
                context_data = node.symbol_node.get_context_data()
                map_to_source_data = node.line_node.map_to_source_data
                if map_to_source_data is not None:
                    map_to_source_data = map_to_source_data[0]
                    file = map_to_source_data.file
                    start_line = map_to_source_data.start_line
                if context_data is not None:
                    fun_name = context_data.getName()
                    address = context_data.getAddress()
                    offset = ip - address

                if map_to_source_data is not None and context_data is not None:
                    st_info += '{0}{1:2s}{2:#0x}{3:1s}{4}{5}{6}{7}{8}' \
                               '{9}{10}{11}'.format(index, '', ip, '', fun_name, '()+', offset, ':', file,
                                                    ', line ', start_line, '\n')
                elif map_to_source_data is None and context_data is not None:
                    st_info += '{0}{1:2s}{2:#0x}{3:1s}{4}{5}{6}{7}'.format(index, '', ip, '',
                                                                           fun_name, '()+', offset, '\n')
                else:
                    st_info += '{0}{1:2s}{2:#0x}{3}'.format(index, '', ip, '\n')
            else:
                st_info += '{0}{1:2s}{2}{3}'.format(index, '', "unknown-pc", '\n')
        print(st_info)

    # Create an alias for backtrace command
    bt = backtrace
    add_function_metadata('backtrace', 'Print back trace', 'runcontrol', 'Target')
    add_function_metadata('bt', 'Print back trace', 'runcontrol', 'Target')

    def bpadd(self, *args, **kwargs):
        """
bpadd:
    Set a software or hardware breakpoint at address, function or
    <file>:<line>, or set a read/write watchpoint, or set a
    cross-trigger breakpoint.

Prototype:
    bp = target.bpadd(*kwargs) or
    bp = session.bpadd(*kwargs)

Options:
    temp
        The breakpoint is removed after it is triggered once.

    skip_prologue
        For function breakpoints, the function prologue is skipped while
        planting the breakpoint.

Optional Arguments:
    kwargs:
        aadr = <breakpoint_address>
            Specify the address at which the Breakpoint should be set.

        file = <file_name>
            Specify the <file-name> in which the Breakpoint should be
            set.

        line = <line_number>
            Specify the <line-number> within the file, where Breakpoint
            should be set.

        type = <breakpoint_type>
            Specify the Breakpoint type
            <breakpoint-type> can be one of the values below:
            auto = Auto - Breakpoint type is chosen by hw_server/TCF
            agent. This is the default type
            hw   = Hardware Breakpoint
            sw   = Software Breakpoint

        mode = <breakpoint_mode>
            Specify the access mode that will trigger the breakpoint.
            <breakpoint-mode> can be a bitwise OR of the values below:
            0x1  = Triggered by a read from the breakpoint location
            0x2  = Triggered by a write to the breakpoint location
            0x4  = Triggered by an instruction execution at the
            breakpoint location. This is the default for Line and
            Address breakpoints
            0x8  = Triggered by a data change (not an explicit write)
            at the breakpoint location

        enable = <mode>
            Specify initial enablement state of breakpoint. When <mode>
            is 0 the breakpoint is disabled, otherwise the breakpoint
            is enabled.  The default is enabled.

        skip_on_step = <value>
            Specify the trigger behaviour on stepping. This option is
            only applicable for cross trigger breakpoints and when
            DBGACK is used as breakpoint input.
                0 = trigger every time core is stopped (default).
                1 = supress trigger on stepping over a code breakpoint.
                2 = supress trigger on any kind of stepping.

        ct_input = <list>, ct_output = <list>
            Specify input and output cross triggers.  <list> is a list
            of numbers identifying the cross trigger pin. For Zynq 0-7
            is CTI for core 0, 8-15 is CTI for core 1, 16-23 is CTI ETB
            and TPIU, and 24-31 is CTI for FTM.

Returns:
    Breakpoint_id

Examples:
    target.bpadd(addr='0x100000')
        Set a Breakpoint at address 0x100000.
    target.bpadd('main')
        Set a function Breakpoint at main.
    target.bpadd(addr='main', type='sw', mode=3)
        Set a function Breakpoint at main, type is 'sw', mode is 3
    t1.bpadd(ct_input=0, ct_output=8, skip_on_step=1)
        Set a cross trigger to stop Zynq core 1 when core 0 stops.

Interactive mode examples:
    bpadd main
    bpadd -addr main -type sw
        """

        if self.__class__.__name__ == 'Target':
            if 'target_id' in kwargs and kwargs.pop("target_id") == "all":
                kwargs["target_id"] = 'all'
            else:
                kwargs["target_id"] = self.__select_target()

        else:
            kwargs["target_id"] = 'all'

        bp = _breakpoint.Breakpoint(self.session)
        bp.add(*args, **kwargs)
        return bp

    add_function_metadata('bpadd', 'Set a Breakpoint/Watchpoint', 'breakpoints', 'Target')

    def bpremove(self, *args, bp_ids: List[int] or int = None):
        """
bpremove:
    Remove the Breakpoints/Watchpoints specified by <id-list> or remove
    all the breakpoints when no id is specified.

Prototype:
    session.bpremove(bp_ids = <bp_id_list> or <bp_id>) or
    target.bpremove(bp_ids = <bp_id_list> or <bp_id>)

Arguments:
    bp_ids = <bp_id_list>
        List of breakpoint ids to be removed.

    --all
        Removes all breakpoints.

Returns:
    None
        Breakpoint(s) removed successfully.
    Exception
        Failed to remove breakpoint(s).

Examples:
    target.bpremove(bp_ids = 0)
    target.bpremove(bp_ids = [1,3])
    target.bpremove('--all')

Interactive mode examples:
    bpremove -bp_ids [1,2]
    bpremove -all
        """

        parser = argparse.ArgumentParser(description='bpremove')
        parser.add_argument('--all', action='store_true', help='Removes all breakpoints')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.all is True:
            ids = '--all'
        elif bp_ids is None:
            raise Exception(f'Invalid input {bp_ids} in \'bp_ids\'. Must be \'--all\' or breakpoint ids.') from None
        else:
            ids = bp_ids
        return self.__bpmodify(action='remove', ids=ids)

    add_function_metadata('bpremove', 'Remove one or more Breakpoints/Watchpoints', 'breakpoints', 'Target')

    def bpenable(self, *args, bp_ids: List[int] or int = None):
        """
bpenable:
    Enable the Breakpoints/Watchpoints specified by <id-list> or
    enable all the breakpoints when no id is specified.

Prototype:
    target.bpenable(bp_ids = <bp_id_list> or <bp_id>) or
    session.bpenable(bp_ids = <bp_id_list> or <bp_id>)

Arguments:
    bp_ids = <bp_id_list>
        List of breakpoint ids to be enabled.

    --all
        Enables all breakpoints.

Returns:
    None
        Breakpoint(s) enabled successfully.
    Exception
        Failed to enable breakpoint(s).

Examples:
    target.bpenable(bp_ids = 0)
    target.bpenable(bp_ids = [1,3])
    target.bpenable('--all')

Interactive mode examples:
    bpenable -bp_ids [1,2]
    bpenable -all
        """

        parser = argparse.ArgumentParser(description='bpenable')
        parser.add_argument('--all', action='store_true', help='Enables all breakpoints')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.all is True:
            ids = '--all'
        elif bp_ids is None:
            raise Exception(f'Invalid input {bp_ids} in \'bp_ids\'. Must be \'--all\' or breakpoint ids.') from None
        else:
            ids = bp_ids
        return self.__bpmodify(action='enable', ids=ids)

    add_function_metadata('bpenable', 'Enable one or more Breakpoints/Watchpoints', 'breakpoints', 'Target')

    def bpdisable(self, *args, bp_ids: List[int] or int = None):
        """
bpdisable:
    Disable the Breakpoints/Watchpoints specified by <id-list> or
    disable all the breakpoints when no id is specified.

Prototype:
    target.bpdisable(bp_ids = <bp_id_list> or <bp_id>) or
    session.bpdisable(bp_ids = <bp_id_list> or <bp_id>)

Arguments:
    bp_ids = <bp_id_list>
        List of breakpoint ids to be disabled.

    --all
        disables all breakpoints.

Returns:
    None
        Breakpoint(s) disabled successfully.
    Exception
        Failed to disable breakpoint(s).

Examples:
    target.bpdisable(bp_ids = 0)
    target.bpdisable(bp_ids = [1,3])
    target.bpdisable('--all')

Interactive mode examples:
    bpdisable -bp_ids [1,2]
    bpdisable -all
        """

        parser = argparse.ArgumentParser(description='bpdisable')
        parser.add_argument('--all', action='store_true', help='Disables all breakpoints')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.all is True:
            ids = '--all'
        elif bp_ids is None:
            raise Exception(f'Invalid input {bp_ids} in \'bp_ids\'. Must be \'--all\' or breakpoint ids.') from None
        else:
            ids = bp_ids
        return self.__bpmodify(action='disable', ids=ids)

    add_function_metadata('bpdisable', 'Disable one or more Breakpoints/Watchpoints', 'breakpoints', 'Target')

    def bpstatus(self, bp_id: int = None):
        """
bpstatus:
    Print the status of Breakpoints/Watchpoints specified by bp_id.

Prototype:
    status = target.bpstatus(bp_id = <bp_id>) or
    status = session.bpstatus(bp_id = <bp_id>)

Arguments:
    bp_id = <bp_id>
        Breakpoint id to print the status for.

Returns:
    Breakpoint status.

Examples:
    status = target.bpstatus(0)

Interactive mode examples:
    bpstatus 0
        """

        if bp_id is None:
            raise Exception('Wrong # args: should be bpstatus(id).') from None
        return self.__bpmodify(action='status', ids=bp_id)

    add_function_metadata('bpstatus', 'Print the Breakpoint/Watchpoint status', 'breakpoints', 'Target')

    def bplist(self):
        """
bplist:
    List all the breakpoints/watchpoints along with brief status
    for each breakpoint and the target on which it is set.

Prototype:
    status = target.bplist() or
    status = session.bplist() or

Returns:
    List of breakpoints.

Interactive mode examples:
    bplist
        """

        bpl_this = ''
        uuids = []
        if len(self.session._bptable) == 0:
            bpl_this = '\nNo breakpoints currently set from this session\n'
        else:
            for id, bpdata in self.session._bptable.items():
                uuid = bpdata.id
                uuids.append(uuid)
                enabled = bpdata.enabled
                location = str(bpdata.location)
                if location is None:
                    if bpdata.ct_input is not None and bpdata.ct_output is not None:
                        location = 'ct_in:' + str(bpdata.ct_input) + ' ct_out:' + str(bpdata.ct_output)
                bpl_this = bpl_this + '\n{0:10s} {1:10s} {2:20s}'.format(str(id), str(1) if enabled is True else str(0),
                                                                         ' ' if location is None else location)
                bps = get_bp_status(self.session, uuid, 'full')
                if len(bps) == 0:
                    continue
                sinfo = ''
                for ctx, ctxdata in bps.items():
                    ctxdatastr = json.dumps(ctxdata)
                    if sinfo == '' and (0 if location is None else len(location)) < 18:
                        sinfo = sinfo + '{0:20s}'.format('target ' + str(ctx) + ': ' + ctxdatastr[0:27])
                    else:
                        sinfo = sinfo + '\n{0:41s} {1:20s}'.format('', 'target ' + str(ctx) + ': ' + ctxdatastr[0:27])
                    length = len(ctxdatastr)
                    pos = 27
                    while (length - pos) > 0:
                        sinfo = sinfo + '\n{0:41s} {1:20s}'.format('', ctxdatastr[pos:pos + 41])
                        pos = pos + 41
                bpl_this = bpl_this + sinfo

        bp_ids = exec_in_dispatch_thread(bp_get_ids, self.session)
        bpl_other = ''
        bpl_other_header = ''
        if len(uuids) < len(bp_ids):
            bpl_other_header = '\n' + '-' * 48 + '\n'
            bpl_other_header = bpl_other_header + 'Breakpoints set from other Debug clients\n'
            bpl_other_header = bpl_other_header + '-' * 48 + '\n'
            for id in bp_ids:
                if id not in uuids:
                    properties = exec_in_dispatch_thread(bp_get_properties, id, self.session)
                    enabled = properties.get('Enabled')
                    loc = str(properties.get('Location'))
                    bpl_other = bpl_other + '\n{0:10s} {1:10s} {2:20s}'.format('-',
                                                                               str(1) if enabled is True else str(0),
                                                                               ' ' if loc is None else loc)
                    bps = get_bp_status(self.session, id)
                    if len(bps) == 0:
                        continue
                    sinfo = ''
                    for ctx, ctxdata in bps.items():
                        ctxdatastr = json.dumps(ctxdata)
                        if sinfo == '':
                            sinfo = sinfo + '{0:20s}'.format('target ' + str(ctx) + ': ' + ctxdatastr[0:27])
                        else:
                            sinfo = sinfo + '\n{0:41s} {1:20s}'.format('',
                                                                       'target ' + str(ctx) + ': ' + ctxdatastr[0:27])
                        length = len(ctxdatastr)
                        pos = 27
                        while (length - pos) > 0:
                            sinfo = sinfo + '\n{0:41s} {1:20s}'.format('', ctxdatastr[pos:pos + 41])
                            pos = pos + 41
                    bpl_other = bpl_other + sinfo

        if len(self.session._bptable) == 0 and bpl_other == '':
            print(bpl_this)
        else:
            header = '{0:10s} {1:10s} {2:20s} {3:20s}'.format("ID", "Enabled", "Location", "Status")
            header = header + '\n{0:10s} {1:10s} {2:20s} {3:20s}'.format("==", "=======", "========", "======")
            if len(self.session._bptable):
                bpl_this = header + bpl_this
            if bpl_other != '':
                bpl_other = bpl_other_header + header + bpl_other
            print(bpl_this + bpl_other)

    add_function_metadata('bplist', 'Print the Breakpoint/Watchpoint status', 'breakpoints', 'Target')

    def dow(self, file: str, *args, **kwargs):
        """
dow:
    Download ELF or binary file to target.

Prototype:
    target.dow(file = <file>, *args, **kwargs)

Required Arguments:
    file = <file_name>
        Elf file to be downloaded. In case of data file, binary
        file is to be downloaded to active target address specified
        by <addr>.

Optional Arguments:
    auto_stop = <0 or 1/False or True>
        Automatically stop before download.

    relocate_sections = <addr>
        Relocate the address map of the program sections to <addr>.
        This option should be used when the code is self-relocating,
        so that the debugger can find debug symbol info for the code.
        <addr> is the relative address, to which all the program
        sections are relocated.

    set_entry = <0 or 1/False or True>
        Set PC register to entry point.

    addr = <addr>
        In case of binary data file, download the data to address specified
        by <addr>.

Options:
    --clear (-c)
        Clear uninitialized data (bss).

    --skip-tcm-clear (-s)
        Clear uninitialized data sections that are part of Versal TCM.
        This is needed when elfs are loaded through debugger, so that
        TCM banks are initialized proporly. When the elfs are part of
        the PDI, PLM initializes the TCM, before loading the elfs.

    --force (-f)
        Overwrite access protection. By default accesses to reserved
        and invalid address ranges are blocked.

    --vaddr (-v)
        Use vaddr from the elf program headers while downloading the elf.
        This option is valid only for elf files.

    --data (-d)
        Download data file.

    --bypass_cache_synq (-b)
        Do not flush/invalidate CPU caches during memory write. Without this
        option, the debugger flushes/invalidates caches to make sure caches are
        in sync.

Returns:
    Nothing, if successful, else exception.

Examples:
    target.dow("/tmp/prog.elf")

Interactive mode examples:
    dow hello.elf -c -relocate_sections 0x30000000
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='File download options')
        parser.add_argument('-c', '--clear', action='store_true', help='Clear uninitialized data (bss)')
        parser.add_argument('-d', '--data', action='store_true', help='Download data file')
        parser.add_argument('-f', '--force', action='store_true', help='Force download')
        parser.add_argument('-v', '--vaddr', action='store_true', help='Use vaddr instead of paddr')
        parser.add_argument('-b', '--bypass_cache_synq', action='store_true', help='bypass_cache_synq mode')
        parser.add_argument('-s', '--skip_tcm_clear', action='store_true',
                            help='Skip clearing uninitialized data (bss) in TCM for Versal')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        argvar = {'file': file, 'data': 0, 'cmds': set(), 'synq': SyncRequest(), 'f': None, 'keepsym': 0, 'err': None,
                  'curpos': 0, 'chunksize': 0x4000, 'total_bytes': 0, 'current_bytes': 0, 'offset': 0,
                  'profile_config': [], 'clear_tcm': 0, 'tcm_size': 0}

        if 'addr' in kwargs:
            if parsed_args.data is True:
                argvar['address'] = check_int(kwargs.pop('addr'))
                argvar['data'] = 1
            else:
                raise Exception(f"address is only applicable with --data option") from None
        else:
            if parsed_args.data is True:
                raise Exception(f"--data is only applicable with valid address") from None

        argvar['mode'] = MODE_VERIFY | MODE_CONTINUEONERROR
        if parsed_args.force is True or self.session._force_mem_accesses:
            argvar['mode'] |= MODE_BYPASS_ADDR_CHECK
        if parsed_args.bypass_cache_synq is True:
            argvar['mode'] |= MODE_BYPASS_CACHE_SYNC

        silent = self.session.get_silent_mode()
        if 'set_entry' not in kwargs:
            argvar['set_entry'] = 0 if argvar['data'] == 1 else 1
        else:
            if argvar['data'] == 1:
                argvar['set_entry'] = 0
            else:
                set_entry = kwargs.pop("set_entry")
                if set_entry not in self.__bool_values:
                    raise TypeError(f"Expected boolean value for set_entry but got {set_entry}") from None
                argvar['set_entry'] = self.__bool_values[set_entry]

        if 'auto_stop' not in kwargs:
            argvar['auto_stop'] = 0 if argvar['data'] == 1 else 1
        else:
            auto_stop = kwargs.pop("auto_stop")
            if auto_stop not in self.__bool_values:
                raise TypeError(f"Expected boolean value for auto_stop but got {auto_stop}") from None
            argvar['auto_stop'] = self.__bool_values[auto_stop]
        keepsym = kwargs.pop('keepsym') if 'keepsym' in kwargs else 0
        relocation_addr = check_int(kwargs.pop('relocate_sections')) if 'relocate_sections' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        argvar['vaddr'] = 1 if parsed_args.vaddr is True else 0
        argvar['clear'] = 1 if parsed_args.clear is True else 0

        if parsed_args.skip_tcm_clear is False:
            rc_data = exec_as_runnable(self.__get_run_ctx, node).getProperties()
            if rc_data.get('CPUType') == "ARM" and rc_data.get('ARMType') == "Cortex-R5":
                while rc_data.get('ParentID') is not None:
                    n = node.info.get_node(rc_data.get('ParentID'))
                    rc_data = exec_as_runnable(self.__get_run_ctx, n).getProperties()
                    if rc_data.get('Name').startswith("Versal"):
                        argvar['clear_tcm'] = 1
                        argvar['tcm_size'] = 0x40000
                        print('WARNING: Uninitialized elf sections like bss, stack, etc. will be cleared\n'
                              '         if they use R5 TCM. Use skip-tcm-clear to skip this.\n'
                              '         Further warnings will be suppressed')
                        break

        rs = exec_as_runnable(self.__get_run_state, node)
        if rs is None:
            raise Exception('Target doesnot support run state') from None
        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        mem_node = self.__get_memory_tgt(node.id)
        if argvar.get('auto_stop') == 1 and rs.is_suspended is False:
            self.stop()

        ts = round(time.time() * 1000)
        argvar['start_time'], argvar['progress_time'] = ts, ts
        if not silent:
            print('{0}{1}{2:4d}{3}{4:4d}{5}{6}'.format(0, '%', 0, 'MB', 0, 'MB/s  ', '??:?? ETA'), end='\r')

        entry = None
        profiling = 0
        if argvar.get('data') == 0:
            f = ElfParse()
            argvar['f'] = f
            f.open(file)
            sec_info = f.get_elf_section_headers()
            if not silent:
                print(f'Downloading Program -- {file} \n{sec_info}')
            entry = f.get_elf_header()['e_entry']
            phl = f.get_program_header()
            for ph in phl:
                if argvar.get('err') is not None:
                    break
                argvar['curpos'] = 0
                argvar['offset'] = ph.get('p_offset')
                argvar['address'] = ph.get('p_vaddr') if argvar.get('vaddr') else ph.get('p_paddr')
                argvar['endpos'] = ph.get('p_filesz')
                if descriptions.describe_p_type(ph.get('p_type')) == 'LOAD':
                    argvar['total_bytes'] += ph.get('p_filesz')
                    self.__download_data(argvar, mem_node)

                    if ph.get('p_filesz') < ph.get('p_memsz') and \
                            (argvar.get('clear') or (argvar.get('clear_tcm') and
                                                     argvar.get('address') < argvar.get('tcm_size'))):
                        argvar['curpos'] = 0
                        clearsz = ph.get('p_memsz') - ph.get('p_filesz')
                        argvar['total_bytes'] += clearsz
                        self.__dow_clear_data(argvar, ph, mem_node)

            if 'scratchaddr' in self.session.profile_config and 'sampfreq' in self.session.profile_config:
                if self.session.gprof is not None and self.session.gprof.is_elf_prof_enabled(file):
                    profiling = 1
        else:
            argvar['f'] = open(argvar.get('file'), 'rb')
            argvar['endpos'] = os.path.getsize(argvar.get('file'))
            argvar['total_bytes'] = argvar['endpos']
            self.__download_data(argvar, mem_node)

        if argvar.get('err') is None:
            with argvar.get('synq').cond:
                argvar.get('synq').cond.wait()

        if argvar.get('err') is not None:
            err = argvar.get('err')
            raise Exception(f'\nFailed to download {file} : {err}') from None
        else:
            if not silent:
                print('Successfully downloaded ', file)

        if profiling == 1:
            big_endian = 0
            size = 4
            gprof = self.session.gprof
            pcreg = self.__get_register_context('pc').getProperties()
            if 'BigEndian' in pcreg and pcreg['BigEndian'] != 0:
                big_endian = 1
            cputype = rc['CPUType']
            if cputype == 'ARM':
                cputype = rc['ARMType']

            gmonparamsize = gprof.get_gmonparam_offsets()['GPARAM_SIZE']
            gprof.set_profile_elf(file)
            gprof.set_prof_endianness(big_endian)
            version = gprof.get_prof_version()
            if version != 1:
                raise Exception('Profile version not supported') from None
            profaddr = gprof.get_prof_addresses()
            cpufreq = gprof.get_prof_cpufreq()
            execsecs = gprof.get_sorted_exec_sections()
            ngsecs = gprof.get_no_of_gmon_sections()
            scratchaddr = self.session.profile_config['scratchaddr']
            sampfreq = self.session.profile_config['sampfreq']
            pmemstartaddr = scratchaddr
            pmemstartaddr = pmemstartaddr + (ngsecs * gmonparamsize)

            for i in range(0, ngsecs):
                secdict = execsecs[i]
                secdict = gprof.get_prof_cg_hist_details(secdict, cputype)
                # Starting address of profiling data
                baseaddr = scratchaddr + (i * gmonparamsize)

                data = [0, pmemstartaddr, secdict['histcount'], pmemstartaddr + secdict['histsize'],
                        0, pmemstartaddr + secdict['histsize'] + secdict['cgsize'], 0, secdict['lowpc'],
                        secdict['highpc'], secdict['highpc'] - secdict['lowpc']]

                self.mwr(baseaddr, word_size=size, size=int(gmonparamsize / 4), words=data)
                # Update pmem start addr to end addr of scratch mem
                pmemstartaddr = pmemstartaddr + secdict['histsize'] + secdict['cgsize']
                # Initialize profile memory
                tmemsize = pmemstartaddr - scratchaddr + (ngsecs * gmonparamsize)
                data = list()
                for j in range(0, tmemsize):
                    data.append(0x00)
                tempaddr = scratchaddr + (ngsecs * gmonparamsize)
                self.mwr(tempaddr, word_size=1, size=tmemsize, words=data)
                # Initialize the variables
                # No. of gmon sections
                self.mwr(profaddr['ngmonsecs'], word_size=4, size=1, words=ngsecs)
                # gmonparams address location
                self.mwr(profaddr['gmonparam'], word_size=4, size=1, words=scratchaddr)
                # Sample freq
                self.mwr(profaddr['sampfreq'], word_size=4, size=1, words=sampfreq)
                # Bin Size
                self.mwr(profaddr['binsize'], word_size=4, size=1, words=0x4)
                # Timer ticks
                self.mwr(profaddr['timerticks'], word_size=4, size=1, words=int(cpufreq / sampfreq))

                gprof.enable_profiling()

        if argvar['set_entry'] == 1:
            if entry is not None:
                print('Setting PC to Program Start Address', '{0:#0{1}x}'.format(entry, 10))
                self.rwr('pc', entry)

        if argvar['data'] == 0:
            data_list = []
            map_table = self.session._memmaptable

            if file in map_table.keys():
                for map in map_table[file]:
                    if dict_get_safe(map, 'auto_sym') != 1 and dict_get_safe(map, 'auto_sec') != 1:
                        data_list.append(map)

            if relocation_addr is not None:
                sh_list = argvar['f'].get_section_header()
                for sh in sh_list:
                    if sh.get('sh_flags') & 0x7:
                        data_list.append({mm.PROP_ADDRESS: sh.get('sh_addr') + relocation_addr,
                                          mm.PROP_SIZE: sh.get('sh_size'),
                                          mm.PROP_FLAGS: mm.FLAG_READ | mm.FLAG_WRITE | mm.FLAG_EXECUTE,
                                          mm.PROP_FILE_NAME: file, mm.PROP_SECTION_NAME: sh.get('sh_name'),
                                          mm.PROP_OFFSET: 0, mm.PROP_ID: file, 'auto_sec': 1})
            else:
                data_list.append({mm.PROP_ADDRESS: 0, mm.PROP_SIZE: 0, mm.PROP_FLAGS: 0, mm.PROP_FILE_NAME: file,
                                  mm.PROP_OFFSET: 0, mm.PROP_ID: file, 'auto_sym': 1})
            map_table[file] = data_list

            for id, maps in map_table.copy().items():
                if file == id:
                    continue
                data_list = []

                for data in maps:
                    if keepsym or dict_get_safe(data, 'auto_sym') != 1:
                        data_list.append(data)
                if len(data_list) == 0:
                    map_table.pop(id)
                else:
                    map_table[id] = data_list

            self.__update_memory_map()

        if argvar['f'] is not None:
            argvar['f'].close()
        # Set the elf file for MB profiling and MB trace
        self.session.mb_profile_config['elf'] = file
        self.session.mb_trace_config['elf'] = file

    add_function_metadata('dow', 'Download ELF and binary file to active target.', 'download', 'Target')

    def memmap(self, *args, **kwargs):
        """
memmap:
    Add/remove a memory map entry for the active target.

Prototype:
    target.memmap(*args, **kwargs)
Note:
    Only the memory regions previously added through memmap
    command can be removed.

Options:
    list
        List the memory regions added to the active target's memory map.

    clear
        Specify whether the memory region should be removed from the target's
        memory map.

Optional Arguments:
    kwargs
        addr=<memory-address>
            Address of the memory region that should be added/removed
            from the target's memory map.

        alignment=<bytes>
            Force alignment during memory accesses for a memory region.
            If alignment is not specified, default alignment is chosen
            during memory accesses.

        size=<memory-size>
            Size of the memory region.

        flags=<protection-flags>
            Protection flags for the memory region.
            <protection-flags> can be a bitwise OR of the values below:
            0x1  = Read access is allowed
            0x2  = Write access is allowed
            0x4  = Instruction fetch access is allowed
            Default value of <protection-flags> is 0x3
            (Read/Write Access).

        relocate_sections=<addr>
            Relocate the address map of the program sections to <addr>.
            This option should be used when the code is self-relocating, so
            that the debugger can find the debug symbol info for the code.
            <addr> is the relative address, to which all the program sections
            are relocated.

        osa=1
            Enable OS awareness for the symbol file.
            Fast process start and fast stepping options are turned off by
            default. These options can be enabled using the osa command. See
            "help osa" for more details.

Returns:
    None
        Successfully modified and written.
    Exception
        Memory address cannot be accessed.

Examples:
    tgt.memmap(addr=0xFC000000, size=0x1000, flags=3)
        Add the memory region 0xFC000000 to target's memory
        map. Read/Write accesses are allowed to this region.

Interactive mode examples:
    memmap -addr 0xFC000000 -size 0x1000 -flags 3
    memmap -list
    memmap -clear
        """
        parser = argparse.ArgumentParser(description='memmap options')
        parser.add_argument('-l', '--list', action='store_true', help='List target memory map')
        parser.add_argument('-c', '--clear', action='store_true', help='Clear an entry from memory map')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.list is True:
            if parsed_args.clear is True or len(kwargs):
                raise Exception('extra args with -list option.') from None
            map_list = ''
            for id, maps in self.session._memmaptable.items():
                for map in maps:
                    map_data = map.copy()
                    map_list += '\n{0:15s}{1:10s}{2:10s}{3:8s}{4:20s}{5}'. \
                        format('{0:#0x}'.format(map_data.pop(mm.PROP_ADDRESS)),
                               '{0:#0x}'.format(map_data.pop(mm.PROP_SIZE)),
                               '{0:#0x}'.format(map_data.pop(mm.PROP_OFFSET)),
                               '{0:#0x}'.format(map_data.pop(mm.PROP_FLAGS)),
                               ntpath.basename(map_data.pop(mm.PROP_FILE_NAME) if mm.PROP_FILE_NAME in map_data else '')
                               , f'\n     properties {map_data}' if len(map_data) else '')
            if map_list != '':
                header = '{0:15s}{1:10s}{2:10s}{3:8s}{4:20s}'.format("Address", "Size", "Offset", "Flags", "FileName")
                header += '\n{0:15s}{1:10s}{2:10s}{3:8s}{4:20s}'.format("=" * 7, "=" * 4, "=" * 6, "=" * 5, "=" * 8)
                print(header + map_list)
            else:
                print('No memory regions currently set for the active target during this session\n\n')
            return

        id = None
        if 'file' in kwargs:
            id = kwargs.get('file')
            if not os.access(id, os.R_OK):
                raise Exception(f'File {id} is not readable.') from None
            if 'addr' not in kwargs:
                kwargs.setdefault('addr', 0)
        elif 'addr' not in kwargs:
            raise Exception('Address of the memory region not specified.') from None
        elif 'size' not in kwargs and parsed_args.clear is False:
            raise Exception('Size of the memory region not specified.') from None
        address = check_int(kwargs.pop('addr'))
        offset = kwargs.pop('offset') if 'offset' in kwargs else 0
        flags = kwargs.pop('flags') if 'flags' in kwargs else 3
        size = kwargs.pop('size') if 'size' in kwargs else 0
        section = kwargs.pop('section') if 'section' in kwargs else None
        relocation_addr = check_int(kwargs.pop('relocate_sections')) if 'relocate_sections' in kwargs else None
        file = kwargs.pop('file') if 'file' in kwargs else None
        alignment = kwargs.pop('alignment') if 'alignment' in kwargs else None
        osa = 1 if 'osa' in kwargs else 0
        props = kwargs.pop('prop') if 'prop' in kwargs else dict()
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if id is None:
            id = address
        map = self.session._memmaptable
        data_list = []
        if parsed_args.clear is True:
            found = 0
            if id in map.keys():
                found = 1
                map.pop(id)
            if id == address:
                for map_id, map_data in map.items():
                    for sec in map_data:
                        if sec['Addr'] == id:
                            map_data.remove(sec)
                            found = 1
                            break
                    if found:
                        break
            if found == 0:
                raise Exception(f'{hex(id) if isinstance(id, int) else id} was not added to target\'s memory map.') \
                    from None
        else:
            if relocation_addr is not None:
                if file is None:
                    raise Exception('file is not specified in the kwargs.') from None

                if file in map.keys():
                    for map_data in map[file]:
                        if dict_get_safe(map_data, 'auto_sec') != 1:
                            data_list.append(map_data)

                f = ElfParse()
                f.open(file)
                sh_list = f.get_section_header()
                f.close()
                for sh in sh_list:
                    if sh.get('sh_flags') & 0x7:
                        data_list.append({mm.PROP_ADDRESS: sh.get('sh_addr') + relocation_addr,
                                          mm.PROP_SIZE: sh.get('sh_size'),
                                          mm.PROP_FLAGS: mm.FLAG_READ | mm.FLAG_WRITE | mm.FLAG_EXECUTE,
                                          mm.PROP_FILE_NAME: file, mm.PROP_SECTION_NAME: sh.get('sh_name'),
                                          mm.PROP_OFFSET: offset,
                                          mm.PROP_ID: file, 'auto_sec': 1})

                map[file] = data_list
            else:
                data = {}
                if file is not None:
                    data[mm.PROP_FILE_NAME] = file
                if section is not None:
                    data[mm.PROP_SECTION_NAME] = section
                data[mm.PROP_ADDRESS] = address
                data[mm.PROP_SIZE] = size
                data[mm.PROP_OFFSET] = offset
                data[mm.PROP_FLAGS] = flags
                if alignment is not None:
                    data['Alignment'] = alignment
                if osa:
                    data['OSA'] = 0
                if len(props) != 0:
                    data.update(props)
                data_list.append(data)
                map[id] = data_list

        self.session._memmaptable = map
        self.__update_memory_map()

    add_function_metadata('memmap', 'Modify memory map of target', 'memorymap', 'Target')

    def osa(self, *args, file=None):
        """
osa:
    Configure OS awareness for a symbol file.

Prototype:
    target.osa(*args, file = <file_name>)

Optional Arguments:
    file = <file_name>
        Symbol file <file-name> to configure OS awareness.If no symbol
        file is specified and only one symbol file exists in target's
        memory map, then that symbol file is used. If no symbol file
        is specified and multiple symbol files exist in target's memory
        map, then an error is thrown.

Options:
    --disable (--d)
        Disable OS awareness for a symbol file. If this option is not
        specified, OS awareness is enabled.

    --fast_exec (--fe)
        Enable fast process start. New processes will not be tracked
        for debug and are not visible in the debug targets view.

    --fast_step (--fs)
        Enable fast stepping. Only the current process will be
        re-synced after stepping. All other processes will not be
        re-synced when this flag is turned on.

Returns:
    None
        OSA is configured successfully.
    Exception
        Ambiguous options are specified.

Examples:
    tgt.osa('--fast_step', file='tmp/core0zynq.elf')
        Enable OSA and turn on fast-exec and fast-step modes.

Interactive mode examples:
    osa -fast_step -file core0zynq.elf
        """
        parser = argparse.ArgumentParser(description='Options for osa function')
        parser.add_argument('-d', '--disable', action='store_true', help='Disable OS awareness')
        parser.add_argument('--fast_exec', action='store_true', help='Enable fast process start')
        parser.add_argument('--fast_step', action='store_true', help='Enable fast stepping')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.disable is True and (parsed_args.fast_exec is True or parsed_args.fast_step is True):
            raise Exception('-fast-exec and -fast-step are not valid when -disable is used.') from None

        match = 0
        file_match = ''
        map_table = self.session._memmaptable
        for id, map_list in map_table.items():
            for map in map_list:
                if 'FileName' in map:
                    if file is not None and dict_get_safe(map, 'FileName') != file:
                        break
                    if match and file_match != dict_get_safe(map, 'FileName'):
                        raise Exception('Cannot configure OSA: Multiple symbol files found in target\'s '
                                        'memory map. Specify a symbol file') from None
                    if parsed_args.disable is True and 'OSA' in map:
                        map.pop('OSA')
                    else:
                        map['OSA'] = {'Mode': parsed_args.fast_step << 1 | parsed_args.fast_exec}
                    if file_match == '':
                        file_match = map['FileName']
                    match = 1

        if match == 1:
            self.__update_memory_map()
            return

        if parsed_args.disable is True:
            raise Exception('Cannot disable OSA: No symbol file found in target\'s memory map.') from None

        if file is None:
            raise Exception('Cannot enable OSA: No symbol file found in target\'s memory map. Specify a symbol file.') \
                from None

        map_table[file] = [{mm.PROP_ADDRESS: 0, mm.PROP_SIZE: 0, mm.PROP_FLAGS: 0, mm.PROP_OFFSET: 0, mm.PROP_ID: file,
                            mm.PROP_FILE_NAME: file,
                            'OSA': {'Mode': parsed_args.fast_step << 1 | parsed_args.fast_exec}}]
        self.__update_memory_map()

    add_function_metadata('osa', 'Configure OS awareness for a symbol file', 'memorymap', 'Target')

    def verify(self, file: str, *args, **kwargs):
        """
verify:
    Verify if ELF/binary file is downloaded correctly to target.

Prototype:
    target.verify(file = <file>, *args, **kwargs)

Required Arguments:
    file = <file_name>
        Elf file to be verified. In case address is provided, binary
        file to be verified if downloaded correctly to active target
        address specified by <addr>.

Optional Arguments:
    kwargs
        auto-stop
            File name containing bitstream.
        addr
            addres

Options:
    --force (-f)
        Overwrite access protection. By default accesses to reserved
        and invalid address ranges are blocked.

    --vaddr (-v)
        Use vaddr from the elf program headers while verifying the
        elf data. This option is valid only for elf files.

    --data (-d)
        Specified file is binary.

Returns:
    Nothing, if successful, else exception.

Examples:
    target.verify("/tmp/prog.elf")

Interactive mode examples:
    verify prog.elf
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='File verify options')
        parser.add_argument('-d', '--data', action='store_true', help='Download data file')
        parser.add_argument('-f', '--force', action='store_true', help='Force download')
        parser.add_argument('-v', '--vaddr', action='store_true', help='Use vaddr instead of paddr')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        argvar = {'file': file, 'data': 0, 'cmds': set(), 'synq': SyncRequest(), 'f': None, 'err': None,
                  'curpos': 0, 'chunksize': 0x4000, 'total_bytes': 0, 'current_bytes': 0, 'sections': [],
                  'auto_stop': 0}

        if 'addr' in kwargs:
            if parsed_args.data is True:
                argvar['address'] = check_int(kwargs.pop('addr'))
                argvar['data'] = 1
            else:
                raise Exception(f"address is only valid with --data option") from None
        else:
            if parsed_args.data is True:
                raise Exception(f"--data is only applicable with valid address") from None

        if 'auto_stop' in kwargs:
            auto_stop = kwargs.pop("auto_stop")
            if auto_stop not in self.__bool_values:
                raise TypeError(f"Expected boolean value for auto_stop but got {auto_stop}") from None
            argvar['auto_stop'] = self.__bool_values[auto_stop]
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        argvar['mode'] = MODE_VERIFY | MODE_CONTINUEONERROR
        if parsed_args.force is True or self.session._force_mem_accesses:
            argvar['mode'] |= MODE_BYPASS_ADDR_CHECK

        argvar['vaddr'] = 1 if parsed_args.vaddr is True else 0

        rs = exec_as_runnable(self.__get_run_state, node)
        if argvar['auto_stop'] == 1 and rs.is_suspended is False:
            self.stop()

        ts = round(time.time() * 1000)
        argvar['start_time'], argvar['progress_time'] = ts, ts
        print('{0}{1}{2:4d}{3}{4:4d}{5}{6}'.format(0, '%', 0, 'MB', 0, 'MB/s  ', '??:?? ETA'), end='\r')

        if argvar.get('data') == 0:
            f = ElfParse()
            argvar['f'] = f
            f.open(file)
            phl = f.get_program_header()
            for ph in phl:
                if descriptions.describe_p_type(ph.get('p_type')) == 'LOAD' and ph.get('p_filesz') > 0:
                    argvar['total_bytes'] += ph.get('p_filesz')
                    argvar['sections'].append([ph.get('p_offset'), ph.get('p_vaddr') if argvar.get('vaddr')
                    else ph.get('p_paddr'), ph.get('p_filesz')])
        else:
            argvar['f'] = open(file, 'rb')
            argvar['total_bytes'] = os.path.getsize(file)
            argvar['sections'].append([0, argvar['address'], argvar['total_bytes']])

        mem_node = self.__get_memory_tgt(node.id)
        if len(argvar.get('sections')):
            for section in argvar.get('sections'):
                if argvar['err'] is not None:
                    break
                endpos = section[2]
                argvar['curpos'] = 0
                size = argvar.get('chunksize')
                argvar['addr'] = section[1]
                while argvar.get('curpos') != endpos:
                    if argvar['err'] is not None:
                        break
                    offset = section[0] + argvar.get('curpos')
                    addr = section[1] + argvar.get('curpos')

                    if endpos != 0 and size > endpos - argvar.get('curpos'):
                        size = endpos - argvar.get('curpos')
                    argvar['cmds'].add((protocol.invokeAndWait(mem_node.mem_read, addr, 0, [], offset, size,
                                                               argvar.get('mode'), self.__verify_callback, argvar)).id)
                    argvar['curpos'] += size
        else:
            raise Exception(f'No loadable sections in the file {file}') from None

        if argvar.get('err') is None:
            with argvar.get('synq').cond:
                argvar.get('synq').cond.wait()

        if argvar.get('err') is not None:
            err = argvar.get('err')
            raise Exception(f'\nFailed to verify {file} due to the error {err}') from None
        else:
            print(f'\nSuccessfully verified {file}')

        if argvar['f'] is not None:
            argvar['f'].close()

    add_function_metadata('verify', 'Verify if ELF/binary file is downloaded correctly to target', 'download', 'Target')

    def dis(self, addr: str or int = None, count: int = 1):
        """
dis:
    Disassemble <num> instructions at address specified by <address>
    The keyword "pc" can be used to disassemble instructions at the current PC.
    Default value for <num> is 1.

Prototype:
    target.dis(addr, count):

Optional Arguments:
    addr = <intruction_addr>
        Address to be disassembled from.

    count = <num>
        Number of instructions to be disassembled.
        count is 1. (Default)

Returns:
    Disassembled instructions, else exception.

Examples:
    ins = target.dis(addr = 0x0, count = 2)

Interactive mode examples:
    dis -addr 0 -count 2
        """
        if addr is None:
            addr = 'pc'
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        if isinstance(addr, str) and addr == 'pc':
            rs = exec_as_runnable(self.__get_run_state, node)
            if rs.is_suspended is False:
                raise Exception(f"Cannot read PC. current target state is \'Running\'") from None
            addr = self.session.rrd('-nv', 'pc')['pc']

        res = exec_in_dispatch_thread(node.get_disassembly_node().disassemble,
                                      check_int(addr), check_int(count) * 4, {dis.PROP_SIMPLIFIED: True})
        info = ''
        for i in range(0, len(res)):
            info += '{0}{1}{2}{3}'.format('{0:0{1}x}'.format(res[i].getAddress(), 8), ': ',
                                          res[i].getInstruction()[0]['Text'], '\n')
        print(info)

    add_function_metadata('dis', 'Disassemble instructions', 'runcontrol', 'Target')

    def fpga(self, *args, **kwargs):
        """
fpga:
    Configure FPGA.

Prototype:
    target.fpga(*args, **kwargs)

Optional Arguments:
    kwargs
        file = <file_name>
            File name containing bitstream.

Options:

    --partial (-p)
        Configure FPGA without first clearing current configuration.
        This options should be used while configuring partial
        bitstreams created before 2014.3 or any partial bitstreams in
        binary format.

    --no_revision_check (-n)
        Disable bitstream vs silicon revision revision compatibility
        check.

    --skip_compatibility_check (-sk)
        Disable bitstream vs FPGA device compatibility check.

    --state (-s)
        Return whether the FPGA is configured.

    --config_status (-c)
        Return configuration status.

    --cor0_status (-c0)
        Return configuration option 0 status.

    --cor1_status (-c1)
        Return configuration option 1 status.

    --ir_status (-i)
        Return IR capture status.

    --boot_status (-b)
        Return boot history status.

    --timer_status (-t)
        Return watchdog timer status.

    --wbstar_status (-w)
        Return warm boot start address status.

Returns:
    Depends on the options used.
    None
        If file or --p option is used, and fpga is configured.
    Configuration value
        Other options.
    Exception
        Failed to configure.

Examples:
    target.fpga(file='zc702.bit')

Interactive mode examples:
    fpga -file test.bit
    fpga -wbstar_status
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='File download options')
        parser.add_argument('--skip_compatibility_check', action='store_true',
                            help='don\'t check bitstream for device compatibility')
        parser.add_argument('-n', '--no_revision_check', action='store_true',
                            help='don\'t check bitstream vs silicon revision')
        parser.add_argument('-s', '--state', action='store_true', help='return done status')
        parser.add_argument('-c', '--config_status', action='store_true', help='return done status')
        parser.add_argument('-p', '--partial', action='store_true', help='partial config')
        parser.add_argument('-i', '--ir_status', action='store_true', help='return ir status')
        parser.add_argument('-b', '--boot_status', action='store_true', help='return boot status')
        parser.add_argument('-t', '--timer_status', action='store_true', help='return timer status')
        parser.add_argument('--cor0_status', action='store_true', help='return cor0 status')
        parser.add_argument('--cor1_status', action='store_true', help='return cor1 status')
        parser.add_argument('-w', '--wbstar_status', action='store_true', help='return wbstar status')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        tcf_xicom = TcfXicom(self.session)

        optcnt = parsed_args.state + parsed_args.config_status + parsed_args.ir_status + parsed_args.boot_status + \
                 parsed_args.timer_status + parsed_args.cor0_status + parsed_args.cor1_status + \
                 parsed_args.wbstar_status

        if optcnt > 1:
            raise Exception('Conflicting options specified.') from None

        silent = self.session.get_silent_mode()
        file = kwargs.pop('file') if 'file' in kwargs else None
        if file is None and optcnt == 0:
            raise Exception('Bitstream file is not specified.') from None
        if file is not None and optcnt > 0:
            raise Exception('Either file or one of the status options must be specified.') from None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        argvar = {'file': file, 'cmds': set(), 'synq': SyncRequest(), 'f': None, 'err': None, 'curpos': 0,
                  'chunksize': 0x4000, 'total_bytes': 0, 'current_bytes': 0,
                  'partial': True if parsed_args.partial is True else False}

        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        if 'JtagDeviceID' in rc.keys():
            if node.get_jtag_device_node() is None:
                node.set_jtag_device_node(TcfNodeJtagDevice(node, self.__get_current_channel(), rc.get('JtagDeviceID')))
            fpga_tgt = self.__get_fpga_target() \
                if 'reg.jprogram' not in exec_as_runnable(self.__get_jtag_device_properties, node) else \
                self.session.get_context_target_map()[node.id]
        else:
            fpga_tgt = self.__get_fpga_target()
        fpga_ctx = self.session.model.launch_node.get_target_context_map()[fpga_tgt]
        fpga_node = self.session.model.get_nodes()[fpga_ctx]
        jtag_ctx = exec_as_runnable(self.__get_run_ctx, fpga_node).getProperties()['JtagNodeID']

        if parsed_args.state is True:
            config_status = exec_in_dispatch_thread(tcf_xicom.xicom_get_config_status, jtag_ctx)
            try:
                index = config_status[2].split(',').index('END OF STARTUP (EOS) STATUS')
            except Exception:
                print('FPGA is not configured.')
                return
            if config_status[1] & (1 << index) != 0:
                print('FPGA is configured.')
            else:
                print('FPGA is not configured.')
            return

        if optcnt:
            if parsed_args.config_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_config_status, jtag_ctx)
                reg_name = 'CONFIG_STATUS'
            elif parsed_args.ir_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_ir_status, jtag_ctx)
                reg_name = 'IR_STATUS'
            elif parsed_args.boot_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_boot_status, jtag_ctx)
                reg_name = 'BOOT_STATUS'
            elif parsed_args.timer_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_timer_status, jtag_ctx)
                reg_name = 'TIMER_STATUS'
            elif parsed_args.cor0_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_cor0_status, jtag_ctx)
                reg_name = 'COR0_STATUS'
            elif parsed_args.cor1_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_cor1_status, jtag_ctx)
                reg_name = 'COR1_STATUS'
            elif parsed_args.wbstar_status is True:
                data = exec_in_dispatch_thread(tcf_xicom.xicom_get_wbstar_status, jtag_ctx)
                reg_name = 'WBSTAR_STATUS'
            else:
                raise Exception('Invalid option provided.') from None

            bits, status, names = data[0], data[1], data[2].split(',')
            props = {}
            bitno, mask, value = 0, 1, 0
            startbit = bitno
            last_name = ''
            res = reg_name + ': ' + str(status)

            for name in names:
                name = name.strip()
                if mask > 1 and last_name != name:
                    endbit = bitno - 1
                    if startbit == endbit:
                        props[last_name + '(Bits [' + str(startbit) + '])'] = value
                    else:
                        props[last_name + '(Bits [' + str(endbit) + ':' + str(startbit) + '])'] = value
                    mask, value, startbit = 1, 0, bitno
                if status & 1:
                    value = value | mask
                bitno += 1
                status = status >> 1
                mask = mask * 2
                last_name = name
            if mask > 1:
                endbit = bitno - 1
                if startbit == endbit:
                    props[last_name + '(Bits [' + str(startbit) + '])'] = value
                else:
                    props[last_name + '(Bits [' + str(endbit) + ':' + str(startbit) + '])'] = value
            max_len = 0
            for name, value in props.items():
                if max_len < len(name):
                    max_len = len(name)
            for name, value in props.items():
                if res != '':
                    res += '\n'
                res += '{0}{1}{2}{3}'.format(' ' * (max_len - len(name)), name, ':', value)
            print(res)
            return

        # Open Bitfile
        argvar['f'] = open(argvar.get('file'), 'rb')
        argvar['total_bytes'] = os.path.getsize(argvar.get('file'))
        if argvar['total_bytes'] == 0:
            raise Exception('Empty bitstream file.') from None

        # Read the bitstream properties
        ln = argvar['total_bytes'] if argvar['total_bytes'] < 1024 else 1024
        data = argvar['f'].read(ln)
        argvar['f'].seek(0)
        bit_props = exec_in_dispatch_thread(tcf_xicom.xicom_get_bitfile_props, jtag_ctx, ln, bytearray(data))[0]
        if bit_props['ISBITFILE'] is True:
            if bit_props['IS_PARTIAL'] is True:
                argvar['partial'] = True
            if parsed_args.skip_compatibility_check is False and bit_props['ISCOMPATIBLE'] is False:
                raise Exception('Bitstream is not compatible with the target.') from None
            if parsed_args.no_revision_check is False and bit_props['IS_REVISION_COMPATIBLE'] is False:
                raise Exception('Bitstream is not compatible with the target revision, use --no_revision_check'
                                ' to allow programming.') from None
        else:
            raise Exception('Unable to parse bitstream header. Cannot determine if the \n'
                            'bitstream is partial or compatible with the jtag device\n.') from None

        # Initialize fpga for programming
        if argvar['partial'] is False:
            if not silent:
                print('Initializing', end='\r')
            if exec_in_dispatch_thread(tcf_xicom.xicom_config_prog, jtag_ctx)[0] != 1:
                raise Exception('fpga initialization failed') from None

        # Start progress
        ts = round(time.time() * 1000)
        argvar['start_time'], argvar['progress_time'] = ts, ts
        if not silent:
            print('{0}{1}{2:4d}{3}{4:4d}{5}{6}'.format(0, '%', 0, 'MB', 0, 'MB/s  ', '??:?? ETA'), end='\r')

        while argvar.get('curpos') != argvar['total_bytes']:
            if argvar['err'] is not None:
                break
            bindata = argvar['f'].read(argvar.get('chunksize'))
            datalen = len(bindata)
            argvar['cmds'].add((protocol.invokeAndWait(tcf_xicom.xicom_config_in, jtag_ctx, argvar['curpos'],
                                                       argvar['total_bytes'], datalen, bindata,
                                                       self.__download_fpga_callback,
                                                       argvar)).id)
            argvar['curpos'] += datalen

        if argvar.get('err') is None:
            with argvar.get('synq').cond:
                argvar.get('synq').cond.wait()

        if argvar.get('err') is not None:
            exec_in_dispatch_thread(tcf_xicom.xicom_cancel, jtag_ctx)
            err = argvar.get('err')
            raise Exception(f'\nFailed to configure bitstream : {err}') from None

        # Start the configuration
        argvar['init_status'] = exec_in_dispatch_thread(tcf_xicom.xicom_config_start, jtag_ctx)[0]
        config_status = exec_in_dispatch_thread(tcf_xicom.xicom_get_config_status, jtag_ctx)
        try:
            if config_status[1] & (1 << config_status[2].split(',').index('END OF STARTUP (EOS) STATUS')) == 0:
                raise Exception('fpga configuration failed. INIT PIN is not HIGH') from None
        except Exception:
            raise Exception('fpga configuration failed. INIT PIN is not HIGH') from None

        argvar['f'].close()
        print('\n')

    add_function_metadata('fpga', 'Configure FPGA with bitstream specified options, or read FPGA state.',
                          'download', 'Target')

    def device_program(self, file: str = None, *args):
        """
device_program:
    Program PDI/BIT.

Prototype:
    target.device_program(*args, file = <PDI/BIT_file>)

Required Arguments:
    file = <PDI/BIT_file>
        PDI or BIT file to be programmed into the device.

Options:
    --partial (--p)
        Format the return data in hexadecimal.

Returns:
    None
        Device is configured.
    Exception
        Configuration failed.

Examples:
    target.device_program("test.pdi")
    target.device_program("test.pdi", '-p')

Interactive mode examples:
    device_program test.pdi
    device_program test.pdi -p
        """
        device_program_stage = ''
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='Device program arguments')
        parser.add_argument('-p', '--partial', action='store_true', help='PDI is partial PDI')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        try:
            tcf_xicom = TcfXicom(self.session)
            silent = self.session.get_silent_mode()
            if file is None:
                raise Exception('PDI file is not specified.') from None

            argvar = {'file': file, 'cmds': set(), 'synq': SyncRequest(), 'f': None, 'err': None, 'curpos': 0,
                      'chunksize': 0x4000, 'total_bytes': os.path.getsize(file), 'current_bytes': 0}

            jtag_ctx = self.__get_jtag_ctx()

            argvar['f'] = open(argvar.get('file'), "rb")
            if argvar['total_bytes'] == 0:
                raise Exception('Empty configuration file.') from None

            # Initialize device for programming
            if parsed_args.partial is False:
                if not silent:
                    print('Initializing', end='\r')
                exec_in_dispatch_thread(tcf_xicom.xicom_config_begin, jtag_ctx, {})

            # Start progress
            device_program_stage = 'config_data'
            ts = round(time.time() * 1000)
            argvar['start_time'], argvar['progress_time'] = ts, ts
            if not silent:
                print('{0}{1}{2:4d}{3}{4:4d}{5}{6}'.format(0, '%', 0, 'MB', 0, 'MB/s  ', '??:?? ETA'), end='\r')

            while argvar.get('curpos') != argvar['total_bytes']:
                if argvar['err'] is not None:
                    break
                bindata = argvar['f'].read(argvar.get('chunksize'))
                datalen = len(bindata)

                argvar['cmds'].add((protocol.invokeAndWait(tcf_xicom.xicom_config_data, jtag_ctx, bindata,
                                                           datalen, self.__download_device_callback,
                                                           argvar)).id)
                argvar['curpos'] += datalen

            if argvar.get('err') is None:
                with argvar.get('synq').cond:
                    argvar.get('synq').cond.wait()

            if argvar.get('err') is not None:
                exec_in_dispatch_thread(tcf_xicom.xicom_cancel, jtag_ctx)
                err = argvar.get('err')
                raise Exception(f'\nFailed to program device : {err}') from None

            exec_in_dispatch_thread(tcf_xicom.xicom_config_end, jtag_ctx, {})

            argvar['f'].close()
            print('\n')
        except Exception as e:
            s = e.args[0]
            if device_program_stage != '' and self.session._add_plm_log_msg:
                self.session._add_plm_log_msg = 0
                s = s + "\nRun \"plm log\" command to see PDI boot messages." \
                        "\n\nThis extra message about \"plm log\" command will not be " \
                        "\ndisplayed for subsequent \"device program\" errors during" \
                        "\nthis session.\n"
            raise Exception(s) from None

    add_function_metadata('device_program', 'Program PDI or BIT file into the device', 'device', 'Target')

    def device_status(self, reg: str = None, *args):
        """
device_status:
    Return JTAG Register Status.

Prototype:
    target.device_status(*args, reg = <jtag_reg>)

Optional Arguments:
    reg = <target_reg>
        JTAG Register for which status is to be returned.
        List of available registers. (Default)

Options:
    --hex (--h)
        Format the return data in hexadecimal.

Returns:
    Status report.

Examples:
    target.device_status()
    target.device_status('error_status')

Interactive mode examples:
    device_status
    device_status -error_status
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='Device program arguments')
        parser.add_argument('--hex', action='store_true', help='Print result in hex format')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        jtag_ctx = self.__get_jtag_ctx()

        if node.get_jtag_reg_node() is None:
            node.set_jtag_reg_node(TcfNodeJtagReg(self.__get_current_channel(), jtag_ctx))
        reg_list = exec_as_runnable(self.__get_jtag_reg_list, node)

        reg_names = {}
        for r in reg_list:
            arg = [node, r]
            reg_def = exec_as_runnable(self.__get_jtag_reg_def, arg)
            reg_names.update({reg_def['name']: r})

        if reg is None:
            print(*reg_names.keys())
        else:
            if reg not in reg_names.keys():
                raise Exception(f'Could not find JTAG register {reg}') from None
            reg_def = exec_as_runnable(self.__get_jtag_reg_def, [node, reg_names[reg]])

            slr = 0
            status = reg.upper() + ': 0x'
            reg_val = exec_in_dispatch_thread(node.get_jtag_reg_node().jtag_reg_get, jtag_ctx, reg_names[reg], slr)
            for b in reg_val[::-1]:
                status += f'{b:02x}'
            status += '\n'
            props = {}
            if 'fields' in reg_def:
                fields = reg_def['fields']
                for field in fields:
                    bits = field['bits']
                    value = 0
                    for bit in bits:
                        byte = reg_val[round(math.modf(bit / 8)[1])]
                        value = (value << 1) | ((byte >> (bit % 8)) & 0x01)
                    name = (field['name'].upper()).replace('_', ' ')
                    bit_range = bits[0]
                    bit_len = len(bits)
                    if bit_len > 1:
                        bit_range = str(bits[0]) + ":" + str(bits[bit_len - 1])
                    value = format(value, 'x') if parsed_args.hex is True else format(value, f"0{bit_len}b")
                    key = '{0}{1}'.format(name, f' (Bits [{bit_range}])')
                    props.update({key: value})

            max_len = 0
            for name, value in props.items():
                if max_len < len(name):
                    max_len = len(name)

            for name, value in props.items():
                status += '{0}{1}{2}{3}'.format(name.rjust(max_len), ':', value, '\n')
            print(status)

    add_function_metadata('device_status', 'Return JTAG Register status', 'device', 'Target')

    def device_authjtag(self, file):
        """
device_authjtag:
    Secure Debug BIN.

Prototype:
    target.device_authjtag(file = <file_name>)

Required Arguments:
    file = <file_name>
        Unlock device for secure debug.

Returns:
    None
        Secure debug is successful
    Exception
        Debug failed.

Examples:
    target.device_authjtag('test.pdi')

Interactive mode examples:
    device_authjtag test.pdi
        """
        total_bytes = os.path.getsize(file)
        if total_bytes == 0:
            raise Exception('Empty secure debug file.') from None

        with open(file, "rb") as f:
            data = f.read(total_bytes)
        tcf_xicom = TcfXicom(self.session)
        exec_in_dispatch_thread(tcf_xicom.xicom_secure_debug, self.__get_jtag_ctx(), data)

    add_function_metadata('device_authjtag', 'Unlock device for secure debug', 'device', 'Target')

    def rrd(self, *args, reg: str = None, access_mode=None):
        """
rrd:
    Read register for active target.
Prototype:
    target.rrd(*args, reg = <target_reg>)
Optional Arguments:
    reg = <target_reg>
        Register to be read. For a processor core target, processor
        core register can be read. For a target representing a group
        of processor cores, system registers or IOU registers can be
        read.
        Read top level registers or groups.(Default)
Options:
    --defs (-d)
        Read register definitions instead of values
    --dict (-di)
        Do not show bit fields along with register values. By default,
        bit fields are shown, when available.
Returns:
    Register names and values, or register definitions
        Successfully read from the register.
    Exception.
        Invalid register is specified or register cannot be read.
Examples:
    target.rrd()
        Read top level registers or groups.
    target.rrd('usr r8')
        Read register r8 in group usr.
    target.rrd(reg = 'usr r8')
        Read register r8 in group usr.

Interactive mode examples:
    rrd
    rrd usr
    rrd 'usr r8'
    rrd 'usr r8' -defs
        """
        parser = argparse.ArgumentParser(description='Register read arguments')
        parser.add_argument('-d', '--defs', action='store_true', help='Return register definitions')
        parser.add_argument('--dict', action='store_true', help='Return result in dict format')
        parser.add_argument('--nvlist', action='store_true', help='Return register name-value list')
        parser.add_argument('-f', '--format_result', action='store_true', help='Format the result')
        parser.add_argument('--no_bits', action='store_true',
                            help='Do not show bit fields along with register values')
        parser.add_argument('reg', nargs='?', help='Register name to read')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.reg is not None:
            if reg is not None:
                raise TypeError(f"Conflicting args: Specify register name either as positional arg or keyword arg")
            reg = parsed_args.reg

        defs = 1 if parsed_args.defs else 0
        nvlist = 1 if parsed_args.nvlist else 0
        format_result = 1 if parsed_args.format_result else 0
        no_bits = 1 if parsed_args.no_bits else 0

        flags = {'defs': defs, 'nvlist': nvlist, 'format_result': format_result, 'no_bits': no_bits}

        if defs + nvlist + format_result > 1:
            raise TypeError(f"conflicting args, use only one of --defs, --format-result, or --nvlist")

        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        # TODO - if the board is reset/powered on/off, then as on today, we cannot detect that and there is no way to
        # reset the current node and current target - below 2 lines, we extract the new node from the old node id
        # if node not in node.info.get_nodes().values():
        #     node = node.info.get_node(node.id)

        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        if access_mode is not None:
            access_modes = exec_as_runnable(self.__get_access_modes, node)
            if access_mode not in access_modes.keys():
                raise Exception(
                    f"Unknown or ambiguous access mode '{access_mode}': must be {', '.join(list(access_modes.keys()))}") from None
            node = access_modes[access_mode]

        if reg is None:
            reg = ""
        reg_path = reg.split(" ")

        data = exec_as_runnable(self.__get_registers, node)

        if reg != "":
            child_data, node_match = self.__get_next_level_children(data, reg_path)
        else:
            node_match = node
            child_data = data

        if not child_data:
            raise Exception(f"Target has no registers.") from None

        data.update(child_data)
        self.__read_registers(data)

        children = node_match.get_reg_children_data()
        if children:
            flags['parent'] = 1
            ctxs = children
        else:
            ctxs = {node_match.id: node_match}

        retval = self.__print_regs(data, ctxs, flags)
        if nvlist:
            return retval
        else:
            print(retval)

    add_function_metadata('rrd', 'Register read', 'registers', 'Target')

    def rwr(self, reg: str, val: int):
        """
rwr:
    Write to register.
Prototype:
    target.rwr(reg = <target_reg>, val = <reg_value>)
Required Arguments:
    reg = <target_reg>
        Register for which value has to be written. For a processor
        core target, the processor core register can be written to. For
        a target representing a group of processor cores, system
        registers or IOU registers can be written.
    val = <reg_val>
        Specified value for the register.
Returns:
    None
        Successfully written on the register.
    Exception.
        Invalid register is specified or register cannot be written.
Examples:
    target.rwr(reg = 'r8', val = 0x0)
    target.rwr('r8', 0)

Interactive mode examples:
    rwr r8 0
    rwr 'usr r8' 1
        """
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        if reg is None:
            reg = ""
        reg_path = reg.split(" ")

        parent = node
        reg_ctx = None
        data = {}
        for name in reg_path:
            match = 0
            regs = exec_as_runnable(self.__get_registers, parent)
            data.update(regs)
            for ctx, child_node in regs.items():
                reg_ctx = child_node.get_context_data()
                if reg_ctx.getName() == name:
                    parent = child_node
                    match = 1
                    break
            if match == 0:
                raise Exception(f"No register match: {name} ") from None
        reg_node = parent

        if reg_ctx is not None:
            if not reg_ctx.isWriteable():
                raise Exception(f"Register '{reg}' is not writable") from None

        bit_fields = reg_ctx.getBitNumbers()
        if bit_fields:
            parent_id = reg_ctx.getParentID()
            parent_node = data[parent_id]
            parent_ctx = parent_node.get_context_data()

            exec_in_dispatch_thread(parent_node.read_register)
            error = parent_node.get_reg_error()
            if error is not None:
                raise Exception(f"Cannot access register: {error}")
            current_value = parent_node.get_reg_value()
            size = parent_ctx.getSize()
            start = size * 8 - 1
            mask = 0

            bf_list = self.__get_bit_fields_list(bit_fields)
            for bf in bf_list:
                for bit in bf:
                    if bit < start:
                        start = bit
                    mask = mask | (1 << bit)
                current_value = (current_value & ~mask) | ((val << start) & mask)
                val = val >> len(bf)
                mask = 0
            val = current_value
            reg_ctx = parent_ctx
            reg_node = parent_node

        endianness = "big" if reg_ctx.isBigEndian() else "little"
        val = val.to_bytes(reg_ctx.getSize(), endianness)
        exec_in_dispatch_thread(reg_node.write_register, val)

    add_function_metadata('rwr', 'Register write', 'registers', 'Target')

    def locals(self, *args, name=None, val=None):
        """
locals:
    Get or set the value of a local variable.

Prototype:
    target.locals(*args,  name = <var_name>, val = <var_value>)

Optional Arguments:
    name = <var_name>
        Variable for which value is to be get/set.
    val = <exp_value>
        Specified value for the variable.

Options:
    --defs (-d)
        Return the variable definitions like address, type, size
        and RW flags.
    --dict (-di)
        Return the result in Tcl dict format, with variable names as
        dict keys and variable values as dict values. For complex data
        like structures, names are in the form of parent.child.

Returns:
    Depends on options used.
    Variable value(s)
        When no option is used.
    Variable definition(s)
        When --defs option is used.

Examples:
    target.locals('--defs')
        Return definitions of all the local variables in the current
        stack frame.

Interactive mode examples:
    locals
    locals -defs
        """
        parser = argparse.ArgumentParser(description='Options for locals function')
        parser.add_argument('-d', '--defs', action='store_true', help='Return variable defintions')
        parser.add_argument('--dict', action='store_true', help='Return result in dict format')
        parser.add_argument('name', nargs='?', help='Variable name')
        parser.add_argument('val', nargs='?', help='Variable value')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.name is not None:
            name = parsed_args.name
        if parsed_args.val is not None:
            if '.' in parsed_args.val:
                val = float(parsed_args.val)
            else:
                val = int(parsed_args.val)
        defs = 1 if parsed_args.defs else 0
        dict = 1 if parsed_args.dict else 0
        options = {'name': name, 'value': val, 'defs': defs, 'dict': dict}
        exprs = {}
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None
        endianness = 'little' if node.mem_context_data.isBigEndian() is False else 'big'
        parent = node

        chan = self.__get_current_channel()
        expr_table = self.session._expr_table
        if expr_table.get(chan, None) is None:
            expr_table.update({chan: {node.id: {}}})
        else:
            if expr_table.get(chan).get(node.id, None) is None:
                expr_table[chan].update({node.id: {}})

        # Get expression children for current node context
        var_node = parent.get_local_variables_node()
        exp_children = exec_as_runnable(self.__get_expression_children, var_node)

        if exp_children is not None:
            for ctx, node in exp_children.items():
                self.__get_variable_expressions(node, exprs)

            for exp, exp_data in exprs.items():
                value = exec_in_dispatch_thread(node.info.get_node(exp).evaluate)
                exp_data.update({'Value': value})
            result = self.__process_expressions(exprs, endianness, True, options)
            if result is not None:
                print(result)

    add_function_metadata('locals', 'Get or set the value of a local variable', 'variables', 'Target')

    def print(self, *args, expr=None, val=None):
        """
print:
    Get or set the value of an expression.
Prototype:
    target.print(*args, expr = <expression>, val = <exp_value>)
Optional Arguments:
    expr = <expression>
        Expression for which value is to be get/set.
    val = <exp_value>
        Specified value for the expression.
Options:
    --add (-a)
        Add the <expression> to auto expression list. The values or
        definitions of the expressions in auto expression list are
        displayed when expression name is not specified. Frequently
        used expressions should be added to the auto expression list.
    --defs (-d)
        Return the expression definitions like address, type, size
        and RW flags. Not all definitions are available for all the
        expressions. For example, address is available only for
        variables and not when the expression includes an operator.
    --dict
        Return the result in Tcl dict format, with variable names as
        dict keys and variable values as dict values. For complex data
        like structures, names are in the form of parent.child.
    --remove (-r)
        Remove the expression from auto expression list. Only
        expressions previously added to the list through -add option
        can be removed. When the expression name is not specified, all
        the expressions in the auto expression list are removed.
Returns:
    Depends on options used.
    Expression value(s)
        When no option or --add is used.
    Expression definition(s)
        When --defs is used.
    None
        When --remove or --set is used.
Examples:
    target.print('--defs')
        Return the definitions of all the expressions in auto
        expression list.
    target.print(expr='g_int_a', val=9919)
        set global variable g_int_a to 9199
    target.print(expr='g_int_a')
        print global variable g_int_a

Interactive mode examples:
    print -defs
        """
        parser = argparse.ArgumentParser(description='Options for print function')
        parser.add_argument('-d', '--defs', action='store_true', help='Return expression defintions')
        parser.add_argument('--dict', action='store_true', help='Return result in dict format')
        parser.add_argument('-a', '--add', action='store_true', help='Add expression to auto list')
        parser.add_argument('-r', '--remove', action='store_true', help='Remove expression from auto list')
        parser.add_argument('expr', nargs='?', help='Expression name')
        parser.add_argument('val', nargs='?', help='Expression value')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.expr is not None:
            if expr is not None:
                raise TypeError(f"Conflicting args: Specify expression either as positional arg or keyword arg")
            expr = parsed_args.expr

        if parsed_args.val is not None:
            if val is not None:
                raise TypeError(f"Conflicting args: Specify value either as positional arg or keyword arg")
            val = parsed_args.val

        defs = 1 if parsed_args.defs else 0
        dict = 1 if parsed_args.dict else 0
        add = 1 if parsed_args.add else 0
        remove = 1 if parsed_args.remove else 0
        options = {'name': expr, 'value': val, 'defs': defs, 'dict': dict, 'add': add, 'remove': remove}

        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        endianness = 'little' if node.mem_context_data.isBigEndian() is False else 'big'
        chan = self.__get_current_channel()
        expr_table = self.session._expr_table
        if expr_table.get(chan, None) is None:
            expr_table.update({chan: {node.id: {}}})
        else:
            if expr_table.get(chan).get(node.id, None) is None:
                expr_table[chan].update({node.id: {}})

        in_exprs = []
        expr_list = self.session._expr_list

        if expr_list.get(chan, None):
            if expr_list.get(chan).get(node.id, None):
                in_exprs = expr_list.get(chan).get(node.id)

        if expr == None:
            if len(in_exprs) == 0 or add != 0:
                raise Exception("Specify an expression") from None
            if defs + remove > 1:
                raise Exception("Conflicting options specified, use only one of --defs(-d), or --remove(-r)") from None

            if remove:
                expr_list.update({chan: {node.id: {}}})
                options.update({'scope': 'auto_expr'})
                return self.__dispose_exprs(expr_list, options)
        else:
            if defs + add + remove > 1:
                raise Exception(
                    "Conflicting options specified, use only one of --add(-a), --defs(-d), --remove(-r)") from None

            if remove:
                if expr not in in_exprs:
                    raise Exception(f"Unknown expression {expr}") from None
                in_exprs.remove(expr)
                expr_list.update({chan: {node.id: in_exprs}})
                return

            if add and expr not in in_exprs:
                in_exprs.append(expr)

        expr_list.update({chan: {node.id: in_exprs}})

        ids = []
        if expr is None:
            for id in in_exprs:
                if id not in ids:
                    ids.append(id)
        else:
            ids.append(expr)

        exprs = {}
        for id in ids:
            expr_table = self.session._expr_table
            node = self.__get_current_node()

            if expr_table.get(chan).get(node.id).get(id, None) is None:
                empty_node = TcfNodeExpression(node, None, None)
                e = exec_in_dispatch_thread(empty_node.create, id)
                expr_id = e.getID()
                n = TcfNodeExpression(node, expr_id, None)
                node.info.update_nodes({expr_id: n})
                expr_table[chan][node.id].update({id: {'data': e.getProperties()}})
            else:
                expr_id = expr_table[chan][node.id][id]['data']['ID']
                if expr_id in node.info.get_nodes().keys():
                    n = node.info.get_node(expr_id)
            self.__get_expressions(n, exprs)

        for exp, exp_data in exprs.items():
            value = exec_in_dispatch_thread(node.info.get_node(exp).evaluate)
            exp_data.update({'Value': value})

        result = self.__process_expressions(exprs, endianness, False, options)
        if result is not None:
            print(result)

    add_function_metadata('print', 'Get or set the value of an expression', 'runcontrol', 'Target')

    def readjtaguart(self, *args, **kwargs):
        """
readjtaguart:
    Start/Stop reading from Jtag Uart..
Prototype:
    target.readjtaguart(*args, *kwargs)
Optional Arguments:
    kwargs
        file = <handle>
            File handle to which the data should be redirected.
        mode = <open_mode>
            File open mode.
Options:
    --stop (-s)
        Stop reading the Jtag Uart output.
Returns:
    None if successful, else exception.
Examples:
    target.readjtaguart()
        Start reading from the Jtag Uart and print the output on
        stdout.
    target.readjtaguart('--stop')
        Stop reading from the Jtag Uart.

Interactive mode examples:
    readjtaguart
    readjtaguart -stop
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='Jtag terminal options')
        parser.add_argument('-s', '--stop', action='store_true', help='Stop the terminal')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        ctx = self.__select_target()

        if parsed_args.stop is True:
            self.__stop_jtag_uart(ctx, terminal=0)
            return

        if ctx not in self.session.stream_table.keys():
            self.session.stream_table[ctx] = {}
            self.session.stream_table[ctx]['ctx'] = ctx

        ctx_stream_table = self.session.stream_table[ctx]
        if 'connected' in ctx_stream_table.keys() and ctx_stream_table['connected'] == 1:
            raise Exception('Jtag Uart connection already exists') from None
        if 'ext_socket' in ctx_stream_table and ctx_stream_table['ext_socket'] == 1:
            port = self.session.stream_table['meta']['port']
            raise Exception(f'Jtag Uart connection already exists on socket port: {port}.') from None
        mode = 'a'
        if 'mode' in kwargs:
            mode = kwargs.pop("mode")
            if mode not in ('a', 'w'):
                raise Exception("Invalid file open mode, must be 'a' or 'w'") from None
        ctx_stream_table['handle'] = open(kwargs.pop('file'), mode) if 'file' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        if 'CPUType' in rc and rc['CPUType'] == 'MicroBlaze' and 'ParentID' in rc:
            node = node.info.get_node(rc['ParentID'])
            rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        if 'UART' not in rc:
            raise Exception('Target doesn\'t support Jtag Uart.') from None
        ctx_stream_table['TXStreamID'] = rc['UART']['TXStreamID']
        exec_in_dispatch_thread(streams_connect, self, ctx_stream_table['TXStreamID'])
        ctx_stream_table['connected'] = ctx_stream_table['readjtaguart_cmd'] = 1
        protocol.invokeAndWait(streams_read, self, ctx_stream_table['TXStreamID'], self.__stream_reader_callback)

    add_function_metadata('readjtaguart', 'Start/Stop reading from Jtag Uart', 'streams', 'Target')

    def jtagterminal(self, *args):
        """
jtagterminal:
    Start/Stop a Jtag based hyper-terminal to communicate with
    ARM DCC or MDM UART interface.
Prototype:
    target.jtagterminal(*args)
Options:
    --stop (-s)
        Stop the Jtag Uart terminal.
    --socket (-so)
        Return the socket port number, instead of starting the terminal.
        External terminal programs can be used to connect to this port.
Returns:
    Socket port number.
Examples:
    target.jtagterminal('--socket')

Interactive mode examples:
    jtagterminal
    jtagterminal -socket
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f'Invalid target, select a target using targets function') from None

        parser = argparse.ArgumentParser(description='Jtag terminal options')
        parser.add_argument('-s', '--stop', action='store_true', help='Stop the terminal')
        parser.add_argument('--socket', action='store_true', help='Return socket instead of opening terminal')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if 'meta' not in self.session.stream_table.keys():
            self.session.stream_table['meta'] = dict()
            self.session.stream_table['meta']['server'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.session.stream_table['meta']['server'].bind(('localhost', 0))
            self.session.stream_table['meta']['port'] = self.session.stream_table['meta']['server'].getsockname()[1]
            self.session.stream_table['meta']['server'].listen(10)

        ctx = self.__select_target()
        if parsed_args.stop is True:
            self.__stop_jtag_uart(ctx)
            return

        if ctx not in self.session.stream_table.keys():
            self.session.stream_table[ctx] = dict()
            self.session.stream_table[ctx]['ctx'] = ctx

        ctx_stream_table = self.session.stream_table[ctx]
        stream_table = self.session.stream_table['meta']

        port = stream_table['port']
        if 'connected' in ctx_stream_table.keys() and ctx_stream_table['connected'] == 1:
            raise Exception('Jtag Uart connection already exists') from None
        if 'ext_socket' in ctx_stream_table and ctx_stream_table['ext_socket'] == 1:
            raise Exception(f'Jtag Uart connection already exists on socket port: {port}') from None
        rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        if rc['CPUType'] == 'MicroBlaze' and 'ParentID' in rc:
            node = node.info.get_node(rc['ParentID'])
            rc = exec_as_runnable(self.__get_run_ctx, node).getProperties()
        if 'UART' not in rc:
            raise Exception('Target doesn\'t support Jtag Uart.') from None

        ctx_stream_table['TXStreamID'] = rc['UART']['TXStreamID']
        ctx_stream_table['RXStreamID'] = rc['UART']['RXStreamID']
        exec_in_dispatch_thread(streams_connect, self, ctx_stream_table['TXStreamID'])
        exec_in_dispatch_thread(streams_connect, self, ctx_stream_table['RXStreamID'])

        if parsed_args.socket is False:
            ctx_stream_table['ext_socket'] = 0
            current_os = platform.system()
            terminal_script = os.path.dirname(os.path.realpath(__file__)) + '/jtag_uart_terminal.py'
            if current_os == "Linux":
                Popen([f'xterm -e python {terminal_script} {port} 1'], shell=True)
            elif current_os == "Windows":
                Popen([f'cmd /c start python {terminal_script} {port} 1'], shell=True)
            else:
                raise Exception(f"ERROR: JTAG-based Hyperterminal not supported on {current_os} platform") from None
        else:
            ctx_stream_table['ext_socket'] = 1

        recv_thread = "stream_sock_thread_" + str(self.session.get_context_target_map()[ctx]) + "_" + \
                      str(ctx_stream_table['ext_socket'])
        threading.Thread(target=self.__stream_sock_thread, name=recv_thread,
                         args=(ctx_stream_table, stream_table,)).start()
        return port

    add_function_metadata('jtagterminal', 'Start/Stop Jtag based hyper-terminal', 'streams', 'Target')

    def rst(self, *args, type: str = 'system', **kwargs):
        """
rst:
    Reset the active target.

Prototype:
    target.rst(type = <reset_type>, *args, *kwargs)

Optional Arguments:
    type = <reset_type>
        Type must be one of 'cores', 'dap', 'por', 'proc', 'processor',
        'ps', 'srst', 'system', 'pmc-por', 'pmc-srst', 'ps-por',
        'ps-srst', 'pl-por', 'pl-srst'.

        pmc-por, pmc-srst, ps-por, ps-srst, pl-por, and pl-srst are
        supported only for Versal devices. For these rst types,
        the following bits are asserted in CRP->RST_PS register.
        PMC_POR - bit7, PS_POR - bit6, PL_POR - bit5, PMC_SRST - bit3,
        PS_SRST - bit2, PL_SRST - bit1.
    kwargs
        isa
            Set ISA to <isa-name>. Supported isa-names are ARM/A32,
            A64, and Thumb. This option is supported with APU, RPU, A9,
            A53, and A72 targets. If this option is not specified, the
            current configuration is not changed.
        endianness
            Set the data endianness to <value>. The following values
            are supported:
            le - Little endian;
            be - Big endian.
            This option is supported with APU, RPU, A9, A53, and A72
            targets. If this option is not specified, the current
            configuration is not changed.
        code_endianness
            Set the instruction endianness to <value>. The following
            values are supported:
            le - Little endian;
            be - Big endian.
            This option is supported with RPU targets of zynqmp and
            versal. If this option is not specified, the current
            configuration is not changed.

Options:
    --stop (-s)
        Suspend cores after reset. If this option is not specified,
        debugger choses the default action, which is to resume the
        cores for -system, and suspend the cores for -processor, and
        -cores. This option is only supported with -processor, -cores,
         and -system options.
    --start (-r)
        Resume the cores after reset. See description of -stop option
        for more details.
    --clear_registers (-c)
        Clear CPU registers after a reset is triggered. This option
        is useful while triggering a reset after the device is powered
        up. Otherwise, debugger can end up reading invalid system
        addresses based on the register contents. Clearing the
        registers will avoid unpredictable behavior.
        This option is supported for ARM targets, when used with
        '-processor' and '-cores'.
    --skip-subsystem-activation (--sk)

Returns:
    None if successful, else exception.

Examples:
    target.rst()
    target.rst('--stop', endianness='le', type='cores')

Interactive mode examples:
    rst
    rst -stop -endianness le -type cores
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f'Target doesn\'t exist.') from None

        parser = argparse.ArgumentParser(description='Reset arguments')
        parser.add_argument('-r', '--start', action='store_true', help='Resume cores after reset')
        parser.add_argument('-s', '--stop', action='store_true', help='Suspend cores after reset')
        parser.add_argument('-c', '--clear_registers', action='store_true', help='Clear core registers after reset')
        parser.add_argument('--skip_subsystem_activation', action='store_true',
                            help='Do not activate default subsystem in Versal')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if type not in ('cores', 'dap', 'por', 'proc', 'processor', 'ps', 'srst', 'system', 'pmc-por', 'pmc-srst',
                        'ps-por', 'ps-srst', 'pl-por', 'pl-srst'):
            raise Exception("Invalid reset type: must one of 'cores', 'dap', 'por', 'proc', 'processor', \n\
                            \r'ps', 'srst', 'system', 'pmc-por', 'pmc-srst', 'ps-por', 'ps-srst', 'pl-por', \n\
                            \r'pl-srst'") from None

        start = 1 if parsed_args.start is True else 0
        stop = 1 if parsed_args.stop is True else 0
        endianness = kwargs.pop('endianness') if 'endianness' in kwargs else None
        code_endianness = kwargs.pop('code_endianness') if 'code_endianness' in kwargs else None
        isa = kwargs.pop('isa') if 'isa' in kwargs else None
        jtag_timeout = kwargs.pop('jtag_timeout') if 'jtag_timeout' in kwargs else 30000
        timeout = kwargs.pop('timeout') if 'timeout' in kwargs else 3000
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if start + stop > 1:
            raise Exception('conflicting options, use only one of -start, or -stop') from None

        if type in ('dap', 'srst', 'por', 'ps'):
            if start + stop:
                raise Exception('WARNING: -start and -stop are only supported with -processor, -cores, or -system') \
                    from None
            if endianness is not None or code_endianness is not None or isa is not None:
                raise Exception('WARNING: -endianness, -code-endianness, and -isa are only supported with -processor, '
                                '-cores, or -system') from None

        tcf_reset = TcfReset(self.session)
        tcf_jtag = TcfJtag(self.session)

        if type in ('srst', 'por'):
            rc = exec_as_runnable(get_cache_data, node.get_run_context()).getProperties()
            if 'JtagGroup' in rc:
                jtag_group_node = node.info.get_node(rc['JtagGroup'])
                rc = exec_as_runnable(get_cache_data, jtag_group_node.get_run_context()).getProperties()
            if 'JtagNodeID' in rc:
                jtag_node_id = rc['JtagNodeID']
                jtag_node = node.info.get_nodes()[jtag_node_id]
                jc = exec_as_runnable(get_cache_data, jtag_node.get_context()).props
                while 'ParentID' in jc and jc['ParentID'] != '':
                    jtag_node = node.info.get_node(jc['ParentID'])
                    jc = exec_as_runnable(get_cache_data, jtag_node.get_context()).props
                cap = exec_as_runnable(get_cache_data, jtag_node.get_capabilities())[0]
                pins = cap['Pins'] if 'Pins' in cap else {}
                if type == 'srst':
                    if 'SRST' not in pins:
                        raise Exception('Jtag scan chain does not support SRST pin') from None
                    cmds = [['setPin', 'SRST', 0], ['delay', 10000], ['setPin', 'SRST', 1]]
                else:
                    if 'POR' not in pins:
                        raise Exception('Jtag scan chain does not support POR pin') from None
                    cmds = [['setPin', 'POR', 0], ['delay', 10000], ['setPin', 'POR', 1]]
                exec_in_dispatch_thread(tcf_jtag.jtag_sequence, jtag_node.id, {}, cmds, bytearray())

        elif type == 'ps':
            mc = exec_as_runnable(get_cache_data, node.get_memory_context())
            if mc is None or ('Name' in mc._props and mc._props['Name'] != 'MicroBlaze PMU'):
                raise Exception('ps reset not suported for target') from None
            try:
                # Block FPD=>PL and LPD=>PL interfaces with the help of AIB in PS
                self.mwr(0xffd80600, '-f', words=0xF)
                # Wait until an ACK or timeout. There is a possibility of glitch
                # on AIB acknowledgement to PMU. So, re-confirm the ACK
                for i in range(0, 2):
                    val = self.mrd(0xffd80604, '-f', '-v')[0]
                    count = 0
                    while (val & 0xF) != 0xF and count < 1000:
                        val = self.mrd(0xffd80604, '-f', '-v')[0]
                        time.sleep(0.001)
                        count += 1
                # On Silicon 1.0, bypass RPLL befor triggering the PS reset
                val = self.mrd(0xffca0044, '-f', '-v')[0]
                if val == 0:
                    l_val = self.mrd(0xff5e0030, '-f', '-v')[0]
                    l_val = (l_val & (~0x8)) | 0x8
                    self.mwr(0xff5e0030, '-f', words=l_val)
                # Block the propagation of the PROG signal to the PL
                l_val = self.mrd(0xffd80004, '-f', '-v')[0]
                l_val = l_val & (~0x2)
                self.mwr(0xffd80004, '-f', words=l_val)
                # Gate the propagation to PL
                l_val = self.mrd(0xffd80004, '-f', '-v')[0]
                l_val = (l_val & (~0x1)) | 0x1
                self.mwr(0xffd80004, '-f', words=l_val)
                # Initiate PS-only reset by writing to PMU-local register
                l_val = self.mrd(0xffd80608, '-f', '-v')[0]
                l_val = (l_val & (~0x400)) | 0x400
                self.mwr(0xffd80608, '-f', words=l_val)
            except Exception as e:
                raise Exception('cannot reset PS.\n', e) from None
        else:
            active_subsystem = 0
            rst_type = ''
            if type == 'processor':
                rst_type = 'core'
                stop = 1
                active_subsystem = 1
            elif type == 'cores':
                rst_type = 'cpu'
                stop = 1
                active_subsystem = 1
            elif type == 'dap':
                rst_type = 'dap'
            else:
                rst_type = 'system'
                if type != 'system':
                    rst_type = type

            rc = exec_as_runnable(get_cache_data, node.get_run_context()).getProperties()
            if rst_type == 'pmc-por' and rc['Name'] == 'DPC':
                try:
                    self.mwr(0xf126031c, words=0x80)
                except Exception as e:
                    raise Exception(f'Memory write error at 0xF126031C. Connection timed out. Error:', e) from None

            capabilities = exec_in_dispatch_thread(tcf_reset.rst_capabilities, '')[0]
            rst_types = capabilities['Types']
            if rst_type not in rst_types:
                raise Exception(f'{rst_type} not supported for target. supported reset types : {rst_types}') from None

            jc = None
            jtag_node_id = ''
            if 'JtagGroup' in rc:
                jtag_group_node = node.info.get_nodes()[rc['JtagGroup']]
                rc = exec_as_runnable(get_cache_data, jtag_group_node.get_run_context()).getProperties()
            if 'JtagNodeID' in rc:
                jtag_node_id = rc['JtagNodeID']
                jtag_node = node.info.get_nodes()[jtag_node_id]
                jc = exec_as_runnable(get_cache_data, jtag_node.get_context()).props
            if jc is None:
                raise Exception(f'Invalid jtag context {jtag_node_id}')

            argvar = dict()
            if stop == 1:
                argvar.update({'suspend': True})
            elif start == 1:
                argvar.update({'suspend': False})
            if endianness == 'le' or endianness == 'be':
                if 'Options' in capabilities and 'endianness' not in capabilities['Options']:
                    raise Exception('endianness option is not supported by the current version of hw_server') from None
                argvar.update({'endianness': endianness})
            elif endianness is not None:
                raise Exception(f'unsuported endianness {endianness}: must be le, or be') from None
            if code_endianness == 'le' or code_endianness == 'be':
                if 'Options' in capabilities and 'code-endianness' not in capabilities['Options']:
                    raise Exception('code-endianness option is not supported by the current version of hw_server') \
                        from None
                argvar.update({'code-endianness': code_endianness})
            elif code_endianness is not None:
                raise Exception(f'unsuported code-endianness {code_endianness}: must be le, or be') from None

            if parsed_args.clear_registers is True:
                if type not in ('processor', 'cores'):
                    raise Exception('--clear_registers is supported only with \'processor\' and \'cores\'') from None
                if 'Options' in capabilities and 'clear-registers' not in capabilities['Options']:
                    raise Exception('--clear_registers is not supported by the current version of hw_server') from None
                argvar.update({'clear-registers': True})
            else:
                # TODO : level
                if type in ('processor', 'cores') and self.session.reset_warnings == 1:
                    found = 0
                    rc = exec_as_runnable(get_cache_data, node.get_run_context()).getProperties()
                    if 'CPUType' in rc and rc['CPUType'] == 'ARM' and 'ARMType' in rc and rc['ARMType'] != 'Cortex-A9':
                        found = 1
                    if 'IsContainer' in rc and rc['IsContainer'] == 1:
                        children = exec_as_runnable(get_cache_data, node.get_children()).get('children')
                        if children is not None:
                            for child, child_node in children.items():
                                rc = exec_as_runnable(get_cache_data, child_node.get_run_context()).getProperties()
                                if 'CPUType' in rc and rc['CPUType'] == 'ARM' and \
                                        'ARMType' in rc and rc['ARMType'] != 'Cortex-A9':
                                    found = 1
                                    break
                    if found == 0:
                        self.session.reset_warnings = 0
                        print('WARNING: If the reset is being triggered after powering on the device,\n'
                              '\r         write bootloop at reset vector address (0xffff0000), or use\n'
                              '\r         -clear-registers option, to avoid unpredictable behavior.\n'
                              '\r         Further warnings will be suppressed')

            if isa is not None:
                if isa in ('ARM', 'A32', 'A64', 'Thumb'):
                    if 'Options' in capabilities and 'isa' not in capabilities['Options']:
                        raise Exception('isa option is not supported by the current version of hw_server') from None
                    argvar.update({'isa': isa})
                else:
                    raise Exception(f'unsupported isa {isa}: must be ARM, A32, A64, or Thumb') from None

            if active_subsystem and parsed_args.skip_subsystem_activation is False:
                is_arm = 0
                rc = exec_as_runnable(get_cache_data, node.get_run_context()).getProperties()
                if 'CPUType' in rc and rc['CPUType'] == 'ARM':
                    is_arm = 1
                if 'IsContainer' in rc and rc['IsContainer'] == 1:
                    child_data = exec_as_runnable(get_cache_data, node.get_children())
                    children = child_data['children'] if 'children' in child_data else None
                    if children is not None:
                        for child, child_node in children.items():
                            rc = exec_as_runnable(get_cache_data, child_node.get_run_context()).getProperties()
                            if 'CPUType' in rc and rc['CPUType'] == 'ARM':
                                is_arm = 1
                                break
                if is_arm == 1:
                    while 'ParentID' in rc and rc['ParentID'] != '':
                        parent_node = node.info.get_node(rc['ParentID'])
                        rc = exec_as_runnable(get_cache_data, parent_node.get_run_context()).getProperties()
                        if rc['Name'].startswith('Versal'):
                            # Activate default subsystem as its not activated by PLM if the elf is not part of PDI
                            # Otherwise, users will see run-time errors
                            if self.session.subsystem_activate_warnings == 1:
                                self.session.subsystem_activate_warnings = 0
                                print('WARNING: Default system will be activated before triggering reset.\n'
                                      '\r         Use skip-activate-subsystem to skip this.\n'
                                      '\r         Further warnings will be suppressed')
                            err = ''
                            ret = None
                            try:
                                ret = self.session.pmc('generic', [0x10241, 0x1c000000], response_size=1)
                            except Exception as e:
                                err = e.args[0].split('Exception: ')[1]
                            if ret != 0x0 and ret != 0x01070000:
                                print("WARNING: Cannot activate default subsystem. This may cause runtime issues if \n"
                                      "\r         PM API is used.")
                                if ret is not None:
                                    print(f"         PLM status: {ret}")
                                if self.session.ipi_channel_mask_warnings == 1:
                                    self.session.ipi_channel_mask_warnings = 0
                                    if err.startswith("timeout waiting for request to be acknowledged"):
                                        print(
                                            '         Check if IPI channel 5 is enabled in Vivado Design. This is\n'
                                            '\r         needed for activating default subsystem. Further warnings \n'
                                            '\r         will be suppressed')
                                    elif err.startswith('AXI AP transaction error'):
                                        print(
                                            '         Cannot access IPI registers. Check if IPI channel 5 in Vivado\n'
                                            '\r         design is configured to allow debugger access. This is needed\n'
                                            '\r         for activating default subsystem. Further warnings will be \n'
                                            '\r         suppressed.')
                                    elif err != '':
                                        print(f'{err}')

            exec_in_dispatch_thread(tcf_reset.rst_cmd, node.id, rst_type, argvar)

            # Wait for JTAG device to become active incase reset caused it to be temporarily disabled.
            if 'ID' in jc:
                jtagid = jc['ID']
                jtag_node = node.info.get_node(jtagid)
                start = round(time.time() * 1000)
                end = start
                while end - start < jtag_timeout:
                    jc = exec_as_runnable(get_cache_data, jtag_node.get_context()).props
                    if 'isActive' in jc and jc['isActive']:
                        break
                    time.sleep(0.01)
                    end = round(time.time() * 1000)
            if stop == 1:
                self.__wait_for_run_state(node, 1, timeout)

    add_function_metadata('rst', 'Target reset', 'reset', 'Target')

    def mb_drrd(self, *args, **kwargs):
        """
mb_drrd:
    Read from MicroBlaze Debug Register.

Prototype:
    target.mb_drrd(*args, **kwargs)

Options:
    args:
        command - 8-bit MDM command to access a debug register.
        bitlen - register width
    kwargs:
        target_id = <id>
            Specify a target id representing the MicroBlaze debug module or
            MicroBlaze instance to access.  If this option is not used and
            '-user' is not specified, the current target is used.

        user = <bscan number>
            Specify user bscan port number.

        which = <instance>
            Specify MicroBlaze instance number.

Returns:
    Register value, if successful, else exception is raised.

Examples:
    target.mb_drrd(3, 28)

Interactive mode examples:
    mb_drrd 3 28
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mb_drrd')
        parser.add_argument('-c', '--current_jtag_target', action='store_true', help='Use current JTAG target')
        parser.add_argument('command', nargs='?', type=int, help='command')
        parser.add_argument('bitlen', nargs='?', type=int, help='bitlen')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        target_id = check_int(kwargs.pop('target_id')) if 'target_id' in kwargs else None
        user = check_int(kwargs.pop('user')) if 'user' in kwargs else None
        which = check_int(kwargs.pop('which')) if 'which' in kwargs else None
        command = check_int(kwargs.pop("command")) if 'command' in kwargs else None
        bitlen = check_int(kwargs.pop("bitlen")) if 'bitlen' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None
        current_jtag_target = 1 if parsed_args.current_jtag_target is True else 0

        if parsed_args.command is not None:
            if command is not None:
                raise Exception("Conflicting args: Specify command either as positional arg or keyword arg")
            command = parsed_args.command
        if parsed_args.bitlen is not None:
            if bitlen is not None:
                raise Exception("Conflicting args: Specify bitlen either as positional arg or keyword arg")
            bitlen = parsed_args.bitlen

        check_int(command)
        check_int(bitlen)
        jtag_tgt = None
        jtag_tgt_ctx_map = self.session.model.launch_node.get_jtag_context_target_map()
        tgt_ctx_map = self.session.model.launch_node.get_target_context_map()
        if current_jtag_target == 1:
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            debug_ports = 8
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'current_jtag_target\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'
            if which is None:
                which = 0
            if which < 0 or which >= debug_ports:
                raise Exception('invalid Microblaze instance specified using which parameter') from None
        elif user is not None or which is not None:
            debug_ports = 8
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'user\' or \'which\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'
            if which is None:
                which = 0
            if which < 0 or which >= debug_ports:
                raise Exception('invalid Microblaze instance specified using which parameter') from None
            ctx = self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
            else:
                raise Exception('non JTAG target not supported') from None
        else:
            ctx = tgt_ctx_map[target_id] if target_id is not None else self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
                if 'JtagChain' in props:
                    user = props['JtagChain'].lower()
                else:
                    raise Exception('target must be a MicroBlaze instance') from None
            else:
                raise Exception('non JTAG target not supported') from None

            if 'MDMConfig' not in props or ((props['MDMConfig'] >> 24) & 0xFF) != 0x42:
                raise Exception('unknown MDM Configuration') from None
            debug_ports = (props['MDMConfig'] >> 8) & 0xFF
            if 'MBCore' in props and 0 <= props['MBCore'] < debug_ports:
                which = props['MBCore']
            else:
                raise Exception('target must be a MicroBlaze instance') from None
            if debug_ports < 8:
                debug_ports = 8

        if jtag_tgt is None:
            raise Exception("Select jtag target using jtag_targets command.")
        jt = self.session.jtag_targets(jtag_tgt)
        jseq = jt.sequence()
        jseq.irshift(state='IRUPDATE', register='bypass')
        jseq.irshift(state='IDLE', register=user)
        jseq.drshift(state="DRUPDATE", bit_len=4, data=1)
        jseq.drshift(state="DRUPDATE", bit_len=8, data=0x0D)
        jseq.drshift(state="DRUPDATE", bit_len=debug_ports, data=1 << which)
        jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
        jseq.drshift(capture=True, state="IDLE", tdi=0, bit_len=bitlen)
        data = jseq.run('--bits')
        jseq.clear()
        del jseq
        return "{0:#0{1}x}".format(int('0b' + data, 2), int(bitlen / 4) + 2)

    add_function_metadata('mb_drrd', 'Read from MicroBlaze Debug Register', 'miscellaneous', 'Target')

    def mdm_drrd(self, *args, **kwargs):
        """
mdm_drrd:
    Read from MDM debug register.

Prototype:
    target.mb_drrd(*args, **kwargs)

Options:
    args:
        command - 8-bit MDM command to access a debug register.
        bitlen - register width
    kwargs:
        target_id = <id>
            Specify a target id representing the MicroBlaze debug module or
            MicroBlaze instance to access.  If this option is not used and
            '-user' is not specified, the current target is used.

        user = <bscan number>
            Specify user bscan port number.

Returns:
    Register value, if successful, else exception is raised.

Examples:
    target.mdm_drrd(0, 32)

Interactive mode examples:
    mdm_drrd 0 32
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mb_drrd')
        parser.add_argument('-c', '--current_jtag_target', action='store_true', help='Use current JTAG target')
        parser.add_argument('command', nargs='?', type=int, help='command')
        parser.add_argument('bitlen', nargs='?', type=int, help='bitlen')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        target_id = check_int(kwargs.pop('target_id')) if 'target_id' in kwargs else None
        user = check_int(kwargs.pop('user')) if 'user' in kwargs else None
        command = check_int(kwargs.pop("command")) if 'command' in kwargs else None
        bitlen = check_int(kwargs.pop("bitlen")) if 'bitlen' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None
        current_jtag_target = 1 if parsed_args.current_jtag_target is True else 0

        if parsed_args.command is not None:
            if command is not None:
                raise Exception("Conflicting args: Specify command either as positional arg or keyword arg")
            command = parsed_args.command
        if parsed_args.bitlen is not None:
            if bitlen is not None:
                raise Exception("Conflicting args: Specify bitlen either as positional arg or keyword arg")
            bitlen = parsed_args.bitlen

        check_int(command)
        check_int(bitlen)
        jtag_tgt = None
        jtag_tgt_ctx_map = self.session.model.launch_node.get_jtag_context_target_map()
        tgt_ctx_map = self.session.model.launch_node.get_target_context_map()
        if current_jtag_target == 1:
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'current_jtag_target\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'

        elif user is not None:
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'user\' or \'which\'') from None
            user = f'user{user}'
            ctx = self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
            else:
                raise Exception('non JTAG target not supported.') from None
        else:
            ctx = tgt_ctx_map[target_id] if target_id is not None else self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
                if 'JtagChain' in props:
                    user = props['JtagChain'].lower()
                else:
                    raise Exception('target must be a MicroBlaze instance') from None
            else:
                raise Exception('non JTAG target not supported') from None

        if jtag_tgt is None:
            raise Exception("Select jtag target using jtag_targets command.")
        jt = self.session.jtag_targets(jtag_tgt)
        jseq = jt.sequence()
        jseq.irshift(state='IDLE', register='bypass')
        jseq.irshift(state='IDLE', register=user)
        jseq.drshift(state="IDLE", bit_len=4, data=1)
        jseq.drshift(state="IDLE", bit_len=8, data=command)
        jseq.drshift(capture=True, state="IDLE", tdi=0, bit_len=bitlen)
        data = jseq.run('--bits')
        jseq.clear()
        del jseq
        return "{0:#0{1}x}".format(int('0b' + data[::-1], 2), int(bitlen / 4) + 2)

    add_function_metadata('mdm_drrd', 'Read from MDM debug register', 'miscellaneous', 'Target')

    def mdm_drwr(self, *args, **kwargs):
        """
mdm_drwr:
    Write to MDM debug register.

Prototype:
    target.mdm_drwr(*args, **kwargs)

Options:
    args:
        command - 8-bit MDM command to access a debug register.
        data - register value
        bitlen - register width
    kwargs:
        target_id = <id>
            Specify a target id representing the MicroBlaze debug module or
            MicroBlaze instance to access.  If this option is not used and
            '-user' is not specified, the current target is used.

        user = <bscan number>
            Specify user bscan port number.

Returns:
    None if successful, else exception is raised.

Examples:
    target.mdm_drwr(8, 0x40, 8)
    target.mdm_drwr('-c', 8, 0x40, 8)
    target.mdm_drwr('-c', command = 8, data = 0x40, bitlen = 8)

Interactive mode examples:
    mdm_drwr 8 40 8
    mdm_drwr 8 40 8 -current_jtag_target
        (options must be specified at the end after arguments)
    mdm_drwr -current_jtag_target -command 8 -data 0x40 -bitlen 8
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mb_drrd')
        parser.add_argument('-c', '--current_jtag_target', action='store_true', help='Use current JTAG target')
        parser.add_argument('command', nargs='?', type=int, help='command')
        parser.add_argument('data', nargs='?', type=int, help='data')
        parser.add_argument('bitlen', nargs='?', type=int, help='bitlen')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        target_id = check_int(kwargs.pop('target_id')) if 'target_id' in kwargs else None
        user = check_int(kwargs.pop('user')) if 'user' in kwargs else None
        command = check_int(kwargs.pop("command")) if 'command' in kwargs else None
        bitlen = check_int(kwargs.pop("bitlen")) if 'bitlen' in kwargs else None
        data = check_int(kwargs.pop("data")) if 'data' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None
        current_jtag_target = 1 if parsed_args.current_jtag_target is True else 0

        if parsed_args.command is not None:
            if command is not None:
                raise Exception("Conflicting args: Specify command either as positional arg or keyword arg")
            command = parsed_args.command
        if parsed_args.bitlen is not None:
            if bitlen is not None:
                raise Exception("Conflicting args: Specify bitlen either as positional arg or keyword arg")
            bitlen = parsed_args.bitlen
        if parsed_args.data is not None:
            if data is not None:
                raise Exception("Conflicting args: Specify data either as positional arg or keyword arg")
            data = parsed_args.data
        check_int(command)
        check_int(bitlen)
        check_int(data)

        jtag_tgt = None
        jtag_tgt_ctx_map = self.session.model.launch_node.get_jtag_context_target_map()
        tgt_ctx_map = self.session.model.launch_node.get_target_context_map()
        if current_jtag_target == 1:
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'current_jtag_target\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'
        elif user is not None:
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'user\' or \'which\'') from None
            user = f'user{user}'
            ctx = self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
            else:
                raise Exception('non JTAG target not supported.') from None
        else:
            ctx = tgt_ctx_map[target_id] if target_id is not None else self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
                if 'JtagChain' in props:
                    user = props['JtagChain'].lower()
                else:
                    raise Exception('target must be a MicroBlaze instance') from None
            else:
                raise Exception('non JTAG target not supported') from None

        if jtag_tgt is None:
            raise Exception("Select jtag target using jtag_targets command.")
        jt = self.session.jtag_targets(jtag_tgt)
        jseq = jt.sequence()
        jseq.irshift(state='IDLE', register='bypass')
        jseq.irshift(state='IDLE', register=user)
        jseq.drshift(state="IDLE", bit_len=4, data=1)
        jseq.drshift(state="IDLE", bit_len=8, data=command)
        jseq.drshift(state="IDLE", bit_len=bitlen, data=data)
        jseq.run()
        jseq.clear()
        del jseq

    add_function_metadata('mdm_drwr', 'Write to MDM debug register', 'miscellaneous', 'Target')

    def mb_drwr(self, *args, **kwargs):
        """
mb_drwr:
    Write to MicroBlaze debug register.

Prototype:
    target.mb_drwr(*args, **kwargs)

Options:
    args:
        command - 8-bit MDM command to access a debug register.
        data - register value
        bitlen - register width
    kwargs:
        target_id = <id>
            Specify a target id representing the MicroBlaze debug module or
            MicroBlaze instance to access.  If this option is not used and
            '-user' is not specified, the current target is used.

        user = <bscan number>
            Specify user bscan port number.

        which = <instance>
            Specify MicroBlaze instance number.
Returns:
    None if successful, else exception is raised.

Examples:
    target.mb_drwr(1, 0x282, 10)

Interactive mode examples:
    mb_drwr 1 0x282 10
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mb_drrd')
        parser.add_argument('-c', '--current_jtag_target', action='store_true', help='Use current JTAG target')
        parser.add_argument('command', nargs='?', type=int, help='command')
        parser.add_argument('data', nargs='?', type=int, help='data')
        parser.add_argument('bitlen', nargs='?', type=int, help='bitlen')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        target_id = check_int(kwargs.pop('target_id')) if 'target_id' in kwargs else None
        user = check_int(kwargs.pop('user')) if 'user' in kwargs else None
        which = check_int(kwargs.pop('which')) if 'which' in kwargs else None
        command = check_int(kwargs.pop("command")) if 'command' in kwargs else None
        bitlen = check_int(kwargs.pop("bitlen")) if 'bitlen' in kwargs else None
        data = check_int(kwargs.pop("data")) if 'data' in kwargs else None

        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None
        current_jtag_target = 1 if parsed_args.current_jtag_target is True else 0

        if parsed_args.command is not None:
            if command is not None:
                raise Exception("Conflicting args: Specify command either as positional arg or keyword arg")
            command = parsed_args.command
        if parsed_args.bitlen is not None:
            if bitlen is not None:
                raise Exception("Conflicting args: Specify bitlen either as positional arg or keyword arg")
            bitlen = parsed_args.bitlen

        if parsed_args.data is not None:
            if data is not None:
                raise Exception("Conflicting args: Specify data either as positional arg or keyword arg")
            data = parsed_args.data
        check_int(command)
        check_int(bitlen)
        check_int(data)
        jtag_tgt = None
        jtag_tgt_ctx_map = self.session.model.launch_node.get_jtag_context_target_map()
        tgt_ctx_map = self.session.model.launch_node.get_target_context_map()
        if current_jtag_target == 1:
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            debug_ports = 8
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'current_jtag_target\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'
            if which is None:
                which = 0
            if which < 0 or which >= debug_ports:
                raise Exception('invalid Microblaze instance specified using which parameter') from None
        elif user is not None or which is not None:
            debug_ports = 8
            if target_id is not None:
                raise Exception('conflicting options specified, target_id cannot be combined with '
                                '\'user\' or \'which\'') from None
            if user is None:
                raise Exception('option user must be specified') from None
            else:
                user = f'user{user}'
            if which is None:
                which = 0
            if which < 0 or which >= debug_ports:
                raise Exception('invalid Microblaze instance specified using which parameter') from None
            ctx = self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
            else:
                raise Exception('non JTAG target not supported') from None
        else:
            ctx = tgt_ctx_map[target_id] if target_id is not None else self.__select_target()
            props = self.__get_target_microblaze_props(ctx)
            if 'JtagNodeID' in props:
                jtag_ctx = props['JtagNodeID']
                jtag_tgt = jtag_tgt_ctx_map[jtag_ctx]
                if 'JtagChain' in props:
                    user = props['JtagChain'].lower()
                else:
                    raise Exception('target must be a MicroBlaze instance') from None
            else:
                raise Exception('non JTAG target not supported') from None

            if 'MDMConfig' not in props or ((props['MDMConfig'] >> 24) & 0xFF) != 0x42:
                raise Exception('unknown MDM Configuration') from None
            debug_ports = (props['MDMConfig'] >> 8) & 0xFF
            if 'MBCore' in props and 0 <= props['MBCore'] < debug_ports:
                which = props['MBCore']
            else:
                raise Exception('target must be a MicroBlaze instance') from None
            if debug_ports < 8:
                debug_ports = 8

        if jtag_tgt is None:
            raise Exception("Select jtag target using jtag_targets command.")
        jt = self.session.jtag_targets(jtag_tgt)
        jseq = jt.sequence()
        jseq.irshift(state='IRUPDATE', register='bypass')
        jseq.irshift(state='IDLE', register=user)
        jseq.drshift(state="DRUPDATE", bit_len=4, data=1)
        jseq.drshift(state="DRUPDATE", bit_len=8, data=0x0D)
        jseq.drshift(state="DRUPDATE", bit_len=debug_ports, data=1 << which)
        jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
        res = bin(data)
        ln = len(res) - 2
        res = res[2:].zfill(bitlen) if ln <= bitlen else res[2:][(ln - bitlen):]
        jseq.drshift(state="IDLE", bit_len=bitlen, data=res)
        jseq.run()
        jseq.clear()
        del jseq

    add_function_metadata('mb_drwr', 'Write to MicroBlaze debug register', 'miscellaneous', 'Target')

    def mbprofile(self, *args, **kwargs):
        """
mbprofile:
    Configure and run the MB profiler, a non-intrusive profiler
    for profiling the application running on MicroBlaze. The output file is
    generated in gmon.out format. The results can be viewed using
    the gprof editor. In case of cycle count, an annotated disassembly
    file is also generated clearly marking the time taken for execution
    of instructions.

Prototype:
    target.mbprofile(self, *args, **kwargs)

Options:
    --count_instr
        Count number of executed instructions.
        By default, the number of clock cycles of executed instructions are counted.

    --cumulate - Cumulative profiling.
        Profiling without clearing the profiling buffers.

    --start
        Enable and start profiling.

    --stop
        Disable/stop profiling.
    kwargs:
        low=<addr>
            Low address of the profiling address range.

        high=<addr>
            High address of the profiling address range.

        freq=<value>
            MicroBlaze clock frequency in Hz.
            Default is 100 MHz.

        out=<filename>
            Output profiling data to file. <filename> Name of the output file for
            writing the profiling data. If the file name is not specified, profiling
            data is written to gmon.out.
Returns:
    Depends on options used.
    low, high, freq, --count-instr, --start, --cumulate
        Returns nothing on successful configuration.
        Error string, in case of error.

    --stop
        Returns nothing, and generates a file.
        Error string, in case of error.

Examples:
    target.mbprofile(low='low', high='high')
    target.mbprofile('--start')
    target.mbprofile('--stop', out="gmon_inst_1.out")

Interactive mode examples:
    mbprofile -low low -high high
    mbprofile -start
    mbprofile -stop -out a.out
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mb_drrd')
        parser.add_argument('-c', '--count_instr', action='store_true', help='count instructions')
        parser.add_argument('-s', '--start', action='store_true', help='enable/start profiling')
        parser.add_argument('-m', '--cumulate', action='store_true', help='cumulative data')
        parser.add_argument('-t', '--stop', action='store_true', help='disable/stop profiling')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        start = 1 if parsed_args.start is True else 0
        stop = 1 if parsed_args.stop is True else 0
        count_instr = 1 if parsed_args.count_instr is True else 0
        cumulate = 1 if parsed_args.cumulate is True else 0

        low = kwargs.pop('low') if 'low' in kwargs else None
        high = kwargs.pop('high') if 'high' in kwargs else None
        freq = check_int(kwargs.pop('freq')) if 'freq' in kwargs else None
        out = kwargs.pop('out') if 'out' in kwargs else 'gmon.out'
        if kwargs:
            raise TypeError(f"Invalid args: {kwargs.keys()}") from None
        mb_profile_config = self.session.mb_profile_config
        if self.session.mbprofiler is None:
            self.session.mbprofiler = MbProfiler(self.session)
        mbprofiler = self.session.mbprofiler
        if start or stop:
            if start and stop:
                raise Exception('conflicting options, use only one of --start or --stop') from None
            if count_instr or cumulate or low is not None or high is not None or freq is not None:
                raise Exception('conflicting options, use only one of --start or --stop or '
                                '(low, high, freq, --count_instr and/or --cumulate)') from None
            if 'cfg_done' in mb_profile_config and mb_profile_config['cfg_done'] == 1:
                if start:
                    mbprofiler.mbprof_start()
                    mb_profile_config['prof_started'] = 1
                if stop:
                    if 'prof_started' in mb_profile_config and mb_profile_config['prof_started'] == 1:
                        mbprofiler.mbprof_gmonout(out)
                        if 'cnt_instr' in mb_profile_config and mb_profile_config['cnt_instr'] == 0:
                            mbprofiler.mbprof_disassembly_annotate(f'{os.path.splitext(out)[0]}.asm')
                    else:
                        raise Exception('Profiler not started, please start the profiler using mbprofile '
                                        '--start command') from None
            else:
                raise Exception('Profiling not configured, please configure before starting or stopping the '
                                'profiling') from None
        else:
            if 'elf' not in mb_profile_config:
                raise Exception('download elf onto the target') from None
            elf = mb_profile_config['elf']
            elf_text_addr = self.__get_elf_text_addrs(elf)
            if high is None or high == 'high':
                high = elf_text_addr['high_addr']
            if low is None or low == 'low':
                low = elf_text_addr['low_addr']
            if high <= low:
                raise Exception('High address cannot be same or smaller than low address') from None
            if freq is None:
                freq = 100000000
            mb_profile_config['low_addr'] = low
            mb_profile_config['high_addr'] = high
            mb_profile_config['freq'] = freq
            mb_profile_config['cumulate'] = cumulate
            mb_profile_config['cnt_instr'] = count_instr

            mbprofiler.mbprof_set_config(mb_profile_config)
            props = self.__get_target_microblaze_props(self.__select_target())
            mbprofiler.mbprof_init(props)
            mb_profile_config['cfg_done'] = 1
            mb_profile_config['prof_started'] = 0

    def pmc(self, cmd: str, data: list = None, ipi: int = 5, **kwargs):
        """
pmc:
    IPI commands to PMC.

Prototype:
    target.pmc(cmd = <command>, data = <arguments>, ipi = <buffer>, **kwargs)

Optional Arguments:
    cmd = <command>
        features <api-id>
        get_device_id
        get_board <addr max-size>

        request_device <node-id> <capabilities> <qos> <ack-type>
        release_device <node-id>
        set_requirement <node-id> <capabilities> <qos> <ack-type>
        self_suspend <node-id> <wakeup-latency> <power-state> <resume-addr>
        request_suspend <subsystem-id> <ack-type> <wakeup-latency> <power-state>
        request_wakeup <node-id> <resume-addr> <ack-type>
        abort_suspend <abort-reason> <node-id>
        setup_wakeup_source <subsystem-id> <node-id> <flag>
        get_device_status <node-id>
        device_ioctl <node-id> <ioctl-id>
        set_max_latency <node-id> <latency>

        reset_assert <node-id> <flag>
        reset_get_state <node-id>

        pin_control_request <node-id>
        pin_control_release <node-id>
        pin_get_fuction <node-id>
        pin_set_fuction <node-id> <function-id>
        pin_get_config_param <node-id> <param-id>
        pin_set_config_param <node-id> <param-id> <param-value>

        clock_enable <node-id>
        clock_disable <node-id>
        clock_get_state <node-id>
        clock_set_divider <node-id> <divider>
        clock_get_divider <node-id> resp <divider>
        clock_set_parent <node-id> <parent-index>
        clock_get_parent <node-id> resp <parent-index>

        pll_set_param <node-id> <param-id> <param-value>
        pll_set_param <node-id> <param-id> resp <param-value>
        pll_set_mode <node-id> <pll-mode>
        pll_get_mode <node-id> resp <pll-mode>

        force_power_down <node-id> <ack-type>
        system_shutdown <shutdown-type> <sub-type>

        All the <addr> arguments can be 32-bit or 64-bit.
        Refer to CDO specification for more details about each command.

        Apart from these commands, a generic command is also supported.
            generic [-response-size <num>] <command> <args>
        <command> should be numeric value of the actual CDO command, for example
        0x1030115 for get_board. <args> should be the arguments corresponding
        to that command.
        If the command is expected to return a response, then -response-size
        should specify the number of words the command would return. This data
        is returned as the command result.

    data = <arguments>
        Arguments to the IPI command.

    ipi = <buffer>
        IPI buffer to be used to trigger the <command>. It can be in
        the range of 0 - 5 for Versal. Default buffer is 0.
        This buffer shouldn't be used by other applications while IPI
        commands are triggered through this command.
    kwargs:
        response_size = <response_size>
Returns:
    None
        If IPI command is triggered successfully.
    Exception
        IPI command cannot be triggered.

Examples:
    target.pmc(cmd='get_board', data=[0xffff0000, 0x100])
        Write the board details to address 0xffff0000. Max buffer size
        is 256 bytes. The result of the command is status and the
        response length.
    target.pmc(cmd='generic', data=[0x1030115, 0xffff0000, 0x100], response_size=2)
        Same as previous example, but use generic command instead of get_board.

Interactive mode examples:
    pmc -cmd get_board -data [0xffff0000, 0x100]
    pmc -cmd generic -data [0x1030115, 0xffff0000, 0x100] -response_size 2
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        pmccmds = self.session.pmccmds
        response_size = kwargs.pop('response_size') if 'response_size' in kwargs else None
        if data is None:
            data = list()
        if len(pmccmds) == 0:
            self.__init_pmc_commands()
        if ipi < 0 or ipi > 5:
            raise Exception(f'invalid ipi {ipi}: should be 0 - 5') from None
        subcmds = pmccmds.keys()
        subcmd = list(filter(lambda k: k.startswith(cmd), subcmds))
        if len(subcmd) > 1 and cmd in subcmds:
            subcmd = list()
            subcmd.append(cmd)
        if len(subcmd) == 1 and subcmd[0] in pmccmds.keys():
            subcmd = subcmd[0]
            if subcmd == 'generic':
                if len(data) > 8:
                    raise Exception('ipi buffer overflow, max buffer size is 8') from None
                if response_size is not None:
                    return self.session.__ipi(ipi, data, response_size=response_size)
                else:
                    return self.session.__ipi(ipi, data)
            if 'args' in pmccmds[subcmd] and len(pmccmds[subcmd]['args']) != len(data):
                data_args = pmccmds[subcmd]['args']
                raise Exception(f"Wrong # of args: should be \'pmc(cmd={subcmd}, data={data_args}\'")
            args = list()
            if subcmd == 'get_board':
                addr = data[0]
                args = data[1:]
                args = split_addr(addr) + args
            cmd = pmccmds[subcmd]['cmd']
            args.insert(0, cmd)
            if 'resp' in pmccmds[subcmd]:
                return self.session.__ipi(ipi, args, response_list=pmccmds[subcmd]['resp'])
            else:
                return self.session.__ipi(ipi, args)
        else:
            if len(subcmd) == 0:
                subcmd = subcmds
            raise Exception(f'bad option \'{cmd}\': must be one of {list(subcmd)}') from None

    add_function_metadata('pmc', 'IPI commands to PMC', 'ipi', 'Target')

    def plm_set_log_level(self, level: int):
        """
plm_set_log_level:
    Configure PLM log level.

Prototype:
    target.plm_set_log_level(level = <log_level>)

Required Arguments:
    level = <log_level>
        Configure the PLM log level. This can be less than or equal
        to the level set during the compile time.
        The following levels are supported.
            0x1 - Unconditional messages (DEBUG_PRINT_ALWAYS)
            0x2 - General debug messages (DEBUG_GENERAL)
            0x3 - More debug information (DEBUG_INFO)
            0x4 - Detailed debug information (DEBUG_DETAILED)

Returns:
    None if successful, else exception.

Examples:
    target.plm_set_log_level(level = 1)

Interactive mode examples:
    plm_set_log_level -level 1
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        log_cmd = 0x040113
        self.session.__check_if_plm_log_supported()
        if level < 0 or level > 4:
            raise Exception('invalid log level, must be 1-4') from None
        self.session.pmc('generic', [log_cmd, 1, level, 0, 0])

    add_function_metadata('plm_set_log_level', 'Configure PLM log level', 'ipi', 'Target')

    def plm_set_debug_log(self, addr: int, size: int):
        """
plm_set_debug_log:
    Configure PLM debug log memory.

Prototype:
    target.plm_set_debug_log(addr = <mem_addr>, size = <mem_size>)

Required Arguments:
    addr = <mem_addr>
        Address to be used for plm debug log.

    size = <mem_size>
        Memory size to be used for plm debug log.

Returns:
    None if successful, else exception.

Examples:
    target.plm_set_debug_log(addr = 0x0, size = 0x4000)

Interactive mode examples:
    plm_set_debug_log -addr 0 -size 0x4000
        """
        if self.__get_current_node() is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        self.session.__check_if_plm_log_supported()
        self.session.pmc('generic', [0x040113, 2, ((addr > 32) & 0xFFFFFFFF), addr & 0xFFFFFFFF, size])

    add_function_metadata('plm_set_debug_log', 'Configure memory for PLM debug log', 'ipi', 'Target')

    def plm_copy_debug_log(self, addr: int):
        """
plm_copy_debug_log:
    Copy PLM debug log.

Prototype:
    target.plm_copy_debug_log(addr = <mem_addr>)

Required Arguments:
    addr = <mem_addr>
        Copy PLM debug log from debug log buffer to user memory
        specified by <addr>.

Returns:
    None if successful, else exception.

Examples:
    target.plm_set_debug_log(addr = 0x0)

Interactive mode examples:
    plm_set_debug_log -addr 0
        """
        if self.__get_current_node() is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None
        self.session.__check_if_plm_log_supported()
        self.session.pmc('generic', [0x040113, 3, ((addr > 32) & 0xFFFFFFFF), addr & 0xFFFFFFFF, 0])

    add_function_metadata('plm_copy_debug_log', 'Copy PLM debug log to user memory', 'ipi', 'Target')

    def plm_log(self, addr: int = None, size: int = None, handle=None, slr: int = None, *args):
        """
plm_log:
    Retrieve the PLM log.

Prototype:
    target.plm_log(addr = <mem_addr>, size = <log_size>)

Optional Arguments:
    addr = <mem_addr>
        Specify the memory address from which the PLM log should be
        retrieved. By default, the address and log size are obtained
        by triggering IPI commands to PLM. If PLM does not respond to
        IPI commands, default address 0xf2019000 is used. This option
        can be used to change default address. If either memory address
        or log size is specified, then the address and size are not
        retrieved from PLM. If only one of address or size options
        is specified, default value is used for the other option.
        See below for description about log size.

    size = <log_size>
        Specify the log buffer size. If this option is not specified,
        then the default size of 1024 bytes is used, only when the
        log memory information cannot be retrieved from PLM.

    handle = <file_handle>
        Specify the file handle to which the data should be redirected.
        If no file handle is given, data is printed on stdout.

    slr = <num>
        Specify the slave slr number. If this option is not specified, the
        default will be SLR0 (master plm). The valid slr numbers are
        from 0 to 3.

Returns:
    None if successful, else exception.

Examples:
    target.plm_log()
    session.plm_log(slr=2)

Interactive mode examples:
    plm_log
        """
        if self.__get_current_node() is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='plm_log')
        parser.add_argument('-s', '--skip_rtca', action='store_true', help='skip_rtca')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        use_rtca = 0
        def_addr = 0xf2019000
        def_size = 1024
        use_defaults = 0
        wrapped_addr = 0
        wrapped_len = 0
        log_cmd = 0x040113
        rtca_addr = 0xf2014000

        addr = def_addr if addr is None else addr
        length = def_size if size is None else size

        if slr is not None:
            rtca_addr = self.__slave_slr_map(slr, rtca_addr, length)
            addr = self.__slave_slr_map(slr, addr, length)
            def_addr = self.__slave_slr_map(slr, def_addr, length)

        ret = self.session.mrd(rtca_addr, '-v', '-f')
        if ret == 0x41435452:
            use_rtca = 1
        skip_rtca = 1 if parsed_args.skip_rtca is True else 0
        log = ''

        if addr is None and size is None:
            if use_rtca and skip_rtca == 0:
                addr = (self.session.mrd(rtca_addr + 0x10, '-f', '-v') |
                        (self.session.mrd(rtca_addr + 0x14, '-f', '-v') << 32))
                if slr is not None:
                    addr = self.__slave_slr_map(slr, addr, length)
                size = self.session.mrd(rtca_addr + 0x18, '-f', '-v') / 4
                offset = self.session.mrd(rtca_addr + 0x1C, '-f', '-v') & 0x7fffffff
                if addr == 0xdeadbeef or addr >> 32 == 0xdeadbeef or offset == 0xdeadbeef:
                    use_defaults = 1
                length = (offset & 0x7fffffff) - 1
                wrapped = offset & 0x80000000
                if wrapped != 0:
                    wrapped_addr = addr
                    wrapped_len = length - 1
                    addr = addr + length + 1
                    length = size - length - 1
            else:
                try:
                    self.session.__check_if_plm_log_supported()
                    ret = self.session.pmc('generic', [log_cmd, 4, 0, 0, 0], response_size=6)
                except Exception as e:
                    err = e.args[0].split('Exception: ')[1]
                    if err.startswith('previous ipi request is pending') or \
                            err.startswith('timeout waiting for request to be acknowledged'):
                        use_defaults = 1
                    else:
                        raise Exception(e) from None
                if ret[0] != 0:
                    use_defaults = 1
                if use_defaults == 0:
                    addr = (ret[1] << 32) | ret[2]
                    length = ret[3]
                    if length == 0:
                        use_defaults = 1
                    else:
                        if slr is not None:
                            addr = self.__slave_slr_map(slr, addr, length)

        if use_defaults:
            addr = def_addr
            length = def_size
            print("WARNING: cannot retrive log buffer information. Using default address 0xf2019000\n"
                  "\r         and size 1024. Use -log-mem-addr or -log-size to change default values")

        data = self.session.mrd(addr, '-f', '-v', word_size=1, size=length)
        for b in data:
            log += '{0:c}'.format(b)
        if wrapped_addr != 0:
            wrapped_data = self.session.mrd(wrapped_addr, '-f', '-v', word_size=1, size=wrapped_len)
            for b in wrapped_data:
                log += '{0:c}'.format(b)
        if handle is not None:
            handle.write(log)
        else:
            print(log)

    add_function_metadata('plm_log', 'Retrieve PLM debug log', 'ipi', 'Target')

    def profile(self, freq: int = None, addr: int = None, out: str = None):
        """
profile:
    Configure and run the GNU profiler.

Prototype:
    target.profile(freq = <sampling_freq>, addr = <scratch_addr>,
                    out = <file_name>)

Optional Arguments:
    freq = <sampling-freq>
        Sampling frequency.

    addr = <scratch_addr>
        Scratch memory for storing the profiling related data. It needs
        to be assigned carefully, as it should not overlap with the
        program sections.

    out = <file-name>
        Name of the output file for writing the profiling data. This
        option also runs the profiler and collects the data.
        If file name is not specified, profiling data is written to
        gmon.out.

Returns:
    Depends on options used.

    None
        Successful configuration when addr or freq is/are specified.

    None, generates file
        When out is specified.

    Exception
        Error in configuration.

Examples:
    target.profile(freq = 10000, addr = 0)
        Configure the profiler with a sampling frequency of 10000
        and scratch memory at 0x0.

Interactive mode examples:
    profile -freq 10000 -addr 0
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        if out is not None:
            if freq is not None or addr is not None:
                raise Exception(f"conflicting options, use only one of -out or (-freq and -scratchaddr)") \
                    from None
        else:
            if freq is None or addr is None:
                raise Exception("invalid arguments, specify -freq and -scratchaddr") from None

        if self.session.gprof is None:
            self.session.gprof = Gprof(self.session)
        gprof = self.session.gprof
        profile_config = self.session.profile_config
        if freq is not None:
            profile_config['sampfreq'] = freq
        if addr is not None:
            profile_config['scratchaddr'] = addr
        if out is not None:
            profile_config['outfile'] = out
            prof_enable = gprof.is_profiling_enabled()
            if prof_enable == 1:
                self.__write_prof_output(out)
                self.session.profile_config = dict()
                self.session.gprof = None
            else:
                raise Exception('profiling not enabled')

    add_function_metadata('profile', 'Configure and run the GNU profiler', 'profiler', 'Target')

    def loadipxact(self, *args, xml=None):
        """
loadipxact:
    Load memory mapped register definitions from a ipxact-xml file, or
    clear previously loaded definitions and return to built-in
    definitions, or return the xml file that is currently loaded.

Prototype:
    session.loadipxact(*args, xml = <file>)

Optional Arguments:
    xml = <xml_file>
        To load register definitions from <xml_file>. This file should
         be in ipxact format.

Options:
    --clear
        Clear definitions loaded from ipxact file and return to
        built-in definitions.

    --list
        Return the ipxact file that is currently loaded.

Returns:
    xml file path
        If -list option is used.
    None
        If -list option is not used and registers are loaded.
    Exception
        Failed to load.

Examples:
    s.loadipxact(xml='test.xml')
    s.loadipxact('--list')
    s.loadipxact('--clear')

Interactive mode examples:
    loadipxact -xml test.xml
    loadipxact -list
    loadipxact -clear
        """
        self.__select_target()
        node = self.__get_current_node()
        if node is None:
            raise Exception("Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='loadipxact options')
        parser.add_argument('-c', '--clear', action='store_true', help='Add registers to memory map')
        parser.add_argument('-l', '--list', action='store_true', help='List open hw designs')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        clear = 1 if parsed_args.clear else 0
        list = 1 if parsed_args.list else 0
        x = 1 if xml is not None else 0

        if clear + list + x != 1:
            raise Exception("Invalid args: specify exactly one of --clear, --list or xml") from None
        if clear == 1:
            if node.id in self.session.ipxactfiles.keys():
                exec_in_dispatch_thread(self.__parse_ipxact, node.id, b'')
                del self.session.ipxactfiles[node.id]
            return
        if list == 1:
            xml_file = self.session.ipxactfiles[node.id] if node.id in self.session.ipxactfiles else ''
            if xml_file == '':
                print('no ipxact files loaded for the current target')
            return xml_file

        with open(xml, 'rb') as f:
            buf = f.read()
        exec_in_dispatch_thread(self.__parse_ipxact, node.id, buf)
        self.session.ipxactfiles.update({node.id: os.path.realpath(xml)})

    add_function_metadata('loadipxact', 'Load memory mapped registers from ipxact xml', 'memorymap', 'Target')

    def mbtrace(self, *args, out: str = None, level: str = 'flow', low: int = 0xFFFFFFFF, high: int = 0x00000000,
                dma: int = 0x44A00000, format: str = 'mdm'):
        """
    mbtrace:
        Configure and run MB program and event trace for tracing the
        application running on MB. The output is the disassembly of
        the executed program.

    Prototype:
        target.mbtrace(*args, out: str = None, level: str = None, low: int = None, high: int = None,
                dma: int = None, format: str = None)

    Options:
        --start
            Enable and start trace. After starting trace the execution of the
            program is captured for later output.

        --stop
            Stop and output trace.

        --con
            Output trace after resuming execution of active target until a
            breakpoint is hit. At least one breakpoint or watchpoint must be
            set to use this option.
            This option is only available with embedded trace.

        --stp
            Output trace after resuming execution of the active target until
            control reaches instruction that belongs to different line of
            source code.

        --nxt
            Output trace after resuming execution of the active target until
            control reaches instruction that belongs to a different line of
            source code, but runs any functions called at full speed.

        out = <filename>
            Output trace data to a file.
            <filename> Name of the output file for writing the trace data.
            If not specified, data is output to standard output.

        level = <level>
            Set the trace level to "full", "flow", "event", or "cycles".
            If not specified, "flow" is used.

        --halt
            Set to halt program execution when the trace buffer is full.
            If not specified, trace is stopped but program execution continues.

        --save
            Set to enable capture of load and get instruction new data value.

        low = <addr>
            Set low address of the external trace buffer address range.
            The address range must indicate an unused accessible memory space.
            Only used with external trace.

        high = <addr>
            Set high address of the external trace buffer address range.
            The address range must indicate an unused accessible memory space.
            Only used with external trace.

        format = <format>
            Set external trace data format to "mdm", "ftm", or "tpiu". If format
            is not specified, "mdm" is used. The "ftm" and "tpiu" formats are
            output by Zynq-7000 PS. Only used with external trace.
    Returns:
        Depends on options used.
            --start, out, level, --halt --save, low, high, format
                Returns nothing on successful configuration.
                Exception string, in case of error.

            --stop, --con, --stp, --nxt
                Returns nothing, and outputs trace data to a file or standard output.
                Exception string, in case of error.

    Examples:
        s.mbtrace()
        s.mbtrace('--start')
        s.mbtrace('--start', '--halt', level='full')
        s.mbtrace('--stop', out='trace.out')
        s.mbtrace('--con', out='trace.out')

Interactive mode examples:
    mbtrace
    mbtrace -start
    mbtrace -start -halt -level full
    mbtrace -stop -out trace.out
    mbtrace -con -out trace.out
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid target, select a target using targets function.") from None

        parser = argparse.ArgumentParser(description='mbtrace options')
        parser.add_argument('--start', action='store_true', help='enable/start trace')
        parser.add_argument('--stop', action='store_true', help='')
        parser.add_argument('--con', action='store_true', help='')
        parser.add_argument('--stp', action='store_true', help='')
        parser.add_argument('--nxt', action='store_true', help='')
        parser.add_argument('-f', '--force', action='store_true', help='')
        parser.add_argument('-a', '--append', action='store_true', help='')
        parser.add_argument('-ha', '--halt', action='store_true', help='')
        parser.add_argument('-s', '--save', action='store_true', help='')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        start = 1 if parsed_args.start is True else 0
        stop = 1 if parsed_args.stop is True else 0
        con = 1 if parsed_args.con is True else 0
        stp = 1 if parsed_args.stp is True else 0
        nxt = 1 if parsed_args.nxt is True else 0
        force = 1 if parsed_args.force is True else 0
        append = 1 if parsed_args.append is True else 0
        halt = 1 if parsed_args.halt is True else 0
        save = 1 if parsed_args.save is True else 0

        exec_cnt = con + stp + nxt
        conflict_cnt = start + stop + exec_cnt
        if conflict_cnt > 0 and conflict_cnt != 1:
            raise Exception('Conflicting options, use only one of -start, -stop, -con, -stp, or -nxt') from None

        action_cnt = force + append
        if action_cnt > 0 and action_cnt != 1:
            raise Exception('Conflicting options, use only one of -force or -append') from None

        if action_cnt > 0 and out is None:
            raise Exception('Only use -force or -append together with -out') from None

        if self.session.mbtrace_obj is None:
            self.session.mbtrace_obj = MbTrace(self.session)
        mbt = self.session.mbtrace_obj
        mbtc = self.session.mb_trace_config

        if 'mbtrace_loaded' not in mbtc or mbtc['mbtrace_loaded'] != 1:
            mbtc['mbtrace_loaded'] = 1
        action = ''
        if force:
            action = 'force'
        if append:
            action = 'append'
        trace_started = 1 if 'trace_started' in mbtc and mbtc['trace_started'] == 1 else 0
        props = self.__get_target_microblaze_props(self.__select_target())
        if 'cfg_done' not in mbtc or mbtc['cfg_done'] != 1:
            mbtc['mode'] = self.__level2mode(level)
            mbtc['halt'] = halt
            mbtc['save'] = save
            mbtc['low'] = low
            mbtc['high'] = high
            mbtc['data_format'] = format
            mbtc['trace_dma'] = dma
            mbt.mbtrace_set_config(mbtc)
            mbt.mbtrace_init(props)
            mbtc['cfg_done'] = 1
            mbtc['trace_started'] = 0
        elif start or (exec_cnt > 0 and trace_started != 1):
            mode = self.__level2mode(level)
            mbt.mbtrace_set(props, mode, halt, save, low, high, format, dma)
        if start:
            mbt.mbtrace_start()
            mbtc['trace_started'] = 1
        if stop:
            if trace_started != 1:
                raise Exception('Trace not started, please start the trace using mbtrace -start command') from None
            mbt.mbtrace_stop()
            mbt.mbtrace_dis(out, action)
            mbtc['trace_started'] = 0
        if exec_cnt > 0 and trace_started != 1:
            mbt.mbtrace_start()
        if con:
            mbt.mbtrace_continue(out, action)
        if stp:
            self.stp()
            mbt.mbtrace_stop()
            mbt.mbtrace_dis(out, action)
        if nxt:
            self.nxt()
            mbt.mbtrace_stop()
            mbt.mbtrace_dis(out, action)

    add_function_metadata('mbtrace', 'Configure and run MB trace.', 'profiler', 'Target')

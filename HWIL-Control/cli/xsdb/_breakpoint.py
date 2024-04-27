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

import argparse
import uuid

from tcf.services import breakpoints
from tcf.services import breakpoints as bp_service

from xsdb._utils import *


#################################################################################################
#   Commands specific to breakpoint object
#################################################################################################

def bp_get_ids(session, sync):
    bp_svc = session._curchan_obj.getRemoteService(breakpoints.NAME)

    class DoneCommand(bp_service.DoneGetIDs):
        def doneGetIDs(self, token, error, ids):
            if error:
                sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'], result=None)
                return False
            else:
                sync.done(error=None, result=ids)

    bp_svc.getIDs(DoneCommand())
    return True


def bp_get_properties(bp_id, session, sync):
    bp_svc = session._curchan_obj.getRemoteService(breakpoints.NAME)

    class DoneCommand(bp_service.DoneGetProperties):
        def doneGetProperties(self, token, error, properties):
            if error:
                sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'], result=None)
                return False
            else:
                sync.done(error=None, result=properties)

    bp_svc.getProperties(bp_id, DoneCommand())
    return True


def bp_get_status(bp_id, session, sync):
    bp_svc = session._curchan_obj.getRemoteService(breakpoints.NAME)

    class DoneCommand(bp_service.DoneGetStatus):
        def doneGetStatus(self, token, error, status):
            if error:
                sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'], result=None)
            else:
                sync.done(error=None, result=status)

    bp_svc.getStatus(bp_id, DoneCommand())
    return True


def get_bp_status(session, uu_id, level='brief'):
    result = exec_in_dispatch_thread(bp_get_status, uu_id, session)
    if len(result) == 0:
        return result
    if 'Error' in result.keys():
        raise Exception(result.get('Error')) from None
    if 'Instances' not in result.keys():
        raise Exception("Breakpoint status data doesn't exist.") from None
    result = result.get('Instances')
    status = {}
    for sinfo in result:
        tid = None
        if 'LocationContext' in sinfo.keys():
            bp_ctx = sinfo.get('LocationContext')
            ctx_tgt_map = session.get_context_target_map()
            if bp_ctx in ctx_tgt_map.keys():
                tid = dict_get_safe(ctx_tgt_map, bp_ctx)
            if tid is None:
                continue
            if level == 'brief':
                tinfo = {}
                if 'Error' in sinfo.keys():
                    tinfo['Error'] = sinfo.get('Error')
                else:
                    if 'Address' in sinfo.keys():
                        tinfo['Address'] = hex(sinfo.get('Address'))
                    if 'HitCount' in sinfo.keys():
                        tinfo['HitCount'] = sinfo.get('HitCount')
                sinfo = tinfo
            else:
                if 'Error' not in sinfo.keys():
                    address = sinfo.get('Address')
                    sinfo['Address'] = hex(address) if address is not None else ''
                else:
                    sinfo['Error'] = '{' + sinfo.get('Error') + '}'
                del sinfo['LocationContext']
        status[tid] = sinfo
    return status


class Breakpoint(object):
    __bp_types = {
        'hw': breakpoints.TYPE_HARDWARE,
        'sw': breakpoints.TYPE_SOFTWARE,
        'auto': breakpoints.TYPE_AUTO
    }

    def __init__(self, session):
        self.show_status = False
        self.enabled = False
        self.ct_input = None
        self.ct_output = None
        self.location = None
        self.id = None
        self.session = session

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(Breakpoint) if callable(getattr(Breakpoint, method)) if
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

    class DoneCommand(bp_service.DoneCommand):
        def __init__(self, sync):
            self.sync = sync

        def doneCommand(self, token, error):
            if error:
                self.sync.done(error=error if isinstance(error, OSError) else error.getAttributes()['Format'],
                               result=None)
                return False
            else:
                self.sync.done(error=None, result=None)

    def __bp_add(self, properties: dict, sync):
        bp_svc = self.session._curchan_obj.getRemoteService(breakpoints.NAME)
        bp_svc.add(properties, self.DoneCommand(sync))
        return True

    def __bp_enable(self, ids: list or tuple, sync):
        bp_svc = self.session._curchan_obj.getRemoteService(breakpoints.NAME)
        bp_svc.enable(ids, self.DoneCommand(sync))
        return True

    def __bp_disable(self, ids: list or tuple, sync):
        bp_svc = self.session._curchan_obj.getRemoteService(breakpoints.NAME)
        bp_svc.disable(ids, self.DoneCommand(sync))
        return True

    def __bp_remove(self, ids: list or tuple, sync):
        bp_svc = self.session._curchan_obj.getRemoteService(breakpoints.NAME)
        bp_svc.remove(ids, self.DoneCommand(sync))
        return True

    def on_breakpoint_event_status_changed(self, id, status):
        if len(status) == 0:
            return
        if 'Error' in status.keys():
            print('Info: Breakpoint', id, 'status : Error {', status.get('Error'), '}')
            return
        if 'Instances' not in status.keys():
            print('Info: Breakpoint', id, 'status: ', status)
            return
        else:
            bp_status = status.get('Instances')
            for sinfo in bp_status:
                if 'LocationContext' in sinfo.keys():
                    tid = None
                    bp_ctx = sinfo.get('LocationContext')
                    ctx_tgt_map = self.session.get_context_target_map()
                    if bp_ctx in ctx_tgt_map.keys():
                        tid = dict_get_safe(ctx_tgt_map, bp_ctx)
                    if tid is None:
                        continue
                    status = ''
                    if 'Error' in sinfo.keys():
                        status = sinfo.get('Error')
                    else:
                        if 'Address' in sinfo.keys():
                            status = status + ("Address: " + str(hex(sinfo.get('Address'))))
                        if 'BreakpointType' in sinfo.keys():
                            status = status + (" Type: " + sinfo.get('BreakpointType'))

                    print('Info: Breakpoint ' + str(id) + ' status: \n\t target ' + str(tid) + ': {' + status + '}',
                          flush=True)
                else:
                    print('Info: Breakpoint' + str(id) + ' status: ')

    def add(self, *args, **kwargs):

        if self.id is not None:
            raise Exception("Breakpoint is already added.") from None

        parser = argparse.ArgumentParser(description='bpadd')
        parser.add_argument('-t', '--temp', action='store_true', help='trigger breakpoint once')
        parser.add_argument('-sk', '--skip_prologue', action='store_true', help='skip function prologue')
        parser.add_argument('arg1', nargs='?', help='Address or File:Line of a breakpoint')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if len(args) != 0:
            if parsed_args.arg1 is not None and ('addr' in kwargs or 'file' in kwargs or 'line' in kwargs):
                raise Exception(f"Unexpected arguments: {args}") from None

        address = None
        file = None
        line = None

        if parsed_args.arg1 is not None:
            arg = parsed_args.arg1.split(':')
            if len(arg) == 1:
                address = arg[0]
            elif len(arg) == 2:
                file = arg[0]
                line = int(arg[1])
            else:
                raise Exception(f"Unexpected arguments: {args}") from None

        bp = {breakpoints.PROP_ID: str(uuid.uuid4()), breakpoints.PROP_ENABLED: True, breakpoints.PROP_TEMPORARY: False,
              breakpoints.PROP_SKIP_PROLOGUE: False}

        if parsed_args.temp:
            bp[breakpoints.PROP_TEMPORARY] = True

        if parsed_args.skip_prologue:
            bp[breakpoints.PROP_SKIP_PROLOGUE] = True

        if 'addr' in kwargs:
            address = str(kwargs.pop("addr"))
        if address is not None:
            bp[breakpoints.PROP_LOCATION] = address
            self.location = bp[breakpoints.PROP_LOCATION]

        if 'file' in kwargs:
            file = kwargs.pop("file")
        if file is not None:
            bp[breakpoints.PROP_FILE] = file

        if 'line' in kwargs:
            line = kwargs.pop("line")
            if not isinstance(line, int):
                raise Exception('\'line\' must be integer.') from None
        if line is not None:
            bp[breakpoints.PROP_LINE] = line

        if 'type' in kwargs:
            bptype = kwargs.pop("type")
            if bptype not in self.__bp_types:
                raise Exception(f"Unknown breakpoint type \'{bptype}\' : must be "
                                f"{', '.join(list(self.__bp_types.keys()))}") from None
            else:
                bp[breakpoints.PROP_TYPE] = self.__bp_types[bptype]

        if 'mode' in kwargs:
            mode = check_int(kwargs.pop("mode"))
            if not isinstance(mode, int):
                raise Exception(f'Invalid mode \'{mode}\'. Must be integer from 0x0 to 0xf.') from None
            bp[breakpoints.PROP_ACCESS_MODE] = mode & 0x0f

        ct_input_list = []
        if 'ct_input' in kwargs:
            ct_input = kwargs.pop("ct_input")
            if isinstance(ct_input, list):
                for c in ct_input:
                    if is_int(c) is False:
                        raise Exception('\'ct_input\' must be list of integers. Refer help for details.') from None
                ct_input_list = ct_input.copy()
            elif isinstance(ct_input, int):
                ct_input_list.append(ct_input)
            else:
                raise Exception('\'ct_input\' must be list of integers or integer. Refer help for details.') from None
            bp[breakpoints.PROP_CT_INP] = ct_input_list
            self.ct_input = bp[breakpoints.PROP_CT_INP]

        ct_output_list = []
        if 'ct_output' in kwargs:
            ct_output = kwargs.pop("ct_output")
            if isinstance(ct_output, list):
                for c in ct_output:
                    if is_int(c) is False:
                        raise Exception('\'ct_output\' must be list of integers. Refer help for details.') from None
                ct_output_list = ct_output.copy()
            elif isinstance(ct_output, int):
                ct_output_list.append(ct_output)
            else:
                raise Exception('\'ct_output\' must be list of integers or integer. Refer help for details.') from None
            bp[breakpoints.PROP_CT_OUT] = ct_output_list
            self.ct_output = bp[breakpoints.PROP_CT_OUT]

        if 'skip_on_step' in kwargs:
            skip_on_step = kwargs.pop("skip_on_step")
            if is_int(skip_on_step) is False:
                raise Exception('\'skip_on_step\' must be integer from 0 to 2.') from None
            if skip_on_step != 0:
                if skip_on_step > 2:
                    raise Exception(f'Unknown skip_on_step \'{skip_on_step}\' : should be 0, 1 or 2.') from None
                if len(ct_input_list) != 0:
                    bp[breakpoints.PROP_SKIP_ON_STEP] = skip_on_step
                else:
                    raise Exception('\'skip_on_step\' is valid only for cross trigger input breakpoints.') from None

        if 'enable' in kwargs and kwargs.pop("enable") == 0:
            bp[breakpoints.PROP_ENABLED] = False

        if 'condition' in kwargs:
            condition = kwargs.pop("condition")
            if isinstance(condition, str):
                bp[breakpoints.PROP_CONDITION] = condition
            else:
                raise Exception('\'condition\' must be string.') from None

        if 'ignore_count' in kwargs:
            ignore_count = kwargs.pop("ignore_count")
            if isinstance(ignore_count, int):
                bp[breakpoints.PROP_IGNORE_COUNT] = ignore_count
            else:
                raise Exception('\'ignore_count\' must be integer.') from None

        if 'target_id' in kwargs:
            tgt_ctx = []
            ctx = kwargs.pop("target_id")
            if ctx != 'all':
                tgt_ctx.append(ctx)
                bp[breakpoints.PROP_CONTEXT_IDS] = tgt_ctx

        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        self.id = bp[breakpoints.PROP_ID]
        self.enabled = bp[breakpoints.PROP_ENABLED]
        self.show_status = True
        s = self.session
        s._bptable[s._bpid] = self
        s._bpid = s._bpid + 1
        exec_in_dispatch_thread(self.__bp_add, bp)
        return s._bpid - 1

    def remove(self):
        """
remove:
    Remove Breakpoints/Watchpoints.

Prototype:
    bp.remove()

Returns:
    Nothing, if the breakpoint is removed successfully.

Examples:
    bp.remove()
        """

        if self.id is None:
            raise Exception("Breakpoint is already removed.") from None

        exec_in_dispatch_thread(self.__bp_remove, [self.id])
        for bpid, bp in self.session._bptable.items():
            if bp.id == self.id:
                del self.session._bptable[bpid]
                break

    def enable(self):
        """
enable:
    Enable Breakpoints/Watchpoints.

Prototype:
    bp.enable()

Returns:
    Nothing, if the breakpoint is enabled successfully.

Examples:
    bp.enable()
        """

        if self.id is None:
            raise Exception("Breakpoint is already removed.") from None

        exec_in_dispatch_thread(self.__bp_enable, [self.id])
        self.enabled = True

    def disable(self):
        """
disable:
    Disable Breakpoints/Watchpoints.

Prototype:
    bp.disable()

Returns:
    Nothing, if the breakpoint is disabled successfully.

Examples:
    bp.disable()
        """

        if self.id is None:
            raise Exception("Breakpoint is already removed.") from None

        exec_in_dispatch_thread(self.__bp_disable, [self.id])
        self.enabled = False

    def status(self):
        """
status:
    Print Breakpoints/Watchpoints status.

Prototype:
    bp.status()

Returns:
    Breakpoint status, if breakpoint exists else exception.

Examples:
    bp.status()
        """

        if self.id is None:
            raise Exception("Breakpoint is already removed.") from None

        status = get_bp_status(self.session, self.id, 'full')

        bpl = ''
        for ctx, ctxdata in status.items():
            bpl = bpl + 'target ' + str(ctx) + ':'
            sinfo = ''
            for key, data in ctxdata.items():
                sinfo = sinfo + ' ' + str(key) + ' ' + str(data)
            sinfo = sinfo + '\n'
            bpl = bpl + sinfo
        return bpl, status

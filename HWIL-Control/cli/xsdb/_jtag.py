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
import sys

from xsdb._tcf_jtag import TcfJtag
from xsdb._tcf_jtag_node_exec_context import TcfJtagNodeExecContext
from xsdb._utils import *


class Jtag(object):

    def __init__(self, chan, id, node: TcfJtagNodeExecContext, session):
        self.session = session
        self.id = id
        self.ctx = node.id
        self.node = node
        self.channel = chan

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(Jtag) if callable(getattr(Jtag, method)) if
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

    def __get_current_node(self):
        if self.__class__.__name__ == 'Jtag':
            return self.node
        else:
            return self.current_jtag_node

    def device_properties(self, *args, **kwargs):
        """
device_properties:
    Get/set device properties.

Prototype:
    jtag_target.device_properties(idcode)
        Get JTAG device properties associated with <idcode>.
    jtag_target.device_properties(props={key value ..})
        Set JTAG device properties.

Required Arguments:
    :param args:
        idcode: idcode of the jtag device
    :param kwargs:
        props : properties of jtag device in dict format

Returns:
    Jtag device properties for the given idcode, or nothing, if the idcode is
    unknown

Examples:
    jtag_target.device_properties(0x6ba00477)

    props = {'idcode': 0x6ba00477, 'irlen': 4}
    jtag_target.device_properties(props=props)

Interactive mode examples:
    jtag device_prop 0x6ba00477
    jtag device_properties -props {'idcode': 0x6ba00477, 'irlen': 4}
        """

        parser = argparse.ArgumentParser(description='device_properties')
        parser.add_argument('idcode', nargs='?', type=int, help='idcode')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        if parsed_args.idcode is not None:
            return exec_in_dispatch_thread(node.get_jtag_device_node().get_jtag_devices_properties, parsed_args.idcode)
        props = kwargs.pop('props') if 'props' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if props is not None:
            if 'idcode' not in props.keys():
                raise Exception('Missing idcode property.') from None
            exec_in_dispatch_thread(node.get_jtag_device_node().set_jtag_devices_properties, props)

    add_function_metadata('jtag device_properties', 'Get/set device properties.', 'jtag', 'Jtag')

    def lock(self, timeout: int = 0):
        """
lock:
    Lock JTAG scan chain containing current JTAG target.
    Wait for scan chain lock to be available and then lock it.  If
    <timeout> is specified the wait time is limited to <timeout>
    milliseconds.

    The JTAG lock prevents other clients from performing any JTAG
    shifts or state changes on the scan chain.  Other scan chains can
    be used in parallel.

    The jtag run_sequence command will ensure that all commands in the
    sequence are performed in order so the use of jtag lock is only
    needed when multiple jtag run_sequence commands needs to be done
    without interruption.

Prototype:
    jtag_target.lock(timeout)

Required Arguments:
    :param timeout: timeout in milliseconds

Returns:
    None

Note:
    A client should avoid locking more than one scan chain since this
    can cause dead-lock.

Examples:
    jtag_target.lock(100)
    session.lock(100)

Interactive mode examples:
    jtag lock
    jtag lock 100
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        timeout = check_int(timeout)
        tcf_jtag = TcfJtag(self.session)
        exec_in_dispatch_thread(tcf_jtag.jtag_lock, node.id, timeout)

    add_function_metadata('jtag lock', 'Lock JTAG scan chain.', 'jtag', 'Jtag')

    def unlock(self):
        """
unlock:
    Unlock JTAG scan chain containing current JTAG target.

Prototype:
    jtag_target.unlock()

Required Arguments:
    None

Returns:
    None

Examples:
    jtag_target.unlock()
    session.unlock()

Interactive mode examples:
    jtag unlock
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        tcf_jtag = TcfJtag(self.session)
        exec_in_dispatch_thread(tcf_jtag.jtag_unlock, node.id)

    add_function_metadata('jtag unlock', 'Unlock JTAG scan chain.', 'jtag', 'Jtag')

    def claim(self, mask: int = 0x1):
        """
claim:
    Claim JTAG device.
    This command will attept to set the claim mask for the current
    JTAG device.  If any set bits in <mask> are already set in the
    claim mask then this command will return error "already claimed".

    The claim mask allow clients to negotiate control over JTAG
    devices.  This is different from jtag lock in that 1) it is
    specific to a device in the scan chain, and 2) any clients can
    perform JTAG operations while the claim is in effect.

Prototype:
    jtag_target.claim(mask)

Required Arguments:
    :param mask: Set claim mask for current JTAG device. Default is 1.

Returns:
    None

Note:
    Currently claim is used to disable the hw_server debugger from
    controlling microprocessors on ARM DAP devices and FPGA devices
    containing Microblaze processors.

Examples:
    jtag_target.claim(1)
    session.claim(1)

Interactive mode examples:
    jtag claim 1
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        tcf_jtag = TcfJtag(self.session)
        exec_in_dispatch_thread(tcf_jtag.jtag_claim, node.id, mask)

    add_function_metadata('jtag claim', 'Claim JTAG device.', 'jtag', 'Jtag')

    def disclaim(self, mask: int = 0x1):
        """
disclaim:
    Disclaim JTAG device.

Prototype:
    jtag_target.disclaim(mask)

Required Arguments:
    :param mask: Clear claim mask for current JTAG device. Default is 1.

Returns:
    None

Examples:
    jtag_target.disclaim(1)
    session.disclaim(1)

Interactive mode examples:
    jtag disclaim 1
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        tcf_jtag = TcfJtag(self.session)
        exec_in_dispatch_thread(tcf_jtag.jtag_disclaim, node.id, mask)

    add_function_metadata('jtag disclaim', 'Disclaim JTAG device.', 'jtag', 'Jtag')

    def skew(self, value: int = None):
        """
skew:
    Get/set JTAG skew.

Prototype:
    jtag_target.skew()
        Get JTAG clock skew for current scan chain.
    jtag_target.skew(clock_skew)
        Set JTAG clock skew for current scan chain.

Required Arguments:
    :param value: Clear claim mask for current JTAG device.

Returns:
    Current Jtag clock skew, if no arguments are specified, or if Jtag skew is
    successfully set.

Note:
    Clock skew property is not supported by some Jtag cables.

Examples:
    jtag_target.skew()
    session.skew()

Interactive mode examples:
    jtag skew
        """

        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None
        tcf_jtag = TcfJtag(self.session)
        if value is None:
            return exec_in_dispatch_thread(tcf_jtag.jtag_get_option, node.id, "skew")
        else:
            if value <= 0:
                raise Exception(f'Invalid skew value: {value}.') from None
            value = check_int(value)
            return exec_in_dispatch_thread(tcf_jtag.jtag_set_option, node.id, "skew", value)

    add_function_metadata('jtag skew', 'Get/set JTAG skew.', 'jtag', 'Jtag')

    def frequency(self, *args):
        """
frequency:
    Get/set JTAG frequency.

Prototype:
    jtag_target.frequency()
        Get JTAG clock frequency for current scan chain.
    jtag_target.frequency(frequency)
        Set JTAG clock frequency for current scan chain. This frequency is
        persistent as long as the hw_server is running, and is reset to the
        default value when a new hw_server is started.
    jtag_target.frequency('--list')
        Get list of supported JTAG clock frequencies for current scan chain.

Required Arguments:
    :param args:
        frequency : frequency value
        '--list' : Get list of supported JTAG clock frequencies for
        current scan chain.

Returns:
    Current Jtag frequency, if no arguments are specified, or if Jtag frequency
    is successfully set.
    Supported Jtag frequencies, if --list option is used.
    Error string, if invalid frequency is specified or frequency cannot be set.

Examples:
    jtag_target.frequency()
    session.frequency()

Interactive mode examples:
    jtag frequency
        """

        # TODO : test option not supported
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None

        parser = argparse.ArgumentParser(description='Jtag frequency')
        parser.add_argument('-l', '--list', action='store_true', help='List open servers')
        parser.add_argument('frequency', nargs='?', type=int, help='Frequency to set')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        tcf_jtag = TcfJtag(self.session)
        if parsed_args.list and parsed_args.frequency is not None:
            raise Exception(f"Conflicting args, specify only one of frequency and --list") from None

        if parsed_args.list is True:
            return exec_in_dispatch_thread(tcf_jtag.jtag_get_option, node.id, "frequency_list")
        if parsed_args.frequency is not None:
            if parsed_args.frequency <= 0:
                raise Exception(f'invalid frequency value: {parsed_args.frequency}') from None
            else:
                exec_in_dispatch_thread(tcf_jtag.jtag_set_option, node.id, "frequency", parsed_args.frequency)
        return exec_in_dispatch_thread(tcf_jtag.jtag_get_option, node.id, "frequency")

    add_function_metadata('jtag frequency', 'Get/set JTAG frequency.', 'jtag', 'Jtag')

    def servers(self, *args, **kwargs):
        """
servers:
    List, open or close JTAG servers.

Prototype:
    jtag_target.servers(*args, **kwargs)
        List, open, and close JTAG servers.  JTAG servers are use to
        implement support for different types of JTAG cables.  An open
        JTAG server will enumberate or connect to available JTAG ports.

Optional Arguments:
    :param args:
        --list:
            List opened servers.  This is the default if no other option
            is given.

       --format:
            Return the format of each supported server string.

    :param kwargs:
        open=<server>
            Specifies server to open.

        close=<server>
            Specifies server to close.

Returns:
    Depends on the options specified

    <none>, --list
    List of open Jtag servers.

    --format
    List of supported Jtag servers.

    close, open
    Nothing if the server is opened/closed

Examples:
    jtag_target.servers()
    session.servers()
    jt.servers('-f')
    jt.servers(open='xilinx-xvc:localhost:10200')
    jt.servers(close='xilinx-xvc:localhost:10200')

Interactive mode examples:
    jtag servers
    jtag servers -open 'xilinx-xvc:localhost:10200'
    jtag servers -close 'xilinx-xvc:localhost:10200'
        """

        tcf_jtag = TcfJtag(self.session)
        parser = argparse.ArgumentParser(description='Jtag servers')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-l', '--list', action='store_true', help='List open servers')
        group.add_argument('-f', '--format', action='store_true', help='List the format of supported server strings')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        open = 1 if 'open' in kwargs else 0
        close = 1 if 'close' in kwargs else 0
        list = 1 if parsed_args.list is True else 0
        format = 1 if parsed_args.format is True else 0

        if open + close + list + format > 1:
            raise Exception(f"Conflicting args, specify only one of open, close, -- list and --format") from None
        if open == 1:
            url = kwargs.pop('open')
        if close == 1:
            url = kwargs.pop('close')
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        ctx_node_map = self.session.model.launch_node.get_jtag_context_node_map()
        sd_data = []
        serverctx_data = {}
        cablectx_data = {}
        for ctx, node in ctx_node_map.items():
            jtag_cable_node = node.get_jtag_cable_node()
            if jtag_cable_node is not None:
                cablectx_data.update({node.id: exec_as_runnable(get_cache_data,
                                                                jtag_cable_node.get_jtag_cable_context())})

                sd_data.append(exec_as_runnable(get_cache_data, jtag_cable_node.get_jtag_cable_server_descriptions()))
                os_data = exec_as_runnable(get_cache_data, jtag_cable_node.get_jtag_cable_open_servers())

                for item in os_data:
                    serverctx_data.update({item: exec_in_dispatch_thread(tcf_jtag.jtagcable_server_ctx, item)})

        descrs = {}
        for cable_data in sd_data:
            for data in cable_data:
                if 'ServerID' not in data:
                    continue
                descrs.update({data['ServerID']: data})

        result = ''
        if format == 1:
            for serverid, descr in descrs.items():
                result += '{0}{1}'.format(' ' * 3, serverid)
                if 'ParamNames' in descr:
                    for name in descr['ParamNames']:
                        result += '{0}{1}{2}'.format(':<', name, '>')
                result += '\n'
            print(result)
            return

        if open == 1:
            fields = url.split(':')
            if fields[0] not in descrs.keys():
                raise Exception(f"Unknown server : must be :{', '.join(descrs.keys())}") from None
            else:
                serverdata = descrs[fields[0]]
                if len(fields) - 1 != len(serverdata['ParamNames']):
                    format = serverdata['ServerID']
                    for name in serverdata['ParamNames']:
                        format += '{0}{1}{2}'.format(':<', name, '>')
                    raise Exception(f'Invalid server format, must be {format}') from None
                arguments = {}
                i = 1
                for name in serverdata['ParamNames']:
                    arguments[name] = fields[i]
                    i = i + 1
                exec_in_dispatch_thread(tcf_jtag.jtagcable_open_server, serverdata['ServerID'], arguments)
                return ''

        if close == 1:
            cableservers = []
            for serverid, data in serverctx_data.items():
                server_ctx = serverctx_data[serverid]
                if 'ID' not in server_ctx or 'ServerID' not in server_ctx or 'isActive' not in server_ctx or \
                        server_ctx['isActive'] == 0:
                    continue
                serverid = data['ServerID']
                cableserver = serverid
                if 'ParamNames' in descrs[serverid]:
                    for name in descrs[serverid]['ParamNames']:
                        cableserver += '{0}{1}'.format(':', server_ctx['Parameters'][name])
                cableservers.append(cableserver)
                if url == cableserver:
                    exec_in_dispatch_thread(tcf_jtag.jtagcable_close_server, server_ctx['ID'])
                    return
            raise Exception(f"unknown server, must be : {', '.join(cableservers)}") from None

        cables = {}
        for id, data in cablectx_data.items():
            if 'ID' not in data or 'ServerID' not in data or 'isActive' not in data or data['isActive'] is False:
                continue
            serverctx = data['ServerID']
            if serverctx not in serverctx_data.keys():
                continue
            server = serverctx_data[serverctx]
            if 'ID' not in server or 'ServerID' not in server or 'isActive' not in server or \
                    server['isActive'] is False:
                continue
            serverid = server['ServerID']
            cableserver = serverid
            if 'ParamNames' in descrs[serverid]:
                for name in descrs[serverid]['ParamNames']:
                    val = server['Parameters'][name]
                    cableserver += f":{val}"
            cables.update({cableserver: 1})

        result = ''
        for serverid, data in serverctx_data.items():
            if 'ID' not in data or 'ServerID' not in data or 'isActive' not in data and data['isActive'] is False:
                continue
            serverid = data['ServerID']
            cableserver = serverid
            if 'ParamNames' in descrs[serverid]:
                for name in descrs[serverid]['ParamNames']:
                    val = data['Parameters'][name]
                    cableserver += f":{val}"
            n = 0
            if cableserver in cables.keys():
                n = cables[cableserver]
            result += '{0}{1}{2}{3:d}{4}'.format(' ' * 3, cableserver, ' cables ', n, '\n')
        print(result)

    add_function_metadata('jtag servers', 'List, open or close JTAG servers.', 'jtag', 'Jtag')

    def sequence(self):
        """
sequence:
    Create JTAG sequence object to work with other jtag sequence commands.

prototype:
    jseq = jtag_target.sequence()

description:
    The jtag sequence command creates a new sequence object.  After
    creation the sequence is empty.  The following sequence object
    commands are available:

    jseq.state(state = <state>, count = <clock>)
        Move JTAG state machine to <new-state> and then generate
        <count> JTAG clocks.  If <clock> is given and <new-state> is
        not a looping state (RESET, IDLE, IRSHIFT, IRPAUSE, DRSHIFT or
        DRPAUSE), the state machine will move towards RESET state.
        Returns:
            None
        Example:
            jseq.state('RESET')

    jseq.irshift(capture: bool, *kwargs)
    jseq.drshift(capture: bool,*kwargs)
        Shift data in IRSHIFT or DRSHIFT state.  Data is either given
        as the last argument or if -tdi option is given then data will
        be all zeros or all ones depending on the argument given to
        -tdi.  The <bit_len> and <data> arguments are not used for
        irshift when the -register option is specified. Available
        keyword arguments:
        register=<name>
            Select instruction register by name.  This option is only
            supported for irshift.
        tdi=<value>
            TDI value to use for all clocks in SHIFT state.
        bit_len=<bit_length>
            bit length of data.
        data=<data>
            Format of <data> is an integer/hex/binary/bits.  The least
            significant bit of data is shifted first.Example for data
            field is data=0b01010010 or data='01010010' or
            data=0xAABBCCDD or data=5543453
        capture=<True/False>
            Capture TDO data during shift and return from sequence run
            command.
        state=<new-state>
            State to enter after shift is complete.  The default is RESET.
        Returns:
            None
        Example:
            jseq.drshift(False, state="DRUPDATE", bit_len=8, data=0b01010010)
            jseq.drshift(state="DRUPDATE", bit_len=8, data='01010010')
            jseq.drshift(state="DRUPDATE", bit_len=32, data=0xAABBCCDD)
            jseq.drshift(state="DRUPDATE", bit_len=32, data=5543453)
            jseq.drshift(state='IDLE', tdi=6, bit_len=2)
            jseq.irshift(register='bypass', state="IRUPDATE")

    jseq.delay(delay = <usec>)
        Generate delay between sequence commands.  No JTAG clocks will
        be generated during the delay.  The delay is guaranteed to be
        at least <usec> microseconds, but can be longer for cables
        that do not support delays without generating JTAG clocks.
        Returns:
            None
        Examples:
            jseq.delay(1000)

    jseq.get_pin(name = <pin>)
        Get value of <pin>.  Supported pins are cable specific.
        Returns:
            Pin value
        Examples:
            jseq.get_pin('TDI')

    jseq.set_pin(name = <pin>, value = <val>)
        Set value of <pin> to <value>.  Supported pins are cable
        specific.
        Returns:
            None
        Examples:
            jseq.set_pin('TDI', 1)

    jseq.atomic(enable = <bool>)
        Set or clear atomic sequences.  This is useful to creating
        sequences that are guaranteed to run with precise timing or
        fail.  Atomic sequences should be as short as possible to
        minimize the risk of failure.
        Returns:
            None
        Examples:
            jseq.atomic(True)

    jseq.run(*args, **kwargs)
        Run JTAG operations in sequence for the currently selected
        jtag target.  This command will return the result from shift
        commands using -capture option and from get_pin commands.
        Available options:
        --binary
            Format return value(s) as binary.  The first bit shifted
            out is the least significant bit in the first byte
            returned.
        --integer
            Format return values(s) as integer.  The first bit shifted
            out is the least significant bit of the integer.
        --bits
            Format return value(s) as binary text string.  The first
            bit shifted out is the first character in the string.
        --hex
            Format return value(s) as hexadecimal text string.  The
            first bit shifted out is the least significant bit of the
            first byte of the in the string.
        --single
            Combine all return values as a single piece of data.
            Without this option the return value is a list with one
            entry for every shift with -capture and every get_pin.
        --detect
            Force scan chain detection on next unlock.
        type=<type>
            Type of sequence
        Returns:
            Result data in desired form.
        Examples:
            result = jseq.run()
            result = jseq.run('--binary')
            result = jseq.run('--bits')
            result = jseq.run('--single')
            result = jseq.run("--single", '--integer')

    jseq.clear()
        Remove all commands from sequence.
        Returns:
            None
        Examples:
            jseq.clear()

    del jseq
        Delete sequence.

Arguments: NA

Returns:
    Jtag sequence object.

Examples:
    jtag = session.jtag_targets(3)
    jseq = jtag.sequence()
    jseq.state('RESET')
    jseq.irshift(state='IRUPDATE', register='bypass')
    jseq.drshift(state="DRUPDATE", bit_len=4, data=1)
    jseq.delay(100)
    jseq.clear()
    del jseq

Interactive mode examples:
    jtag sequence
    jtagseq state RESET
    jtagseq delay 100
    jtagseq atomic
    jtagseq get_pin TDI
    jtagseq set_pin TDI 0
    jtagseq drshift -capture True -state IDLE -tdi 0 -bit_len 2
    jtagseq run -binary
    jtagseq clear
        """
        node = self.__get_current_node()
        if node is None:
            raise Exception(f"Invalid jtag target, select a target using jtag_targets function.") from None

        name = '{0}{1:d}'.format('jtagseq#', self.session.jtag_seq_id)
        self.session.jtag_seq_id += 1
        self.session._jtagseq_node = JtagSequence(self.session, name, self.ctx, node)
        return self.session._jtagseq_node

    add_function_metadata('jtag sequence', 'Create JTAG sequence object.', 'jtag', 'Jtag')


class JtagSequence(object):
    jtag_states = ["RESET", "IDLE", "DRSELECT", "DRCAPTURE", "DRSHIFT", "DREXIT1",
                   "DRPAUSE", "DREXIT2", "DRUPDATE", "IRSELECT", "IRCAPTURE", "IRSHIFT",
                   "IREXIT1", "IRPAUSE", "IREXIT2", "IRUPDATE"]

    def __init__(self, session, name, ctx, jtag_node: TcfJtagNodeExecContext):
        self.session = session
        self.jtag_ctx_id = ctx
        self.ctx = name
        self.jtag_node = jtag_node
        self.jtag_ctx = jtag_node.get_context_data().props
        self._commands = list()
        self._data = bytearray()

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(JtagSequence) if callable(getattr(JtagSequence, method)) if
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

    def state(self, state: str, count: int = 0):
        """
state:
    Move JTAG state machine to <new_state> and then generate <count>
    JTAG clocks. If <clock> is given and <new-state> is not a looping
    state (RESET, IDLE, IRSHIFT, IRPAUSE, DRSHIFT or DRPAUSE) then
    state machine will move towards RESET state.

Prototype:
    jseq.state(state = <state>, count = <clock>)

Required Arguments:
    state = <state>
        state ('RESET', 'IDLE', 'IRSHIFT', 'IRPAUSE', 'DRSHIFT'
         or 'DRPAUSE')

Optional Arguments:
    count = <clock>
        Number of JTAG clocks to be generated.

Returns:
    None

Examples:
    jseq.state('RESET')
        """
        if state not in self.jtag_states:
            raise Exception(f'state {state} doesnot exist') from None
        self._commands.append(["state", state, count])

    def delay(self, val: int):
        """
delay:
    Generate delay between sequence commands. No JTAG clocks will be
    generated during the delay.

Prototype:
    jseq.delay(delay = <usec>)

Required Arguments:
    delay = <usec>
        Delay in microseconds. The delay is guaranteed to be at least
        <usec> microseconds, but can be longer for cables that do not
        support delays without generating JTAG clocks.

Returns:
    None

Examples:
    jseq.delay(1000)
        """
        self._commands.append(["delay", val])

    def get_pin(self, name: str):
        """
get_pin:
    Get value of <pin>. Supported pins are cable specific.

Prototype:
    jseq.get_pin(name = <pin>)

Required Arguments:
    name = <pin>
        Pin name whose value is to be extracted.

Returns:
    Pin value

Examples:
    jseq.get_pin('TDI')
        """
        self._commands.append(["getPin", name])

    def set_pin(self, name: str, value: int):
        """
set_pin:
    Set the value of <pin>. Supported pins are cable specific.

Prototype:
    jseq.set_pin(name = <pin>, value = <val>)

Required Arguments:
    name = <pin>
        Pin name whose value is to be set.

    value = <val>
        New value of the pin.

Returns:
    None

Examples:
    jseq.set_pin('TDI', 1)
        """
        self._commands.append(["setPin", name, value])

    def atomic(self, enable: bool = True):
        """
atomic:
    Set or clear atomic sequences. This is useful to creating sequences
    that are guaranteed to run with precise timing or fail. Atomic
    sequences should be as short as possible to minimize the risk of
    failure.

Prototype:
    jseq.atomic(enable = <bool>)

Optional Arguments:
    enable = <bool>
        Set enable to set the atomic sequences. False for clearing the
        sequences. Enable is true (default).

Returns:
    None

Examples:
    jseq.atomic(True)
        """
        self._commands.append(["atomic", enable])

    # def progress(self, id: int):
    #     self._commands.append(["progress", id])

    def clear(self):
        """
clear:
    Remove all commands from sequence.

Prototype:
    jseq.clear()

Arguments:
    None

Returns:
    None

Examples:
    jseq.clear()
        """
        self._commands.clear()
        self._data = bytearray()

    def __shift(self, capture: bool, shift_type: str, **kwargs):
        reg = 1 if 'register' in kwargs else 0
        tdi = 1 if 'tdi' in kwargs else 0
        data = 1 if 'data' in kwargs else 0
        if reg == 1 and shift_type != 'i':
            raise Exception("register is only valid for irshift") from None

        props = {}
        if reg + tdi + data == 0:
            props['tdi'] = 0
        if 'compare' in kwargs or 'mask' in kwargs:
            props['compare'] = kwargs.pop("compare") if 'compare' in kwargs else 0
            props['mask'] = kwargs.pop("mask") if 'mask' in kwargs else -1
        if 'state' in kwargs:
            props['state'] = kwargs.pop("state")
            if props['state'] not in self.jtag_states:
                state = props['state']
                raise Exception(f'state {state} doesnot exist') from None
        if 'data' in kwargs:
            props['data'] = kwargs.pop("data")
        if reg:
            props['reg'] = kwargs.pop("register")
        if tdi:
            props['tdi'] = kwargs.pop("tdi")
            props['tdi'] = check_int(props['tdi'])
        if 'bit_len' in kwargs:
            props['bit_len'] = kwargs.pop("bit_len")
            props['bit_len'] = check_int(props['bit_len'])
        else:
            if shift_type == 'd':
                raise Exception("bit_len is needed for drshift") from None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if 'tdi' in props:
            if 'bit_len' not in props:
                raise Exception('Wrong # args: should be \'shift \'[options\'] bit_len\'') from None
        elif 'reg' in props:
            props['bit_len'] = self.jtag_ctx['irLen'] if 'irLen' in self.jtag_ctx else 0
            devprops = dict()
            if self.jtag_ctx['irLen'] > 0 and 'idCode' in self.jtag_ctx:
                devprops = exec_in_dispatch_thread(self.jtag_node.get_jtag_device_node().get_jtag_devices_properties,
                                                   self.jtag_ctx['idCode'])
            register = '{0}{1}'.format('reg.', props['reg'])
            if register not in devprops.keys():
                reg_list = list()
                register = register.lstrip('reg.')
                for key in devprops.keys():
                    if key.startswith('reg.'):
                        reg_list.append(key.lstrip('reg.'))
                raise Exception(f'Unknown or ambiguous register name \'{register}\': must be {reg_list}') from None
            else:
                props['data'] = devprops[register]
        else:
            if 'bit_len' not in props or 'data' not in props:
                raise Exception('Wrong # args: should be \'shift \'[options\'] bit_len data\'') from None

            if isinstance(props['data'], str):  # binary string
                props['data'] = int(props['data'][::-1], 2)

        shift_command = ["shift", shift_type, capture, props['bit_len']]
        shift_options = dict()
        if 'state' in props:
            shift_options['state'] = props['state']
        if 'data' in props:
            if isinstance(props['data'], (bytes, bytearray)) is True:
                # Append data to object's member variable. Size should be ceil of size in bits / 8.
                self._data += props['data'][: -(props['bit_len'] // -8)]
            else:
                # If data is not in bytearray format convert it to bytes and append to object's member variable
                truncated_data = props['data'] & ((1 << props['bit_len']) - 1)
                self._data += truncated_data.to_bytes(-(props['bit_len'] // -8), sys.byteorder)
        else:
            shift_options["value"] = props['tdi']

        shift_command.append(shift_options)
        self._commands.append(shift_command)

    def irshift(self, capture: bool = False, **kwargs):
        """
irshift:
    Shift data in IRSHIFT state. Data is either given as the last
    argument or if -tdi option is given then data will be all zeros
    or all ones depending on the argument given to -tdi.

Prototype:
    jseq.irshift(capture : bool, *kwargs)

Arguments
    Capture
        Capture TDO data during shift and return from sequence run
        command. Default is True
    kwargs:
        state
            State to enter after shift is complete.  The default is
            'RESET'.
        register
            Select instruction register by name. This option is only
            supported for irshift.
        tdi
            TDI value to use for all clocks in SHIFT state.

Returns:
    None

Examples:
    jseq.irshift(register='bypass', state="IRUPDATE")
    jseq.irshift(tdi=0, bit_len=256)
        """
        self.__shift(capture, shift_type='i', **kwargs)

    def drshift(self, capture: bool = False, **kwargs):
        """
drshift:
    Shift data in DRSHIFT state. Data is either given as the last
    argument or if -tdi option is given then data will be all zeros
    or all ones depending on the argument given to -tdi.

Prototype:
    jseq.drshift(capture: bool,*kwargs)

Arguments
    capture
        Capture TDO data during shift and return from sequence run
        command.
    kwargs:
        state
            State to enter after shift is complete.  The default is
            RESET.
        register
            Select instruction register by name. This option is only
            supported for irshift.
        tdi
            TDI value to use for all clocks in SHIFT state.

Returns:
    None

Examples:
    jseq.drshift(False, state="DRUPDATE", bit_len=8, data=0b01010010)
    jseq.drshift(state="DRUPDATE", bit_len=8, data='01010010')
    jseq.drshift(state="DRUPDATE", bit_len=32, data=0xAABBCCDD)
    jseq.drshift(state="DRUPDATE", bit_len=32, data=5543453)
    jseq.drshift(state='IDLE', tdi=6, bit_len=2)
        """
        self.__shift(capture, shift_type='d', **kwargs)

    def run(self, *args, **kwargs):
        """
run:
    Run JTAG operations in sequence for the currently selected jtag
    target.

Prototype:
    jseq.run(*args, **kwargs)

Options:
    -bin
        Format of data is binary.

    -bits
        Format of data is a binary text string. The first bit in the
        string is shifted first.

    -hex
        Format of data is a hexadecimal text string. The least
        significant bit of the first byte in the string is shifted
        first.

    -int
        Format of data is an integer. The least significant bit of data
        is shifted first.

    -single
            Combine all return values as a single piece of data.
            Without this option the return value is a list with one
            entry for every shift with -capture and every get_pin.

    -detect
            Force scan chain detection on next unlock.
Optional Arguments:
    kwargs:
        type
            Type of sequence.

Returns:
    Result data in desired form.

Examples:
    result = jseq.run()
    result = jseq.run('--binary')
    result = jseq.run('--bits')
    result = jseq.run('--single')
    result = jseq.run("--single", '--integer')
        """
        parser = argparse.ArgumentParser(description='Jtag sequence run')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--binary', action='store_true', help='return binary data')
        group.add_argument('-b', '--bits', action='store_true', help='return binary string data')
        group.add_argument('--hex', action='store_true', help='return hex data')
        group.add_argument('-i', '--integer', action='store_true', help='return int data')
        parser.add_argument('-d', '--detect', action='store_true', help='force scan chain detection on next unlock')
        parser.add_argument('-s', '--single', action='store_true', help='return a single data value')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        params = dict()
        if parsed_args.detect is True:
            params['detect'] = 1
        if 'type' in kwargs:
            params['type'] = kwargs.pop('type')
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        tcf_jtag = TcfJtag(self.session)
        seq_result = exec_in_dispatch_thread(tcf_jtag.jtag_sequence, self.jtag_ctx_id, params, self._commands, self._data)

        index = 0
        res = list()
        if parsed_args.single is False:
            for command in self._commands:
                if command[0] == "shift":
                    if command[2] is False:
                        continue
                    size_in_bytes = -(command[3] // -8)
                    result = seq_result[index: index + size_in_bytes]
                    index += size_in_bytes
                elif command[0] == "getPin":
                    size_in_bytes = 1
                    result = seq_result[index: index + size_in_bytes]
                    index += size_in_bytes
                else:
                    continue
                bits = command[3]
                byte_list = list(result)
                int_val = 0
                for c in reversed(byte_list):
                    int_val = (int_val << 8) + c
                if parsed_args.hex is True:
                    res.append("{0:0{1}x}".format(int.from_bytes(result, 'big'), (size_in_bytes * 2)))
                elif parsed_args.integer is True:
                    res.append(int_val)
                elif parsed_args.binary is True:
                    res.append(result)
                elif parsed_args.bits is True:
                    res.append((bin(int_val)[2:].zfill(bits))[::-1])
            if len(res) == 1:
                return res[0]
            else:
                return res
        else:
            size_in_bytes = len(seq_result)
            byte_list = list(seq_result)
            int_val = 0
            for c in reversed(byte_list):
                int_val = (int_val << 8) + c
            if parsed_args.hex is True:
                return "{0:0{1}x}".format(int.from_bytes(seq_result, 'big'), (size_in_bytes * 2))
            elif parsed_args.integer is True:
                return int_val
            elif parsed_args.binary is True:
                return seq_result
            elif parsed_args.bits is True:
                return (bin(int_val)[2:].zfill(size_in_bytes * 8))[::-1]

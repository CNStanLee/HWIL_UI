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

# !/usr/bin/env python3
import argparse
import atexit
import fnmatch
import json
import os
import queue
import re
import socket
import subprocess
import time
from subprocess import PIPE
from io import StringIO
import shlex
import platform

import tcf
import xsdb
from xsdb import _xsdb
from xsdb import _svf
from subprocess import Popen

from xsdb import _tfile, _stapl, _jtag
from xsdb._jtag import Jtag
from xsdb._stapl import Stapl
from xsdb._tcf_gdbremote import TcfGdbRemote
from xsdb._tcf_jtag import TcfJtag
from xsdb._tcf_memsock import TcfMemSock
from xsdb._tfile import TFile
from xsdb._svf import SVF
from xsdb._logger import *
from xsdb._utils import *
from xsdb._target import Target
from xsdb._tcf_model import TcfModel
from xsdb._tcf_node import TcfNode
from xsdb._tcf_node_launch import TcfNodeLaunch
from xsdb._tcf_context_params import TcfContextParams
from tcf.services import xicom as xicom_service
from tcf.services import jtag as jtag_service

trace_listener = 0

# TODO : to be removed. This is added to ease the merges between rigel and xsdb_python repos
rigel = 1

# LOGGING_LEVEL = logging.DEBUG
LOGGING_LEVEL = logging.INFO

__all__ = ("start_debug_session", "interactive", "dispose", "help")
debug_session = None


#################################################################################################
#   Creates a session object.
#   Commands specific to session object.
#################################################################################################

class Session(Target, Jtag):
    model = None
    _targets = []
    _jtag_targets = []
    __nodes = {}

    def __init__(self):
        self.curchan = None
        self.curtarget = None
        self.cur_jtag_target = None
        self.current_node = None
        self.current_jtag_node = None
        self._jtagseq_node = None
        self._force_mem_accesses = 0
        self._stream_sock_poll_delay = 50000
        self._silent_mode = False
        self._enable_source_line_view = True
        self._bptable = {}
        self._bpid = 0
        self._mem_targets = {}
        self.__xsdbserver_table = {'start': 0}
        self.__channel_map = {}
        self._memmaptable = {}
        self._stapl_node = None
        self._svf_node = None
        self._expr_table = {}
        self._expr_list = {}
        self.__channel_id = 0
        self._curchan_obj = None
        self.stream_table = {}
        self.mb_profile_config = dict()
        self.profile_config = dict()
        self.mbtrace_obj = None
        self.gprof = None
        self.mb_trace_config = dict()
        self.mbprofiler = None
        self.reset_warnings = 1
        self.jtag_seq_id = 0
        self.ipxactfiles = dict()
        self.subsystem_activate_warnings = 1
        self.ipi_channel_mask_warnings = 1
        self.session = None
        self.pmccmds = dict()
        self._tfile_node = None
        self._add_plm_log_msg = 1
        self.deferred_queue = queue.Queue()
        self.__jtag_targets = {}
        #_logger.init_logger(LOGGING_LEVEL)
        threading.Thread(target=self.__deferred_thread, name="deferred_thread", daemon=True).start()

    # Support partial functions
    def __getattr__(self, name):
        global debug_session

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(debug_session) if callable(getattr(debug_session, method)) if
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

    def __deferred_thread(self):
        while True:
            self.deferred_queue.get()()

    def process_interactive_cmds(self, cmd, subcmd, arg_list, debug_session, return_arg):
        args = list()
        pos = 0
        if cmd == 'tfile' and subcmd in ('read', 'write', 'close', 'readdir', 'fstat', 'fsetstat'):
            args.append(return_arg)
            pos = pos + 1
        kwargs = dict()
        prev = ""
        list_arg = 0
        string_arg = 0
        string_arg_data = ''
        for arg in arg_list:
            if prev == "":
                prev = arg
                continue
            else:
                if prev[0] == '-':
                    if arg[0] == '-':
                        if prev[1] != '-' and len(prev) != 2:
                            args.append(f'-{prev}')
                        else:
                            args.append(prev)
                        prev = arg
                    else:
                        # Process String Arg
                        if (arg[0] == '\'' or arg[0] == '\"') and list_arg == 0:
                            string_arg = 1
                        if string_arg == 1:
                            if arg[0] in ('\'', '\"'):
                                if arg[-1] in ('\'', '\"'):
                                    string_arg_data = string_arg_data + arg[1:-1]
                                    string_arg = 0
                                    kwargs[prev[1:]] = string_arg_data
                                    string_arg_data = ''
                                    prev = ''
                                else:
                                    string_arg_data = string_arg_data + arg[1:]

                            elif arg[-1] in ('\'', '\"'):
                                string_arg_data = string_arg_data + arg[:-1]
                                string_arg = 0
                                kwargs[prev[1:]] = string_arg_data
                                string_arg_data = ''
                                prev = ''
                            else:
                                string_arg_data = string_arg_data + arg
                            continue

                        # process list of lists arg
                        if arg.startswith('[[') and string_arg == 0:
                            arg = arg.replace(',', ', ')
                            kwargs[prev[1:]] = [item.strip("[]").split(", ") for item in
                                                arg.strip("[]").split("], [")]
                            prev = ""
                            continue

                        # Process List Arg
                        if arg[0] == '[' and string_arg == 0:
                            arg = arg.replace(',', ', ')
                            kwargs[prev[1:]] = [item for item in arg.strip("[]").split(", ")]
                            prev = ""
                            continue

                        # Process Normal Arg
                        else:
                            if isinstance(arg, str):
                                if arg.startswith('0x'):
                                    arg = int(arg, 16)
                                elif arg.isnumeric():
                                    arg = int(arg)
                            kwargs[prev[1:]] = arg
                            prev = ""
                else:
                    prev = prev.replace('\'', '') if prev[0] == '\'' else prev.replace('\"', '')
                    args.insert(pos, prev)
                    pos += 1
                    prev = arg

        if prev != "":
            if prev[0] == '-':
                if prev[1] != '-' and len(prev) != 2:
                    args.append(f'-{prev}')
                else:
                    args.append(prev)
            else:
                prev = prev.replace('\'', '') if prev[0] == '\'' else prev.replace('\"', '')
                args.insert(pos, prev)

        # convert kwargs values to integers if any
        i = 0
        for val in args.copy():
            if isinstance(val, str):
                if val.isnumeric():
                    args[i] = int(val)
                if val.startswith('0x'):
                    args[i] = int(val, 16)
            i = i + 1

        for name, value in kwargs.items():
            if isinstance(value, list):
                i = 0
                for n in value.copy():
                    if isinstance(n, list):
                        value[i] = [int(x, 16) if x.startswith('0x') else int(x) for x in n]
                    elif n.isnumeric():
                        value[i] = int(n)
                    elif n.startswith('0x'):
                        value[i] = int(n, 16)
                    elif n.startswith('\'{'):
                        n = n.replace('\'{', '').replace('}\'', '').replace(' ', '').replace(',', ' ')
                        value[i] = dict(i.split(":") for i in shlex.split(n))
                        for k, v in value[i].items():
                            if isinstance(v, str):
                                if v.isnumeric():
                                    value[i].update({k: int(v)})
                                if v.startswith('0x'):
                                    value[i].update({k: int(v, 16)})
                    i = i + 1
            else:
                if isinstance(value, str):
                    if value.isnumeric():
                        kwargs[name] = int(value)
                    if value.startswith('0x'):
                        kwargs[name] = int(value, 16)
                    if value.startswith('{'):
                        value = value.replace('{', '').replace('}', '').replace(' ', '').replace(',', ' ')
                        kwargs[name] = dict(i.split(":") for i in shlex.split(value))
                        for k, v in kwargs[name].copy().items():
                            if isinstance(v, str):
                                if v.isnumeric():
                                    kwargs[name].update({k: int(v)})
                                if v.startswith('0x'):
                                    kwargs[name].update({k: int(v, 16)})
        try:
            if cmd in ('tfile', 'stapl', 'svf', 'jtagseq') and subcmd is not None:
                node = "_" + cmd + "_node"
                if getattr(debug_session, node) is None:
                    getattr(debug_session, cmd)()
                ret = getattr(getattr(debug_session, node), subcmd)(*args, **kwargs)
            else:
                ret = getattr(debug_session, cmd)(*args, **kwargs)
            if ret is not None:
                return ret
            else:
                return None
        except Exception as e:
            return e

    def get_target_state(self, run):
        node = run.arg
        if not node.get_run_state().validate(run):
            return False
        else:
            if node.get_run_state().getError() is not None:
                run.sync.done(error=node.get_run_state().getError().getAttributes()['Format'], result=None)
            data = node.get_run_state().getData()
            run.sync.done(error=None, result=data)
            return True

    def _get_targets(self, run):
        self.model.launch_node.clear_targets()
        ret_data = self.model.launch_node.get_targets(run, self.model.launch_node.get_root_children())
        if ret_data is None:
            return False
        else:
            if ret_data['error'] == '':
                self.model.launch_node.set_target_ids()
                run.sync.done(error=None, result=ret_data['data'])
            else:
                run.sync.done(error=ret_data['error'], result=None)
            return True

    def __print_targets(self, targets):
        result = ''
        # Sort the targets into a list of tuples
        tgt_list = sorted(targets.items(), key=lambda k_v: k_v[1]['target_id'])
        for target_ctx, target_dict in enumerate(tgt_list):
            target = target_dict[1]
            if target.get('id', None) != '':
                if result != '':
                    result += '\n'
                target_id = target.get('target_id', None)
                level = target.get('level', None)
                rc = target.get('run_context', None)
                name = rc.get('Name', None)
                info = ''
                if 'AdditionalInfo' in rc.keys():
                    name += rc.get('AdditionalInfo', None)
                state = target.get('run_state', None)
                if state is not None:
                    if state.is_suspended is False:
                        info = '(Running)'
                        if state.state_data != {}:
                            if 'StateName' in state.state_data.keys() and state.state_data.get('StateName', None):
                                info = '(' + state.state_data.get('StateName', None) + ')'
                    elif state.suspend_reason != "":
                        info = '(' + state.suspend_reason + ')'
                        if state.state_data != {} and 'Context' in state.state_data.keys():
                            info += ',' + state.state_data.get('Context', None)
                    else:
                        info = '(Suspended)'
                n = level * 3 + 3
                if self.curtarget is not None and target_id == self.curtarget.id:
                    active = '*'
                else:
                    active = ''
                result += "{0}{1:3d}{2:2s}{3} {4}".format(" " * n, target_id, active, name, info)
        return result

    def __launch_server(self, server, url):
        props = None
        cmd = server + ' -S -d -I10 -s ' + url
        p = subprocess.run([cmd], shell=True, stdout=PIPE, stderr=PIPE)
        out = p.stdout.decode().split("\n")
        err = p.stderr.decode().split("\n")[0]
        if err != '':
            raise Exception(err) from None
        for line in out:
            if line.startswith("Server-Properties"):
                props = json.loads(line.strip('Server-Properties: '))
                continue
            print(line)
        return props

    def connect(self, *args, host: str = '127.0.0.1', port: int = '3121', server: str = 'hw_server', **kwargs):
        """
connect:
    Connect to hw_server, xrt_server, or tcf-agent.

Prototype:
    channel = connect(host = <host_name/ip>, port = <port_num>,
                      server = <hw_server>, *args, **kwargs)

Arguments:
    host = <host name/ip>
        Name/IP address of the host machine where server is running

    port = <port num>
        TCP port number where the server is listening

    url = <url>
        URL of the server in 'tcp:<hostname>:<port>' format

    server = <server_name>
        Server executable to auto-start. Default is hw_server

    set = <channel-id>
        Set active connection to <channel-id>

    xvc_url = <url>
        Open Xilinx Virtual Cable connection

Options:
    --list
        List open connections

    --new
        Create a new connection, even one exist to the same url

    --symbols
        Launch symbol server to enable source level debugging
        for remote connections

Returns:
    Return value depends on arguments/options used.
    Channel ID, if connection is successful, or
    Exception, if the connection cannot be established
        When url, port or host is specified.
    List of open channels
        When list option is used.
    None
        When set option is used.

Examples:
    channel = session.connect('remotehost')
    session.connect(url="TCP:xhdbfarmrke9:3121")

Interactive mode examples:
    connect -host xhdbfarmrke9
    connect -list

        """
        parser = argparse.ArgumentParser(description='connect')
        parser.add_argument('-n', '--new', action='store_true',
                            help='create new connection even if one exist to the same url')
        parser.add_argument('-l', '--list', action='store_true', help='list connections')
        parser.add_argument('-s', '--symbols', action='store_true', help='enable symbol level debug')
        parser.add_argument('host', nargs='?', help='Host name')
        parser.add_argument('port', nargs='?', help='Port number')

        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.host is not None:
            host = parsed_args.host
        if parsed_args.port is not None:
            port = parsed_args.port
        port = check_int(port)

        if parsed_args.list is True:
            output = list()
            for channel_name, objects in self.__channel_map.items():
                peer = objects[0].remote_peer.attrs
                name = peer.get('TransportName') + ":" + peer.get('Host') + ":" + peer.get('Port')
                if channel_name == self.curchan:
                    active = '*'
                else:
                    active = ' '
                output.append("{0:3s}{1}{2}{3:2s}{4}".format('', active, channel_name, '', name))
            return output

        set_chan = kwargs.pop("set", None)
        if set_chan is not None:
            if set_chan in self.__channel_map.keys():
                self._curchan_obj = self.__channel_map[set_chan][0]
                self.model = self.__channel_map[set_chan][1]
                self.curchan = set_chan
            else:
                raise Exception(f'Channel {set_chan} is not available') from None
            return

        url = kwargs.pop("url", None)
        xvc_url = kwargs.pop("xvc_url", None)

        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if url is None:
            url = f'TCP:{host}:{port}'
        else:
            # TCF doesn't accept lower case "tcp", so replace "tcp" with "TCP"
            url = url.replace("tcp", "TCP")

        if rigel == 1:
            # TODO: remove after python porting is done
            if url is None:
                url = f'tcp:{host}:{port}'
            c = f'connect -url {url}'
            if xvc_url is not None:
                c += f' -xvc-url {xvc_url}'
            # if 'path' in kwargs:
            #     c += f' -path {kwargs.pop("path")}'
            c += f' -server {server}'
            try:
                _xsdb.cmd(c)
            except Exception as e:
                pass

        if parsed_args.symbols is True:
            # Use symbol server for remote connections
            props = self.__launch_server('symbol_server', 'tcp:127.0.0.1:0')
            if "Port" in props.keys():
                sym_url = "TCP:127.0.0.1:" + str(props.get("Port"))
            else:
                print("WARNING: Unable to launch symbol server")

        if parsed_args.new is False:
            for channel_name, objects in self.__channel_map.items():
                peer = objects[0].remote_peer.attrs
                name = peer.get('TransportName') + ":" + peer.get('Host') + ":" + peer.get('Port')
                if url == name:
                    self.curchan = channel_name
                    self.curtarget = None
                    self.current_node = None
                    self.model = objects[1]
                    return self.curchan
        try:
            chan = tcf.connect(url)
            if chan is not None:
                self._curchan_obj = chan
                self.model = TcfModel(chan, self.session)
                self.curchan = "tcfchan#" + str(self.__channel_id)
                self.curtarget = None
                self.current_node = None
                self.__channel_map[self.curchan] = [chan, self.model]
                self.__channel_id = self.__channel_id + 1
                if trace_listener == 1:
                    protocol.invokeAndWait(chan.addTraceListener, TraceListener())
                protocol.invokeAndWait(self.model.on_connected)
                exec_as_runnable(self._get_targets)
                print(self.curchan)
            else:
                raise Exception(f"Could not connect to the server") from None

        except Exception as e:
            if url != "TCP:127.0.0.1:0" and url != "TCP:127.0.0.1:3121":
                raise Exception(e)
            else:
                props = self.__launch_server(server, url)
                if url == "TCP:127.0.0.1:0":
                    if "Port" in props.keys():
                        url = "TCP:127.0.0.1:" + str(props.get("Port"))
                    else:
                        raise Exception(f"Unable to get port number of {server}") from None
                self.connect(url=url)

        if xvc_url is not None:
            fields = xvc_url.split(':')
            if len(fields) > 3:
                raise Exception(f'invalid xvc url, expected format tcp:host:port, got {xvc_url}') from None
            if fields[0].lower() == 'tcp':
                host = fields[1]
                port = fields[2]
                if host == '':
                    host = '127.0.0.1'
                if port == '':
                    port = '10200'
                arguments = {'host': host, 'port': port}
                tcf_jtag = TcfJtag(self.session)
                exec_in_dispatch_thread(tcf_jtag.jtagcable_open_server, 'xilinx-xvc', arguments)

        return self.curchan

    add_function_metadata('connect', 'Connect to hw_server, xrt_server or tcf-agent', 'connections', 'Session')

    def disconnect(self, chan: str = None):
        """
disconnect:
    Disconnect from the hw_server, xrt_server, or tcf-agent.

Prototype:
    disconnect(chan = <channel_id>)

Optional Arguments:
    chan = <channel_id>
        To disconnect from the specified channel id.
        Disconnect from the active connection. (Default)

Returns:
    None

Examples:
    session.disconnect()
    session.disconnect(chan)

Interactive mode examples:
    disconnect -chan tcfchan#0
    disconnect
        """

        if chan is None:
            chan = self.curchan
            if chan is None:
                raise Exception("No channel specified.") from None

        if rigel == 1:
            # TODO: Remove after porting all commands to python
            _xsdb.cmd(f'disconnect {chan}')

        if chan in self.__channel_map.keys():
            node = self.__channel_map.get(chan, None)
            if node[0].state == channel.STATE_OPEN:
                protocol.invokeAndWait(node[0].close)
                print(f'Info: {chan} closed.')
                if chan == self.curchan:
                    self.curchan = None
                    self.model = None
                    self.curtarget = None
                    self.current_node = None
                    del self._targets[:]
                    self.cur_jtag_target = None
                    self.current_jtag_node = None
                    self._jtagseq_node = None
                    self._mem_targets.clear()
                    self._stapl_node = None
                    self._svf_node = None
                    self._tfile_node = None
                    self._curchan_obj = None
                    self.pmccmds = dict()
                    self.jtag_seq_id = 0
                    self.ipxactfiles = dict()
                    self._bptable = {}
                    self._bpid = 0
                    self.mbprofiler = None
                    self.stream_table = {}
                    self.mb_profile_config = dict()
                    self.profile_config = dict()
                    self.gprof = None
                    self.mb_trace_config = dict()
                    self.mbtrace_obj = None
                    for node in self.__nodes:
                        del self.__nodes[node]
                del self.__channel_map[chan]
        else:
            raise Exception(f"Channel '{chan}' doesn't exist.") from None

    add_function_metadata('disconnect', 'Disconnect from the hw_server, xrt_server, or tcf-agent', 'connections',
                          'Session')

    def __get_curchan(self):
        if self.curchan is None:
            raise Exception(f"Invalid target, connect to hw_server/TCF agent using connect function") from None
        return self.curchan

    def __get_server_version(self, sync):

        class DoneHWCommand(xicom_service.DoneHWCommand):
            def __init__(self, sync):
                self.sync = sync

            def doneHW(self, token, error, args):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result=args)

        xsv = self._curchan_obj.getRemoteService(xicom_service.NAME)
        xsv.get_hw_server_version_info(DoneHWCommand(sync))

    def version(self, *args):
        """
version
    version [options]
        Get Vitis or hw_server version. When no option is specified,
        the Vitis build version is returned.
options
    -server
        Get the hw_server build version for the active connection.
returns
    Vitis or hw_server version, on success.
    Error string, if server version is requested when there is no connection.

Examples:
    session.version()

Interactive mode examples:
    version -s
        """
        parser = argparse.ArgumentParser(description='version')
        parser.add_argument('-s', '--server', action='store_true', help='Get hw_server version')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        if parsed_args.server is True:
            version = exec_in_dispatch_thread(self.__get_server_version)
            print(version['version'])
        # TODO print xsdb version here

    add_function_metadata('version', 'Get Vitis or hw_server version', 'connections', 'Session')

    def __filter_parser(self, text):
        pattern = r'''
            (?P<open_paren> \( ) |
            (?P<close_paren> \) ) |
            (?P<word> [A-Za-z_\-*#0-9\[\],:]+) |
            (?P<operator> [#=!~]+) |
            (?P<eof> $) |
            (?P<error> \S)
        '''
        scan = re.compile(pattern=pattern, flags=re.VERBOSE).finditer
        stack = [[]]

        for match in scan(text):
            token_type = match.lastgroup
            token = match.group(0)
            if token_type == 'open_paren':
                stack.append([])
            elif token_type == 'close_paren':
                top = stack.pop()
                stack[-1].append(top)
            elif token_type == 'word' or token_type == 'operator':
                stack[-1].append(token)
            elif token_type == 'whitespace':
                pass
            elif token_type == 'eof':
                break
            else:
                raise Exception("Error in filter expression")

        return stack

    def __match_filters(self, filter, props, case_insensitive=0):
        prop = filter[0].strip()
        op = filter[1].strip()
        pattern = filter[2].strip()

        if prop in props.keys():
            prop_value = props[prop]
            if isinstance(prop_value, int):
                prop_value = str(prop_value)
        else:
            raise Exception(f'property \'{prop}\' cannot be filtered. Use one of these {list(props.keys())}')

        if case_insensitive:
            prop_value = prop_value.lower()
            pattern = pattern.lower()

        # Check for operator
        if op == '==':
            return (prop_value == pattern)
        elif op == '!=':
            return (prop_value != pattern)
        elif op == '=~':
            return (fnmatch.fnmatch(prop_value, pattern) != 0)
        elif op == '!~':
            return (fnmatch.fnmatch(prop_value, pattern) == 0)
        else:
            raise Exception(f"Unhandled filter code ", op) from None

    result = False

    def __parse_filter_string(self, stack, props, level, case_insensitive):
        items = len(stack)
        conditions = []
        operator = []
        i = 0
        while i < items:
            operand = stack[i]
            for op in operand:
                if isinstance(op, list):
                    level += 1

            if level > 0:
                conditions.append(self.__parse_filter_string(operand, props, 0, case_insensitive))
                result = conditions[0]

            if level == 0:
                pattern = ""
                start = False
                formatted_operand = []
                for op in operand:
                    if re.match("([!=~])+", op):
                        start = True
                        formatted_operand.append(op)
                        continue
                    if start:
                        pattern += (op + " ")
                    else:
                        formatted_operand.append(op)
                formatted_operand.append(pattern)
                conditions.append(self.__match_filters(formatted_operand, props, case_insensitive))
                result = conditions[0]
            if i < items - 1:
                operator.append(stack[i + 1])
            i += 2
            level = 0

        for i in range(len(conditions) - 1):
            result = conditions[0]
            if operator[i] == 'and':
                result = result and conditions[i + 1]
            elif operator[i] == 'or':
                result = result or conditions[i + 1]
            else:
                raise Exception(f"Unknown operator ", operator) from None
        return result

    def __create_target_properties_dict(self, tgts):
        new_dict = {}
        for tgt in tgts.values():
            id = tgt.get('id')
            if id == "":
                continue
            new_dict[id] = {}
            new_dict[id]['ctx'] = tgt.get('id', None)
            new_dict[id]['target_id'] = tgt.get('target_id', None)
            new_dict[id]['level'] = tgt.get('level', None)
            new_dict[id]['parent'] = tgt.get('parent', None)
            rc = tgt.get('run_context', None)
            if rc is not None:
                new_dict[id]['name'] = rc.get('Name', None)
                new_dict[id]['parent_ctx'] = rc.get('ParentID', None)
                new_dict[id]['jtag_device_ctx'] = rc.get('JtagNodeID', None)
            state = tgt.get('run_state', None)
            new_dict[id]['state_reason'] = None
            if state is not None:
                new_dict[id]['state_reason'] = state.suspend_reason
        return new_dict

    def __get_device_indices(self, jtag_tgts, parent='', index=0, level=0):
        if parent not in jtag_tgts:
            return
        for ctx in jtag_tgts[parent]['children']:
            jc = jtag_tgts[ctx]['context']
            if jc['ParentID'] == '':
                index = 0
            if level == 1:
                node = jtag_tgts[ctx]
                node['props']['index'] = index
                index = index + 1
            self.__get_device_indices(jtag_tgts, ctx, index, level + 1)

    def __get_debug_targets_properties(self, tgts, jtag_tgts):
        tgts_properties_dict = {}
        port_descriptions = dict()
        self.__get_device_indices(jtag_tgts)
        jtag_ctx_node_map = self.model.launch_node.get_jtag_context_node_map()
        for ctx, tgt in tgts.items():
            if ctx == '':
                continue
            data = {'target_id': tgt['target_id'], 'target_ctx': tgt['id'], 'level': tgt['level'], 'name': '',
                    'parent_ctx': '', 'parent': '', 'state_reason': '', 'is_current': None, 'bscan': '',
                    'jtag_device_id': None, 'jtag_device_ctx': '', 'jtag_device_index': None, 'jtag_device_name': '',
                    'jtag_cable_id': None, 'jtag_cable_ctx': '', 'jtag_cable_name': '', 'jtag_cable_manufacturer': '',
                    'jtag_cable_product': '', 'jtag_cable_serial': ''}
            rc = tgt.get('run_context', None)
            if rc is not None:
                if 'Name' in rc.keys():
                    data['name'] = rc['Name']
                else:
                    data['name'] = tgt['id']
                if 'AdditionalInfo' in rc.keys():
                    data['name'] += rc['AdditionalInfo']
                data['parent_ctx'] = ""
                data['parent'] = ""
                if tgt['parent'] != "":
                    data['parent'] = tgt['parent']
                    data['parent_ctx'] = rc['ParentID']
                rs = tgt['run_state']
                reason = ''
                if rs is not None:
                    if rs.is_suspended is False:
                        if 'StateName' in rs.state_data:
                            reason = rs.state_data['StateName']
                        else:
                            reason = 'Running'
                    elif rs.is_suspended is True:
                        reason = rs.suspend_reason
                    else:
                        reason = "Stopped"
                data['state_reason'] = reason
                data['is_current'] = 0
                if self.curtarget is not None and self.curtarget.id == tgt['target_id']:
                    data['is_current'] = 1
                data['bscan'] = rc['JtagChain'] if 'JtagChain' in rc else ''
                jtaggroup = rc['JtagGroup'] if 'JtagGroup' in rc else None
                if jtaggroup is None:
                    tgts_properties_dict.update({ctx: data})
                    continue
                jtagrc = tgts[jtaggroup]['run_context']
                if jtagrc is not None and 'JtagNodeID' in jtagrc:
                    jtag_node_id = jtagrc['JtagNodeID']
                    node = jtag_tgts[jtag_node_id]
                    node_props = node['props']
                    data['jtag_device_id'] = node_props['node_id']
                    data['jtag_device_ctx'] = node_props['target_ctx']
                    data['jtag_device_index'] = node_props['index'] if 'index' in node_props else 0
                    if 'name' in node_props:
                        data['jtag_device_name'] = node_props['name']
                    while node['parent'] != "":
                        node = jtag_tgts[node['parent']]
                    data['jtag_cable_id'] = node['props']['node_id']
                    data['jtag_cable_ctx'] = node['props']['target_ctx']
                    data['jtag_cable_name'] = node['props']['jtag_cable_name']
                    jtag_node = jtag_ctx_node_map[data['jtag_cable_ctx']]
                    jtag_cable_node = jtag_node.get_jtag_cable_node()

                    if jtag_cable_node is not None:
                        exec_as_runnable(get_cache_data, jtag_cable_node.get_jtag_cable_open_servers())
                        if len(jtag_cable_node.jtag_cable_port_descriptions):
                            for server, server_node in jtag_cable_node.jtag_cable_port_descriptions.items():
                                port_descriptions.update({server: exec_as_runnable(get_cache_data, server_node)})
                    for server, port_desc in port_descriptions.items():
                        if len(port_desc):
                            port_desc = port_desc[0]
                            if port_desc['NodeID'] == data['jtag_cable_ctx']:
                                data['jtag_cable_manufacturer'] = port_desc['Manufacturer']
                                data['jtag_cable_product'] = port_desc['ProductID']
                                data['jtag_cable_serial'] = port_desc['Serial']
                                name = ''
                                if (('Description' in port_desc and port_desc['Description'] != "") and
                                        not ('isError' in port_desc and port_desc['isError']) and
                                        not ('isInitializing' in port_desc and port_desc['isInitializing'])):
                                    name = port_desc['Description']
                                    if 'Serial' in port_desc and port_desc['Serial'] != "":
                                        name = name + ' ' + port_desc['Serial']
                                else:
                                    if 'Manufacturer' in port_desc and port_desc['Manufacturer'] != "":
                                        name = port_desc['Manufacturer']
                                        if 'ProductID' in port_desc and port_desc['ProductID'] != "":
                                            name = name + ' ' + port_desc['ProductID']
                                        else:
                                            name = name + ' cable'
                                        if 'Serial' in port_desc and port_desc['Serial'] != "":
                                            name = name + ' ' + port_desc['Serial']
                                    elif 'ProductID' in port_desc and port_desc['ProductID'] != "":
                                        name = port_desc['ProductID']

                                data['jtag_cable_name'] = name
                                break
            tgts_properties_dict.update({ctx: data})
        return tgts_properties_dict

    def _get_target_obj(self, ctx_id):
        node = self.model.get_node(ctx_id)
        for t in self._targets:
            if ctx_id == t.ctx:
                return t
        t = _target.Target(self.curchan, ctx_id, node, debug_session)
        self._targets.append(t)
        return t

    def targets(self, *args, **kwargs):
        """
targets:
    List all targets or switch between targets.

Prototype:
    tlist = session.targets(**kwargs)
        List all the targets.
    session.targets(id = <target_id>, **kwargs)
        Select <target id> as active target.

Arguments:
    kwargs
        id = <target_id>
            Target to be selected as active target.

        index = <index>
            Include targets based on jtag scan chain position.
            This is identical to specifying -filter
            "jtag_device_index==<index>".

        timeout = <sec>
            Poll until the targets specified by filter option are found
            on the scan chain, or until timeout. This option is valid
            only with filter option. The timeout value is in seconds.
            Default timeout is 3 seconds.

        filter = <filter-expression>
            Specify filter expression to control which targets are
            included in list based on its properties. Filter
            expressions support operators ==, !=, =~, !~, and, or
            Strings must be quoted. String matching operators =~ and
            !~ match lhs string with rhs pattern using or string match.

Options:
    --set (-s)
        Set current target to entry single entry in list. This is
        useful in comibination with -filter option.  An error will
        be generate if list is empty or contains more than one entry.
    --nocase (-n)
        Use case insensitive filter matching
    --target-properties (-t)
        Returns a list of dictionaries containing target properties.

Returns:
    Return value depends on options used.
    Target list
        When target id is not mentioned.
    None
        When target id is mentioned.

Examples:
    session.ta() | session.targets()
        List all the targets.
    session.targets(id = 2)
        Set target with id 2 as active target.
    session.ta('-s', filter='name=~*A9*0')
        Set target whose name matches wildcard "*A9*0" as active target.
    session.targets("--set", filter='(name =~ MicroBlaze #0*) and (bscan==USER2)')
        Set target whose name matches wildcard "MicroBlaze #0*" and bscan is USER2.

Interactive mode examples:
    targets -id 2
    targets -set -filter '(name=~*A9*0)'
    ta -set -filter '(name=~*A9*0) and (parent == APU)'
    ta -target_properties -id 2
        """

        parser = argparse.ArgumentParser(description='targets')
        parser.add_argument('-s', '--set', action='store_true', help='O')
        parser.add_argument('-l', '--list', action='store_true', help='O')
        parser.add_argument('-t', '--target_properties', action='store_true', help='O')
        parser.add_argument('id', nargs='?', help='Target id')
        parser.add_argument('-n', '--nocase', action='store_true', help='Case insensitive match in filter')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))
        id = check_int(kwargs.pop("id")) if 'id' in kwargs else None
        filter = kwargs.pop("filter", None)
        timeout = 3000 if 'timeout' not in kwargs else check_int(kwargs.pop('timeout'))
        case_insensitive_match = 1 if parsed_args.nocase is True else 0
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if parsed_args.id is not None:
            if id is not None:
                raise Exception("Conflicting args: Specify target id either as positional arg or keyword arg")
            id = int(parsed_args.id)

        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        tgts = exec_as_runnable(self._get_targets)
        jtag_tgts = {}
        if jtag_service.NAME in sorted(protocol.invokeAndWait(self.session._curchan_obj.getRemoteServices)):
            jtag_tgts = exec_as_runnable(self.model.launch_node.jtag_targets)
        target_ctx_map = self.model.launch_node.get_target_context_map()
        debug_target_properties = self.__get_debug_targets_properties(tgts, jtag_tgts)
        if parsed_args.target_properties:
            tp = {}
            if id is None:
                return debug_target_properties
            else:
                tp.update({target_ctx_map[id]: debug_target_properties[target_ctx_map[id]]})
            return tp

        if id is not None:
            if id not in target_ctx_map.keys():
                raise Exception(f"No target with id {id}") from None
            node = self.model.get_node(target_ctx_map[id])
            ctx = node.get_run_context_data().getID()

            for t in self._targets:
                if ctx == t.ctx:
                    self.curtarget = t
                    self.current_node = node
                    t.node = node
                    return t
            t = _target.Target(self.curchan, id, node, debug_session)
            self._targets.append(t)
            self.curtarget = t
            self.current_node = node
            return t

        # Filter based on properties
        if filter is not None:
            ctx = None
            new_targets = []
            new_tgts = {}
            # TODO - proper handling
            # temp hack to add () if () are not present at the front and end of the filter string
            if filter[0] != '(':
                filter = '(' + filter + ')'
            if filter.count('(') != filter.count(')'):
                raise Exception('Braces missing in the filter option.') from None
            filter_stack_list = self.__filter_parser(filter)
            filter_stack = []
            for stk in filter_stack_list:
                if isinstance(stk, list):
                    filter_stack = stk
            start_time = round(time.time() * 1000)
            delta = 0
            while delta < timeout:
                for ctx_id, tgt in tgts.items():
                    if ctx_id == '':
                        continue
                    props = debug_target_properties[ctx_id]
                    if self.__parse_filter_string(filter_stack, props, 0, case_insensitive_match):
                        id = tgt['target_id']
                        ctx = tgt['id']
                        name = tgt['run_context']['Name']
                        new_targets.append(name)
                        new_tgts.update({ctx: tgt})
                if len(new_targets):
                    break
                tgts = exec_as_runnable(self._get_targets)
                target_ctx_map = self.model.launch_node.get_target_context_map()
                delta = round(time.time() * 1000) - start_time

            if parsed_args.set:
                if id is None or ctx is None:
                    raise Exception(f"No target with filter '{filter}'") from None
                if len(new_targets) > 1:
                    raise Exception(f"More than one targets with filter '{filter}':", new_targets) from None
                node = self.model.get_node(target_ctx_map[id])
                for t in self._targets:
                    if ctx == t.ctx:
                        self.curtarget = t
                        self.current_node = node
                        return t

                t = _target.Target(self.curchan, id, node, debug_session)
                self._targets.append(t)
                self.curtarget = t
                self.current_node = node
                return t
            else:
                tgts = new_tgts

        result = self.__print_targets(tgts)
        if parsed_args.list == 0:
            print(result)
        else:
            return result.split('\n')

    add_function_metadata('targets', 'List all targets or switch between targets', 'connections', 'Session')

    def get_context_target_map(self):
        return self.model.launch_node.get_context_target_map()

    def jtag_targets(self, *args, **kwargs):
        """
jtag_targets:
    List all JTAG targets or switch between JTAG targets.

Prototype:
    tlist = session.jtag_targets(**kwargs)
        List all JTAG targets.
    session.jtag_targets(id = <target_id>, **kwargs)
        Set jtag target with specified target id as active JTAG target.

Arguments:
    kwargs
        id = <target_id>
            Target to be selected as active target.

        timeout = <sec>
            Poll until the targets specified by filter option are found
            on the scan chain, or until timeout. This option is valid
            only with filter option. The timeout value is in seconds.
            Default timeout is 3 seconds.

        filter = <filter-expression>
            Specify filter expression to control which targets are
            included in list based on its properties. Filter
            expressions support operators ==, !=, =~, !~, and, or
            Strings must be quoted. String matching operators =~ and
            !~ match lhs string with rhs pattern using or string match.

Options:
    --set (-s)
        Set current target to entry single entry in list. This is
        useful in combination with -filter option.  An error will
        be generate if list is empty or contains more than one entry.
    --nocase (-n)
        Use case insensitive filter matching
    --target-properties (-t)
        Returns a list of dictionaries containing target properties.
    --open
        Open all targets in list.  List can be shorted by specifying
        target-ids and using filters.
    --close
        Close all targets in list.  List can be shorted by specifying
        target-ids and using filters.

Returns:
    Return value depends on options used.
    Jtag target list
        When target id is not mentioned.
    None
        When target id is mentioned.

    Filtered jtag targets list when filter option is used.
    Python list consisting of jtag target properties when
    target_properties is used.

    Exception:
        Failed to select the JTAG target.

Examples:
    tlist = session.jtag_targets()
        List all the targets.
    session.jtag_targets(id = 2)
        Select target with id 2 as active target.
    session.jtag_targets('-t')
        Display target properties of active target.

Interactive mode examples:
    jtag targets -id 1
    jtag ta -n -filter '(name == arm_dap)'
    jtag ta -t -id 1
        """

        parser = argparse.ArgumentParser(description='targets')
        parser.add_argument('id', nargs='?', help='Target id')
        parser.add_argument('-t', '--target_properties', action='store_true',
                            help='Return an array of dicts containing target properties')
        parser.add_argument('-s', '--set', action='store_true',
                            help='Set current target to single entry in filtered list')
        parser.add_argument('-o', '--open', action='store_true', help='Open all targets in list')
        parser.add_argument('-c', '--close', action='store_true', help='Closes all targets in list')
        parser.add_argument('-n', '--nocase', action='store_true', help='Case insensitive match in filter')
        parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose information')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        _services = sorted(protocol.invokeAndWait(self.session._curchan_obj.getRemoteServices))
        if jtag_service.NAME not in _services:
            return
        id = check_int(kwargs.pop("id")) if 'id' in kwargs else None
        filter = kwargs.pop("filter", None)
        timeout = 3000 if 'timeout' not in kwargs else check_int(kwargs.pop('timeout'))
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None

        if parsed_args.id is not None:
            if id is not None:
                raise Exception("Conflicting args: Specify target id either as positional arg or keyword arg")
            id = int(parsed_args.id)

        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        tgts = exec_as_runnable(self.model.launch_node.jtag_targets)
        target_ctx_map = self.model.launch_node.get_jtag_target_context_map()
        ctx_target_map = self.model.launch_node.get_jtag_context_target_map()
        ctx_node_map = self.model.launch_node.get_jtag_context_node_map()

        if parsed_args.verbose is False:
            new_tgts = dict()
            for ctx, data in tgts.items():
                if ctx != '' and data['props']['is_active']:
                    new_tgts.update({ctx: data})
            tgts = new_tgts

        tgts_properties_dict = {}
        for ctx, data in tgts.items():
            if ctx != '':
                tgts_properties_dict.update({ctx: data['props']})

        # Filter based on properties
        if filter is not None:
            # TODO - proper handling
            # temp hack to add () if () are not present at the front and end of the filter string
            if filter[0] != '(' and filter[-1] != ')':
                filter = '(' + filter + ')'
            if filter.count('(') != filter.count(')'):
                raise Exception('Braces missing in the filter option.') from None
            filter_stack_list = self.__filter_parser(filter)
            filter_stack = []
            for stk in filter_stack_list:
                if isinstance(stk, list):
                    filter_stack = stk
            new_targets = []
            new_tgts = {}
            case_insensitive_match = 1 if parsed_args.nocase is True else 0
            start_time = round(time.time() * 1000)
            delta = 0
            while delta < timeout:
                for ctx, props in tgts_properties_dict.items():
                    if self.__parse_filter_string(filter_stack, props, 0, case_insensitive_match):
                        new_targets.append(ctx_target_map[ctx])
                        new_tgts.update({ctx_target_map[ctx]: tgts[ctx]})
                if len(new_targets):
                    break
                tgts = exec_as_runnable(self.model.launch_node.jtag_targets)
                tgts_properties_dict = {}
                for ctx, data in tgts.items():
                    if ctx != '':
                        tgts_properties_dict.update({ctx: data['props']})
                delta = round(time.time() * 1000) - start_time

            if parsed_args.set is True:
                if len(new_targets) == 0:
                    raise Exception(f"No target with filter '{filter}'") from None
                if len(new_targets) > 1:
                    raise Exception(f"More than one targets with filter '{filter}':", new_targets) from None
                id = new_targets[0]
            else:
                tgts = new_tgts

        if parsed_args.open is True or parsed_args.close is True:
            for ctx, data in tgts.items():
                if ctx == '':
                    continue
                props = data['props']
                jtag_node = ctx_node_map[ctx]
                jtag_cable_node = jtag_node.get_jtag_cable_node()
                if jtag_cable_node is None:
                    continue
                if parsed_args.open is True and props['level'] == 0 and props['is_active'] and props['is_open'] == 0:
                    exec_in_dispatch_thread(jtag_cable_node.openport, ctx)
                elif parsed_args.close is True and props['level'] == 0 and props['is_active'] and props['is_open']:
                    exec_in_dispatch_thread(jtag_cable_node.closeport, ctx)
                protocol.invokeAndWait(jtag_cable_node.get_jtag_cable_context().reset)
            return None

        if parsed_args.target_properties is True:
            tp = {}
            if filter is not None:
                for tgt, prop in tgts.items():
                    tp.update({prop['id']: prop['props']})
                return tp
            if id is None:
                return tgts_properties_dict
            else:
                tp.update({target_ctx_map[id]: tgts[target_ctx_map[id]]['props']})
            return tp

        if id is not None:
            if id not in target_ctx_map.keys():
                raise Exception(f"No target with id {id}") from None
            node = self.model.get_node(target_ctx_map[id])
            ctx = target_ctx_map[id]
            for jt in self._jtag_targets:
                if ctx == jt.ctx:
                    self.cur_jtag_target = jt
                    self.current_jtag_node = node
                    return jt

            jt = _jtag.Jtag(self.curchan, id, node, debug_session)
            self._jtag_targets.append(jt)
            self.cur_jtag_target = jt
            self.current_jtag_node = node
            return jt

        print(self.model.launch_node.print_jtag_targets(tgts))

    add_function_metadata('jtag_targets', 'jtag devices', 'jtag', 'Session')

    def tfile(self):
        """
tfile:
    Create a TFile object to work with other TFile functions.

Prototype:
    session.tfile()

Returns:
    TFile object

Examples:
    tf = session.tfile()

Interactive mode examples:
    tfile
        """
        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        self._tfile_node = _tfile.TFile(debug_session)
        return self._tfile_node

    add_function_metadata('tfile', 'Create a TFile object to work with other TFile functions', 'tfile', 'Session')

    def stapl(self):
        """
stapl:
    Create a stapl object to work with other stapl functions.

Prototype:
    session.stapl()

Returns:
    stapl object

Examples:
    stapl = session.stapl()

Interactive mode examples:
    stapl
        """
        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        self._stapl_node = _stapl.Stapl(self.curchan, debug_session)
        return self._stapl_node

    add_function_metadata('stapl', 'Creates stapl object', '', 'Session')

    def gdb_connect(self, server, **kwargs):
        """
gdb_connect:
    Connect to GDB remote server.

Prototype:
    session.gdb_connect(server = <gdb_server>)

Optional Arguments:
    server = <gdb_server>

    kwargs
        multiprocess = 0/1
            Enable/disable multiprocess mode.
        extended = 0/1
            Enable/disable extended mode.
        auto_attach = 0/1
            Enable/disable auto attach mode.
        architecture = <arch>
            specify default architecture.
        osabi = <osabi>
            specify default osabi.
        log = <level>
            specify log level

Returns:
    None

Examples:
    session.gdb_connect('localhost:3121')

Interactive mode examples:
    gdb_connect -server localhost:3121
        """
        serverparams = dict()
        if 'multiprocess' in kwargs:
            serverparams.update({'multiprocess': check_int(kwargs.pop("multiprocess"))})
        if 'extended' in kwargs:
            serverparams.update({'extended': check_int(kwargs.pop("extended"))})
        if 'auto_attach' in kwargs:
            serverparams.update({'auto_attach': check_int(kwargs.pop("auto_attach"))})
        if 'architecture' in kwargs:
            serverparams.update({'architecture': kwargs.pop("architecture")})
        if 'osabi' in kwargs:
            serverparams.update({'osabi': kwargs.pop("osabi")})
        if 'log' in kwargs:
            serverparams.update({'log': check_int(kwargs.pop("log"))})
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        try:
            if 'GdbClient' not in sorted(protocol.invokeAndWait(self._curchan_obj.getRemoteServices)):
                raise Exception('launching xrt_server')
        except Exception as e:
            self.session.connect(server='xrt_server', port=0)

        fields = server.split(':')
        if fields[0].lower() == 'tcp':
            fields.remove(fields[0])
        serverparams['host'] = fields[0]
        serverparams['port'] = fields[1]
        if serverparams['host'] == '':
            serverparams['host'] = '127.0.0.1'
        gc = TcfGdbRemote(self.session)
        exec_in_dispatch_thread(gc.gdbclient_connect, serverparams)

    add_function_metadata('gdb_connect', 'Connect to GDB remote server', 'connections', 'Session')

    def gdb_disconnect(self, id: int = None):
        """
gdb_disconnect:
    Disconnect from GDB remote server.

Prototype:
    session.gdb_disconnect(target = <target_id>)

Optional Arguments:
    target = <target_id>
        To disconnect from the mentioned target_id.
        Disconnect from the active GDB remote server (Default).

Returns:
    None

Examples:
    session.gdb_disconnect(1)

Interactive mode examples:
    gdb_disconnect 1
        """
        tp = self.targets('-t')
        l0_tgt = None
        match = None
        if id is None:
            for tgt, props in tp.items():
                if 'level' in props and props['level'] == 0:
                    l0_tgt = props
                if 'is_current' in props and props['is_current'] == 1:
                    match = l0_tgt
                    break
        else:
            tid = check_int(id)
            for tgt, props in tp.items():
                if 'level' in props and props['level'] == 0:
                    l0_tgt = props
                if 'target_id' in props and props['target_id'] == tid:
                    match = l0_tgt
                    break
        if match is None or 'target_ctx' not in match or match['target_ctx'] == '':
            raise Exception('Invalid target. Use \'targets\' command to select a target') from None
        gc = TcfGdbRemote(self.session)
        exec_in_dispatch_thread(gc.gdbclient_disconnect, match['target_ctx'])

    add_function_metadata('gdb_disconnect', 'Disconnect from GDB remote server', 'connections', 'Session')

    def svf(self):
        """
svf:
    Create a svf object to work with other svf functions.

Prototype:
    svf_obj = svf()

Returns:
    svf object.

Examples:
    svf_obj = svf()

Interactive mode examples:
    svf
        """
        if self.curchan is None:
            raise Exception("Invalid target. Use 'connect' command to connect to hw_server/TCF agent")

        self._svf_node = _svf.SVF(self.curchan, debug_session)
        return self._svf_node

    add_function_metadata('svf', 'Create a svf object to work with other svf functions', 'svf', 'Session')

    def get_force_mem_accesses(self):
        return self._force_mem_accesses

    def set_force_mem_accesses(self, value):
        self._force_mem_accesses = value

    def get_source_line_view(self):
        return self._enable_source_line_view

    def set_source_line_view(self, value):
        self._enable_source_line_view = value

    def get_silent_mode(self):
        return self._silent_mode

    def set_silent_mode(self, value):
        if value > 2:
            raise Exception(
                f"Expected 0-2, got {value} instead\n  0 - display all info messages\n  1 - suppress progress info\n  2 - suppress progress and target status info\n") from None
        self._silent_mode = value

    def get_stream_sock_poll_delay(self):
        return self._stream_sock_poll_delay

    def set_stream_sock_poll_delay(self, value):
        self._stream_sock_poll_delay = value

    # Usage:
    # Get all parameters
    #   xsdpy.configparams()
    # Enable silent-mode
    #   xsdpy.configparams('silent-mode', 1)
    # Get silent-mode value
    #   xsdpy.configparams('silent-mode')
    # Get disable access value for target 2
    #   xsdpy.configparams('disable-access', id=2)
    # Disable access for target 2
    #   xsdpy.configparams('disable-access', 1, id=2)

    def configparams(self, *args, **kwargs):
        """
configparams
    List the name and description for available configuration
    parameters.  Configuration parameters can be global or
    connection specific, therefore the list of available
    configuration parameters and their value might change
    depending on the current connection.

    configparams(options, name)
        Get configuration parameter value(s).

    configparams(options, name, value)
        Set configuration parameter value.

Prototype:
    session.configparams(options, param, value)

Arguments:
    --all
        Include values for all contexts in result.

    param
        Specify context of value to get or set.

    value
        Specify target id or value to get or set.

Returns:
    Depends on the arguments specified.

    <none>
        List of parameters and description of each parameter.

    <parameter name>
        Parameter value or error, if unsupported parameter is specified.

    <parameter name> <parameter value>
        Nothing if the value is set, or error, if the unsupported parameter is
        specified.

Examples:
    session.configparams('force-mem-accesses', 1)
        Disable access protection for the <dow>, <mrd>, and <mwr> commands.

    session.configparams('xvc-capabilities', 'control')
        Write context parameters string xvc-capabilities

Interactive mode examples:
    configparams force-mem-accesses 1
    configparams force-mem-accesses
        """
        parser = argparse.ArgumentParser(description='Configure debugger parameters')
        parser.add_argument('-a', '--all', action='store_true', help='Include values for all contexts in result')
        parser.add_argument('param', nargs='?', help='Parameter name to get or set')
        parser.add_argument('value', nargs='?', help='Parameter value to set')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        param = parsed_args.param
        value = parsed_args.value

        defs = {}
        defs.update({'force-mem-accesses':
                         {'description': 'overwrite access proctection for all memory accesses performed from xsdb',
                          'type': 'boolean',
                          'getter': 'get_force_mem_accesses',
                          'setter': 'set_force_mem_accesses'
                          },
                     'source-line-view':
                         {'description': 'enable source line view while debugging an elf',
                          'type': 'boolean',
                          'getter': 'get_source_line_view',
                          'setter': 'set_source_line_view'
                          },
                     'silent-mode':
                         {'description': 'enable silent mode to suppress info messages',
                          'type': 'integer',
                          'minimum': 0,
                          'getter': 'get_silent_mode',
                          'setter': 'set_silent_mode'
                          },
                     'stream-sock-poll-delay':
                         {'description': 'delay between jtagterminal socket polls in milliseconds',
                          'type': 'integer',
                          'getter': 'get_stream_sock_poll_delay',
                          'setter': 'set_stream_sock_poll_delay'
                          }
                     })

        cp = TcfContextParams(self.session.curchan, self.session)
        defs.update(exec_in_dispatch_thread(cp.get_definitions))

        names = sorted(defs.keys())
        if parsed_args.param is None:
            result = ''
            for name in names:
                if name == 'sdk-launch-timeout' or name == 'vitis-launch-timeout':
                    continue
                data = defs[name]['description']
                if result != '':
                    result += '\n'
                result += '  ' + name.ljust(30) + '  ' + data
            print(result)
        else:
            ctx = ""
            if self.current_node and self.current_node.id is not None:
                ctx = self.current_node.id

            if param not in names:
                raise Exception(f"Unknown or ambiguous parameter {param}") from None
            if value is not None:
                type = defs[param].get('type', None)
                if type == 'integer':
                    if value is not None and value.isdigit():
                        value = int(value)
                    else:
                        raise Exception(f"Expected integer but got \'{value}\' for parameter \'{param}\'") from None
                    minimum = defs[param].get('minimum', None)
                    if minimum is not None:
                        if value < minimum:
                            raise Exception(f"Value must be greater than {minimum} for parameter \'{param}\'") from None
                if type == 'boolean':
                    if value == '1' or value == 'True':
                        value = True
                    elif value == '0' or value == 'False':
                        value = False
                    else:
                        raise Exception(
                            f"Expected boolean but got \'{value}\' for parameter {param}. Specify True/1 or False/0") from None
                if type == 'string':
                    if value is not None and value.isdigit():
                        raise Exception(f"Expected string but got \'{value}\' for parameter {param}.") from None
                setter = defs[param].get('setter', None)
                if setter:
                    getattr(self, setter)(value)
                else:
                    exec_in_dispatch_thread(cp.set, ctx, param, value)
                return
            getter = defs[param].get('getter', None)
            if getter:
                result = getattr(self, getter)()
            else:
                if parsed_args.all is True:
                    result = exec_in_dispatch_thread(cp.get_values, param)
                else:
                    result = exec_in_dispatch_thread(cp.get, ctx, param)
            print(result)

    add_function_metadata('configparams', 'List name and description for available config '
                                          'params', 'connections', 'Session')

    def __xsdb_server_thread(self, host, port):
        __xsdbserver_table = self.__xsdbserver_table
        debug_session = start_debug_session()
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        __xsdbserver_table['server'] = server
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.settimeout(1)
        server.bind((host, port))
        hostname = socket.gethostname()
        print(f'Connect to this XSDB server use host {hostname} and port {server.getsockname()[1]}')
        server.listen(10)
        while True:
            try:
                conn, port = server.accept()
            except Exception as e:
                if isinstance(e, OSError) and e.strerror == 'Bad file descriptor':
                    return
                continue
            print(f'new connection from {conn.getsockname()[0]}:{conn.getsockname()[1]}')
            ignore_once = 0
            __xsdbserver_table['chan'] = conn
            return_arg = None
            while True:
                sys.stdout = sys.__stdout__
                conn.settimeout(1)
                data = None
                try:
                    data = conn.recv(4096)
                except Exception as e:
                    if isinstance(e, socket.timeout):
                        continue
                    if isinstance(e, OSError) and e.strerror == 'Bad file descriptor':
                        break
                string = ''.join(map(chr, data))
                string = string.replace('\r', '').replace('\n', '')
                dict_strings = string.split('{')
                if len(dict_strings) != 1:
                    string = dict_strings[0]
                    for i in range(1, len(dict_strings)):
                        dict_end = dict_strings[i].split('}')
                        dict_end[0] = dict_end[0].replace('\'', '').replace(' ', '').replace(',', ', ')
                        string = string + '{' + dict_end[0] + '}' + dict_end[1]
                else:
                    string = dict_strings[0]
                string = string.replace('{', '\'{').replace('}', '}\'')
                result = StringIO()
                sys.stdout = result
                arg_list = [ele for ele in shlex.split(string, posix=False).copy() if ele.strip()]
                if len(arg_list) == 0:
                    continue
                k = 0
                cmd = arg_list[k].lower()
                subcmd = None
                if cmd == 'help':
                    try:
                        if len(arg_list) == 1:
                            help()
                        elif len(arg_list) == 2:
                            subcmd = arg_list[1].lower()
                            if subcmd == 'interactive':
                                print('Example commands in interactive mode:')
                                print('\r   connect\n   targets\n   jtag targets')
                                print('\r   stapl config -part [xcvc1902, xcvm1802]')
                                print('\r   tfile open \'/tmp/tfile_text.txt\' -flags 0x0F')
                                print('\r   jtag device_prop -props {\'idcode\': 0x6ba00477, \'irlen\': 4}\n')
                            else:
                                help(subcmd)
                        elif len(arg_list) == 3:
                            category = arg_list[1].lower()
                            fun = arg_list[2].lower()
                            cmd_str = f'{category} {fun}'
                            help(cmd_str)
                        else:
                            print('invalid help command\r\n')
                    except Exception as e:
                        print(e, '\r\n')
                    continue
                if cmd == 'jtag':
                    cmd = cmd + '_targets' if arg_list[k + 1].startswith('t') else arg_list[k + 1]
                    arg_list = arg_list[k + 2:]
                elif (cmd in ('tfile', 'stapl', 'svf', 'jtagseq')) and len(arg_list) != 1:
                    subcmd = arg_list[k + 1]
                    arg_list = arg_list[k + 2:]
                else:
                    arg_list = arg_list[k + 1:]
                ret = self.process_interactive_cmds(cmd, subcmd, arg_list, debug_session, return_arg)
                if ret is not None:
                    if cmd == 'tfile' and subcmd in ('open', 'opendir'):
                        return_arg = ret
                    if isinstance(ret, NameError):
                        if ignore_once > 0:
                            ret = f'unknown command \'{string}\'' + '\r\n# '
                        else:
                            ret = '# '
                        ignore_once = 1
                    elif isinstance(ret, (str, list, int, dict)):
                        if isinstance(ret, (int, list, dict)):
                            ret = str(ret)
                        ret = 'okay\r\n' + ret + '\r\n\r\n# '
                    elif isinstance(ret, Exception):
                        ret = str(ret)
                        ret = 'error\r\n' + ret + '\r\n# '
                    else:
                        ret = 'okay\r\n\r\n#'
                    conn.send(ret.encode())
                else:
                    conn.send('okay\r\n'.encode())

                res = result.getvalue()
                if res is not None:
                    if res.startswith('Unknown attribute'):
                        continue
                    if res != '':
                        res = res.replace('\n', '\r\n')
                        if ret is None:
                            res = res + '\r\n# '
                        else:
                            res = 'okay\r\n' + res + '\r\n# '
                        conn.send(res.encode())
                    else:
                        if ret is None:
                            conn.send('\r\n# '.encode())
                del result

    def xsdbserver_start(self, host: str = '0.0.0.0', port: int = 0):
        """
xsdbserver_start:
    Start XSDB command server listener.  The XSDB command server
    allows external processes to connect to XSDB to evaluate
    commands.  The XSDB server reads commands from the
    connected socket one line at a time.  After evaluation, a
    line is sent back starting with 'okay' or 'error' followed
    by the result or error as a backslash quoted string.

Prototype:
    session.xsdbserver_start(host = <hostip>, port = <port>)

Optional Arguments:
    host = <addr>
        Limits the network interface on which to listen for incoming
        connections.

    port = <port>
        Specifies port to listen on.  If this option is not specified,
        or if the port is zero, a dynamically allocated port
        number is used.

Returns:
    Server details are displayed on the console if the server is started
    successfully. Error string, if a server has been already started.

Examples:
    session.xsdbserver_start()
    session.xsdbserver_start('0.0.0.0', 35535)

Interactive mode examples:
    xsdbserver_start
    xsdbserver_start '0.0.0.0' 35535

        """
        __xsdbserver_table = self.__xsdbserver_table
        if __xsdbserver_table['start'] == 1:
            raise Exception('XSDB server already started') from None

        threading.Thread(target=self.__xsdb_server_thread, args=(host, port), name="xsdb_server_thread",
                         daemon=True).start()
        __xsdbserver_table['start'] = 1

    add_function_metadata('xsdbserver_start', 'Start XSDB command server listener', 'connections', 'Session')

    def xsdbserver_disconnect(self):
        """
xsdbserver_disconnect:
    Disconnect current XSDB server connection.

Prototype:
    session.xsdbserver_disconnect()

Returns:
    Nothing, if the connection is closed.
    Exception, if the server has not been started already.

Examples:
    session.xsdbserver_disconnect()

Interactive mode examples:
    xsdbserver_disconnect
        """
        __xsdbserver_table = self.__xsdbserver_table
        if __xsdbserver_table['start'] == 0:
            raise Exception('XSDB server not started') from None
        if 'chan' not in __xsdbserver_table or __xsdbserver_table['chan'] is None:
            raise Exception('XSDB server not connected') from None
        conn = __xsdbserver_table['chan']
        conn.close()
        time.sleep(2)
        if 'chan' in __xsdbserver_table:
            __xsdbserver_table.pop('chan')

    add_function_metadata('xsdbserver_disconnect', 'Disconnect XSDB command server listener', 'connections', 'Session')

    def xsdbserver_stop(self):
        """
xsdbserver_stop:
    Stop XSDB command server listener and disconnect connected
    client if any.

Prototype:
    session.xsdbserver_stop()

Returns:
    Nothing, if the server is closed successfully.
    Exception, if the server has not been started already.

Examples:
    session.xsdbserver_stop()

Interactive mode examples:
    xsdbserver_stop
        """
        __xsdbserver_table = self.__xsdbserver_table
        if __xsdbserver_table['start'] == 0:
            raise Exception('XSDB server not started') from None
        if 'chan' in __xsdbserver_table and __xsdbserver_table['chan'] is not None:
            conn = __xsdbserver_table['chan']
            conn.close()
            time.sleep(2)
        server = __xsdbserver_table['server']
        server.close()
        time.sleep(2)
        __xsdbserver_table['start'] = 0
        if 'chan' in __xsdbserver_table:
            __xsdbserver_table.pop('chan')
        if 'server' in __xsdbserver_table:
            __xsdbserver_table.pop('server')

    add_function_metadata('xsdbserver_stop', 'Stop XSDB command server listener', 'connections', 'Session')

    def xsdbserver_version(self):
        """
xsdbserver_version:
    Return XSDB command server protocol version.

Prototype:
    session.xsdbserver_version()

Returns:
    Server version if there is an active connection.
    Error string, if there is no active connection.

Examples:
    session.xsdbserver_version()

Interactive mode examples:
    xsdbserver_version
        """
        __xsdbserver_table = self.__xsdbserver_table
        if 'chan' not in __xsdbserver_table or __xsdbserver_table['chan'] is None:
            raise Exception('XSDB server not connected') from None
        print("XSDB Server Protocol Version 0.1")

    add_function_metadata('xsdbserver_version', 'XSDB command server version', 'connections', 'Session')


def start_debug_session():
    """
    start_debug_session:
        Start debugging session and get session object.

    Prototype:
        session = start_debug_session()

    Returns:
        Session object

    Examples:
        session = xsdb.start_debug_session()

    """

    global debug_session
    if debug_session is None:
        protocol.startEventQueue()
        debug_session = Session()
        debug_session.session = debug_session
    try:
        _xsdb.start()
    except Exception as e:
        if rigel == 1:
            raise Exception(f"Cannot start XSDB Manager, " + str(e)) from None
    return debug_session


def interactive():
    current_os = platform.system()
    try:
        if current_os == "Linux":
            import gnureadline
        elif current_os == "Windows":
            import pyreadline
        else:
            raise Exception(f"{current_os} platform doesn\'t support readline package") from None
    except Exception as e:
        if current_os in ("Windows", "Linux"):
            lib = 'gnureadline' if current_os == "Linux" else pyreadline
            out = f'Unable to import {lib} library'
        else:
            out = e
        print(f"WARNING!! {out}.Navigation keys may not work.\r\n"
              "Install it using pip command and add the library path using sys.path.append()\r\n"
              "before entering the interactive mode.\r\n")
        time.sleep(0.5)
    debug_session = start_debug_session()
    prev_cmd = list()
    return_arg = None
    help_keywords = ['help', '--help', '-help', '-h', '--h']
    set_arg = 0
    while True:
        try:
            string = input('% ')
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        string = re.sub(' +', ' ', string)
        string = string.replace('\r', '').replace('\n', '')
        dict_strings = string.split('{')
        if len(dict_strings) != 1:
            string = dict_strings[0]
            for i in range(1, len(dict_strings)):
                dict_end = dict_strings[i].split('}')
                dict_end[0] = dict_end[0].replace('\'', '').replace(' ', '').replace(',', ', ')
                string = string + '{' + dict_end[0] + '}' + dict_end[1]
        else:
            string = dict_strings[0]
        string = string.replace('{', '\'{').replace('}', '}\'')

        pattern = r"\[ *(.*?) *\]"
        string = re.sub(pattern, lambda match: "[" + match.group(1).replace(" ", "") + "]", string)
        string = string.replace(' ,', ',').replace(', ', ',')

        arg_list = [ele for ele in shlex.split(string, posix=False).copy() if ele.strip()]

        if len(arg_list) == 0:
            if len(prev_cmd) == 0:
                print("Enter Command")
                continue
            arg_list = prev_cmd
        else:
            prev_cmd = arg_list
        k = 0
        # cmd = arg_list[k].lower()
        # if cmd == 'set':
        #     set_arg = 1
        #     k = k + 1
        cmd = arg_list[k].lower()
        subcmd = None
        if cmd == 'help':
            try:
                if len(arg_list) == 1:
                    help()
                elif len(arg_list) == 2:
                    subcmd = arg_list[1].lower()
                    if subcmd == 'interactive':
                        print('Example commands in interactive mode:')
                        print('\r   connect\n   targets\n   jtag targets')
                        print('\r   stapl config -part [xcvc1902, xcvm1802]')
                        print('\r   tfile open \'/tmp/tfile_text.txt\' -flags 0x0F')
                        print('\r   jtag device_prop -props {\'idcode\': 0x6ba00477, \'irlen\': 4}\n')
                    else:
                        help(subcmd)
                elif len(arg_list) == 3:
                    category = arg_list[1].lower()
                    fun = arg_list[2].lower()
                    cmd_str = f'{category} {fun}'
                    help(cmd_str)
                else:
                    print('invalid help command\r\n')
            except Exception as e:
                print(e, '\r\n')
            continue
        if cmd in ('exit', 'quit'):
            break
        if cmd == 'after':
            subcmd = arg_list[k + 1]
            if subcmd.startswith('0x'):
                subcmd = int(subcmd, 16)
            elif subcmd.isnumeric():
                subcmd = int(subcmd)
            else:
                print('\'after\' command expectes integer')
                continue
            sec = subcmd / 1000
            time.sleep(sec)
            continue

        if cmd in ('source', 'python', 'py'):
            subcmd = arg_list[k + 1]
            if subcmd.endswith('.py'):
                out, err = Popen([f'python {subcmd}'], stderr=subprocess.PIPE, shell=True).communicate()
                if err is not None:
                    [print(line) for line in err.decode().split("\n")]
            else:
                print('Error: Argument is not a python file')
            continue
        elif cmd == 'jtag':
            if len(arg_list) == 1:
                print('jtag command incorrect. Please refer help jtag')
                continue
            cmd = cmd + '_targets' if arg_list[k + 1].startswith('t') else arg_list[k + 1]
            arg_list = arg_list[k + 2:]
        elif (cmd in ('tfile', 'stapl', 'svf', 'jtagseq')) and len(arg_list) != 1:
            subcmd = arg_list[k + 1]
            arg_list = arg_list[k + 2:]
        else:
            arg_list = arg_list[k + 1:]

        if subcmd in help_keywords or [keyword for keyword in help_keywords if keyword in arg_list]:
            print('please use \'help\' followed by command')
            continue
        ret = debug_session.process_interactive_cmds(cmd, subcmd, arg_list, debug_session, return_arg)
        if ret is not None:
            if cmd == 'tfile' and subcmd in ('open', 'opendir'):
                return_arg = ret
            print(ret)


@atexit.register
def dispose():
    global debug_session
    debug_session = None
    _xsdb.stop()


def __help_usage():
    return """
xsdb - Xilinx system debug package
-----------------------------------
xsdb implements a set of functions to debug Xilinx processors and applications.
To use the package, run start_debug_session(), which returns a Session object.
This object can be used to run other debug functions. Some of these functions
can return other objects, using which some more debug functions can be run.
Below is an example to connect to hw, server, download test.elf and foo.elf on
targets 3 and 4, set breakpoints at main and foo, and run the elfs.

    session = start_debug_session()
    session.connect(url="TCP:localhost:3121")
    session.targets(3)
    # All subsequent commands are run on target 3, until the target is changed
    # with targets() function
    session.dow("test.elf")
    session.bpadd(addr="main")
    session.con()
    session.targets(4)
    # All subsequent commands are run on target 4
    session.dow("foo.elf")
    session.bpadd(addr="foo")
    session.con()

targets() function in the above example returns a Target object, which can be
used to run other debug functions on that target, without changing the current
target. The previous example would look like below, when Target object is used.

    session = start_debug_session()
    session.connect(url="TCP:localhost:3121")
    t3 = session.targets(3)
    t3.dow("test.elf")
    t3.bpadd(addr="main")
    t3.con()
    t4 = session.targets(4)
    t4.dow("foo.elf")
    t4.bpadd(addr="foo")
    t4.con()
"""


__categories = {
    "breakpoints": "Target breakpoints/watchpoints",
    "connections": "Connections and Targets management",
    "download": "ELF or binary file download to target",
    "device": "ACAP/FPGA device configuration",
    "ipi": "IPI commands to PMC",
    "jtag": "JTAG access",
    "memory": "Target memory access",
    "memorymap": "Target memorymap and symbol files",
    "miscellaneous": "Miscellaneous",
    "profiler": "Configure and run profiler",
    "registers": "Target register accesses",
    "reset": "Target reset",
    "runcontrol": "Program Execution",
    "streams": "Jtag UART",
    "svf": "SVF operations",
    "stapl": "STAPL operations",
    "tfile": "Target file system",
    "variables": "Variables and expressions"
}


def __max_len(keys):
    max_len = 0
    for key in keys:
        key_len = len(key)
        if max_len < key_len:
            max_len = key_len
    return max_len


def __get_brief(keys):
    global function_metadata

    h = ''
    keys.sort()
    max_len = __max_len(keys)
    for fn in keys:
        h += fn
        pad = max_len - len(fn)
        h += "{}".format(" " * pad)
        h += f' - {function_metadata.get(fn).get("brief")}\n'
    return h


def help(type: str = None):
    global __categories
    global function_metadata

    if type is None or type == '':
        max_len = __max_len(__categories.keys())
        h = """
Available help categories:
--------------------------
"""
        for key, val in __categories.items():
            h += key
            pad = max_len - len(key)
            h += "{}".format(" " * pad)
            h += f' - {val}\n'
        h += """
Run xsdb.help("usage") to see a usage example.
Run xsdb.help("<category>"), where <category> is one of the above categories,
to see more details about the <category>.
Run xsdb.help("functions") to see a list of all available functions.
"""
    elif type == 'usage':
        h = __help_usage()
    elif type == 'functions':
        h = """
Available functions:
--------------------
"""
        h += __get_brief(list(function_metadata.keys()))
        h += """
Run xsdb.help("<function>"), where <function> is one of the above functions,
to see more details about the <function>.
"""
    elif type in __categories.keys():
        h = '\n' + __categories.get(type) + '\n'
        h += """
Category functions:
-------------------
"""
        keys = []
        for fn in function_metadata.keys():
            if type == function_metadata.get(fn).get('category'):
                keys.append(fn)
        h += __get_brief(keys)
        h += """
Run xsdb.help("<function>"), where <function> is one of the above functions,
to see more details about the <function>.
"""
    elif type in function_metadata.keys():
        fun = type.split()
        fun = fun[len(fun) - 1]
        cls_name = function_metadata.get(type).get('class')
        cls = getattr(sys.modules[__name__], cls_name)
        h = getattr(cls, fun).__doc__
        # h += '\n'
    else:
        raise Exception(f"Unknown category {type}: must be {', '.join(list(__categories.keys()))}") from None
    print(h)

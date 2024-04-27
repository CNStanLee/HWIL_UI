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

from xsdb._tcf_node_jtagdevice import TcfNodeJtagDevice
from xsdb._utils import *
from xsdb._tcf_children import TcfChildren
from xsdb._tcf_node import TcfNode
from xsdb._tcf_children_exec_context import TcfChildrenExecContext
from xsdb._tcf_jtag_children_exec_context import TcfJtagChildrenExecContext
from xsdb._tcf_node_info import TcfNodeInfo


##################################################################################################
# TcfNodeLaunch -
#   * Creates the TcfNodeLaunch object.
#   * This is created once for each connection
#   * This object creates a root node and get the top level children
#   * All the targets and related information like context and state are populated here
##################################################################################################


class TcfNodeLaunch(TcfNode):
    def __init__(self, channel, info: TcfNodeInfo, session):
        super().__init__(channel, info)
        self.session = session
        self.__next_target_id = 0
        self.__info = info
        self.__children = TcfChildrenExecContext(self)
        self.__root_children = self.RootChildrenTcfChildren(self)
        data = {}
        data.update({"": self})
        self.__info.update_nodes(data)
        self.__targets = {'data': {}, 'error': ''}
        self.__caches = []
        self.__target_ctx_map = {}
        self.__ctx_target_map = {}
        self.__ctx_nodes_map = {}
        self.__jtag_children = TcfJtagChildrenExecContext(self)
        self.__root_jtag_children = self.RootJtagChildrenTcfChildren(self)
        self.__jtag_caches = []
        self.__jtag_targets = {'data': {}, 'error': ''}
        self.__jtag_target_properties = {}
        self.__jtag_ctx_nodes_map = {}
        self.__jtag_ctx_target_map = {}
        self.__jtag_target_ctx_map = {}

    # ---------------------------------------------------------------------------------------------
    # ---- FilteredChildrenTcfChildren-------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------
    class RootChildrenTcfChildren(TcfChildren):
        def __init__(self, launch_node):
            super().__init__(launch_node)
            self.__launch_node = launch_node

        def startDataRetrieval(self):
            if not self.__launch_node.get_children().validate(self):
                return False
            self.set(None, self.__launch_node.get_children().getError(), self.__launch_node.get_children().getData())
            return True

    # ---------------------------------------------------------------------------------------------
    def get_root_children(self):
        return self.__root_children

    # ---------------------------------------------------------------------------------------------
    def get_children(self):
        return self.__children

    # ---------------------------------------------------------------------------------------------

    def update_ctx_node_map(self):
        for id, data in self.__targets['data'].items():
            if 'children' in data.keys():
                for ctx, node in data['children'].items():
                    self.__ctx_nodes_map.update({ctx: node})

    def set_target_ids(self):
        self.update_ctx_node_map()
        self.__next_target_id = 0

        def __assign_target_ids(ctx="", level=-1):
            if ctx not in self.__ctx_target_map:
                self.__targets['data'][ctx]['target_id'] = self.__next_target_id
                self.__info.get_node(ctx).target_id = self.__next_target_id
                self.__targets['data'][ctx]['level'] = level
                self.__info.get_node(ctx).level = level
                self.__target_ctx_map[self.__next_target_id] = ctx
                self.__ctx_target_map[ctx] = self.__next_target_id
                self.__next_target_id += 1
                if 'children' in self.__targets['data'][ctx]:
                    level += 1
                    for child in self.__targets['data'][ctx]['children']:
                        __assign_target_ids(child, level)
            else:
                self.__targets['data'][ctx]['target_id'] = self.__ctx_target_map[ctx]

        __assign_target_ids()

    # ---------------------------------------------------------------------------------------------
    def get_targets(self, run, c: TcfChildren):
        done = True
        if c.node.id not in self.__targets['data']:
            self.__targets['data'][c.node.id] = {}

        if c not in self.__caches:
            self.__caches.append(c)
        if not c.validate(run):
            return None
        else:
            self.__caches.remove(c)
            if c.getError() is not None:
                self.__targets['error'] = c.getError()
                return self.__targets

            data = c.getData()
            children_data = data['children']
            mem_children_data = data['mem_children']
            self.__targets['data'][c.node.id]['id'] = c.node.id
            self.__targets['data'][c.node.id]['children'] = children_data

            # Get mem context for mem children
            for node in mem_children_data.values():
                if node.get_memory_context() not in self.__caches:
                    self.__caches.append(node.get_memory_context())
                if not node.get_memory_context().validate(run):
                    done = False
                else:
                    self.__caches.remove(node.get_memory_context())
                    if node.get_memory_context().getError() is not None:
                        self.__targets['error'] = node.get_memory_context().getError()
                        return self.__targets
                    node.mem_context_data = node.get_memory_context().getData()
            if done is False:
                return None

            # Get context of children
            for ctx, node in children_data.items():
                if ctx not in self.__targets['data']:
                    self.__targets['data'][ctx] = {}

                if node.get_run_context() not in self.__caches:
                    self.__caches.append(node.get_run_context())
                if not node.get_run_context().validate(run):
                    done = False
                else:
                    self.__caches.remove(node.get_run_context())
                    if node.get_run_context().getError() is not None:
                        self.__targets['error'] = node.get_run_context().getError()
                        return self.__targets
                    node.set_run_context_data(node.get_run_context().getData())

                    state = node.get_run_context_data().hasState()
                    if state:
                        if node.get_run_state() not in self.__caches:
                            self.__caches.append(node.get_run_state())
                        if not node.get_run_state().validate(run):
                            done = False
                        else:
                            self.__caches.remove(node.get_run_state())
                            if node.get_run_state().getError() is not None:
                                self.__targets['error'] = node.get_run_state().getError()
                                return self.__targets
                            node.set_run_state_data(node.get_run_state().getData())
                    else:
                        if not self.get_targets(run, node.get_children()):
                            done = False
                        else:
                            done = True
                    self.__targets['data'][ctx]['run_context'] = node.get_run_context_data().getProperties()
                    self.__targets['data'][ctx]['run_state'] = node.get_run_state_data()
                    self.__targets['data'][ctx]['id'] = ctx
                    if c.node.id != "":
                        parent_name = c.node.get_run_context_data().getName()
                        self.__targets['data'][ctx]['parent'] = parent_name
                    else:
                        self.__targets['data'][ctx]['parent'] = ""
            if done is False:
                return None

        if not self.__caches:
            return self.__targets
        else:
            return None

    # ---------------------------------------------------------------------------------------------
    def clear_targets(self):
        self.__ctx_target_map = {}
        self.__target_ctx_map = {}
        self.__ctx_nodes_map = {}
        self.__targets = {'data': {}, 'error': ''}

    # ---------------------------------------------------------------------------------------------
    def on_context_added(self, context):
        self.__children.on_context_added(context)

    # ---------------------------------------------------------------------------------------------
    def get_target_name(self, context):
        return self.__targets['data'][context]['run_context']['Name']

    # ---------------------------------------------------------------------------------------------
    def get_target_id(self, context):
        return self.__targets['data'][context]['target_id']

    # ---------------------------------------------------------------------------------------------
    def get_target_context_map(self):
        return self.__target_ctx_map

    # ---------------------------------------------------------------------------------------------
    def get_context_target_map(self):
        return self.__ctx_target_map

    # ---------------------------------------------------------------------------------------------
    def on_context_added_or_removed(self):
        self.__root_children.reset()

    # --------------JTAG Targets-------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    def get_jtag_children(self):
        return self.__jtag_children

    def jtag_targets(self, run):
        self.clear_jtag_targets()
        ret_data = self.get_jtag_targets(run, self.get_root_jtag_children())
        if ret_data is None:
            return False
        else:
            if ret_data['error'] == '':
                self.set_jtag_target_ids()
                self.get_jtag_target_properties(ret_data['data'])
            run.sync.done(error=None if ret_data['error'] == '' else ret_data['error'], result=ret_data['data'])

    class RootJtagChildrenTcfChildren(TcfChildren):
        def __init__(self, launch_node):
            super().__init__(launch_node)
            self.__launch_node = launch_node

        def startDataRetrieval(self):
            if not self.__launch_node.get_jtag_children().validate(self):
                return False
            self.set(None, self.__launch_node.get_jtag_children().getError(),
                     self.__launch_node.get_jtag_children().getData())
            return True

    def get_root_jtag_children(self):
        return self.__root_jtag_children

    def print_jtag_targets(self, targets):
        result = ''
        tgt_list = sorted(targets.items(), key=lambda k_v: k_v[1]['target_id'])
        for target_ctx, target_dict in enumerate(tgt_list):
            target = target_dict[1]
            if target['id'] == '':
                continue
            info = ''
            props = target['props']
            if 'state' in props and props['state'] != "":
                info += props['state']
            if 'idcode' in props and props['idcode'] != '0':
                info += 'idcode ' + props['idcode']
            if 'irlen' in props and props['irlen'] != '0':
                info += ' ' + 'irlen ' + str(int(props['irlen'], 16))
            if 'is_fpga' in props and props['is_fpga'] != 0:
                info += ' ' + 'fpga'
            if 'is_pdi_programmable' in props and props['is_pdi_programmable'] != 0:
                info += ' ' + 'pdi_programmable'
            if props['is_active'] == 0:
                info += ' ' + 'inactive'
            elif target['level'] == 0 and props['is_open'] == 0:
                info += ' ' + 'closed'
            active = '*' if self.session.cur_jtag_target and self.session.cur_jtag_target.ctx == target_dict[0] else ' '

            result += "{0}{1:3d}{2:2s}{3}{4}{5}".format(
                " " * (target['level'] * 3 + 3), target['target_id'], active, props['name'],
                ' (' + info + ')' if len(info) else '', '\n')
        return result

    def update_jtag_ctx_node_map(self):
        for id, data in self.__jtag_targets['data'].items():
            if 'children' in data.keys():
                for ctx, node in data['children'].items():
                    self.__jtag_ctx_nodes_map.update({ctx: node})

    def set_jtag_target_ids(self):
        self.update_jtag_ctx_node_map()
        self.__next_target_id = 0

        def __assign_target_ids(ctx="", level=-1):
            if ctx not in self.__jtag_ctx_target_map:
                self.__jtag_targets['data'][ctx]['target_id'] = self.__next_target_id
                self.__jtag_targets['data'][ctx]['level'] = level
                self.__jtag_target_ctx_map[self.__next_target_id] = ctx
                self.__jtag_ctx_target_map[ctx] = self.__next_target_id
                self.__next_target_id += 1
                if 'children' in self.__jtag_targets['data'][ctx]:
                    level += 1
                    for child in self.__jtag_targets['data'][ctx]['children']:
                        __assign_target_ids(child, level)
            else:
                self.__jtag_targets['data'][ctx]['target_id'] = self.__jtag_ctx_target_map[ctx]

        __assign_target_ids()

    def get_jtag_target_properties(self, tgts):
        for ctx, data in tgts.items():
            cable = 0
            props = {'target_ctx': '', 'level': None, 'node_id': None, 'is_open': None, 'is_active': None,
                     'is_current': None, 'name': '', 'jtag_cable_name': '', 'state': '', 'jtag_cable_manufacturer': '',
                     'jtag_cable_product': '', 'jtag_cable_serial': None, 'idcode': None, 'irlen': None,
                     'is_fpga': None}
            if ctx == '':
                continue
            jc = data['context']
            nid = data['target_id']
            jcc = data['cable_ctx'] if data['cable_ctx'] is not None else dict()
            parent_props = dict()
            if data['level'] == 0:
                cable = 1
            else:
                node = data
                while True:
                    if node['parent'] is not None and node['parent'] in tgts.keys():
                        parent = tgts[node['parent']]
                        if parent['level'] != 0:
                            node = parent
                        else:
                            break
                parent_props = tgts[parent['id']]['props']
            open, active = 0, 0
            if 'isActive' in jc and jc['isActive']:
                open, active = 1, 1
            if ('isActive' in jcc and jcc['isActive']) or ('isInitializing' in jcc and jcc['isInitializing']):
                active = 1
            props['is_open'], props['is_active'], props['node_id'] = open, active, nid
            props['level'] = data['level']
            props['target_ctx'] = ctx
            props['is_current'] = 0
            if self.session.cur_jtag_target is not None:
                if self.session.cur_jtag_target.ctx == ctx:
                    props['is_current'] = 1
            name = None
            if cable == 1:
                if (('Description' in jcc and jcc['Description'] != "") and
                        not ('isError' in jcc and jcc['isError']) and
                        not ('isInitializing' in jcc and jcc['isInitializing'])):
                    name = jcc['Description']
                    if 'Serial' in jcc and jcc['Serial'] != "":
                        name = name + ' ' + jcc['Serial']
                else:
                    if 'Manufacturer' in jcc and jcc['Manufacturer'] != "":
                        name = jcc['Manufacturer']
                        if 'ProductID' in jcc and jcc['ProductID'] != "":
                            name = name + ' ' + jcc['ProductID']
                        else:
                            name = name + ' cable'
                        if 'Serial' in jcc and jcc['Serial'] != "":
                            name = name + ' ' + jcc['Serial']
                    elif 'ProductID' in jcc and jcc['ProductID'] != "":
                        name = jcc['ProductID']

            jtag_cable_name = name
            if name is None:
                name = jc['Name'] if 'Name' in jc else 'Unknown'

            state = ''
            if 'isInitializing' in jcc and jcc['isInitializing']:
                state = 'initializing'
                if 'Description' in jcc and jcc['Description'] != "":
                    state = state + ': ' + jcc['Description']
            elif 'isActive' in jcc and jcc['isActive'] and 'isError' in jcc and jcc['isError']:
                state = 'error'
                if 'Description' in jcc and jcc['Description'] != "":
                    state = state + ': ' + jcc['Description']
            elif open and 'Status' in jc and jc['Status'] != "":
                state = 'error' + jc['Status']
            props['name'] = name
            if jtag_cable_name is not None:
                props['jtag_cable_name'] = jtag_cable_name
            else:
                props['jtag_cable_name'] = parent_props['name'] if 'name' in parent_props else ''
            props['state'] = state

            props['jtag_cable_manufacturer'] = jcc['Manufacturer'] if 'Manufacturer' in jcc else ''
            props['jtag_cable_product'] = jcc['ProductID'] if 'ProductID' in jcc else ''
            props['jtag_cable_serial'] = jcc['Serial'] if 'Serial' in jcc else ''
            if 'idCode' in jc and jc['idCode'] != 255:
                props['idcode'] = "{0:0x}".format(jc['idCode'])
            else:
                props['idcode'] = '0'
            props['irlen'] = "{0:0x}".format(jc['irLen']) if 'irLen' in jc else '0'
            props['is_fpga'] = 0
            props['is_pdi_programmable'] = 0
            if len(data['properties']):
                if 'reg.jprogram' in data['properties']:
                    props['is_fpga'] = 1
                if 'is_pdi_program_supported' in data['properties'] and data['properties']['is_pdi_program_supported']:
                    props['is_pdi_programmable'] = 1
            data['props'] = props
            ctx_node_map = self.get_jtag_context_node_map()
            ctx_node_map[ctx].set_props(props)

    def get_jtag_targets(self, run, c: TcfChildren):
        done = True
        if c.node.id not in self.__jtag_targets['data']:
            self.__jtag_targets['data'][c.node.id] = {}

        if c not in self.__jtag_caches:
            self.__jtag_caches.append(c)
        if not c.validate(run):
            return None
        else:
            self.__jtag_caches.remove(c)
            if c.getError() is not None:
                self.__jtag_targets['error'] = c.getError()
                return self.__jtag_targets

            children_data = c.getData()['jtag_children']
            self.__jtag_targets['data'][c.node.id]['id'] = c.node.id
            self.__jtag_targets['data'][c.node.id]['children'] = children_data

            # Get context of children
            for ctx, node in children_data.items():
                if ctx not in self.__jtag_targets['data']:
                    self.__jtag_targets['data'][ctx] = {}

                # Get jtag cable properties
                cable_node = node.get_jtag_cable_node()
                if cable_node is not None:
                    if cable_node.get_jtag_cable_context() not in self.__jtag_caches:
                        self.__jtag_caches.append(cable_node.get_jtag_cable_context())
                    if not cable_node.get_jtag_cable_context().validate(run):
                        done = False
                    else:
                        self.__jtag_caches.remove(cable_node.get_jtag_cable_context())
                        if cable_node.get_jtag_cable_context().getError() is not None:
                            self.__jtag_targets['error'] = cable_node.get_jtag_cable_context().getError()
                            return self.__jtag_targets
                        node.set_jtag_cable_context_data(cable_node.get_jtag_cable_context().getData())

                # Get context
                if node.get_context() not in self.__jtag_caches:
                    self.__jtag_caches.append(node.get_context())
                if not node.get_context().validate(run):
                    done = False
                else:
                    self.__jtag_caches.remove(node.get_context())
                    if node.get_context().getError() is not None:
                        self.__jtag_targets['error'] = node.get_context().getError()
                        return self.__jtag_targets
                    node.set_context_data(node.get_context().getData())

                    # Get jtag device properties for node
                    ctx_data = node.get_context().getData()
                    if node.get_jtag_device_node() is None:
                        node.set_jtag_device_node(TcfNodeJtagDevice(node, node.channel, ctx_data.props['idCode']))
                    if node.get_jtag_device_node().get_jtagdevice_properties() not in self.__jtag_caches:
                        self.__jtag_caches.append(node.get_jtag_device_node().get_jtagdevice_properties())
                    if not node.get_jtag_device_node().get_jtagdevice_properties().validate(run):
                        done = False
                    else:
                        self.__jtag_caches.remove(node.get_jtag_device_node().get_jtagdevice_properties())
                        if node.get_jtag_device_node().get_jtagdevice_properties().getError() is not None:
                            self.__jtag_targets['error'] = \
                                node.get_jtag_device_node().get_jtagdevice_properties().getError()
                            return self.__jtag_targets
                        node.set_properties_data(node.get_jtag_device_node().get_jtagdevice_properties().getData())

                    if not self.get_jtag_targets(run, node.get_children()):
                        done = False
                    else:
                        done = True
                    self.__jtag_targets['data'][ctx]['context'] = node.get_context_data().props
                    self.__jtag_targets['data'][ctx]['properties'] = node.get_properties_data()
                    self.__jtag_targets['data'][ctx]['cable_ctx'] = node.get_jtag_cable_context_data()
                    self.__jtag_targets['data'][ctx]['id'] = ctx
                    if node.id != "":
                        parent_name = node.get_context_data().props['ParentID']
                        self.__jtag_targets['data'][ctx]['parent'] = parent_name
                    else:
                        self.__jtag_targets['data'][ctx]['parent'] = ""
            if done is False:
                return None

        if not self.__jtag_caches:
            return self.__jtag_targets
        else:
            return None

    def get_jtag_target_context_map(self):
        return self.__jtag_target_ctx_map

    def get_jtag_context_target_map(self):
        return self.__jtag_ctx_target_map

    def get_jtag_context_node_map(self):
        return self.__jtag_ctx_nodes_map

    def clear_jtag_targets(self):
        self.__jtag_ctx_target_map = {}
        self.__jtag_target_ctx_map = {}
        self.__jtag_ctx_nodes_map = {}
        self.__jtag_targets = {'data': {}, 'error': ''}

    def on_jtag_context_added(self, context):
        self.__jtag_children.on_jtag_context_added(context)

    def on_jtag_cable_context_added(self, context):
        self.__jtag_children.on_jtag_cable_context_added(context)

    def on_jtag_context_added_or_removed(self):
        self.__root_jtag_children.reset()
        self.__jtag_children.reset()

    def on_jtag_cable_server_added_or_removed(self):
        for ctx, node in self.__jtag_ctx_nodes_map.items():
            cable_node = node.get_jtag_cable_node()
            if cable_node is not None:
                cable_node.get_jtag_cable_server_descriptions().reset()
                cable_node.get_jtag_cable_open_servers().reset()

    def on_jtag_devices_changed(self):
        for ctx, node in self.__jtag_ctx_nodes_map.items():
            device_node = node.get_jtag_device_node()
            if device_node is not None and isinstance(device_node, TcfNodeJtagDevice):
                device_node.get_jtagdevice_properties().reset()
        for ctx, node in self.__ctx_nodes_map.items():
            device_node = node.get_jtag_device_node()
            if device_node is not None and isinstance(device_node, TcfNodeJtagDevice):
                device_node.get_jtagdevice_properties().reset()

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
from xsdb._tcf_node import TcfNode

#################################################################################################
# TcfChildren -
#   * This is a TcfCache object to retrieve the children of a particular context.
#   * Creates a cache object for each request to server
#################################################################################################


class TcfChildren(cache.DataCache):
    def startDataRetrieval(self):
        pass

    def __init__(self, node: TcfNode = None):
        super(TcfChildren, self).__init__(node.channel)
        self.node = node
        self.node.add_data_cache(self)

    # -------------------------------------------------------------------------------------------
    def add(self, node: TcfNode):
        if self.isValid():
            data = self.getData()
            if data is not None:
                data.update({id: node})

    # -------------------------------------------------------------------------------------------
    def onNodeDisposed(self, id):
        if self.isValid():
            data = self.getData()
            if data is not None:
                if len(data) != 0:
                    rc_children = data.get("children", None)
                    mem_children = data.get("mem_children", None)
                    if rc_children is None and mem_children is None:
                      # TODO : FIXME : temp condition (if id in data) added to avoid crash at data.pop(id)
                      # in case the parent cache(self) is of type JtagChildrenTcfChildren. (id received here is targetid).
                      # Issue is seen while adding virtual devices using stapl and RunCtrl context removed event received.
                      if id in data:
                          data.pop(id)
                    else:
                        if len(rc_children) != 0:
                            if id in rc_children:
                                rc_children.pop(id)
                        if len(mem_children) != 0:
                            if id in mem_children:
                                mem_children.pop(id)


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
from tcf.util import cache
from xsdb._tcf_node_info import TcfNodeInfo


##################################################################################################
# TcfNode -
#   * Creates the TcfNode object.
#   * This is created for each context.
#   * Internally creates more caches to get children, contexts etc.
##################################################################################################
class TcfNode(object):
    def __init__(self, channel, info:TcfNodeInfo, ctx_id: str = '', parent: str = ''):
        self.id = ctx_id
        self.parent = parent
        self.channel = channel
        self.info = info
        self.__caches = []
        self.__disposed = False

    # ---------------------------------------------------------------------------------------------
    def get_caches(self):
        return self.__caches

    # ---------------------------------------------------------------------------------------------
    def add_data_cache(self, c: cache.DataCache):
        if c is not None:
            self.__caches.append(c)

    # ---------------------------------------------------------------------------------------------
    def remove_data_cache(self, c: cache.DataCache):
        if c is not None:
            self.__caches.remove(c)

    # ---------------------------------------------------------------------------------------------
    def flush_all_caches(self):
        if self.__caches is None:
            return
        for c in self.__caches:
            c.reset()

    # ---------------------------------------------------------------------------------------------
    def dispose(self):
        assert not self.__disposed
        for c in self.__caches:
            c.dispose()
        if self.parent is not None and self.parent.get_caches() is not None:
            for c in self.parent.get_caches():
                if isinstance(c, xsdb._tcf_children.TcfChildren):
                    c.onNodeDisposed(self.id)
        if self.id is not None:
            self.info.remove_node(self.id)
        self.__disposed = True

    # ---------------------------------------------------------------------------------------------
    def is_disposed(self):
        return self.__disposed

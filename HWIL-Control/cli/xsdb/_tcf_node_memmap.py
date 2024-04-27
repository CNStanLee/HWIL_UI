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

from tcf.services import memorymap as memmap_service


#################################################################################################
# TcfNodeMemoryMap -
#   * set and get commands for a memory context in memorymap service
#################################################################################################


class TcfNodeMemoryMap(object):
    def __init__(self, __tcf_node_exec_ctx, channel, id: str):
        self.id = id
        self.channel = channel
        self.node = __tcf_node_exec_ctx
        # self.__get_memmap_data = self.MemMapGetData(channel, id)

    def set(self, memoryMap, sync=None):
        mm = self.channel.getRemoteService(memmap_service.NAME)

        class DoneSet(memmap_service.DoneSet):
            def __init__(self, sync):
                self.__sync = sync

            def doneSet(self, token, error):
                if self.__sync is not None:
                    self.__sync.done(error=error, result=None)

        mm.set(self.id, memoryMap, DoneSet(sync))

    def get(self, sync=None):
        mm = self.channel.getRemoteService(memmap_service.NAME)

        class DoneGet(memmap_service.DoneGet):
            def __init__(self, sync):
                self.__sync = sync

            def doneGet(self, token, error, memoryMap):
                if self.__sync is not None:
                    self.__sync.done(error=error, result=memoryMap)

        mm.get(self.id, DoneGet(sync))

    # class MemMapGetData(cache.DataCache):
    #     def __init__(self, channel, context_id):
    #         super().__init__(channel)
    #         self.__context_id = context_id
    #         self.__channel = channel
    #
    #     def startDataRetrieval(self):
    #         mm = self.__channel.getRemoteService(memmap_service.NAME)
    #         mm_data = self
    #
    #         class DoneGet(memmap_service.DoneGet):
    #             def doneGet(self, token, error, memoryMap):
    #                 mm_data.set(token, error, memoryMap)
    #
    #         mm.get(self.__context_id, DoneGet())
    #
    # def get_memmap_data(self):
    #     return self.__get_memmap_data

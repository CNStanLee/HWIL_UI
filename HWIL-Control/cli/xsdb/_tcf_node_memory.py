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
from tcf.services import memory as mem_service
from xsdb import _logger


#################################################################################################
# TcfNodeMemory -
#   * Creates TcfCache for getting context data of memory.
#   * read, write, fill commands for a memory context in memory service
#################################################################################################


class MemCtxTcfData(cache.DataCache):
    def __init__(self, channel, id):
        super().__init__(channel)
        self.id = id

    def startDataRetrieval(self):
        mem = self._channel.getRemoteService(mem_service.NAME)
        mem_ctx = self

        class DoneGetContext(mem_service.DoneGetContext):
            def doneGetContext(self, token, error, context):
                _logger.debug(" [R] {0:3s} [Memory getContext] ---- {1}".format(token.id, context))
                if error is not None:
                    if error.getAttributes()['Format'] == "Invalid context":
                        error = None
                mem_ctx.set(token, error, context)

        mem_ctx._command = mem.getContext(self.id, DoneGetContext())
        _logger.debug(" [C] {0:3s} [Memory getContext] ---- {1}".format(mem_ctx._command.id, self.id))
        return False


class TcfNodeMemory(object):
    def __init__(self, channel, id: str):
        self.id = id
        self.channel = channel
        self.__mem_context = MemCtxTcfData(self.channel, self.id)
        self.mem_context_data = None

    class DoneMemory(mem_service.DoneMemory):
        def __init__(self, sync, callback, callback_arg, size, buf, offset):
            self.__sync = sync
            self.__callback = callback
            self.__callback_arg = callback_arg
            self.__size = size
            self.__buf = buf
            self.__offset = offset

        def doneMemory(self, token, error):
            if self.__callback is not None:
                self.__callback(self.__callback_arg, self.__size, self.__buf, self.__offset, error, token.id)
            if self.__sync is not None:
                self.__sync.done(error=error, result=None)

    def mem_read(self, addr: int, ws: int, buf: bytearray, offs: int, sz: int, mode: int, callback=None,
                 callback_arg=None, sync=None):
        ctx = self.__mem_context.getData()
        return ctx.get(addr, ws, buf, offs, sz, mode, self.DoneMemory(sync, callback, callback_arg, sz, buf, offs))

    def mem_write(self, addr: int, ws: int, buf: bytearray, offs: int, sz: int, mode: int, callback=None,
                  callback_arg=None, sync=None):
        ctx = self.__mem_context.getData()
        return ctx.set(addr, ws, buf, offs, sz, mode, self.DoneMemory(sync, callback, callback_arg, sz, None, offs))

    def mem_fill(self, addr: int, ws: int, value: int, sz: int, mode: int, callback=None,
                 callback_arg=None, sync=None):
        ctx = self.__mem_context.getData()
        return ctx.fill(addr, ws, value, sz, mode, self.DoneMemory(sync, callback, callback_arg, sz, None, 0))

    def get_memory_context(self):
        return self.__mem_context

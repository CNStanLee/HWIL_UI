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

from tcf.services import linenumbers as ln_service
from tcf.util import cache

#################################################################################################
# TcfNodeLineNumber -
#   * Creates TcfCache for getting data from tcf-linenumbers service.
#################################################################################################

class TcfNodeLineNumber(object):
    def __init__(self, channel, id: str, pid, ipl, iph):
        self.id = id
        self.channel = channel
        self.map_to_source_data = []
        self.map_to_source = self.LineNumberMapToSourceData(channel, pid, ipl, iph)

    class LineNumberMapToSourceData(cache.DataCache):
        def __init__(self, channel, pid, ipl, iph):
            super().__init__(channel)
            self.__pid = pid
            self.__ipl = ipl
            self.__iph = iph
            self.__channel = channel

        def startDataRetrieval(self):
            ln = self.__channel.getRemoteService(ln_service.NAME)
            line_data = self

            class DoneMapToSource(ln_service.DoneMapToSource):
                def doneMapToSource(self, token, error, areas):
                    line_data.set(token, error, areas)

            line_data._command = ln.mapToSource(self.__pid, self.__ipl, self.__iph, DoneMapToSource())
            return False

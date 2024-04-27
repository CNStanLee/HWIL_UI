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

from tcf.services import streams as streams_service


def streams_connect(obj, stream_id, sync):
    ss = obj.session._curchan_obj.getRemoteService(streams_service.NAME)

    class DoneConnect(streams_service.DoneConnect):
        def __init__(self, sync):
            self.sync = sync

        def doneConnect(self, token, error):
            self.sync.done(error=error, result=None)

    ss.connect(stream_id, DoneConnect(sync))


def streams_disconnect(obj, stream_id, sync):
    ss = obj.session._curchan_obj.getRemoteService(streams_service.NAME)

    class DoneDisconnect(streams_service.DoneDisconnect):
        def __init__(self, sync):
            self.sync = sync

        def doneDisconnect(self, token, error):
            self.sync.done(error=error, result=None)

    ss.disconnect(stream_id, DoneDisconnect(sync))


def streams_read(obj, TXStreamID, callback=None):
    ss = obj.session._curchan_obj.getRemoteService(streams_service.NAME)

    class DoneRead(streams_service.DoneRead):
        def __init__(self, callback, TXStreamID):
            self.TXStreamID = TXStreamID
            self.callback = callback

        def doneRead(self, token, error, lost_size, data, eos):
            self.callback(self.TXStreamID, error, lost_size, data, eos)

    ss.read(TXStreamID, 4096, DoneRead(callback, TXStreamID))


def streams_write(obj, RXStreamID, data):
    ss = obj.session._curchan_obj.getRemoteService(streams_service.NAME)

    class DoneWrite(streams_service.DoneWrite):
        def doneWrite(self, token, error):
            if error:
                raise Exception(f'{error}') from None

    ss.write(RXStreamID, data, 0, len(data), DoneWrite())

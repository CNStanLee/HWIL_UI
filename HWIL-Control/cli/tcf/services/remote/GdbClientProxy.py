# *****************************************************************************
# * Copyright (c) 2020 Xilinx, Inc.
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the Eclipse Public License 2.0
# * which accompanies this distribution, and is available at
# * https://www.eclipse.org/legal/epl-2.0/
# *
# * Contributors:
# *     Xilinx
# *****************************************************************************

from tcf.services import gdbclient, DoneHWCommand


class GdbClientProxy(gdbclient.GdbClientService):
    """TCF gdbclient service interface."""

    def __init__(self, channel):
        super(GdbClientProxy, self).__init__(channel)

    def connect(self, Serverparameters, done: DoneHWCommand) -> None:
        return self.send_command("connect", (Serverparameters,), done)

    def disconnect(self, id: str, done: DoneHWCommand) -> None:
        return self.send_command("disconnect", (id,), done)

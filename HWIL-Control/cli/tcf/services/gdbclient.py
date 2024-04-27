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
from tcf import services
from tcf.services import DoneHWCommand

NAME = "GdbClient"
"""GdbClient service name."""


class GdbClientService(services.Service):
    """TCF GdbClient service interface."""
    def getName(self) -> str:
        """
        Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def connect(self, Serverparameters:{}, done: DoneHWCommand) -> None:
        """
        Connect to GDB server.

        :param Serverparameters: Server parameters
        :param done: Callback with result and any error.
        """
        raise NotImplementedError("Abstract method")

    def disconnect(self, id: str, done: DoneHWCommand) -> None:
        """
        Deletes the target and any associated devices.

        :param id: Context id of the target
        :param done: Callback with the result and any error
        """
        raise NotImplementedError("Abstract method")

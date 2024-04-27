# *****************************************************************************
# * Copyright (c) 2023 Xilinx, Inc.
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the Eclipse Public License 2.0
# * which accompanies this distribution, and is available at
# * https://www.eclipse.org/legal/epl-2.0/
# *
# * Contributors:
# *     Xilinx
# *****************************************************************************

from typing import Any, Dict, ByteString

from . import DoneHWCommand
from .. import services

NAME = "MemSock"


class MemsockService(services.Service):
    """TCF Xicom service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def connect(self, params: dict, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current cor1 reg.

        :param params: Server Parameters
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def disconnect(self, id, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current cor1 reg.

        :param id: id
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")
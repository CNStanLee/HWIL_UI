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

from . import DoneHWCommand
from .. import services

NAME = "XilinxReset"


class XilinxResetService(services.Service):
    """TCF XilinxReset service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def reset(self, ctx: str, type: str, params: dict, done: DoneHWCommand = None) -> services.TokenType:
        """
        reset command

        :param ctx: Context ID of the target
        :param type: Type of reset
        :param params: parameters in dict format
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def getCapabilities(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
         Command to get capabilities.

        :param ctx: Context ID of the target
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

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

NAME = "stapl"


class StaplService(services.Service):
    """TCF Xicom service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def start(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current cor1 reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def stop(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
         Command to get and return current wbstar reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def close(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
         Cancel all running commands on a given node and channel.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")


class StaplListener(object):
    """Stapl event listener.
    """

    def staplData(self, size, data):
        """Called when stapl data is received.
        :param size: stapl Notes size in bytearray format
        :param data: stapl data in bytearray format

        """
        pass

    def staplNotes(self, size, data):
        """Called when stapl Notes is received.
        :param size: stapl Notes size in bytearray format
        :param data: stapl Notes in bytearray format

        """
        pass

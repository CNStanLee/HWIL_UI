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

NAME = "JtagDevice"


class JtagDeviceService(services.Service):
    """TCF JtagDevice service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def get_devices(self, done: DoneHWCommand = None) -> services.TokenType:
        """
        Get list of known idcodes
        :param done: Done callback
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def get_properties(self, idcode: int, done: DoneHWCommand = None) -> services.TokenType:
        """
        Get properties associated with idcode
        :param idcode: idcode of device
        :param done: Done callback
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def set_properties(self, props: Dict[str, Any], done: DoneHWCommand = None) -> services.TokenType:
        """
        Set properties associated with idcode
        :param props: Properties to set
        :param done: Done callback
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def add_listener(self, listener):
        """Add Jtagdevice service event listener.
        :param listener: Event listener implementation.
        """
        raise NotImplementedError("Abstract method")

    def remove_listener(self, listener):
        """Remove Jtagdevice service event listener.
        :param listener: Event listener implementation.
        """
        raise NotImplementedError("Abstract method")


class JtagDeviceListener(object):
    """
        JtagDeviceListener event listener
    """

    def devicesChanged(self):
        """Called when a new jtag device props are changed.
        """
        pass

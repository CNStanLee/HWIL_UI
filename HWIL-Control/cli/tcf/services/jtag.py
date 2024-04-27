# Copyright 2022 Xilinx, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. |JtagContext| replace::   :class:`JtagContext`

Jtag service provides basic operations to run Jtag-based transactions on a target.


.. _properties:

Properties
^^^^^^^^^^
+--------------------------+-------+------------------------------------------+
| Name                     | Type  | Description                              |
+==========================+=======+==========================================+
| ID                       | |str| | Context ID of the node in the hw_server  |
+--------------------------+-------+------------------------------------------+
| ParentID                 | |str| | Context ID of the parent node in the     |
|                          |       | hw_server.                               |
+--------------------------+-------+------------------------------------------+
| Name                     | |str| | Name of Jtag node                        |
+--------------------------+-------+------------------------------------------+
| idCode                   | |int| | IDCODE of Jtag node                      |
+--------------------------+-------+------------------------------------------+
| irLen                    | |int| | IR length Jtag node                      |
+--------------------------+-------+------------------------------------------+
| isTap                    | |int| | flag indicating if node is a JTAG tap    |
+--------------------------+-------+------------------------------------------+
| isMux                    | |int| | flag indicating if node is a mux         |
+--------------------------+-------+------------------------------------------+
| isBranch                 | |int| | flag indicating whether node is branched |
+--------------------------+-------+------------------------------------------+
| isActive                 | |int| | flag indicating whether node is active   |
+--------------------------+-------+------------------------------------------+

"""

from typing import Dict, List, Any, NewType, ByteString
from . import DoneHWCommand
from .. import services

NAME = "Jtag"


class JtagService(services.Service):
    """TCF Jtag service interface."""

    def getName(self):
        """
        Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def get_context(self, context_id: str, done: DoneHWCommand) -> Dict[str, Any]:
        """
        Gets context information on a given context id

        :param context_id: Context id of the context
        :param done: Callback with result and any error.
        :return: A dictionary of context parameters
        """
        raise NotImplementedError("Abstract method")

    def get_children(self, context_id: str, done: DoneHWCommand) -> List[str]:
        """
        Gets the children of a given context.  If no context is given then gets top level contexts.

        :param context_id: Context id of desired context
        :param done: Callback with result and any error.
        :return: List of child contexts
        """
        raise NotImplementedError("Abstract method")

    def get_capabilities(self, context_id: str, done: DoneHWCommand) -> Dict[str, Any]:
        """
        Gets the capabilites of a given context.

        :param context_id: Context id of the context
        :param done: Callback with result and any error.
        :return: A dictionary of the capabilities
        """
        raise NotImplementedError("Abstract method")

    def set_option(
        self, context_id: str, key: str, value: str or int, done: DoneHWCommand
    ) -> services.TokenType:
        """
        Sets an option for a Jtag context

        :param context_id: Context id of the context
        :param key: Name of the option
        :param value: New value of the option
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def get_option(self, context_id: str, key: str, done: DoneHWCommand) -> services.TokenType:
        """
        Retrieves an option value for a specific Jtag context.  The value is returned in the results

        :param context_id: Context id of the context
        :param key: Name of the option
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def lock(self, context_id: str, timeout: int, done: DoneHWCommand) -> services.TokenType:
        """
        Locks a specific Jtag context

        :param context_id: Context id of the context
        :param timeout: timeout in milliseconds
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def unlock(self, context_id: str, done: DoneHWCommand) -> services.TokenType:
        """
        Unlocks a specific Jtag context

        :param context_id: Context id of the context
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def claim(self, context_id: str, mask: int, done: DoneHWCommand) -> services.TokenType:
        """
        Set claim mask for current JTAG device.

        :param context_id: Context id of the context
        :param mask: The claim mask allow clients to negotiate control
        over JTAG devices
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def disclaim(self, context_id: str, mask: int, done: DoneHWCommand) -> services.TokenType:
        """
        Clear claim mask for current JTAG device.

        :param context_id: Context id of the context
        :param mask: The claim mask allow clients to negotiate control
        over JTAG devices
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def sequence(
        self, context_id: str, params: dict, commands: list, data: ByteString, done: DoneHWCommand
    ) -> services.TokenType:
        """
        Run JTAG sequence operations contained in list of commands

        :param context_id: Context id of the context
        :param commands: List of JTAG sequence operations and their parameters
        :param params: params in dict format
        :param data: Byte string of data corresponding to specified list of commands
        :param done: Callback with the result and any error
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def add_listener(self, listener):
        """Add Jtag service event listener.
        :param listener: Event listener implementation.
        """
        raise NotImplementedError("Abstract method")

    def remove_listener(self, listener):
        """Remove Jtag service event listener.
        :param listener: Event listener implementation.
        """
        raise NotImplementedError("Abstract method")


class JtagListener(object):
    """Jtag event listener is notified when jtag context hierarchy changes,
    and when jtag is modified by Jtag service commands.
    """

    def contextAdded(self, contexts):
        """Called when a new jtag access context(s) is created.
        :param contexts: A list of |JtagContext| properties which have been
        added to jtag space.
        :type contexts: |list|

        """
        pass

    def contextChanged(self, contexts):
        """Called when a jtag access context(s) properties changed.
        :param contexts: A list of |JtagContext| properties which have been
        changed in jtag space.

        :type contexts: |list|

        """
        pass

    def contextRemoved(self, context_ids: List[str]):
        """Called when jtag access context(s) is removed.
        :param context_ids: A list of the IDs of jtag contexts which have
        been removed from jtag space.

        :type context_ids: |list|

        """
        pass
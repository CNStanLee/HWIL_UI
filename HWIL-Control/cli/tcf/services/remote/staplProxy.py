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
import base64
import json
from typing import ByteString, Dict, Any
from tcf.services import DoneHWCommand, Token, stapl
from tcf import channel


class staplProxy(stapl.StaplService):
    """TCF Stapl service interface."""

    def __init__(self, channel):
        super(staplProxy, self).__init__(channel)
        self.listeners = {}

    def start(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current cor1 reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("start", (ctx,), done)

    def stop(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
         Command to get and return current wbstar reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("stop", (ctx,), done)

    def close(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
         Cancel all running commands on a given node and channel.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("close", (ctx,), done)

    def addListener(self, listener):
        """Add stapl service event listener.
        :param listener: Event listener implementation.
        """
        l = ChannelEventListener(self, listener)
        self.channel.addEventListener(self, l)
        self.listeners[listener] = l

    def removeListener(self, listener):
        """Remove stapl service event listener.
        :param listener: Event listener implementation.
        """
        l = self.listeners.get(listener)
        if l:
            del self.listeners[listener]
            self.channel.removeEventListener(self, l)


class ChannelEventListener(channel.EventListener):
    def __init__(self, service, listener):
        self.service = service
        self.listener = listener

    def event(self, name, data):
        try:
            args = channel.fromJSONSequence(data)
            stapl_data = base64.b64decode(args[1])
            if name == "staplData":
                assert len(args) == 2
                self.listener.staplData(args[0], stapl_data)
            elif name == "staplNotes":
                assert len(args) == 2
                self.listener.staplNotes(args[0], stapl_data)
            else:
                raise IOError("Stapl service: unknown event: " + name)
        except Exception as x:
            import sys
            x.tb = sys.exc_info()[2]
            self.service.channel.terminate(x)

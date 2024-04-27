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

from typing import Dict, Any
from tcf.services import DoneHWCommand, Token, jtagdevice
from tcf import channel


class JtagDeviceProxy(jtagdevice.JtagDeviceService):
    """TCF JtagCable service interface."""

    def __init__(self, channel):
        super(JtagDeviceProxy, self).__init__(channel)
        self.listeners = {}

    def get_devices(self, done: DoneHWCommand = None) -> Token:
        """
        Get list of known idcodes
        :param done: Done callback
        :return: Token of request
        """
        return self.send_xicom_command("getDevices", (), done)

    def get_properties(self, idcode: int, done: DoneHWCommand = None) -> Token:
        """
        Get properties associated with idcode
        :param idcode: idcode of device
        :param done: Done callback
        :return: Token of request
        """
        return self.send_xicom_command("getProperties", (idcode,), done)

    def set_properties(self, props: Dict[str, Any], done: DoneHWCommand = None) -> Token:
        """
        Set properties associated with idcode
        :param props: Properties to set
        :param done: Done callback
        :return: Token of request
        """
        return self.send_xicom_command("setProperties", (props,), done)

    def addListener(self, listener):
        """Add Jtag service event listener.
        :param listener: Event listener implementation.
        """
        l = ChannelEventListener(self, listener)
        self.channel.addEventListener(self, l)
        self.listeners[listener] = l

    def removeListener(self, listener):
        """Remove Jtag service event listener.
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
            if name == "devicesChanged":
                self.listener.devicesChanged()
            else:
                raise IOError("JtagDevice service: unknown event: " + name)
        except Exception as x:
            import sys
            x.tb = sys.exc_info()[2]
            self.service.channel.terminate(x)

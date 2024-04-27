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

from tcf import services
from . import DoneHWCommand

NAME = "JtagCable"


class JtagCableService(services.Service):
    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def getServerDescriptions(self, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def getOpenServers(self, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def getServerContext(self, server_id, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def getPortDescriptions(self, server_id, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def getContext(self, port_id, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def openServer(self, server_id, params, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def closeServer(self, server_id: str, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def openPort(self, port_id, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")

    def closePort(self, port_id, done: DoneHWCommand):
        raise NotImplementedError("Abstract method")


class JtagCableListener(object):
    """
        JtagCableListener event listener
    """

    def contextAdded(self, contexts):
        pass

    def contextChanged(self, contexts):
        pass

    def contextRemoved(self, contexts):
        pass

    def serverAdded(self, contexts):
        pass

    def serverRemoved(self, contexts):
        pass

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

from tcf.channel.Command import Command
from tcf.services import Service, DoneHWCommand, Token, jtagcable
from tcf import channel


class JtagCableProxy(jtagcable.JtagCableService):
    def __init__(self, channel):
        self.channel = channel
        self.listeners = {}

    def getServerDescriptions(self, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetServerDescriptionsCommand(Command):
            def __init__(self):
                super(GetServerDescriptionsCommand, self).__init__(
                    service.channel, service, "getServerDescriptions", None
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetServerDescriptionsCommand().token

    def getOpenServers(self, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetOpenServersCommand(Command):
            def __init__(self):
                super(GetOpenServersCommand, self).__init__(
                    service.channel, service, "getOpenServers", None
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetOpenServersCommand().token

    def getServerContext(self, server_id, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetServerContextCommand(Command):
            def __init__(self):
                super(GetServerContextCommand, self).__init__(
                    service.channel, service, "getServerContext", (server_id,)
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetServerContextCommand().token

    def getPortDescriptions(self, server_id, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetPortDescriptionsCommand(Command):
            def __init__(self):
                super(GetPortDescriptionsCommand, self).__init__(
                    service.channel, service, "getPortDescriptions", (server_id,)
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetPortDescriptionsCommand().token

    def getContext(self, port_id, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetPortContextCommand(Command):
            def __init__(self):
                super(GetPortContextCommand, self).__init__(
                    service.channel, service, "getContext", (port_id,)
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetPortContextCommand().token

    def openPort(self, port_id, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetPortOpenCommand(Command):
            def __init__(self):
                super(GetPortOpenCommand, self).__init__(
                    service.channel, service, "openPort", (port_id,)
                )

            def done(self, error, args):
                if not error:
                    error = self.toError(args[0])
                done.doneHW(self.token, error, None)

        return GetPortOpenCommand().token

    def closePort(self, port_id, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetPortCloseCommand(Command):
            def __init__(self):
                super(GetPortCloseCommand, self).__init__(
                    service.channel, service, "closePort", (port_id,)
                )

            def done(self, error, args):
                if not error:
                    error = self.toError(args[0])
                done.doneHW(self.token, error, None)

        return GetPortCloseCommand().token

    def openServer(self, server_id, params, done: DoneHWCommand = None) -> Token:
        return self.send_xicom_command("openServer", (server_id, params), done)

    def closeServer(self, server_id: str, done: DoneHWCommand = None) -> Token:
        return self.send_xicom_command("closeServer", (server_id,), done)

    def addListener(self, listener):
        """Add JtagCable service event listener.
        :param listener: Event listener implementation.
        """
        l = ChannelEventListener(self, listener)
        self.channel.addEventListener(self, l)
        self.listeners[listener] = l

    def removeListener(self, listener):
        """Remove JtagCable service event listener.
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
            if name == "contextAdded":
                assert len(args) == 1
                self.listener.contextAdded(args[0])
            elif name == "contextChanged":
                assert len(args) == 1
                self.listener.contextChanged(args[0])
            elif name == "contextRemoved":
                assert len(args) == 1
                self.listener.contextRemoved(args[0])
            elif name == "serverAdded":
                assert len(args) == 1
                self.listener.serverAdded(args[0])
            elif name == "serverRemoved":
                assert len(args) == 1
                self.listener.serverAdded(args[0])
            else:
                raise IOError("Jtag service: unknown event: " + name)
        except Exception as x:
            import sys
            x.tb = sys.exc_info()[2]
            self.service.channel.terminate(x)

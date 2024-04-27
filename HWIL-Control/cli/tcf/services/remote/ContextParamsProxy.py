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
from tcf.services import Service, DoneHWCommand, Token, contextparams
from tcf import channel


class ContextParamsProxy(contextparams.ContextParamsService):
    def __init__(self, channel):
        self.channel = channel

    def getDefinitions(self, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetDefinitionsCommand(Command):
            def __init__(self):
                super(GetDefinitionsCommand, self).__init__(
                    service.channel, service, "getDefinitions", None
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetDefinitionsCommand().token

    def getValues(self, param_name, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self

        class GetValuesCommand(Command):
            def __init__(self):
                super(GetValuesCommand, self).__init__(
                    service.channel, service, "getValues", (param_name,)
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetValuesCommand().token

    def get(self, ctx, param_name, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self
        #contextID = self.getID()
        contextID = ctx
        class GetCommand(Command):
            def __init__(self):
                super(GetCommand, self).__init__(
                    service.channel, service, "get", (contextID, param_name)
                )

            def done(self, error, args):
                argResult = None
                if not error:
                    assert len(args) == 2
                    error = self.toError(args[0])
                    argResult = args[1]
                done.doneHW(self.token, error, argResult)

        return GetCommand().token

    def set(self, ctx, param_name, param_value, done: DoneHWCommand = None) -> Token:
        done = self._makeCallback(done)
        service = self
        #contextID = self.getID()
        contextID = ctx

        class SetCommand(Command):
            def __init__(self):
                super(SetCommand, self).__init__(
                    service.channel, service, "set", (contextID, param_name, param_value)
                )

            def done(self, error, args):
                if not error:
                    assert len(args) == 1
                    error = self.toError(args[0])
                done.doneSet(self.token, error, None)

        return SetCommand().token

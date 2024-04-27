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
from tcf import channel
from tcf.services import DoneHWCommand, Token, xilinxreset


class XilinxResetProxy(xilinxreset.XilinxResetService):
    """TCF Stapl service interface."""

    def __init__(self, channel):
        super(XilinxResetProxy, self).__init__(channel)

    def reset(self, ctx: str, type: str, params: dict, done: DoneHWCommand = None) -> Token:
        """
        reset command

        :param ctx: Context ID of the target
        :param type: Type of reset
        :param params: parameters in dict format
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("reset", (ctx, type, params), done)

    def getCapabilities(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
         Command to get capabilities.

        :param ctx: Context ID of the target
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getCapabilities", (ctx,), done)

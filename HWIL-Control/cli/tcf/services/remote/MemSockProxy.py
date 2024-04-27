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
from tcf.services import DoneHWCommand, Token, memsock
from tcf import channel


class MemSockProxy(memsock.MemsockService):
    """TCF Stapl service interface."""

    def __init__(self, channel):
        super(MemSockProxy, self).__init__(channel)
        self.listeners = {}

    def connect(self, params: dict, done: DoneHWCommand = None) -> Token:
        """
        :param params: Server Parameters
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("connect", (params,), done)

    def disconnect(self, id, done: DoneHWCommand = None) -> Token:
        """
        :param id: id
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("disconnect", (id,), done)


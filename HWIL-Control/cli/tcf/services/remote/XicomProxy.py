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

from typing import ByteString, Dict, Any
from tcf.services import DoneHWCommand, Token, xicom


class XicomProxy(xicom.XicomService):
    """TCF Xicom service interface."""

    def __init__(self, channel):
        super(XicomProxy, self).__init__(channel)
        self.listeners = {}

    def get_hw_server_version_info(self, done: DoneHWCommand, **props) -> Token:
        """
        Get's the hw_server version information.

        :param done: Callback when command is complete
        :param props: Property arguments
        :return: Token of request
        """
        return self.send_xicom_command("getHwServerVersionInfo", props, done)

    def config_begin(
            self, ctx: str, props: Dict[str, Any] = None, done: DoneHWCommand = None
    ) -> Token:
        """
        Initiates the configuration process.

        :param ctx: Context ID of the device to configure
        :param props: Configuration properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        if not props:
            props = {}
        return self.send_xicom_command("configBegin", (ctx, props), done)

    def config_data(self, ctx: str, data: ByteString, done: DoneHWCommand = None) -> Token:
        """
        Sends chunk of configuration data

        :param ctx: Context ID of the device to configure
        :param data: Data chunk to configure
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("configData", (ctx, data), done)

    def config_end(
            self, ctx: str, props: Dict[str, Any] = None, done: DoneHWCommand = None
    ) -> Token:
        """
        Ends the configuration process.

        :param ctx: Context ID of the device to configure
        :param props: Configuration properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        if not props:
            props = {}
        return self.send_xicom_command("configEnd", (ctx, props), done)

    def config_reset(
            self, ctx: str, props: Dict[str, Any] = None, done: DoneHWCommand = None
    ) -> Token:
        """
        Resets the device configuration.

        :param ctx: Context ID of the device to configure
        :param props: Configuration reset properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        if not props:
            props = {}
        return self.send_xicom_command("configReset", (ctx, props), done)

    def secure_debug(self, ctx: str, data: ByteString, done: DoneHWCommand = None) -> Token:
        """
        Enables secure debug using authentication data.

        :param ctx: Context ID of the device
        :param data: Authentication data
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("secureDebug", (ctx, data), done)

    def config_in(self, ctx, start_pos, total_bytes, data_bytes, data, done):
        return self.send_command("configIn", (ctx, start_pos, total_bytes, data_bytes, data), done)

    def config_start(self, ctx, done):
        return self.send_command("configStart", (ctx,), done)

    def jtag_reg_list(self, ctx: str or int, done: DoneHWCommand = None) -> Token:
        """
        Retrieves list of available JTAG register context IDs

        :param ctx: Context ID of device or idcode of a jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("jtagRegList", (ctx,), done)

    def jtag_reg_def(self, reg_ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Retrieves the definition of a given JTAG register context ID

        :param reg_ctx: JTAG register context ID
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("jtagRegDef", (reg_ctx,), done)

    def jtag_reg_get(self, ctx: str, reg_ctx: str, slr: int = 0, done: DoneHWCommand = None) -> Token:
        """
        Retrieves the current value for a given register

        :param ctx: Context ID of device
        :param reg_ctx: JTAG register context ID
        :param slr: Select which SLR to read
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_xicom_command("jtagRegGet", (ctx, reg_ctx, slr), done)

    def readback_config(
            self, ctx: str, props: Dict[str, Any] = None, done: DoneHWCommand = None
    ) -> Token:
        """
        Reads back configuration through the SBI that has been previously set up with another PDI.

        :param ctx: Context ID of the device
        :param props: Property arguments
        +-------------------+----------------------+------------------------------------------+
        | Name              | Type                 | Description                              |
        +===================+======================+==========================================+
        | size              | |int|                | Byte size of the readback                |
        +-------------------+----------------------+------------------------------------------+
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        if not props:
            props = {}
        return self.send_xicom_command("readbackConfig", (ctx, props), done)

    def get_bit_file_properties(self, ctx: str, data_count: int, data: int, done: DoneHWCommand = None) -> Token:
        """
        Returning a list of properties by reading the header of a bitfile.

        :param ctx: rContext ID of the jtag device
        :param data_count: size of data bytes
        :param data: header data
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getBitfileProperties", (ctx, data_count, data), done)

    def config_prog(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to issue config prog sequences and check that FPGA is ready to program.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("configProg", (ctx,), done)

    def get_config_status(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current config status.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getConfigStatus", (ctx,), done)

    def get_ir_status(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return an IR capture status.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getIRStatus", (ctx,), done)

    def get_boot_status(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current config status.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getBootStatus", (ctx,), done)

    def get_timer_reg(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current timer reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getTimerReg", (ctx,), done)

    def get_cor0_reg(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current cor0 reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getCOR0", (ctx,), done)

    def get_cor1_reg(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
        Command to get and return current cor1 reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getCOR1", (ctx,), done)

    def get_wbstar(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
         Command to get and return current wbstar reg.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("getWBSTAR", (ctx,), done)

    def cancel(self, ctx: str, done: DoneHWCommand = None) -> Token:
        """
         Cancel all running commands on a given node and channel.

        :param ctx: rContext ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        return self.send_command("cancel", (ctx,), done)

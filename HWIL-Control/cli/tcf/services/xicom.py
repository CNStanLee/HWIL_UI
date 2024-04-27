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

NAME = "Xicom"
XICOM_EVEREST_SERVICE = "XicomEverest"
"""Xicom services names."""


class DoneXicom(services.DoneHWCommand):
    """Client call back interface for generic commands."""

    def doneHW(self, token, error, results):
        """Called when memory operation command command is done.

        :param token: Command handle.
        :param error: Error object or **None**.
        :param results: List of results from command
        """
        pass


class XicomService(services.Service):
    """TCF Xicom service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return NAME

    def get_hw_server_version_info(self, done, **props):
        """
        Get's the hw_server version information.

        :param done: Callback when command is complete
        :param props: Property arguments
        :return: Token of request
        """
        raise NotImplementedError("Abstract method")

    def config_begin(self, ctx: str, props: Dict[str, Any] = {}, done: DoneHWCommand = None) -> services.TokenType:
        """
        Initiates the configuration process.

        :param ctx: Context ID of the device
        :param props: Configuration properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def config_data(self, ctx: str, data: ByteString, done: DoneHWCommand = None) -> services.TokenType:
        """
        Sends chunk of configuration data

        :param ctx: Context ID of the device to configure
        :param data: Data chunk to configure
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract Method")

    def config_end(self, ctx: str, props: Dict[str, Any] = {}, done: DoneHWCommand = None) -> services.TokenType:
        """
        Ends the configuration process.

        :param ctx: Context ID of the device to configure
        :param props: Configuration properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def config_reset(self, ctx: str, props: Dict[str, Any] = {}, done: DoneHWCommand = None) -> services.TokenType:
        """
        Resets the device configuration.

        :param ctx: Context ID of the device to configure
        :param props: Configuration reset properties
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def config_secure_debug(self, ctx: str, data: ByteString, done: DoneHWCommand = None) -> services.TokenType:
        """
        Enables secure debug using authentication data.

        :param ctx: Context ID of the device
        :param data: Authentication data
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract Method")

    def config_in(self, ctx, start_pos, total_bytes, data_bytes, data, done):
        raise NotImplementedError("Abstract method")

    def config_start(self, ctx, done):
        raise NotImplementedError("Abstract method")

    def jtag_reg_list(self, ctx: str or int, done: DoneHWCommand = None) -> services.TokenType:
        """
        Retrieves list of available JTAG register context IDs

        :param ctx: Context ID of device or idcode of a jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def jtag_reg_def(self, reg_ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Retrieves the definition of a given JTAG register context ID

        :param reg_ctx: JTAG register context ID
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def jtag_reg_get(self, ctx: str, reg_ctx: str, slr: int = 0, done: DoneHWCommand = None) -> services.TokenType:
        """
        Retrieves the current value for a given register

        :param ctx: Context ID of device
        :param reg_ctx: JTAG register context ID
        :param slr: Select which SLR to read
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_bit_file_properties(self, ctx: str, size: int, data: int, done: DoneHWCommand = None) -> services.TokenType:
        """
        Returning a list of properties by reading the header of a bitfile.

        :param ctx: Context ID of the jtag device
        :param size: size of data bytes
        :param data: header data
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def config_prog(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to issue config prog sequences and check that FPGA is ready to program.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_config_status(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current config status.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_ir_status(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return an IR capture status.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_boot_status(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current config status.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_timer_reg(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current timer reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_cor0_reg(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current cor0 reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_cor1_reg(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
        Command to get and return current cor1 reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def get_wbstar(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
         Command to get and return current wbstar reg.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

    def cancel(self, ctx: str, done: DoneHWCommand = None) -> services.TokenType:
        """
         Cancel all running commands on a given node and channel.

        :param ctx: Context ID of the jtag device
        :param done: Callback with the result and any error
        :return: Token of command sent
        """
        raise NotImplementedError("Abstract method")

class XicomEverestService(services.Service):
    """TCF JtagCable service interface."""

    def getName(self):
        """Get this service name.

        :returns: The value of string :const:`NAME`
        """
        return XICOM_EVEREST_SERVICE

    def config(self, ctx: str, data: bytes, options: Dict[str, Any] = {}, done: DoneHWCommand = None) -> Dict[str, Any]:
        """
        Configures the device with given PDI data

        :param ctx: Context ID of the device to update
        :param data: Binary data to configure device
        :param options: dict of optional parameters for configuration
        :param done: Callback with the result and any error
        :return: Dictionary of success
        """
        raise NotImplementedError("Abstract method")

    def get_status(self, ctx: str, need_definitions: bool, done: DoneHWCommand) -> Dict[str, Any]:
        """
        Grabs the status registers from the pmc_tap
        :param ctx: Context ID of the device to update
        :param need_definitions: Flag to grab the bit definitions of the status registers
        :param done: Callback with the result and any error
        :return: Dictionary of status registers
        """
        raise NotImplementedError("Abstract method")

    def get_static(self, ctx: str, need_definitions: bool, done: DoneHWCommand) -> Dict[str, Any]:
        """
        Grabs the static status registers from the pmc_tap
        :param ctx: Context ID of the device to update
        :param need_definitions: Flag to grab the bit definitions of the status registers
        :param done: Callback with the result and any error
        :return: Dictionary of status registers
        """
        raise NotImplementedError("Abstract method")

    def reset(self, ctx: str, done: DoneHWCommand) -> Dict[str, Any]:
        """
        Runs a system reset through the pmc_tap
        :param ctx: Context ID of the device to reset
        :param done: Callback with the result and any error
        :return: Dictionary of status registers
        """
        raise NotImplementedError("Abstract method")

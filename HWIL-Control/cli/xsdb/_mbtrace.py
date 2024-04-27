#######################################################################
# Copyright (c) 2023 Xilinx, Inc.  All rights reserved.
#
# This   document  contains  proprietary information  which   is
# protected by  copyright. All rights  are reserved. No  part of
# this  document may be photocopied, reproduced or translated to
# another  program  language  without  prior written  consent of
# XILINX Inc., San Jose, CA. 95124
#
# Xilinx, Inc.
# XILINX IS PROVIDING THIS DESIGN, CODE, OR INFORMATION "AS IS" AS A
# COURTESY TO YOU.  BY PROVIDING THIS DESIGN, CODE, OR INFORMATION AS
# ONE POSSIBLE   IMPLEMENTATION OF THIS FEATURE, APPLICATION OR
# STANDARD, XILINX IS MAKING NO REPRESENTATION THAT THIS IMPLEMENTATION
# IS FREE FROM ANY CLAIMS OF INFRINGEMENT, AND YOU ARE RESPONSIBLE
# FOR OBTAINING ANY RIGHTS YOU MAY REQUIRE FOR YOUR IMPLEMENTATION.
# XILINX EXPRESSLY DISCLAIMS ANY WARRANTY WHATSOEVER WITH RESPECT TO
# THE ADEQUACY OF THE IMPLEMENTATION, INCLUDING BUT NOT LIMITED TO
# ANY WARRANTIES OR REPRESENTATIONS THAT THIS IMPLEMENTATION IS FREE
# FROM CLAIMS OF INFRINGEMENT, IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE.
#
#######################################################################
import os.path
from xsdb._breakpoint import get_bp_status
from xsdb._elf import ElfParse
from xsdb._utils import *
import struct

class MbTrace(object):
    def __init__(self, session):
        self.session = session
        self.trace_dict = dict()
        self.trace_elftext = None
        self.trace_read_seq = None
        self.trigger_event = [
            "Debug stop",
            "Continue execution",
            "Stop program trace",
            "Start program trace",
            "Stop performance monitor",
            "Start performance monitor",
            "Disable profiling",
            "Enable profiling"
        ]

        self.exception_event = [
            "Stream exception",
            "Unaligned data access exception",
            "Illegal op-code exception",
            "Instruction bus error exception",
            "Data bus error exception",
            "Divide exception",
            "Floating point unit exception",
            "Privileged instruction exception",
            "Unexpected exception 8",
            "Debug",
            "Interrupt",
            "Non-maskable break",
            "Break",
            "Unexpected exception 13",
            "Unexpected exception 14",
            "Unexpected exception 15",
            "Data storage exception",
            "Instruction storage exception",
            "Data TLB miss exception",
            "Instruction TLB miss exception",
            "Unexpected exception 20",
            "Unexpected exception 21",
            "Unexpected exception 22",
            "Unexpected exception 23",
            "Unexpected exception 24",
            "Unexpected exception 25",
            "Unexpected exception 26",
            "Unexpected exception 27",
            "Unexpected exception 28",
            "Unexpected exception 29",
            "Unexpected exception 30",
            "Unexpected exception 31",
        ]
        # Opcode definitions
        self.INST_PC_OFFSET = 1
        self.INST_NO_OFFSET = 0
        self.IMMVAL_MASK_NON_SPECIAL = 0x0000
        self.IMMVAL_MASK_MTS = 0x4000
        self.IMMVAL_MASK_MFS = 0x0000
        self.OPCODE_MASK_H = 0xFC000000
        self.OPCODE_MASK_H1 = 0xFFE00000
        self.OPCODE_MASK_H2 = 0xFC1F0000
        self.OPCODE_MASK_H12 = 0xFFFF0000
        self.OPCODE_MASK_H4 = 0xFC0007FF
        self.OPCODE_MASK_H13S = 0xFFE0E7F0
        self.OPCODE_MASK_H23S = 0xFC1FC000
        self.OPCODE_MASK_H34 = 0xFC00FFFF
        self.OPCODE_MASK_H14 = 0xFFE007FF
        self.OPCODE_MASK_H24 = 0xFC1F07FF
        self.OPCODE_MASK_H124 = 0xFFFF07FF
        self.OPCODE_MASK_H1234 = 0xFFFFFFFF
        self.OPCODE_MASK_H3 = 0xFC000700
        self.OPCODE_MASK_H3B = 0xFC00E600
        self.OPCODE_MASK_H32 = 0xFC00FC00
        self.OPCODE_MASK_H32B = 0xFC00E000
        self.OPCODE_MASK_H34B = 0xFC0004FF
        self.OPCODE_MASK_H23N = 0xFC1F8000
        self.OPCODE_MASK_H34C = 0xFC0007E0
        self.OPCODE_MASK_H8 = 0xFF000000
        self.DELAY_SLOT = 1
        self.NO_DELAY_SLOT = 0
        self.opcodes = [
            ["add", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x00000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsub", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x04000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x08000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsubc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x0C000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addk", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x10000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsubk", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["cmp", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000001, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["cmpu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000003, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addkc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x18000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsubkc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x1C000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x20000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["rsubi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x24000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["addic", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x28000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["rsubic", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x2C000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["addik", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x30000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["rsubik", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x34000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["addikc", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x38000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["rsubikc", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x3C000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["mul", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x40000000, self.OPCODE_MASK_H4, "mult_inst"],
            ["mulh", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x40000001, self.OPCODE_MASK_H4, "mult_inst"],
            ["mulhu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x40000003, self.OPCODE_MASK_H4, "mult_inst"],
            ["mulhsu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x40000002, self.OPCODE_MASK_H4, "mult_inst"],
            ["idiv", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x48000000, self.OPCODE_MASK_H4, "div_inst"],
            ["idivu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x48000002, self.OPCODE_MASK_H4, "div_inst"],
            ["bsll", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000400, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["bsra", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000200, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["bsrl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000000, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["get", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C000000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["put", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C008000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["nget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C004000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["nput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00C000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["cget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C002000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["cput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00A000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ncget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C006000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ncput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00E000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["muli", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x60000000, self.OPCODE_MASK_H, "mult_inst"],
            ["bslli", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64000400, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bsrai", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64000200, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bsrli", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64000000, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bsefi", "INST_TYPE_RD_R1_IMM_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64004000, self.OPCODE_MASK_H32B, "barrel_shift_inst"],
            ["bsifi", "INST_TYPE_RD_R1_IMM_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64008000, self.OPCODE_MASK_H32B, "barrel_shift_inst"],
            ["or", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x80000000, self.OPCODE_MASK_H4, "logical_inst"],
            ["and", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x84000000, self.OPCODE_MASK_H4, "logical_inst"],
            ["xor", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x88000000, self.OPCODE_MASK_H4, "logical_inst"],
            ["andn", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x8C000000, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmpbf", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x80000400, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmpbc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x84000400, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmpeq", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x88000400, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmpne", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x8C000400, self.OPCODE_MASK_H4, "logical_inst"],
            ["clz", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x900000E0, self.OPCODE_MASK_H34, "logical_inst"],
            ["swapb", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x900001E0, self.OPCODE_MASK_H34, "logical_inst"],
            ["swaph", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x900001E2, self.OPCODE_MASK_H34, "logical_inst"],
            ["sra", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000001, self.OPCODE_MASK_H34, "logical_inst"],
            ["src", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000021, self.OPCODE_MASK_H34, "logical_inst"],
            ["srl", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000041, self.OPCODE_MASK_H34, "logical_inst"],
            ["sext8", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000060, self.OPCODE_MASK_H34, "logical_inst"],
            ["sext16", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000061, self.OPCODE_MASK_H34, "logical_inst"],
            ["wic", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000068, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000064, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc.flush", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT,
             self.IMMVAL_MASK_NON_SPECIAL, 0x90000074, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc.clear", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT,
             self.IMMVAL_MASK_NON_SPECIAL, 0x90000066, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc.clear.ea", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT,
             self.IMMVAL_MASK_NON_SPECIAL, 0x900000e6, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc.ext.flush", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT,
             self.IMMVAL_MASK_NON_SPECIAL, 0x90000476, self.OPCODE_MASK_H34B, "special_inst"],
            ["wdc.ext.clear", "INST_TYPE_RD_R1_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT,
             self.IMMVAL_MASK_NON_SPECIAL, 0x90000466, self.OPCODE_MASK_H34B, "special_inst"],
            ["mts", "INST_TYPE_SPECIAL_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_MTS, 0x9400C000,
             self.OPCODE_MASK_H13S, "special_inst"],
            ["mfs", "INST_TYPE_RD_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_MFS, 0x94008000,
             self.OPCODE_MASK_H23S, "special_inst"],
            ["mfse", "INST_TYPE_RD_SPECIAL", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_MFS, 0x94088000,
             self.OPCODE_MASK_H23S, "special_inst"],
            ["br", "INST_TYPE_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x98000000,
             self.OPCODE_MASK_H124, "branch_inst"],
            ["brd", "INST_TYPE_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x98100000,
             self.OPCODE_MASK_H124, "branch_inst"],
            ["brld", "INST_TYPE_RD_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x98140000,
             self.OPCODE_MASK_H24, "branch_inst"],
            ["bra", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x98080000,
             self.OPCODE_MASK_H124, "branch_inst"],
            ["brad", "INST_TYPE_R2", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x98180000,
             self.OPCODE_MASK_H124, "branch_inst"],
            ["brald", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x981C0000,
             self.OPCODE_MASK_H24, "branch_inst"],
            ["brk", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x980C0000, self.OPCODE_MASK_H24, "branch_inst"],
            ["beq", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9C000000, self.OPCODE_MASK_H14, "branch_inst"],
            ["beqd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9E000000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["bne", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9C200000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bned", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9E200000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["blt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9C400000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bltd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9E400000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["ble", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9C600000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bled", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9E600000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["bgt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9C800000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bgtd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9E800000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["bge", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9CA00000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bged", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x9EA00000,
             self.OPCODE_MASK_H14, "branch_inst"],
            ["ori", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xA0000000, self.OPCODE_MASK_H, "logical_inst"],
            ["andi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xA4000000, self.OPCODE_MASK_H, "logical_inst"],
            ["xori", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xA8000000, self.OPCODE_MASK_H, "logical_inst"],
            ["andni", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xAC000000, self.OPCODE_MASK_H, "logical_inst"],
            ["imm", "INST_TYPE_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB0000000,
             self.OPCODE_MASK_H12, "immediate_inst"],
            ["rtsd", "INST_TYPE_R1_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB6000000,
             self.OPCODE_MASK_H1, "return_inst"],
            ["rtid", "INST_TYPE_R1_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB6200000,
             self.OPCODE_MASK_H1, "return_inst"],
            ["rtbd", "INST_TYPE_R1_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB6400000,
             self.OPCODE_MASK_H1, "return_inst"],
            ["rted", "INST_TYPE_R1_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB6800000,
             self.OPCODE_MASK_H1, "return_inst"],
            ["bri", "INST_TYPE_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB8000000,
             self.OPCODE_MASK_H12, "branch_inst"],
            ["brid", "INST_TYPE_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB8100000,
             self.OPCODE_MASK_H12, "branch_inst"],
            ["brlid", "INST_TYPE_RD_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xB8140000, self.OPCODE_MASK_H2, "branch_inst"],
            ["brai", "INST_TYPE_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB8080000,
             self.OPCODE_MASK_H12, "branch_inst"],
            ["braid", "INST_TYPE_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB8180000,
             self.OPCODE_MASK_H12, "branch_inst"],
            ["bralid", "INST_TYPE_RD_IMM", self.INST_NO_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xB81C0000, self.OPCODE_MASK_H2, "branch_inst"],
            ["brki", "INST_TYPE_RD_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xB80C0000, self.OPCODE_MASK_H2, "branch_inst"],
            ["beqi", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBC000000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beqid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBE000000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bnei", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBC200000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bneid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBE200000, self.OPCODE_MASK_H1, "branch_inst"],
            ["blti", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBC400000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bltid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBE400000, self.OPCODE_MASK_H1, "branch_inst"],
            ["blei", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBC600000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bleid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBE600000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bgti", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBC800000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bgtid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBE800000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bgei", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBCA00000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bgeid", "INST_TYPE_R1_IMM", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBEA00000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beaeqi", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBD000000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beaeqid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBF000000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beanei", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBD200000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beaneid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBF200000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bealti", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBD400000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bealtid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBF400000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bealei", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBD600000, self.OPCODE_MASK_H1, "branch_inst"],
            ["bealeid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBF600000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beagti", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBD800000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beagtid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBF800000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beagei", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBDA00000, self.OPCODE_MASK_H1, "branch_inst"],
            ["beageid", "INST_TYPE_R1_IMML", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xBFA00000, self.OPCODE_MASK_H1, "branch_inst"],
            ["lbu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC0000000, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lbur", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC0000200, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lbuea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC0000080, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lhu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC4000000, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lhur", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC4000200, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lhuea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC4000080, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lw", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000000, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lwr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000200, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lwx", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000400, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["lwea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000080, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["sb", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD0000000, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["sbr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD0000200, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["sbea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD0000080, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["sh", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD4000000, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["shr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD4000200, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["shea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD4000080, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["sw", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000000, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["swr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000200, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["swx", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000400, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["swea", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000080, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["lbui", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xE0000000, self.OPCODE_MASK_H, "memory_load_inst"],
            ["lhui", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xE4000000, self.OPCODE_MASK_H, "memory_load_inst"],
            ["lwi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xE8000000, self.OPCODE_MASK_H, "memory_load_inst"],
            ["lli", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xEC000000, self.OPCODE_MASK_H, "memory_load_inst"],
            ["sbi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xF0000000, self.OPCODE_MASK_H, "memory_store_inst"],
            ["shi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xF4000000, self.OPCODE_MASK_H, "memory_store_inst"],
            ["swi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xF8000000, self.OPCODE_MASK_H, "memory_store_inst"],
            ["sli", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xFC000000, self.OPCODE_MASK_H, "memory_store_inst"],
            ["nop", "INST_TYPE_NONE", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x80000000,
             self.OPCODE_MASK_H1234, "logical_inst"],
            ["la", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x30000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["tuqula", "INST_TYPE_RD", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x3000002A, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["not", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xA800FFFF, self.OPCODE_MASK_H34, "logical_inst"],
            ["neg", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x04000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["rtb", "INST_TYPE_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0xB6000004,
             self.OPCODE_MASK_H1, "return_inst"],
            ["sub", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x04000000, self.OPCODE_MASK_H, "arithmetic_inst"],
            ["lmi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xE8000000, self.OPCODE_MASK_H, "memory_load_inst"],
            ["smi", "INST_TYPE_RD_R1_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xF8000000, self.OPCODE_MASK_H, "memory_store_inst"],
            ["msrset", "INST_TYPE_RD_IMM15", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x94100000, self.OPCODE_MASK_H23N, "special_inst"],
            ["msrclr", "INST_TYPE_RD_IMM15", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x94110000, self.OPCODE_MASK_H23N, "special_inst"],
            ["fadd", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000000, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["frsub", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000080, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fmul", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fdiv", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000180, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.lt", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000210, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.eq", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000220, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.le", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000230, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.gt", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000240, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.ne", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000250, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.ge", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000260, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fcmp.un", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000200, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["flt", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000280, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fint", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000300, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["fsqrt", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000380, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["tget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C001000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tcget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C003000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C005000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tncget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C007000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C009000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tcput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00B000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00D000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tncput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00F000, self.OPCODE_MASK_H32, "anyware_inst"],
            ["eget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C000400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ecget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C002400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["neget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C004400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["necget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C006400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["eput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C008400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ecput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00A400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["neput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00C400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["necput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00E400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["teget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C001400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tecget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C003400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tneget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C005400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnecget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C007400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["teput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C009400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tecput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00B400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tneput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00D400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnecput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00F400, self.OPCODE_MASK_H32, "anyware_inst"],
            ["aget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C000800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["caget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C002800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["naget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C004800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ncaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C006800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["aput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C008800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["caput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00A800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["naput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00C800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ncaput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00E800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["taget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C001800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tcaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C003800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C005800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tncaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C007800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["taput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C009800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tcaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00B800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00D800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tncaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00F800, self.OPCODE_MASK_H32, "anyware_inst"],
            ["eaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C000C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ecaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C002C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["neaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C004C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["necaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C006C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["eaput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C008C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["ecaput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00AC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["neaput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00CC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["necaput", "INST_TYPE_R1_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00EC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["teaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C001C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tecaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C003C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tneaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C005C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnecaget", "INST_TYPE_RD_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C007C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["teaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C009C00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tecaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00BC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tneaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00DC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["tnecaput", "INST_TYPE_IMM7", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6C00FC00, self.OPCODE_MASK_H32, "anyware_inst"],
            ["getd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000000, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000080, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["cgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000100, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tcgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000180, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ngetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000200, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tngetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000280, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ncgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000300, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tncgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000380, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["putd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000400, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL, 0x4C000480,
             self.OPCODE_MASK_H34C, "anyware_inst"],
            ["cputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000500, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tcputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000580, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["nputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000600, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000680, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ncputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000700, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tncputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000780, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["egetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000020, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tegetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0000A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ecgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000120, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tecgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0001A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["negetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000220, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnegetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0002A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["necgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000320, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnecgetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0003A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["eputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000420, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["teputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0004A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ecputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000520, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tecputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0005A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["neputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000620, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tneputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0006A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["necputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000720, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnecputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0007A0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["agetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000040, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0000C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["cagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000140, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tcagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0001C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["nagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000240, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0002C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ncagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000340, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tncagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0003C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["aputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000440, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["taputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0004C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["caputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000540, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tcaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0005C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["naputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000640, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0006C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ncaputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000740, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tncaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0007C0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["eagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000060, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["teagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0000E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ecagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000160, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tecagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0001E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["neagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000260, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tneagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0002E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["necagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000360, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnecagetd", "INST_TYPE_RD_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0003E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["eaputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000460, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["teaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0004E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["ecaputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000560, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tecaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0005E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["neaputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000660, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tneaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0006E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["necaputd", "INST_TYPE_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C000760, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["tnecaputd", "INST_TYPE_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x4C0007E0, self.OPCODE_MASK_H34C, "anyware_inst"],
            ["addl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x00000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsubl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x04000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addlc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x08000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsublc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x0C000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addlk", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x10000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsublk", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["addlkc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x18000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["rsublkc", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x1C000100, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["cmpl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000101, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["cmplu", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x14000103, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["mull", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x40000100, self.OPCODE_MASK_H4, "mult_inst"],
            ["bslll", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000500, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["bslra", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000300, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["bslrl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x44000100, self.OPCODE_MASK_H3, "barrel_shift_inst"],
            ["bsllli", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64002400, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bslrai", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64002200, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bslrli", "INST_TYPE_RD_R1_IMMS", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64002000, self.OPCODE_MASK_H3B, "barrel_shift_inst"],
            ["bslefi", "INST_TYPE_RD_R1_IMM_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x64006000, self.OPCODE_MASK_H32B, "barrel_shift_inst"],
            ["bslifi", "INST_TYPE_RD_R1_IMM_IMM", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x6400A000, self.OPCODE_MASK_H32B, "barrel_shift_inst"],
            ["orl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x80000100, self.OPCODE_MASK_H4, "logical_inst"],
            ["andl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x84000100, self.OPCODE_MASK_H4, "logical_inst"],
            ["xorl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x88000100, self.OPCODE_MASK_H4, "logical_inst"],
            ["andnl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x8C000100, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmplbf", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x80000500, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmpleq", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x88000500, self.OPCODE_MASK_H4, "logical_inst"],
            ["pcmplne", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x8C000500, self.OPCODE_MASK_H4, "logical_inst"],
            ["srla", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000101, self.OPCODE_MASK_H34, "logical_inst"],
            ["srlc", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000121, self.OPCODE_MASK_H34, "logical_inst"],
            ["srll", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000141, self.OPCODE_MASK_H34, "logical_inst"],
            ["sextl8", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000160, self.OPCODE_MASK_H34, "logical_inst"],
            ["sextl16", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000161, self.OPCODE_MASK_H34, "logical_inst"],
            ["sextl32", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x90000162, self.OPCODE_MASK_H34, "logical_inst"],
            ["beaeq", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D000000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealeq", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D000100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beaeqd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F000000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealeqd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F000100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beane", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D200000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealne", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D200100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beaned", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F200000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealned", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F200100, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D400000, self.OPCODE_MASK_H14, "branch_inst"],
            ["beallt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D400100, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealtd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F400000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealltd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F400100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beale", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D600000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealle", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D600100, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealed", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F600000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealled", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F600100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beagt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D800000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealgt", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9D800100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beagtd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F800000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealgtd", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9F800100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beage", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9DA00000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealge", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9DA00100, self.OPCODE_MASK_H14, "branch_inst"],
            ["beaged", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9FA00000, self.OPCODE_MASK_H14, "branch_inst"],
            ["bealged", "INST_TYPE_R1_R2", self.INST_PC_OFFSET, self.DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x9FA00100, self.OPCODE_MASK_H14, "branch_inst"],
            ["imml", "INST_TYPE_IMML", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xB2000000, self.OPCODE_MASK_H8, "immediate_inst"],
            ["ll", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000100, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["llr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xC8000300, self.OPCODE_MASK_H4, "memory_load_inst"],
            ["sl", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000100, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["slr", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0xD8000300, self.OPCODE_MASK_H4, "memory_store_inst"],
            ["dadd", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000400, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["drsub", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000480, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dmul", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000500, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["ddiv", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000580, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.lt", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000610, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.eq", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000620, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.le", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000630, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.gt", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000640, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.ne", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000650, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.ge", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000660, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dcmp.un", "INST_TYPE_RD_R1_R2", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000600, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dbl", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000680, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dlong", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000700, self.OPCODE_MASK_H4, "arithmetic_inst"],
            ["dsqrt", "INST_TYPE_RD_R1", self.INST_NO_OFFSET, self.NO_DELAY_SLOT, self.IMMVAL_MASK_NON_SPECIAL,
             0x58000780, self.OPCODE_MASK_H4, "arithmetic_inst"],
        ]

    def mbtrace_set_config(self, config: dict):
        self.trace_dict = config
        self.trace_dict['init_done'] = 0

    def mbtrace_init(self, props):
        td = self.trace_dict
        td['ctrl_reg'] = 0
        td['cmd_reg'] = 0
        td['cycles'] = 0
        td['packet_count'] = 0
        td['tpiu_packet'] = list()
        td['tpiu_index'] = 0
        td['ftm_packet'] = list()
        td['ftm_index'] = 0
        td['dis_getaddr'] = 0x0
        td['dis_items'] = list()
        td['dis_index'] = 0
        td['init_done'] = 1

        mode = td['mode']
        halt = td['halt']
        save = td['save']
        low = td['low']
        high = td['high']
        data_format = td['data_format']
        trace_dma = td['trace_dma']
        self.mbtrace_set(props, mode, halt, save, low, high, data_format, trace_dma)

    def mbtrace_set(self, props, mode, halt, saveld, low, high, data_format, trace_dma):
        td = self.trace_dict
        self.__mbtrace_checkinit()
        td['mode'] = mode
        td['halt'] = halt
        td['save'] = saveld
        td['low'] = low
        td['high'] = high
        td['data_format'] = data_format
        td['trace_dma'] = trace_dma
        # Determine MicroBlaze properties: bscan, which, mdmaddr, mdmconfig
        td['bscan'] = ''
        if 'JtagChain' in props:
            td['bscan'] = props['JtagChain'][4:]
        if 'MBCore' in props and props['MBCore'] >= 0:
            td['which'] = props['MBCore']
        else:
            raise Exception('Invalid target. Only supported for MicroBlaze targets') from None
        td['mdmaddr'] = ''
        if 'MDMAddr' in props:
            td['mdmaddr'] = props['MDMAddr']
        td['mdmconfig'] = props['MDMConfig']
        # Configuration Register Read
        config_extended_debug = self.__mb_get_config(161)
        config_trace_size = self.__mb_get_config(269, 271)
        config_has_external_trace = self.__mb_get_config(275)
        config_addr_size = self.__mb_get_config(276, 281)
        config_data_size_64 = self.__mb_get_config(282)

        if config_extended_debug == 0:
            raise Exception('Trace is not enabled in the design. Enable Extended Debug in '
                            'MicroBlaze configuration') from None
        elif config_trace_size == 0:
            raise Exception('Trace is not enabled in the design. Set Profile Size in '
                            'MicroBlaze configuration') from None
        pc_items = 2
        if config_addr_size > 0 and config_data_size_64 == 1:
            pc_items = 4 if config_addr_size > 16 else 3
        td['pc_items'] = pc_items

        config_mdm = self.__mb_trace_mdm_read_config()
        config_mdm_trace_output = 0
        config_mdm_trace_protocol = 0
        if config_mdm & 0x00400000:
            config_mdm_ext = self.__mb_trace_mdm_read_ext_config()
            config_mdm_trace_output = (config_mdm_ext >> 35) & 3
            config_mdm_trace_protocol = (config_mdm_ext >> 37) & 1
        config_mdm_mb_dbg_ports = ((config_mdm >> 8) & 0xFF) > 1
        output = config_mdm_trace_output
        if output > 0 and config_has_external_trace == 0:
            output = 0
        td['output'] = output
        td['protocol'] = config_mdm_trace_protocol
        td['dbg_ports'] = config_mdm_mb_dbg_ports
        if output > 0 and mode == 0:
            raise Exception('Full trace not available with external trace') from None
        if output > 0 and low > high:
            raise Exception('Must give valid low and high address for external memory trace buffer') from None
        saveret = mode != 2
        savepc = mode == 2
        ctrl = mode << 4 | halt << 3 | savepc << 2 | saveld << 1 | saveret
        self.__mb_trace_write_control(ctrl)
        # Stop and clear trace
        cmd_stop = 2
        cmd_clear = 8
        cmd = cmd_clear | cmd_stop
        self.__mb_trace_write_command(cmd)

        # Prepare read data JTAG sequence
        bscan = td['bscan']
        which = td['which']
        if output == 0 and bscan != '':
            dbg_ports = td['dbg_ports']
            if self.trace_read_seq is not None:
                self.trace_read_seq = None
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            jt = self.session.jtag_targets(jtag_tgt)
            self.trace_read_seq = jt.sequence()
            self.trace_read_seq.irshift(state='IRUPDATE', register='bypass')
            self.trace_read_seq.irshift(state='IDLE', register=f'user{bscan}')
            self.trace_read_seq.drshift(state="DRUPDATE", bit_len=4, data=1)
            if dbg_ports > 1:
                length = dbg_ports if dbg_ports > 8 else 8
                self.trace_read_seq.drshift(state="DRUPDATE", bit_len=8, data=0x0D)
                self.trace_read_seq.drshift(state="DRUPDATE", bit_len=length, data=1 << which)
            for i in range(0, 512 - 1):
                self.trace_read_seq.drshift(state="DRUPDATE", bit_len=8, data=0x66)
                self.trace_read_seq.drshift(capture=True, state="DRUPDATE", bit_len=18, tdi=0)
            self.trace_read_seq.drshift(state="DRUPDATE", bit_len=8, data=0x66)
            self.trace_read_seq.drshift(capture=True, state="IDLE", bit_len=18, tdi=0)

            # Set AXI Stream delay between words required by FTM
            if output == 2 and data_format != 'mdm':
                self.__mb_trace_mdm_write_control(0x10, 8)

            # Set external trace low and high address
            lowaddr = low >> 16
            highaddr = high >> 16
            if output == 3:
                self.__mb_trace_mdm_write_low_addr(lowaddr)
                self.__mb_trace_mdm_write_high_addr(highaddr)
            elif output > 0:
                self.session.mwr(trace_dma + 16, lowaddr)
                self.session.mwr(trace_dma + 20, highaddr)

            # Get current ELF contents and prepare disassembly
            self.trace_elftext = dict()
            if 'elf' in td:
                elf_file = td['elf']
                f = ElfParse()
                f.open(elf_file)
                secs = f.get_exec_sections()
                for sec in secs:
                    secname = sec['sh_name']
                    secdata = f.get_elf_section_data(secname)
                    secbin = secdata[secname]['secbin']
                    secaddr = secdata[secname]['loadaddr']
                    inst = list()
                    for i in range(0, len(secbin), 4):
                        inst.append(int.from_bytes(secbin[i:i + 4], byteorder='little', signed=False))
                    for index in range(0, len(inst)):
                        instr = inst[index]
                        self.trace_elftext[secaddr] = [hex(instr), self.__disassemble(secaddr, instr)]
                        secaddr += 4
                f.close()

    def mbtrace_start(self):
        td = self.trace_dict
        self.__mbtrace_checkinit()
        output = td['output']
        halt = td['halt']
        if output == 3:
            self.__mb_trace_mdm_write_control(halt, 1)
        elif output > 0:
            trace_dma_addr = td['trace_dma']
            self.session.mwr(trace_dma_addr + 24, halt)
        cmd_start = 4
        self.__mb_trace_write_command(cmd_start)

    def mbtrace_stop(self):
        self.__mbtrace_checkinit()
        cmd_stop = 2
        self.__mb_trace_write_command(cmd_stop)

    def mbtrace_dis(self, filename=None, action='', lines=-1):
        chan = None
        if filename is not None:
            if os.path.isfile(filename) and action == '':
                raise Exception('Overwrite of existing file isn\'t enabled, use -force to overwrite, or '
                                '-append to append data') from None
            if action == 'append':
                chan = open(filename, 'a')
            else:
                chan = open(filename, 'w')
        self.__mbtrace_dis_internal(chan, lines)
        if filename is not None:
            chan.close()

    def mbtrace_continue(self, filename=None, action=''):
        td = self.trace_dict
        output = td['output']
        halt = td['halt']
        control = td['ctrl_reg']
        self.__mbtrace_checkinit()
        if output > 0:
            raise Exception('External debug must not be enabled to use continue') from None
        if halt == 0:
            control = control | 0x8
            self.__mb_trace_write_control(control)
        bp_addresses = list()
        for key, bpdata in self.session._bptable.items():
            uuid = bpdata.id
            enabled = bpdata.enabled
            bps = get_bp_status(self.session, uuid, 'full')
            if len(bps) == 0:
                continue
            for ctx, ctxdata in bps.items():
                if ctx == self.session.curtarget.node.target_id and enabled:
                    bp_address = ctxdata['Address']
                    bp_addresses.append(int(bp_address, 0))
                    break
        if len(bp_addresses) == 0:
            raise Exception('Must set at least one breakpoint or watchpoint to use continue') from None
        chan = None
        if filename is not None:
            if os.path.isfile(filename) and action == '':
                raise Exception('Overwrite of existing file isn\'t enabled, use -force to overwrite, or '
                                '-append to append data') from None
            if action == 'append':
                chan = open(filename, 'a')
            else:
                chan = open(filename, 'w')
        while True:
            self.session.con('-b')
            pc = self.session.rrd('-nv', 'pc')['pc']
            # workaround to avoid issue with next con in the loop
            self.session.stpi()
            self.session.stop()
            err = self.__mbtrace_dis_internal(chan)
            if err:
                break
            if pc in bp_addresses:
                break
            self.__mb_trace_write_control(control)
            cmd_stop = 2
            cmd_clear = 8
            cmd_start = 4
            self.__mb_trace_write_command(cmd_clear | cmd_stop)
            self.__mb_trace_write_command(cmd_start)
            total_cycles = 0
            td['cycles'] = total_cycles
        if filename is not None:
            chan.close()

    def __mbtrace_checkinit(self):
        td = self.trace_dict
        if td['init_done'] == 1:
            return 1
        raise Exception('Trace not configured, please configure using command mbtrace') from None

    def __get_instr(self, pc, disas=0):
        if len(self.trace_elftext) == 0:
            result = self.session.mrd('-v', pc)
            if disas:
                result = self.__disassemble(pc, result)
        else:
            result = self.trace_elftext[pc]
            if result == '':
                if disas == 0:
                    result = 0x00000000
            else:
                result = result[disas]
        return result

    def __puts_dis(self, chan, pc, cycles=None, extra=None):
        text = self.__get_instr(pc, 1)
        if text == '':
            return 1
        if cycles is None:
            cycle_text = "       "
        else:
            cycle_text = str(cycles)
        if extra is not None:
            text = '{0:s}{1:42s}; {2:s}\n'.format(cycle_text, text, extra)
        else:
            text = '{0:s}{1:s}\n'.format(cycle_text, text)
        if chan is None:
            print(text)
        else:
            chan.write(text)
        return 0

    def __puts_event(self, chan, event, extra=''):
        td = self.trace_dict
        mode = td['mode']
        total_cycles = td['cycles']
        e = "{0:0{1}x}".format(event, 4)
        text = f"event ({e}): "
        if event & 0xC000 == 0x8000:
            for i in range(0, 8):
                if event & (1 << i) != 0:
                    text += f'\"{self.trigger_event[i]}\"'
        if event & 0xC000 == 0xC000:
            ec = event & 0x1F
            text += f'\"{self.exception_event[ec]}\"'
        if event & 0xC000 == 0x4000:
            total_cycles = total_cycles + (event & 0x3FFFF)
        if mode != 2:
            cycle_text = "       "
        elif total_cycles == 0:
            cycle_text = "       "
        else:
            cycle_text = f'{str(total_cycles)}'
        text = '{0:s}{1:50s}{2:s}'.format(cycle_text, text, extra)
        if chan is None:
            print(text)
        else:
            chan.write(text.encode())
        total_cycles = 0
        td['cycles'] = total_cycles

    def __get_tpiu_byte(self):
        td = self.trace_dict
        tpiu_packet = td['tpiu_packet']
        tpiu_index = td['tpiu_index']

        if len(tpiu_packet) == 0:
            low = td['low']
            high = td['high']
            data_format = td['data_format']
            dis_getaddr = td['dis_getaddr']

            frame = list()
            i = 0
            while i < 4:
                item = self.session.mrd('-v', dis_getaddr)
                if item != 0x7FFFFFFF:
                    frame.append(item)
                    i += 1
                dis_getaddr += 4
            if dis_getaddr >= high + 0x10000:
                dis_getaddr = low
            td['dis_getaddr'] = dis_getaddr

            packet_count = td['packet_count']
            packet_count += 1
            td['packet_count'] = packet_count

            blist = list()
            for k in range(0, 4):
                for i in range(0, 4):
                    b = (frame[k] >> (i * 8)) & 0xFF
                    blist.append(b)

            if data_format == 'tpiu':
                final = blist[15]
                for k in range(0, 15):
                    b = blist[k]
                    if k & 1 == 1:
                        tpiu_packet.append(b)
                    elif b & 1 == 0:
                        tpiu_packet.append((b & 0xFE) | (final & 1))
                        final = final >> 1
                    else:
                        id = (b & 0xFE) | (final & 1)
                        if id != 0x40 and id != 0x41:
                            raise Exception(f'Packet error: expected ID 0x40 or 0x41, found {hex(id)}') from None
                        final = final >> 1
            else:
                tpiu_packet = blist
            td['tpiu_packet'] = tpiu_packet
            tpiu_index = 0

        res = tpiu_packet[tpiu_index]
        tpiu_index += 1
        if tpiu_index == len(tpiu_packet):
            td['tpiu_packet'] = list()
        td['tpiu_index'] = tpiu_index
        return res

    def __get_ftm_byte(self):
        td = self.trace_dict
        ftm_packet = td['ftm_packet']
        ftm_index = td['ftm_index']

        if len(ftm_packet) == 0:
            expecting_first = 1
            type = 'unknown'
            index = 0
            expected_len = 0
            done = 0
            data = 0
            while done == 0:
                b = self.__get_tpiu_byte()
                if b & 0x80 == 0:
                    if expecting_first:
                        index = 0
                        if b == 0x00:
                            type = 'sync'
                            expected_len = 8
                        elif b == 0x20:
                            type = 'trigger'
                            expected_len = 4
                            data = b
                        elif b == 0x28:
                            # Manual does not include this packet type
                            type = "undocumented"
                            expected_len = 4
                            data = b
                        elif b == 0x68:
                            type = "overflow"
                            expected_len = 4
                            data = b
                        elif (b & 0x87) == 5:
                            # Trace packet
                            type = "trace"
                            expected_len = 5
                            data = (b >> 3) & 0xf
                        else:
                            raise Exception(f'Unexpected packet type: {hex(b)} = {hex((b & 0x87))}') from None
                    else:
                        # Last data byte
                        index += 1
                        length = index + 1
                        if length != expected_len:
                            raise Exception(f'Unexpected packet length: expected {expected_len} '
                                            f'found {length}') from None
                        if type == "trace":
                            data = ((b & 0x7F) << 25) | data
                            done = 1
                        if type == "cycles":
                            data = ((b & 0x7F) << 25) | data
                            print(f'FTM cycles: {data}')
                        if type == "trigger":
                            data = (b << 24) | data
                            print(f'FTM trigger (packet = {hex(data)})')
                        if type == "overflow":
                            data = (b << 24) | data
                            print(f'FTM FIFO overflow (packet = {hex(data)}')
                        if type == "undocumented":
                            data = (b << 24) | data
                            print(f'FTM undocumented packet type (packet = {hex(data)})')
                        expecting_first = int(not expecting_first)
                else:
                    index += 1
                    if type in ('trace', 'cycles'):
                        data = ((b & 0x7f) << ((index - 1) * 7 + 4)) | data
                    if type in ('trigger', 'overflow', 'undocumented'):
                        data = ((b & 0xff) << (index * 8)) | data
                    if type in ('trace', 'trigger'):
                        if index == expected_len:
                            type = 'cycles_next'
                            if type == 'trace':
                                print(f'Trace: {hex(data)}')
                            if type == 'trigger':
                                print(f'Trigger (packet = {hex(data)})')
                    if type == 'cycles_next':
                        type = 'cycles'
                        expected_len = 5
                        data = (b >> 3) & 0xf

            for i in range(0, 4):
                b = (data >> (i * 8)) & 0xff
                ftm_packet.append(b)
            ftm_index = 0
            td['ftm_packet'] = ftm_packet

        res = ftm_packet[ftm_index]
        ftm_index += 1
        if ftm_index == len(ftm_packet):
            td['ftm_packet'] = list()
        td['ftm_index'] = ftm_index
        return res

    def __get_dis_item(self):
        td = self.trace_dict
        output = td['output']
        protocol = td['protocol']
        dis_items = td['dis_items']
        dis_index = td['dis_index']
        trace_id = 110  # Must match the MDM parameter C_TRACE_ID with default value 110

        if output == 3 or output == 1 or (output == 1 and protocol == 1):
            if len(dis_items) == 0:
                # Read packet
                low = td['low']
                high = td['high']
                dis_getaddr = td['dis_getaddr']
                packet = self.session.mrd('-v', dis_getaddr, word_size=20)
                dis_getaddr += 80
                if dis_getaddr >= high + 0x10000:
                    dis_getaddr = low
                td['dis_getaddr'] = dis_getaddr

                packet_count = td['packet_count']
                data = list()
                data_is_id = 0
                for f in range(0, 5):
                    final = (packet[f * 4 + 3] >> 24) & 0xff
                    for k in range(f * 4, f * 4 + 4):
                        for i in range(0, 4):
                            b = (packet[k] >> (i * 8)) & 0xff
                            if k == (f * 4) + 3 and i == 3:
                                break
                            if i & 1 == 1:
                                if data_is_id:
                                    if b != 0x20:
                                        raise Exception(
                                            f'Packet error {packet_count}: expected ID 0x20, found {hex(b)} (protocol'
                                            f' {protocol}') from None
                                    data_is_id = 0
                                else:
                                    data.append(b)
                            elif b & 1 == 0:
                                data.append((b & 0xfe) | (final & 1))
                                final = final >> 1
                            else:
                                id_byte = (b & 0xfe) | (final & 1)
                                if protocol == 0 and id_byte != 0x20:
                                    raise Exception(
                                        f'Packet error {packet_count}: expected ID 0x20, found {hex(b)} (protocol'
                                        f' {protocol}') from None
                                if protocol == 1 and id_byte != trace_id * 2 and id_byte != (trace_id + 1) * 2:
                                    raise Exception(f'Packet error ({packet_count}): expected ID {hex(trace_id)} or'
                                                    f' {hex(trace_id + 1)}, found {hex(int(id_byte / 2))}'
                                                    f'(protocol {protocol})')
                                data_is_id = protocol == 1 and id_byte == trace_id * 2
                                final = final >> 1

                if len(data) != 72:
                    raise Exception(f'Packet error {packet_count}: expected 72 bytes, found {len(data)} (protocol'
                                    f' {protocol}') from None

                dis_items = list()
                for k in range(0, len(data), 9):
                    dis_items.append(data[k] + (data[k + 1] << 8) + ((data[k + 8] << 16) & 0x30000))
                    dis_items.append(data[k + 2] + (data[k + 3] << 8) + ((data[k + 8] << 14) & 0x30000))
                    dis_items.append(data[k + 4] + (data[k + 5] << 8) + ((data[k + 8] << 12) & 0x30000))
                    dis_items.append(data[k + 6] + (data[k + 7] << 8) + ((data[k + 8] << 10) & 0x30000))
                td['dis_items'] = dis_items
                dis_index = 0
        elif output == 2:
            if len(dis_items) == 0:
                data_format = td['data_format']
                if data_format == 'mdm':
                    # Read packet
                    low = td['low']
                    high = td['high']
                    dis_getaddr = td['dis_getaddr']
                    packet = self.session.mrd('-v', dis_getaddr, word_size=18)
                    dis_getaddr += 72
                    if dis_getaddr >= high + 0x10000:
                        dis_getaddr = low
                    td['dis_getaddr'] = dis_getaddr

                    data = list()
                    for k in range(0, 18):
                        for i in range(0, 4):
                            b = (packet[k] >> (i * 8)) & 0xff
                            data.append(b)
                    dis_items = list()
                    for k in range(0, len(data), 9):
                        dis_items.append(data[k] + (data[k + 1] << 8) + ((data[k + 8] << 16) & 0x30000))
                        dis_items.append(data[k + 2] + (data[k + 3] << 8) + ((data[k + 8] << 14) & 0x30000))
                        dis_items.append(data[k + 4] + (data[k + 5] << 8) + ((data[k + 8] << 12) & 0x30000))
                        dis_items.append(data[k + 6] + (data[k + 7] << 8) + ((data[k + 8] << 10) & 0x30000))

                if data_format in ('tpiu', 'ftm'):
                    data = list()
                    for k in range(0, 18 * 4):
                        data.append(self.__get_ftm_byte())
                    dis_items = list()
                    for k in range(0, len(data), 9):
                        dis_items.append(data[k] + (data[k + 1] << 8) + ((data[k + 8] << 16) & 0x30000))
                        dis_items.append(data[k + 2] + (data[k + 3] << 8) + ((data[k + 8] << 14) & 0x30000))
                        dis_items.append(data[k + 4] + (data[k + 5] << 8) + ((data[k + 8] << 12) & 0x30000))
                        dis_items.append(data[k + 6] + (data[k + 7] << 8) + ((data[k + 8] << 10) & 0x30000))
                td['dis_items'] = dis_items
                dis_index = 0

        else:
            # Return an item from the embedded trace buffer
            if len(dis_items) == 0:
                if self.trace_read_seq is not None:
                    tdo_value = self.trace_read_seq.run('--binary')
                    for val in tdo_value:
                        d = ''
                        for b in val:
                            d += format(b, '08b')[::-1]
                        d = ('00' + d)[:20]
                        val = int(('0b' + d), 2)
                        dis_items.append(val)
                else:
                    mdmaddr = td['mdmaddr']
                    for i in range(0, 512):
                        dis_items.append(self.session.mrd('-v', mdmaddr + 0x5980))
                td['dis_items'] = dis_items
                dis_index = 0

        res = dis_items[dis_index]
        dis_index += 1
        if dis_index == len(dis_items):
            td['dis_items'] = list()
        td['dis_index'] = dis_index
        return res

    def __mbtrace_dis_internal(self, chan=None, lines=-1):
        td = self.trace_dict
        mode = td['mode']
        control = td['ctrl_reg']
        output = td['output']
        protocol = td['protocol']
        low = td['low']
        high = td['high']
        pc_items = td['pc_items']
        self.__mbtrace_checkinit()
        if output == 0:
            cmd_sample = 1
            self.__mb_trace_write_command(cmd_sample)
            read_status_val = self.__mb_trace_read_status()
            count = int(read_status_val, 16) & 0xFFFF
        else:
            if output == 3:
                stat = self.__mb_trace_mdm_read_status()
                resp = stat & 3
                wrap = (stat >> 2) & 1
                curraddr = self.__mb_trace_mdm_read_curraddr()
            else:
                trace_dma_addr = td['trace_dma']
                stat = self.session.mrd('-v', trace_dma_addr + 8)
                resp = stat & 3
                wrap = (stat >> 2) & 1
                curraddr = self.session.mrd('-v', trace_dma_addr + 12)
            if resp != 0:
                raise Exception(f'External trace response error {resp}:'
                                f' Check address range {hex(low)} - {hex(high)}') from None
            # Protocol 0: 18 32-bit words per packet = 16 36-bit words = 32 items
            # Protocol 1: 20 32-bit words per packet = 16 36-bit words = 32 items
            bytes_per_packet = 72 + (8 * protocol)
            if wrap:
                count = int((high + 0x10000 - low) / bytes_per_packet * 32)
                dis_getaddr = curraddr
            else:
                count = int((curraddr - low) / bytes_per_packet * 32)
                dis_getaddr = low
            td['dis_getaddr'] = dis_getaddr

        td['dis_items'] = list()
        td['dis_index'] = 0
        err = 0
        i = 0

        if mode == 0:
            line = 0
            while (i < count) and (line < lines or lines == -1):
                i += 8
                line += 1
                traceline = list()
                for n in range(0, 8):
                    item = self.__get_dis_item()
                    traceline.append(item)
                cycles = ((traceline[0] >> 3) & 0x7FFF) + 1
                msr = ((traceline[0] << 12) & 0x7000) | ((traceline[1] >> 6) & 0xFFF)
                regaddr = (traceline[1] >> 1) & 0x1F
                regwr = traceline[1] & 1
                exckind = (traceline[2] >> 13) & 0x1F
                exc = (traceline[2] >> 12) & 1
                datard = (traceline[2] >> 11) & 1
                datawr = (traceline[2] >> 10) & 1
                be = (traceline[2] >> 6) & 0xF
                data = ((traceline[2] << 26) & 0xFC000000) | ((traceline[3] << 8) & 0x3FFFF00) | \
                       ((traceline[4] >> 10) & 0xFF)
                addr = ((traceline[4] << 22) & 0xFFC00000) | ((traceline[5] << 4) & 0x3FFFF0) | \
                       ((traceline[6] >> 14) & 0xF)
                pc = ((traceline[6] << 18) & 0xFFFC0000) | traceline[7]
                # Skip output of last item if it is a branch with delayslot, immediate value or return,
                # since those instructions will be re-executed when execution continues
                if i >= count:
                    instr = self.__get_instr(pc)
                    instr = int(instr, 16)
                    opcode = instr >> 26
                    if opcode in (0x2E, 0x2F):
                        # Static branch
                        delay_slot = ((opcode == 0x2E) and (instr & 0x00100000) != 0) or \
                                     ((opcode == 0x2F) and (instr & 0x02000000) != 0)
                        if delay_slot:
                            break
                    elif opcode in (0x26, 0x27):
                        delay_slot = ((opcode == 0x26) and (instr & 0x00100000) != 0) or \
                                     ((opcode == 0x27) and (instr & 0x02000000) != 0)
                        if delay_slot:
                            break
                    elif opcode in (0x2C, 0x2D):
                        break
                if regwr:
                    err = self.__puts_dis(chan, pc, cycles, f'r{regaddr}={hex(data)}')
                elif datawr:
                    err = self.__puts_dis(chan, pc, cycles, f'*{hex(addr)}={hex(data)}')
                else:
                    err = self.__puts_dis(chan, pc, cycles)
                if err:
                    break

        if mode != 0:
            pc = 0
            line = 0
            before_pc = 1
            new_reg_value = 0
            next_imm_valid = 0
            next_imm = 0x0000
            long_imm = 0
            next_item = None
            at_dyn_ret = 1
            at_first_pc = 0
            branch_delay_slot = 0
            loadget_delay_slot = 0
            delayslot_pc = 0x0
            item_branch_count = 0
            saveld = (control & 0x2) != 0
            while i < count and (line < lines or lines == -1):
                if next_item is None:
                    item = self.__get_dis_item()
                else:
                    item = next_item
                    next_item = None
                kind = (item >> 16) & 3
                if kind == 0:
                    long_cycle_count = 0
                    if mode == 3:
                        branch_count = (item & 0xC000) >> 14
                        if branch_count == 3:
                            branch_count = 1
                            long_cycle_count = 1
                        max_branch_count = 2
                    else:
                        branch_count = (item & 0xF000) >> 12
                        max_branch_count = 12
                    if branch_count > max_branch_count or (output == 0 and branch_count == 0):
                        raise Exception(
                            f'Unexpected branch count {branch_count} in read data {hex(item)} '
                            f'(item {i} of {count})') from None
                    item_branch_count = branch_count
                    if before_pc:
                        i += 1
                        continue
                    n = 0
                    while n < branch_count:
                        cycles = None
                        if mode == 3:
                            if long_cycle_count:
                                # Branch and long cycle count
                                taken = item & 1
                                cycles = ((item >> 1) & 0x1FFF) + 1
                            else:
                                # Branch and short cycle count
                                taken = (item >> (7 - n * 7)) & 1
                                cycles = ((item >> (8 - n * 8)) & 0x3F) + 1
                        else:
                            # Branch only
                            taken = (item >> (11 - n)) & 1
                        done = 0
                        at_dyn_ret = mode == 2
                        while done == 0:
                            instr = self.__get_instr(pc)
                            instr = int(instr, 16)
                            opcode = instr >> 26
                            if opcode in (0x2E, 0x2F):
                                # Static branch
                                err = self.__puts_dis(chan, pc, cycles)

                                delay_slot = (opcode == 0x2E and ((instr & 0x00100000) != 0)) or \
                                             (opcode == 0x2F and ((instr & 0x02000000) != 0))
                                absolute = opcode == 0x2E and (instr & 0x00080000) != 0
                                imm = instr & 0xFFFF
                                if opcode == 0x2E and taken == 0:
                                    raise Exception(
                                        f'Unconditional static branch in {hex(item)} ({n}) not taken, '
                                        f'PC {hex(pc)} (item {i} of {count})') from None

                                if delay_slot:
                                    delayslot_pc = pc + 4
                                    instr = self.__get_instr(delayslot_pc)
                                    instr = int(instr, 16)
                                    opcode = instr >> 26
                                    is_get = saveld and opcode == 0x1B and (instr & 0x8000) == 0
                                    is_getd = saveld and opcode == 0x13 and (instr & 0x0400) == 0
                                    is_load = saveld and (
                                            opcode == 0x30 or opcode == 0x31 or opcode == 0x32 or
                                            opcode == 0x38 or opcode == 0x39 or opcode == 0x3A)
                                    loadget_delay_slot = is_get or is_getd or is_load
                                    long_imm = 0
                                    if loadget_delay_slot == 0:
                                        err = self.__puts_dis(chan, delayslot_pc)
                                    if taken == 0:
                                        pc += 8
                                elif taken == 0:
                                    pc += 4

                                if next_imm_valid > 0:
                                    # Immediate value - 24-bit (imml) sign extend
                                    if (imm & 0x800000) != 0:
                                        imm = 0xFFFFFF0000000000 | imm | next_imm
                                    else:
                                        imm = imm | next_imm
                                elif (imm & 0x8000) != 0:
                                    imm = 0xFFFF0000 | imm
                                if pc_items > 2:
                                    # Long branch
                                    if taken and absolute:
                                        pc = imm & 0xFFFFFFFFFFFFFFFF
                                    if taken and absolute == 0:
                                        pc = (pc + imm) & 0xFFFFFFFFFFFFFFFF
                                else:
                                    if taken and absolute:
                                        pc = imm & 0xFFFFFFFF
                                    if taken and absolute == 0:
                                        pc = (pc + imm) & 0xFFFFFFFF

                                next_imm_valid = 0
                                done = 1
                                line += 2
                            elif opcode in (0x26, 0x27):
                                # Dynamic branch
                                err = self.__puts_dis(chan, pc, cycles)
                                pc += 4
                                delay_slot = (opcode == 0x26 and ((instr & 0x00100000) != 0)) or (
                                        opcode == 0x27 and ((instr & 0x02000000) != 0))
                                if delay_slot:
                                    err = self.__puts_dis(chan, pc)
                                    pc += 4
                                if n != branch_count - 1:
                                    raise Exception(
                                        f'Unexpected dynamic branch for {hex(item)} ({n}), '
                                        f'PC {hex(pc)} (item {i} of {count})') from None
                                if opcode == 0x26 and taken == 0:
                                    raise Exception(
                                        f'Unconditional dynamic branch in {hex(item)} ({n}) '
                                        f'not taken, PC {hex(pc)} (item {i} of {count})') from None
                                next_imm_valid = 0
                                done = 1
                                line += 2
                                at_dyn_ret = 1
                            elif opcode == 0x2D:
                                # Return
                                err = self.__puts_dis(chan, pc, cycles)
                                pc += 4
                                err |= self.__puts_dis(chan, pc)
                                pc += 4
                                if n != branch_count - 1:
                                    raise Exception(
                                        f'Unexpected dynamic branch for {hex(item)} ({n}), '
                                        f'PC {hex(pc)} (item {i} of {count})') from None
                                next_imm_valid = 0
                                done = 1
                                line += 2
                                at_dyn_ret = 1
                            elif opcode == 0x2C:
                                # Immediate value - 24-bit (imml) or 16-bit (imm)
                                if ((instr >> 24) & 3) == 2:
                                    next_imm = (instr & 0xFFFFFF) << 16
                                    next_imm_valid = 2
                                else:
                                    next_imm = (instr & 0xFFFF) << 16
                                    next_imm_valid = 1
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                line += 1
                            else:
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                next_imm_valid = 0
                                line += 1
                            if err:
                                break
                        if err:
                            break
                        n += 1
                elif kind == 1:
                    new_pc = item & 0xFFFF
                    for pc_item in range(2, pc_items + 1):
                        i += 1
                        item = self.__get_dis_item()
                        while i < count and item == 0:
                            i += 1
                            item = self.__get_dis_item()
                        new_pc = (new_pc << 16) | (item & 0xFFFF)
                        if (item >> 16) != 1:
                            raise Exception(
                                f"Unexpected PC read data {pc_item} {hex(item)} (item {i} of {count})") from None
                    if mode == 2:
                        err = self.__puts_dis(chan, pc)

                    # Set current PC to first PC after continue execution
                    if at_first_pc:
                        pc = new_pc
                        at_first_pc = 0

                    # Look ahead to check if the PC is for a debug stop event
                    next_item = self.__get_dis_item()
                    if (next_item & 0x3C0FF) == 0x38001:
                        at_dyn_ret = 1

                    # Check if PC is in already output delay slot
                    if branch_delay_slot and pc == delayslot_pc:
                        at_dyn_ret = 1
                        branch_delay_slot = 0

                    if at_dyn_ret == 0:
                        # Output to return, dynamic branch, or load/get when enabled
                        done = 0
                        while done == 0 and new_pc != pc:
                            instr = self.__get_instr(pc)
                            instr = int(instr, 16)
                            opcode = instr >> 26
                            if opcode in (0x2E, 0x2F):
                                # Static branch
                                done = 1
                                line += 2
                                raise Exception(
                                    f"Unexpected branch before PC read {hex(new_pc)}, "
                                    f"PC {hex(pc)} (item {i} of {count})") from None
                            elif opcode in (0x26, 0x27):
                                # Dynamic branch
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                line += 1
                                delay_slot = (opcode == 0x26 and ((instr & 0x00100000) != 0)) or \
                                             (opcode == 0x27 and ((instr & 0x02000000) != 0))
                                if delay_slot:
                                    err = self.__puts_dis(chan, pc)
                                    delayslot_pc = pc
                                    branch_delay_slot = 1
                                    pc += 4
                                    line += 1
                                done = 1
                            elif opcode == 0x2D:
                                # Return
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                err |= self.__puts_dis(chan, pc)
                                delayslot_pc = pc
                                branch_delay_slot = 1
                                pc += 4
                                done = 1
                                line += 2
                            elif opcode == 0x2C:
                                # Immediate value
                                long_imm = ((instr >> 24) & 3) == 2
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                line += 1
                            elif opcode in (0x30, 0x31, 0x32, 0x38, 0x39, 0x3A):
                                # Load
                                if saveld:
                                    done = 1
                                else:
                                    err = self.__puts_dis(chan, pc)
                                    pc += 4
                                    line += 1
                            elif opcode == 0x13:
                                # Dynamic get or put
                                if saveld and (instr & 0x0400) == 0:
                                    done = 1
                                else:
                                    err = self.__puts_dis(chan, pc)
                                    pc += 4
                                    line += 1
                            elif opcode == 0x1B:
                                # Get or put
                                if saveld and (instr & 0x8000) == 0:
                                    done = 1
                                else:
                                    err = self.__puts_dis(chan, pc)
                                    pc += 4
                                    line += 1
                            else:
                                err = self.__puts_dis(chan, pc)
                                pc += 4
                                line += 1
                            if err:
                                break
                    at_dyn_ret = mode == 2
                    before_pc = 0
                    pc = new_pc

                elif kind == 2:
                    new_reg_value = (item & 0xFFFF) << 16
                    i += 1
                    item = self.__get_dis_item()
                    while i < count and item == 0:
                        i += 1
                        item = self.__get_dis_item()
                    new_reg_value = new_reg_value | (item & 0xFFFF)
                    if (item >> 16) != 2:
                        raise Exception(f'Unexpected load/get read data 2 {hex(item)} (item {i} of {count})') from None
                    # Output to load or get
                    done = loadget_delay_slot or mode == 2
                    while done == 0:
                        instr = self.__get_instr(pc)
                        instr = int(instr, 16)
                        opcode = instr >> 26
                        if opcode == 0x13:
                            # Dynamic get or put
                            if (instr & 0x0400) == 0:
                                err = self.__puts_dis(chan, pc, None, f'={hex(new_reg_value)}')
                                done = 1
                            else:
                                err = self.__puts_dis(chan, pc)
                            pc += 4
                            line += 1

                        elif opcode == 0x1B:
                            # Get or put
                            if (instr & 0x8000) == 0:
                                err = self.__puts_dis(chan, pc, None, f'={hex(new_reg_value)}')
                                done = 1
                            else:
                                err = self.__puts_dis(chan, pc)
                            pc += 4
                            line += 1
                        elif opcode in (0x2E, 0x2F):
                            # Static branch
                            raise Exception(
                                f'Unexpected static branch for load/get read {hex(item)}, '
                                f'PC {hex(pc)} (item {i} of {count})') from None
                        elif opcode in (0x26, 0x27):
                            # Dynamic branch
                            err = self.__puts_dis(chan, pc)
                            pc += 4
                            line += 1
                            delay_slot = (opcode == 0x26 and ((instr & 0x00100000) != 0)) or \
                                         (opcode == 0x27 and ((instr & 0x02000000) != 0))
                            if delay_slot == 0:
                                raise Exception(
                                    f'Unexpected dynamic branch for load/get read {hex(item)}, '
                                    f'PC {hex(pc)} (item {i} of {count})') from None
                            next_imm_valid = 0
                            at_dyn_ret = 1
                        elif opcode == 0x2D:
                            # Return
                            err = self.__puts_dis(chan, pc)
                            pc += 4
                            next_imm_valid = 0
                            line += 1
                            at_dyn_ret = 1
                        elif opcode == 0x2C:
                            # Immediate value
                            long_imm = ((instr >> 24) & 3) == 2
                            err = self.__puts_dis(chan, pc)
                            pc += 4
                            line += 1
                        elif opcode in (0x30, 0x31, 0x32, 0x38, 0x39, 0x3A):
                            # Load (lbu, lhu, lw, lbui, lhui, lwi) or load long (ll, lli)
                            long = (instr & 0x00000200) != 0 and opcode == 0x32
                            if long or long_imm:
                                for load_item in range(3, 5):
                                    i += 1
                                    item = self.__get_dis_item()
                                    while i < count and item == 0:
                                        i += 1
                                        item = self.__get_dis_item()
                                    new_reg_value = (new_reg_value << 16) | (item & 0xFFFF)
                                    if (item >> 16) != 2:
                                        raise Exception(
                                            f'Unexpected load read data {load_item} {hex(item)}'
                                            f' (item {i} of {count})') from None
                                err = self.__puts_dis(chan, pc, None, f'={hex(new_reg_value)}')
                                long_imm = 0
                            else:
                                err = self.__puts_dis(chan, pc, None, f'={hex(new_reg_value)}')
                                pc += 4
                                line += 1
                                done = 1
                        else:
                            err = self.__puts_dis(chan, pc)
                            pc += 4
                            line += 1

                        if err:
                            break

                    if loadget_delay_slot:
                        err = self.__puts_dis(chan, delayslot_pc, None, f'={hex(new_reg_value)}')
                    loadget_delay_slot = 0
                    if before_pc:
                        i += 1
                        continue

                elif kind == 3:
                    event = item & 0xFFFF
                    if event != 0x8001 and event != 0x8002:
                        self.__puts_event(chan, event)
                    if (event & 0xC000) == 0xC000:
                        at_dyn_ret = 1
                    if (event & 0xC0FF) == 0x8002:
                        at_first_pc = 1
                else:
                    raise Exception(f'Unexpected read data: {hex(item)} (item {i} of {count}') from None
                if err:
                    break
                i += 1
            return err

    def __mb_trace_mdm_mrd(self, mdmaddr, ctrl):
        s = self.session
        s.configparams('debug-poll-enable', 0)
        s.mwr(mdmaddr + 0x10, ctrl)
        result = s.mrd('-v', mdmaddr + 0x14)
        s.configparams('debug-poll-enable', 1)
        return result

    def __mb_trace_mdm_mwr(self, mdmaddr, ctrl, value):
        s = self.session
        s.configparams('debug-poll-enable', 0)
        s.mwr(mdmaddr + 0x10, ctrl)
        s.mwr(mdmaddr + 0x14, value)
        s.configparams('debug-poll-enable', 1)

    def __mb_get_config(self, frm, to=-1):
        trace_dict = self.trace_dict
        if to == -1:
            to = frm
        mdmaddr = trace_dict['mdmaddr'] if 'mdmaddr' in trace_dict else ''
        if mdmaddr == '':
            bscan = dict_get_value_or_error_out(trace_dict, 'bscan')
            which = dict_get_value_or_error_out(trace_dict, 'which')
            config = self.session.mb_drrd(0x07, 288, user=bscan, which=which)
            config_bin = bin(int(config, 16))[2:]
            val = config_bin[frm:to + 1]
            val = val[::-1] if len(val) > 1 else val
            return int(val, 2)
        wordaddr = int(frm / 32) * 4
        bitshift = 31 - (frm % 32)
        bitmask = (1 << (to - frm + 1)) - 1
        configword = self.session.mrd('-v', (mdmaddr + 0x41C0 + wordaddr))
        return (configword[0] >> bitshift) & bitmask

    def __mb_trace_read_status(self):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            bscan = td['bscan']
            which = td['which']
            return self.session.mb_drrd(0x63, 18, user=bscan, which=which)
        else:
            return self.session.mrd('-v', mdmaddr + 0x58C0)

    def __mb_trace_mdm_read_config(self):
        td = self.trace_dict
        return td['mdmconfig'] & 0xffffffff

    def __mb_trace_mdm_read_ext_config(self):
        td = self.trace_dict
        return td['mdmconfig']

    def __mb_trace_mdm_read_status(self):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            return self.session.mdm_drrd(0x4A, 3)
        return self.__mb_trace_mdm_mrd(mdmaddr, 0x69402)

    def __mb_trace_mdm_read_curraddr(self):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            return self.session.mdm_drrd(0x4B, 32)
        return self.__mb_trace_mdm_mrd(mdmaddr, 0x6961f)

    def __mb_trace_write_control(self, value):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            bscan = td['bscan']
            which = td['which']
            self.session.mb_drwr(0x61, value, 22, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5840, value)
        td['ctrl_reg'] = value

    def __mb_trace_write_command(self, value):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            bscan = td['bscan']
            which = td['which']
            self.session.mb_drwr(0x62, value, 4, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5880, value)
        td['cmd_reg'] = value

    def __mb_trace_mdm_write_low_addr(self, value):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            self.session.mdm_drwr(0x4c, value, 16)
        else:
            self.__mb_trace_mdm_mwr(mdmaddr, 0x6980f, value)

    def __mb_trace_mdm_write_high_addr(self, value):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            self.session.mdm_drwr(0x4d, value, 16)
        else:
            self.__mb_trace_mdm_mwr(mdmaddr, 0x69a0f, value)

    def __mb_trace_mdm_write_control(self, value, size):
        td = self.trace_dict
        mdmaddr = td['mdmaddr'] if 'mdmaddr' in td else ''
        if mdmaddr == '':
            self.session.mdm_drwr(0x4e, value, size)
        else:
            data = 0x69c00 if size == 1 else 0x69c07
            self.__mb_trace_mdm_mwr(mdmaddr, data, value)

    def __regRD(self, instr):
        return f'r{(instr >> 21) & 0x1F}'.ljust(3)

    def __regR1(self, instr):
        return f'r{(instr >> 16) & 0x1F}'.ljust(3)

    def __regR2(self, instr):
        return f'r{(instr >> 11) & 0x1F}'

    def __imm(self, instr):
        value = instr & 0xFFFF
        if value & 0x8000 == 0:
            return f'{value}'
        else:
            return f'{value - 65536}'

    def __imms(self, instr):
        return f'{instr & 0x3F}'

    def __immw(self, instr):
        if instr & 0x00004000:
            value = (instr >> 6) & 0x3F
        else:
            value = ((instr >> 6) & 0x3F) - (instr & 0x3F) + 1
        return f'{value}'

    def __imm7(self, instr):
        return f'{instr & 0x7F}'

    def __imm15(self, instr):
        return f'{instr & 0x7fff}'

    def __imml(self, instr):
        return f'{instr & 0xffffff}'

    def __spec1(self, instr):
        value = instr & 0x1807
        if value == 0x0001:
            return "rmsr"
        if value == 0x0007:
            return "rfsr"
        if value == 0x0800:
            return "rslr"
        if value == 0x0802:
            return "rshr"
        if value == 0x1000:
            return "rpid"
        if value == 0x1001:
            return "rzpr"
        if value == 0x1002:
            return "rtlbx"
        if value == 0x1003:
            return "rtlblo"
        if value == 0x1004:
            return "rtlbhi"
        if value == 0x1005:
            return "rtlbsx"
        return f"UNKNOWN={hex(value)}]"

    def __spec2(self, instr):
        value = instr & 0x300F
        if value == 0x0000:
            return "pc"
        if value == 0x0001:
            return "rmsr"
        if value == 0x0003:
            return "rear"
        if value == 0x0005:
            return "resr"
        if value == 0x0007:
            return "rfsr"
        if value == 0x000B:
            return "rbtr"
        if value == 0x000D:
            return "redr"
        if value == 0x1000:
            return "rpid"
        if value == 0x1001:
            return "rzpr"
        if value == 0x1002:
            return "rtlbx"
        if value == 0x1003:
            return "rtlblo"
        if value == 0x1004:
            return "rtlbhi"
        if value == 0x2000:
            return "rpvr0"
        if value == 0x2001:
            return "rpvr1"
        if value == 0x2002:
            return "rpvr2"
        if value == 0x2003:
            return "rpvr3"
        if value == 0x2004:
            return "rpvr4"
        if value == 0x2005:
            return "rpvr5"
        if value == 0x2006:
            return "rpvr6"
        if value == 0x2007:
            return "rpvr7"
        if value == 0x2008:
            return "rpvr8"
        if value == 0x2009:
            return "rpvr9"
        if value == 0x200a:
            return "rpvr10"
        if value == 0x200b:
            return "rpvr11"
        return f"UNKNOWN={hex(value)}"

    def __reginfo(self, value, bitnames):
        text = ''
        for bit in bitnames:
            if value & 1 == 1:
                text = f'{bit} {text}'
            value = value >> 1
        if len(text) > 0:
            text = text[0:-1]
            return text
        else:
            return ''

    def __excinfo(self, kind):
        if kind == 0:
            return "Fast Simplex Link Exception"
        if kind == 1:
            return "Unaligned Exception"
        if kind == 2:
            return "Illegal Opcode Exception"
        if kind == 3:
            return "Instruction Bus Exception"
        if kind == 4:
            return "Data Bus Exception"
        if kind == 5:
            return "Divide Exception"
        if kind == 6:
            return "FPU Exception"
        if kind == 7:
            return "Privileged Instruction Exception"
        if kind == 9:
            return "Debug Exception"
        if kind == 10:
            return "Interrupt"
        if kind == 11:
            return "External Non Maskable Break"
        if kind == 12:
            return "External Maskable Break"
        if kind == 16:
            return "Data Storage Exception"
        if kind == 17:
            return "Instruction Storage Exception"
        if kind == 18:
            return "Data TLB Miss Exception"
        if kind == 19:
            return "Instruction TLB Miss Exception"
        return f"Unknown Exception {kind}"

    def __disassemble(self, pc, instr, exception_taken=0, exception_kind=0, reg_write=0, reg_addr=0, new_reg_value=0):
        opcode = None
        type = ''
        for op in self.opcodes:
            mask = op[6]
            code = op[5]
            if code & mask == instr & mask:
                opcode = op
                break
        if opcode is not None:
            mnemonic = opcode[0]
            type = opcode[1]
            arg = ''
            if type == "INST_TYPE_RD_R1_R2":
                arg = f'{self.__regRD(instr)}, {self.__regR1(instr)}, {self.__regR2(instr)}'
            if type == "INST_TYPE_RD_R1_IMM":
                arg = f'{self.__regRD(instr)}, {self.__regR1(instr)}, {self.__imm(instr)}'
            if type == "INST_TYPE_RD_R1":
                arg = f'{self.__regRD(instr)}, {self.__regR1(instr)}'
            if type == "INST_TYPE_RD_R2":
                arg = f'{self.__regRD(instr)}, {self.__regR2(instr)}'
            if type == "INST_TYPE_RD_IMM":
                arg = f'{self.__regRD(instr)}, {self.__imm(instr)}'
            if type == "INST_TYPE_R2":
                arg = f'{self.__regR2(instr)}'
            if type == "INST_TYPE_R1_R2":
                arg = f'{self.__regR1(instr)}, {self.__regR2(instr)}'
            if type == "INST_TYPE_R1_IMM":
                arg = f'{self.__regR1(instr)}, {self.__imm(instr)}'
            if type == "INST_TYPE_IMM":
                arg = f'{self.__imm(instr)}'
            if type == "INST_TYPE_SPECIAL_R1":
                arg = f'{self.__spec1(instr)}, {self.__regR1(instr)}'
            if type == "INST_TYPE_RD_SPECIAL":
                arg = f'{self.__regRD(instr)}, {self.__spec2(instr)}'
            if type == "INST_TYPE_R1":
                arg = f'{self.__regR1(instr)}'
            if type == "INST_TYPE_RD_R1_IMMS":
                arg = f'{self.__regRD(instr)}, {self.__regR1(instr)}, {self.__imms(instr)}'
            if type == "INST_TYPE_RD_R1_IMM_IMM":
                arg = f'{self.__regRD(instr)}, {self.__regR1(instr)}, {self.__immw(instr)}, {self.__imms(instr)}'
            if type == "INST_TYPE_RD_IMM7":
                arg = f'{self.__regRD(instr)}, {self.__imm7(instr)}'
            if type == "INST_TYPE_IMM7":
                arg = f'{self.__imm7(instr)}'
            if type == "INST_TYPE_R1_IMM7":
                arg = f'{self.__regR1(instr)}, {self.__imm7(instr)}'
            if type == "INST_TYPE_RD_R1_SPECIAL":
                arg = f'{self.__regR1(instr)}, {self.__regR2(instr)}'
            if type == "INST_TYPE_RD_IMM15":
                arg = f'{self.__regRD(instr)}, {self.__imm15(instr)}'
            if type == "INST_TYPE_RD":
                arg = f'{self.__regRD(instr)}'
            if type == "INST_TYPE_IMML":
                arg = f'{self.__imml(instr)}'
            if type == "INST_TYPE_R1_IMML":
                arg = f'{self.__regR1(instr)}, {self.__imml(instr)}'
            if type == "INST_TYPE_NONE":
                arg = f''
        else:
            mnemonic = 'UNKNOWN'
            arg = ''

        # Result of operation stored in destination register (if any)
        # First check for exception
        result = ''
        if exception_taken == 1:
            rd = reg_addr
            value = new_reg_value
            kind = exception_kind
            result = f'r{rd}<={value} ({self.__excinfo(kind)})'
        elif opcode is not None and type.startswith('INST_TYPE_RD'):
            if reg_write == 1:
                rd = self.__regRD(instr)
                value = new_reg_value
                result = f"{rd}<={value}"
                reg = ''
                if mnemonic in ('mfs', 'mfse'):
                    reg = self.__spec2(instr)
                if mnemonic in ('msrset', 'msrclr'):
                    reg = 'rmsr'
                if reg == 'rmsr':
                    regtext = self.__reginfo(value,
                                             ['BE', 'IE', 'C', 'BIP', 'FSL', 'ICE', 'DZ', 'DCE', 'EE', 'EIP', 'PVR'])
                    result = f'{result} {regtext}'
                if reg == 'resr':
                    ecNames = [" ", "Unaligned data access", "Illegal op-code", "Instruction bus error",
                               "Data bus error", "Divide by zero", "Floating point unit"]
                    ecValue = value & 0x1F
                    if 0 < ecValue < 7:
                        ecText = ecNames[ecValue]
                    else:
                        ecText = "{0:0X}".format(ecValue)
                    essText = "{0:0X}".format((value >> 5) & 0x7F)
                    regtext = f'ESS={essText} EC={ecText}'
                    if value & 0x1000 != 0:
                        regtext = f'DS {regtext}'
                    result = f'{result} ({regtext})'
                if reg == 'rfsr':
                    regtext = self.__reginfo(value, ['DO', 'UF', 'OF', 'DZ', 'IO'])
                    result = f'{result} {regtext}'

        # Output formatted result
        pctxt = "{0:0{1}x}".format(pc, 8)
        if result == '':
            text = '{0:s}: {1:14s}{2:s}'.format(pctxt, mnemonic, arg)
        else:
            text = '{0:s}: {1:14s}{2:25s}{3:s}'.format(pctxt, mnemonic, arg, result)
        return text

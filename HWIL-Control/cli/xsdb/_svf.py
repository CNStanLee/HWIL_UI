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

import argparse
from xsdb._elf import ElfParse
from elftools.elf import descriptions
from xsdb._utils import *


class SVF(object):
    def __init__(self, chan, session):
        self.session = session
        self.channel = chan
        self.daps = dict()
        self.commands = dict()
        self.outfile = None
        self.scan_chain = dict()
        self.device_index = 0
        self.delaytcks = 0
        self.linkdap = 0
        self.dbgbase = 0
        self.ctibase = 0
        self.arch = None
        self.cpu_type = None
        self.config_dict = dict()
        self.fileptr = None
        # AP indices
        self.AHB = 0
        self.APB = 1
        self.JTAG = 2
        # Base address for DBG & CTI registers
        self.A53_DBGBASE = 0x80410000
        self.A53_CTIBASE = 0x80420000
        self.A9_DBGBASE = 0x80090000
        self.R5_DBGBASE = 0x803f0000
        # Offsets of DBG registers
        self.DBGDTRRX = 0x80
        self.DBGDTRTX = 0x8c
        self.DBGITR = 0x84
        self.DBGDRCR = 0x90
        self.DBGDSCR = 0x88
        self.DBGOSLAR = 0x300
        self.DBGVCR = 0x1c
        # Offsets of CTI registers
        self.CTICTRL = 0x0
        self.CTIINTACK = 0x10
        self.CTIAPPSET = 0x14
        self.CTIAPPCLR = 0x18
        self.CTIAPPPULSE = 0x1c
        self.CTIOUTEN0 = 0xa0
        self.CTIOUTEN1 = 0xa4
        self.CTIGATE = 0x140
        self.CTILAR = 0xfb0
        # Instructions
        self.ARMV8_MRS_DBG_DTR_X0 = 0xd5330400
        self.ARMV8_MSR_X0_TO_DLR = 0xd51b4520
        self.ARMV8_INSTR_IC_IALLU = 0xd508751f
        self.ARMV8_INSTR_DSB_SYS = 0xd5033f9f
        self.ARMV7_MOVE_CP14_C5_TO_GPR = 0xee100e15
        self.ARMV7_MOVE_GPR_TO_PC = 0xe1a0f000
        self.ARMV7_MCR_CP15_R0_ICIALLU = 0xee070f15
        self.ARMV7_DATA_SYNC_BARRIER = 0xee070f9a
        self.ARMV7_INSTR_SYNC_BARRIER = 0xee070f95
        self.T32_MOVE_CP14_C5_TO_GPR = 0x0e15ee10
        self.T32_MOVE_GPR_TO_PC = 0x0f35ee64
        self.T32_MCR_CP15_R0_ICIALLU = 0x0f15ee07
        self.T32_MCR_CP15_R0_BPIALL = 0x0fd5ee07
        self.T32_INSTR_DSB_SYS = 0x8f4ff3bf
        self.DAP_ABORT = 8
        self.DAP_DPACC = 0xa
        self.DAP_APACC = 0xb
        self.bscan_dict = {'user1': 0x02, 'user2': 0x03, 'user3': 0x22, 'user4': 0x23, 'pmu': 0x0e4}
        self.cmd_dict = {'a64': {'open': self.__zynqmp_open, 'mwr': self.__arm_mwr, 'dow': self.__arm_dow,
                                 'stop': self.__a64_stop, 'con': self.__a64_con, 'setpc': self.__a64_setpc},
                         'a32': {'open': self.__zynqmp_open, 'mwr': self.__arm_mwr, 'dow': self.__arm_dow,
                                 'stop': self.__a32_stop, 'con': self.__a32_con, 'setpc': self.__a32_setpc},
                         'armv7': {'open': self.__zynq_open, 'mwr': self.__arm_mwr, 'dow': self.__arm_dow,
                                   'stop': self.__armv7_stop, 'con': self.__armv7_con,
                                   'setpc': self.__armv7_setpc},
                         'mb': {'open': self.__mb_open, 'mwr': self.__mb_mwr, 'dow': self.__mb_dow,
                                'stop': self.__mb_stop, 'con': self.__mb_con, 'setpc': self.__mb_setpc}}

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(SVF) if callable(getattr(SVF, method)) if
                              not method.startswith('_')]
            for method in public_methods:
                if is_ss(method, name):
                    matches.append(method)
            if len(matches) == 0:
                raise NameError(f"Unknown attribute '{name}'") from None
            if len(matches) > 1:
                raise NameError(f"Ambiguous attribute '{name}': {matches}") from None
            return getattr(self, matches[0])(*args, **kwargs)

        return unknown

    @staticmethod
    def __get_mask(offset):
        mask = ''
        if offset > 64:
            for i in range(0, offset, 4):
                if offset - i > 4:
                    count = 4
                else:
                    count = offset - i
                mask = '{0}{1}'.format(format((int('1' * count, 2)), 'x'), mask)
        else:
            mask = '{0}'.format(format((int('1' * offset, 2)), 'x'))
        return mask

    def __writesvf(self, data):
        if self.outfile is None or self.fileptr is None:
            raise Exception('SVF not configured') from None
        data = f'{data}\n'
        self.fileptr.write(data)

    def __write_header_trailer_regs(self, device_index):
        tir_offset = 0
        tir_mask = 0
        tdr_mask = 0
        hir_offset = 0
        hir_mask = 0
        hdr_mask = 0
        scan_chain = self.config_dict['scan_chain']
        total_devices = int(len(scan_chain) / 2)
        for i in range(0, device_index):
            tir_offset = tir_offset + (scan_chain[(i * 2) + 1])
        if tir_offset != 0:
            tir_mask = self.__get_mask(tir_offset)
        if device_index != 0:
            tdr_mask = self.__get_mask(device_index)
        for i in range(device_index + 1, total_devices):
            hir_offset = hir_offset + scan_chain[(i * 2) + 1]
        if hir_offset != 0:
            hir_mask = self.__get_mask(hir_offset)
        hdr_devices = total_devices - device_index - 1
        if hdr_devices != 0:
            hdr_mask = self.__get_mask(hdr_devices)

        self.__writesvf(f'HIR {hir_offset} TDI ({hir_mask}) SMASK ({hir_mask});')
        self.__writesvf(f'TIR {tir_offset} TDI ({tir_mask}) SMASK ({tir_mask});')
        self.__writesvf(f'HDR {hdr_devices} TDI (0) SMASK ({hdr_mask});')
        self.__writesvf(f'TDR {device_index} TDI (00) SMASK ({tdr_mask});')

    # ---------------------------------------------------------------------------------------#
    # DAP internal routines
    # ---------------------------------------------------------------------------------------#
    def __cmd_getaps(self, name):
        aps = {0: {'idr': 880214020, 'name': 'AXI-AP', 'mem': 1, 'cfg': 2, 'ctrl': 0x30006000, 'size': [8, 16, 32]},
               1: {'idr': 1148649474, 'name': 'APB-AP', 'mem': 1, 'cfg': 0, 'ctrl': 0x80000000, 'size': 32,
                   'base': 2147483651},
               2: {'idr': 611713040, 'name': 'JTAG-AP', 'mem': 0}}
        if name in self.daps.keys():
            self.daps[name].update({'aps': aps})
        else:
            raise Exception("No DAP present") from None

    def __cmd_reset(self, name):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'RESET')
        else:
            raise Exception("No DAP present") from None

    def __cmd_abort(self, name):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'ABORT')
        else:
            raise Exception("No DAP present") from None

    def __cmd_dpwrite(self, name, addr, value):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'DPWRITE {addr} {value}')
        else:
            raise Exception("No DAP present") from None

    def __cmd_apwrite(self, name, ap, addr, value):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'APWRITE {ap} {addr} {value}')
        else:
            raise Exception("No DAP present") from None

    def __cmd_dpread(self, name, addr):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'DPREAD {addr}')
        else:
            raise Exception("No DAP present") from None

    def __cmd_apread(self, name, ap, addr):
        if name in self.daps.keys():
            self.daps[name]['cmds'].append(f'APREAD {ap} {addr}')
        else:
            raise Exception("No DAP present") from None

    @staticmethod
    def __csw_size(size):
        if size == 1:
            ret = 0
        elif size == 2:
            ret = 1
        elif size == 4:
            ret = 2
        elif size == 8:
            ret = 3
        else:
            raise Exception(f'unsupported CSW size: {size}') from None
        return ret

    def __cmd_memwrite(self, name, ap, addr, value, size=4, ctrl=None):
        if name not in self.daps.keys():
            raise Exception("No DAP present") from None
        if 'aps' not in self.daps[name].keys():
            self.__cmd_getaps(name)
        if ap not in self.daps[name]['aps'].keys() or 'mem' not in self.daps[name]['aps'][ap].keys():
            raise Exception(f'Invalid AP Index : {ap}') from None
        if (addr & (size - 1)) != 0:
            raise Exception(f'Invalid AP address alignment: {addr}') from None
        if ctrl is not None:
            apctrl = ctrl
        else:
            apctrl = self.daps[name]['aps'][ap]['ctrl']
        apctrl = (apctrl & ~7) | self.__csw_size(size)
        self.daps[name]['cmds'].append(f'MEMWRITE {ap} {apctrl} {addr} {value}')

    def __cmd_memread(self, name, ap, addr, refval=2, refmask=0, size=4, ctrl=None):
        if name not in self.daps.keys():
            raise Exception("No DAP present") from None
        if 'aps' not in self.daps[name].keys():
            self.__cmd_getaps(name)
        if ap not in self.daps[name]['aps'].keys() or 'mem' not in self.daps[name]['aps'][ap].keys():
            raise Exception(f'Invalid AP Index : {ap}') from None
        if (addr & (size - 1)) != 0:
            raise Exception(f'Invalid AP address alignment: {addr}') from None
        if ctrl is not None:
            apctrl = ctrl
        else:
            apctrl = self.daps[name]['aps'][ap]['ctrl']
        apctrl = (apctrl & ~7) | self.__csw_size(size)
        self.daps[name]['cmds'].append(f'MEMREAD {ap} {apctrl} {addr} {refval} {refmask}')

    def __cmd_run(self, name):
        if name not in self.daps.keys():
            raise Exception("No DAP present") from None
        dap = self.daps[name]
        run_data = {'ir': 15, 'stickybits': 2, 'select': 0xff0000ff}
        rst_cmd = 0
        ncmds = len(dap['cmds'])
        complete = 0
        self.__run_clear_stickybits(name, run_data)
        csw_shadow = -1
        csw_done = 0
        refval = 2
        refmask = 0
        while complete < ncmds:
            for i in range(complete, ncmds):
                cmd = (dap['cmds'][i]).split()
                j = 0
                for n in cmd.copy():
                    if isinstance(n, str):
                        if n.isnumeric() or n.startswith('-'):
                            cmd[j] = int(n)
                        if n.startswith('0x'):
                            cmd[j] = int(n, 16)
                    j = j + 1
                if cmd[0] == 'ABORT':
                    self.__run_set_abort(run_data)
                    self.__writesvf("SDR 35 TDI (8) TDO (2) MASK(7);")
                    self.__run_set_dpacc(run_data)
                    self.__writesvf("SDR 35 TDI (7) TDO (2) MASK(7);")
                elif cmd[0] == 'DPREAD':
                    self.__run_dpread(run_data, cmd[1])
                elif cmd[0] == 'DPWRITE':
                    self.__run_dpwrite(run_data, cmd[1], cmd[2])
                elif cmd[0] == 'APREAD':
                    self.__run_apread(run_data, cmd[1], cmd[2])
                elif cmd[0] == 'APWRITE':
                    self.__run_apwrite(run_data, cmd[1], cmd[2], cmd[3])
                elif cmd[0] == 'MEMREAD':
                    ap = cmd[1]
                    csw = cmd[2]
                    if csw_done == 0 or (csw_shadow != csw):
                        csw_shadow = csw
                        csw_done = 1
                        self.__run_apwrite(run_data, ap, 0x00, csw)
                    refval = '{0}'.format(format(cmd[4], 'x'))
                    refmask = '{0}'.format(format(cmd[5], 'x'))
                    self.__run_apwrite(run_data, ap, 0x04, cmd[3])
                    self.__run_apread(run_data, ap, 0x0C)
                elif cmd[0] == 'MEMWRITE':
                    ap = cmd[1]
                    csw = cmd[2]
                    if csw_done == 0 or (csw_shadow != csw):
                        csw_shadow = csw
                        csw_done = 1
                        self.__run_apwrite(run_data, ap, 0x00, csw)
                    self.__run_apwrite(run_data, ap, 0x04, cmd[3])
                    self.__run_apwrite(run_data, ap, 0x0c, cmd[4])

                elif cmd[0] == 'DOWNLOAD':
                    file = cmd[1]
                    is_data_file = cmd[2]
                    addr = cmd[3]
                    if is_data_file == 1:
                        f = open(file, 'rb')
                        f.seek(0, 2)
                        total_bytes = f.tell()
                        f.seek(0, 0)
                        if total_bytes > 0:
                            # Set up auto-incr mode for download
                            self.__writesvf("// auto-inc")
                            if self.cpu_type == 'a9':
                                self.__run_apwrite(run_data, self.AHB, 0x00, 0x00000012)
                            else:
                                self.__run_apwrite(run_data, self.AHB, 0x00, 0x30006012)
                            self.__writesvf("// address ")
                            self.__run_apwrite(run_data, self.AHB, 0x04, addr)
                            self.__writesvf("// data")
                            total_words = int(total_bytes / 4)
                            for k in range(0, total_words):
                                # Set up address - TAR auto-inc can handle only address @ 1 KB boundary
                                if ((addr + (4 * k)) % 0x400) == 0:
                                    self.__run_apwrite(run_data, self.AHB, 0x04, addr + (4 * k))
                                self.__run_apwrite(run_data, self.AHB, 0x0c, int.from_bytes(f.read(4), "little"))
                        f.close()
                    else:
                        f = ElfParse()
                        f.open(file)
                        phl = f.get_program_header()
                        for ph in phl:
                            total_bytes = 0
                            offset = 0
                            if descriptions.describe_p_type(ph.get('p_type')) == 'LOAD':
                                total_bytes = ph.get('p_filesz')
                                offset = ph.get('p_offset')
                                addr = ph.get('p_paddr')

                            if total_bytes > 0:
                                # Set up auto-incr mode for download
                                self.__writesvf("// auto-inc")
                                if self.cpu_type == 'a9':
                                    self.__run_apwrite(run_data, self.AHB, 0x00, 0x00000012)
                                else:
                                    self.__run_apwrite(run_data, self.AHB, 0x00, 0x30006012)
                                self.__writesvf("// address ")
                                if self.cpu_type == 'r5' and addr == 0x0:
                                    addr = addr + 0xffe00000
                                self.__run_apwrite(run_data, self.AHB, 0x04, addr)
                                self.__writesvf("// data")

                                total_words = int(total_bytes / 4)
                                for k in range(0, total_words):
                                    # Set up address - TAR auto-inc can handle only address @ 1 KB boundary
                                    if ((addr + (4 * k)) % 0x400) == 0:
                                        self.__run_apwrite(run_data, self.AHB, 0x04, addr + (4 * k))
                                    self.__run_apwrite(run_data, self.AHB, 0x0c, int.from_bytes(f.read_at(offset, 4),
                                                                                                "little"))
                                    offset += 4
                        f.close()
                elif cmd[0] == 'RESET':
                    self.__run_apwrite(run_data, self.JTAG, 0x00, 0x0, 1)
                    self.__run_apwrite(run_data, self.JTAG, 0x04, 0x1, 1)
                    self.__run_apwrite(run_data, self.JTAG, 0x00, 0xd, 1)
                    self.delay(500000)
                    open_cmd = self.cmd_dict[self.arch]['open']
                    if self.cpu_type == 'r5':
                        open_cmd = self.__zynqmp_open
                    if open_cmd == self.__zynqmp_open:
                        self.config_dict['linkdap'] = 1
                        open_cmd()
                        self.config_dict['linkdap'] = 0
                    open_cmd()
                    rst_cmd = 1
                else:
                    raise Exception(f"invalid DAP command: {cmd[0]}") from None
                complete = complete + 1
        self.__run_set_dpacc(run_data)
        if rst_cmd:
            self.__writesvf("SDR 35 TDI (3);")
            self.__writesvf("SDR 35 TDI (7);")
        else:
            self.__writesvf(f"SDR 35 TDI (3) TDO ({refval}) MASK({refmask});")
            self.__writesvf(f"SDR 35 TDI (7) TDO (0) MASK(20);")
        dap['cmds'].clear()
        return

    # DAP Abort
    def __run_set_abort(self, run_data):
        if run_data['ir'] != self.DAP_ABORT:
            run_data['ir'] = self.DAP_ABORT
            ir = '{0}'.format(format(run_data['ir'], 'x'))
            self.__writesvf(f'SIR 4 TDI ({ir}) SMASK (f);')

    # DP Access
    def __run_set_dpacc(self, run_data):
        if run_data['ir'] != self.DAP_DPACC:
            run_data['ir'] = self.DAP_DPACC
            ir = '{0}'.format(format(run_data['ir'], 'x'))
            self.__writesvf(f'SIR 4 TDI ({ir}) SMASK (f);')

    # AP Access
    def __run_set_apacc(self, run_data):
        if run_data['ir'] != self.DAP_APACC:
            run_data['ir'] = self.DAP_APACC
            ir = '{0}'.format(format(run_data['ir'], 'x'))
            self.__writesvf(f'SIR 4 TDI ({ir}) SMASK (f);')

    def __run_set_dpselect(self, run_data, addr):
        self.__run_set_dpacc(run_data)
        diff = (run_data['select'] ^ (addr >> 4)) & 0xF
        if diff != 0:
            run_data['select'] = run_data['select'] ^ diff
            svftdi = '{0}'.format(format(((run_data['select'] << 3) | 4), 'x'))
            self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')

    def __run_set_apselect(self, run_data, ap, addr):
        diff = (run_data['select'] ^ ((ap << 24) | addr)) & 0xff0000f0
        if diff != 0:
            run_data['select'] = run_data['select'] ^ diff
            self.__run_set_dpacc(run_data)
            svftdi = '{0}'.format(format(((run_data['select'] << 3) | 4), 'x'))
            self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')
        self.__run_set_apacc(run_data)

    def __run_clear_stickybits(self, name, run_data):
        if name not in self.daps.keys():
            raise Exception("No DAP present") from None
        dap = self.daps[name]
        if run_data['stickybits']:
            addr = 4
            data = dap['ctrl'] | run_data['stickybits']
            self.__run_set_dpselect(run_data, addr)
            svftdi = '{0}'.format(format(((data << 3) | ((addr & 0xc) >> 1)), 'x'))
            self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')
            run_data['stickybits'] = 0

    def __run_dpread(self, run_data, addr):
        self.__run_set_dpselect(run_data, addr)
        svftdi = '{0}'.format(format((((addr & 0xc) >> 1) | 1), 'x'))
        self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')

    def __run_dpwrite(self, run_data, addr, data):
        self.__run_set_dpselect(run_data, addr)
        svftdi = '{0}'.format(format(((data << 3) | ((addr & 0xc) >> 1)), 'x'))
        self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')

    def __run_apread(self, run_data, ap, addr):
        self.__run_set_apselect(run_data, ap, addr)
        svftdi = '{0}'.format(format((((addr & 0xc) >> 1) | 1), 'x'))
        self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')

    def __run_apwrite(self, run_data, ap, addr, data, ignoretdo=0):
        self.__run_set_apselect(run_data, ap, addr)
        svftdi = '{0}'.format(format(((data << 3) | ((addr & 0xc) >> 1)), 'x'))
        if ignoretdo != 0:
            self.__writesvf(f'SDR 35 TDI ({svftdi});')
        else:
            self.__writesvf(f'SDR 35 TDI ({svftdi}) TDO (2) MASK(7);')
        delaytcks = self.config_dict['delaytcks']
        if delaytcks != 0:
            self.__writesvf(f'RUNTEST {delaytcks} TCK;')

    def __mb_open(self):
        scan_chain = self.config_dict['scan_chain']
        device_index = self.config_dict['device_index']
        bscan = self.config_dict['bscan']
        cpu_index = self.config_dict['cpu_index']

        self.__writesvf("TRST OFF;")
        self.__writesvf("ENDIR IDLE;")
        self.__writesvf("ENDDR IDLE;")
        self.__writesvf("STATE RESET;")
        self.__writesvf("STATE IDLE;")
        self.__write_header_trailer_regs(device_index)
        ir_len = scan_chain[(device_index * 2) + 1]
        if ir_len == 0:
            raise Exception("irlen should be non-zero") from None
        bypass = self.__get_mask(ir_len)
        # For ZynqMP (PMU & MBs on PL)
        if ir_len == 12 and bscan != 0x0e4:
            bscan = (0x24 << 6) | bscan
        # Bypass
        self.__writesvf("// bypass")
        self.__writesvf(f"SIR $ir_length TDI ({bypass});")

        # Select USER bscan
        # MDM USER register
        self.__writesvf("// select user bscan for pmu mdm")
        bscan = '{0}'.format(format(bscan, 'x'))
        self.__writesvf(f"SIR $ir_length TDI ({bscan});")

        # Select MDM port
        self.__writesvf("// select mdm port")
        self.__writesvf("SDR 4 TDI (01);")

        # Select which MB
        self.__writesvf("// which mb")
        self.__writesvf("SDR 8 TDI (0d);")
        # CPU index should always be 0 for PMU
        if bscan in ('e4', 'E4'):
            cpu_index = 0
        select_mb_reg_bitlen = 8
        if cpu_index > 7:
            select_mb_reg_bitlen = cpu_index + 1
        cpu_index = '{0}'.format(format((1 << cpu_index), 'x'))
        self.__writesvf(f"SDR {select_mb_reg_bitlen} TDI ({cpu_index});")

    def __mb_mwr(self, addr, val):
        # sequence of instructions to write words to memory:
        # "imm HIDATA"
        # "ori r11,r0,LODATA"
        # "imm HIADDR"
        # "swi r11,r0,LOADDR"
        bitlen = 136
        hexval = '0x96'  # MDM sync
        hexval += 'b000'  # imm
        hexval += "{0:0{1}x}".format(((val >> 16) & 0xFFFF), 4)
        hexval += 'a160'
        hexval += "{0:0{1}x}".format((val & 0xFFFF), 4)
        hexval += 'b000'  # imm
        hexval += "{0:0{1}x}".format(((addr >> 16) & 0xFFFF), 4)
        hexval += 'f960'  # swi r11, r0
        hexval += "{0:0{1}x}".format((addr & 0xFFFF), 4)
        revbits = (bin(int(hexval, 16)).zfill(bitlen))[:1:-1]
        bitvals = int(revbits, 2)
        bitvals = '{0}'.format(format(bitvals, 'x'))
        self.__writesvf("SDR 8 TDI (04);")
        self.__writesvf(f'SDR 136 TDI ({bitvals});')

    def __mb_dow(self, file, is_data, addr):
        offset = 0
        if is_data == 1:
            f = open(file, 'rb')
            f.seek(0, 2)
            total_bytes = f.tell()
            f.seek(0, 0)
            self.__mb_dow_mem(f, 1, total_bytes, addr, offset)
            f.close()
        else:
            f = ElfParse()
            f.open(file)
            phl = f.get_program_header()
            for ph in phl:
                total_bytes = 0
                offset = 0
                if descriptions.describe_p_type(ph.get('p_type')) == 'LOAD':
                    total_bytes = ph.get('p_filesz')
                    offset = ph.get('p_offset')
                    addr = ph.get('p_paddr')

                if total_bytes > 0:
                    self.__mb_dow_mem(f, 0, total_bytes, addr, offset)
            f.close()

    def __mb_dow_mem(self, f, is_data, total_bytes, addr, offset):
        chunk_size = self.config_dict['chunk_size']
        tempaddr = addr
        if total_bytes > 0:
            for i in range(0, total_bytes, chunk_size):
                rem_bytes = total_bytes - i
                if rem_bytes < chunk_size:
                    chunk_size = rem_bytes
                if is_data == 1:
                    bindata = f.read(chunk_size)
                else:
                    bindata = f.read_at(offset, chunk_size)
                hexval = '0x96'
                bitlen = 8
                chunk_size_words = int(chunk_size / 4)
                for bytecnt in range(0, chunk_size_words):
                    wordval = int.from_bytes(bindata[bytecnt * 4: (bytecnt + 1) * 4], 'little')
                    hexval += 'b000'
                    hexval += "{0:0{1}x}".format(((wordval >> 16) & 0xFFFF), 4)
                    hexval += 'a160'
                    hexval += "{0:0{1}x}".format((wordval & 0xFFFF), 4)
                    hexval += 'b000'
                    hexval += "{0:0{1}x}".format(((tempaddr >> 16) & 0xFFFF), 4)
                    hexval += 'f960'
                    hexval += "{0:0{1}x}".format((tempaddr & 0xFFFF), 4)

                    bitlen += 128
                    offset += 4
                    tempaddr += 4

                revbits = (bin(int(hexval, 16)).zfill(bitlen))[:1:-1]
                bitvals = hex(int(revbits, 2))[2:].zfill(int(bitlen / 4))
                self.__writesvf("SDR 8 TDI (04);")
                self.__writesvf(f"SDR {bitlen} TDI ({bitvals});")

    def __mb_stop(self):
        # Control Register - Dbg WakeUp, Normal Stop, Disable interrupts & ARM
        self.__writesvf("SDR 8 TDI (01);")
        self.__writesvf("SDR 10 TDI (0249);")
        # Try to reset MB_CONTROL_STOP, then set it again
        self.__writesvf("SDR 8 TDI (01);")
        self.__writesvf("SDR 10 TDI (0040);")
        self.__writesvf("SDR 8 TDI (01);")
        self.__writesvf("SDR 10 TDI (0048);")

    def __mb_con(self):
        self.__writesvf("SDR 8 TDI (01);")
        self.__writesvf("SDR 10 TDI (0105);")

    def __mb_setpc(self, value):
        val = '{0}'.format(format(value, 'x'))
        self.__writesvf(f"// setting pc to 0x{val}")
        bitlen = 72
        hexval = '0x96'
        hexval += 'b000'
        hexval += "{0:0{1}x}".format(((value >> 16) & 0xFFFF), 4)
        hexval += 'b808'
        hexval += "{0:0{1}x}".format((value & 0xFFFF), 4)
        revbits = (bin(int(hexval, 16)).zfill(bitlen))[:1:-1]
        bitvals = int(revbits, 2)
        bitvals = '{0}'.format(format(bitvals, 'x'))
        self.__writesvf('SDR 8 TDI (04);')
        self.__writesvf(f'SDR 72 TDI ({bitvals});')
        # start execution
        self.__writesvf('SDR 8 TDI (01);')
        self.__writesvf('SDR 10 TDI (0105);')
        self.__writesvf('SDR 8 TDI (04);')
        self.__writesvf(f'SDR 72 TDI ({bitvals});')

    def __arm_mwr(self, addr, val):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.AHB, addr, val)
        self.__cmd_run(dapname)

    def __arm_dow(self, f, data, addr):
        # TODO : what if filename path has spaces, runcmd splits into two
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.daps[dapname]['cmds'].append(f'DOWNLOAD {f} {data} {addr}')
        self.__cmd_run(dapname)
        self.delay(100)

    def __a64_stop(self):
        self.__armv8_stop()
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV8_INSTR_IC_IALLU)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV8_INSTR_DSB_SYS)
        self.__cmd_run(dapname)

    def __a64_con(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.DBGOSLAR, 0)
        self.__cmd_memwrite(dapname, self.APB, self.DBGDSCR, 0x3006327)

        # Invalidate cache
        self.__cmd_memwrite(dapname, self.APB, self.DBGITR, self.ARMV8_INSTR_IC_IALLU)
        self.__cmd_memwrite(dapname, self.APB, self.DBGITR, self.ARMV8_INSTR_DSB_SYS)
        self.__cmd_run(dapname)
        self.__armv8_con()

    def __a64_setpc(self, value):
        device_index = self.config_dict['device_index']
        setval = '{0}'.format(format(value, 'x'))
        self.__writesvf(f'// setting pc to 0x{setval}')
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGOSLAR, 0)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x3006327)
        # Select DBGDTRRX (offset - 0x80) and write the value of PC
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDTRTX, (value >> 32) & 0xffffffff)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDTRRX, (value & 0xffffffff))

        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_CP14_C5_TO_GPR
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV8_MRS_DBG_DTR_X0)
        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_GPR_TO_PC
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV8_MSR_X0_TO_DLR)
        self.__cmd_run(dapname)

    def __a32_stop(self):
        self.__armv8_stop()
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MCR_CP15_R0_ICIALLU)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MCR_CP15_R0_BPIALL)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_INSTR_DSB_SYS)
        self.__cmd_run(dapname)

    def __a32_con(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGOSLAR, 0)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x3006327)

        # Invalidate cache
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MCR_CP15_R0_ICIALLU)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MCR_CP15_R0_BPIALL)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_INSTR_DSB_SYS)
        self.__cmd_run(dapname)
        self.__armv8_con()

    def __a32_setpc(self, value):
        setval = '{0}'.format(format(value, 'x'))
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__writesvf(f'// setting pc to 0x{setval}')

        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDTRRX, self.value)
        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_CP14_C5_TO_GPR
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MOVE_CP14_C5_TO_GPR)
        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_GPR_TO_PC
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.T32_MOVE_GPR_TO_PC)
        self.__cmd_run(dapname)

    def __armv7_stop(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDRCR, 0x1)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x3186003)
        # Invalidate cache
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_MCR_CP15_R0_ICIALLU)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_DATA_SYNC_BARRIER)
        self.__cmd_run(dapname)
        self.delay(100)
        # Check if the core has stopped
        self.__cmd_memread(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0xa, 0xa)
        self.__cmd_run(dapname)

    def __armv7_setpc(self, value):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        setval = '{0}'.format(format(value, 'x'))
        self.__writesvf(f"// setting pc to 0x{setval}")
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDTRRX, value)

        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_CP14_C5_TO_GPR
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_MOVE_CP14_C5_TO_GPR)
        # Select DBGITR (offset - 0x84) and write the instruction INSTR_MOVE_GPR_TO_PC
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_MOVE_GPR_TO_PC)
        self.__cmd_run(dapname)

    def __armv7_con(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'

        # Invalidate cache
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_MCR_CP15_R0_ICIALLU)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGITR, self.ARMV7_INSTR_SYNC_BARRIER)
        self.__cmd_run(dapname)
        self.delay(100)

        # Check if the instruction complete bit is set
        self.__cmd_memread(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x10000000, 0x10000000)
        self.__cmd_run(dapname)

        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDRCR, 0x8)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x03184003)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDRCR, 0x2)
        self.__cmd_run(dapname)

    def __armv8_stop(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        # Unlock CTI access by writing to OS Lock Access Register
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGOSLAR, 0)
        # Unlock CTI registers
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x2007C02)
        # Unlock CTI registers
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTILAR, 0xc5acce55)
        # Close CTI gate
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIGATE, 0x00000000)
        # Enable CTI
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTICTRL, 0x00000001)
        # Disable chan#0 -> TrigOut#1
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIOUTEN1, 0x00000000)
        # Ack TrigOut#1
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIINTACK, 0x00000002)
        # Clear chan#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIAPPCLR, 0x00000001)
        # Enable chan#0 -> TrigOut#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIOUTEN0, 0x00000001)
        # Set active chan#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIAPPSET, 0x00000001)
        # Clear chan#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIAPPCLR, 0x00000001)
        self.__cmd_run(dapname)
        self.delay(100)
        # Check if stopped, check bit 0 & overrun errors of DSCR & ACK of the transaction
        self.__cmd_memread(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x800000a, 0xe800000a)
        self.__cmd_run(dapname)

    def __armv8_con(self):
        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'

        # Unlock CTI registers
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTILAR, 0xc5acce55)
        # Clear sticky bits (RCR)
        self.__cmd_memwrite(dapname, self.APB, self.dbgbase + self.DBGDRCR, (1 << 3))
        # Close CTI gate
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIGATE, 0x00000000)
        # Enable CTI
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTICTRL, 0x00000001)
        # Disable chan#0 -> TrigOut#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIOUTEN0, 0x00000000)
        # Clear chan#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIAPPCLR, 0x00000001)
        # Ack TrigOut#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIINTACK, 0x00000001)
        # Enable chan#0 -> TrigOut#1
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIOUTEN1, 0x00000001)
        # Pulse chan#0
        self.__cmd_memwrite(dapname, self.APB, self.ctibase + self.CTIAPPPULSE, 0x00000001)

        self.delay(100)
        # Check if running, check bit 0 & overrun errors of DSCR & ACK of the transaction
        self.__cmd_memread(dapname, self.APB, self.dbgbase + self.DBGDSCR, 0x2, 0xe800000a)
        self.__cmd_run(dapname)

    def __zynq_open(self):
        device_index = self.config_dict['device_index']
        name = f'dap{device_index}'
        ctrl = 0x50000001
        self.daps[name] = {'cmds': list(), 'ctrl': ctrl}
        self.__writesvf("TRST OFF;")
        self.__writesvf("ENDIR IDLE;")
        self.__writesvf("ENDDR IDLE;")
        self.__writesvf("STATE RESET;")
        self.__writesvf("STATE IDLE;")
        self.__writesvf("RUNTEST 100000 TCK;")
        self.__write_header_trailer_regs(device_index)

        self.__cmd_dpwrite(name, 4, ctrl)
        self.__cmd_run(name)
        self.__cmd_apwrite(name, 0, 0, 0x2)
        self.__cmd_run(name)
        self.__cmd_apwrite(name, 1, 0, 0x80000002)
        self.__cmd_run(name)
        self.__cmd_memwrite(name, self.APB, self.dbgbase + self.DBGVCR, 0x0)
        self.__cmd_run(name)

    def __zynqmp_open(self):
        device_index = self.config_dict['device_index']
        linkdap = self.config_dict['linkdap']
        self.__writesvf('TRST OFF;')
        self.__writesvf('ENDIR IDLE;')
        self.__writesvf('ENDDR IDLE;')
        self.__writesvf('STATE RESET;')
        self.__writesvf('STATE IDLE;')
        if linkdap == 1:
            device_index = device_index - 1
            self.__write_header_trailer_regs(device_index)
            self.__writesvf("SIR 12 TDI (824);")
            self.__writesvf("SDR 32 TDI (3);")
            self.__writesvf("RUNTEST 10000 TCK;")
            self.__writesvf("STATE IDLE;")
            self.__writesvf("ENDIR IDLE;")
            self.__writesvf("ENDDR IDLE;")
            self.__writesvf("STATE RESET;")
            self.__writesvf("RUNTEST 10000 TCK;")
            self.__writesvf("STATE IDLE;")
        else:
            name = f'dap{device_index}'
            ctrl = 0x50000001
            self.daps[name] = {'cmds': list(), 'ctrl': ctrl}
            self.__writesvf('RUNTEST 100000 TCK;')
            self.__write_header_trailer_regs(device_index)
            self.__writesvf('SIR 4 TDI (0e);')
            self.__writesvf('SDR 32 TDI (00000000) TDO (05ba00477) MASK (0fffffff);')

            self.__cmd_dpwrite(name, 4, ctrl)
            self.__cmd_run(name)
            self.__cmd_apwrite(name, 0, 0, 0x30006002)
            self.__cmd_run(name)
            self.__cmd_apwrite(name, 1, 0, 0x80000002)
            self.__cmd_run(name)

    def config(self, *args, **kwargs):
        """
config:
    Configure options for SVF file.

Prototype:
    svf.config(*args, *kwargs)

Options:
    -linkdap (-l)
        Generate SVF for linking DAP to the jtag chain for ZynqMP
        Silicon versions 2.0 and above.

Optional Arguments:
kwargs:
    device_index
        List of idcode-irlength pairs. Can be found using
        jtag.targets() command.

    cpu_index
        Specify the cpu-index to generate the SVF file.
        For A53#0 - A53#3 on ZynqMP, use cpu-index 0 -3
        For R5#0 - R5#1 on ZynqMP, use cpu-index 4 -5
        For A9#0 - A9#1 on Zynq, use cpu-index 0 -1
        If multiple MicroBlaze processors are connected to MDM,
        select the specific MicroBlaze index for execution.

    out
        Output SVF file.

    delay
        Delay in ticks between AP writes.

    scan_chain
        List of idcode-irlength pairs. Can be found using
        jtag.targets() command.

    bscan
        This is used to specify user bscan port to which MDM is
        connected.

    mb_chunksize
        This used to specify the chunk size in bytes for each
        transaction while downloading. Supported only for Microblaze
        processors.

    exec_mode
        Execution mode for ARM v8 cores. Supported modes are
        a32 - v8 core is setup in 32 bit mode.
        a64 - v8 core is setup in 64 bit mode.

Returns:
    None

Examples:
    svf.config(scan_chain = [0x14738093,12,0x5ba00477,4],
               device_index = 1, cpu_index = 0, out = "test.svf")

Interactive mode examples:
    svf config -scan_chain [0x14738093,12,0x5ba00477,4]
               -device_index 1 -cpu_index 0 -out test.svf
        """
        parser = argparse.ArgumentParser(description='svf config')
        parser.add_argument('--linkdap', '-l', action='store_true', help='dap link')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if 'scan_chain' not in kwargs:
            raise Exception('scan chain not specified') from None
        bscan = kwargs.pop('bscan') if 'bscan' in kwargs else 'user2'
        if bscan not in self.bscan_dict.keys():
            raise Exception(f'unknown bscan option {bscan}') from None

        scan_chain = kwargs.pop('scan_chain')
        self.outfile = kwargs.pop('out') if 'out' in kwargs else 'out.svf'
        device_index = check_int(kwargs.pop('device_index') if 'device_index' in kwargs else 0)
        cpu_index = check_int(kwargs.pop('cpu_index') if 'cpu_index' in kwargs else 0)
        delay = check_int(kwargs.pop('delay') if 'delay' in kwargs else 0)
        mb_chunksize = check_int(kwargs.pop('mb_chunksize') if 'mb_chunksize' in kwargs else 1024)
        exec_mode = kwargs.pop('exec_mode') if 'exec_mode' in kwargs else 'a64'

        self.config_dict = {'scan_chain': scan_chain, 'cpu_index': cpu_index, 'device_index': device_index,
                            'delaytcks': delay, 'bscan': self.bscan_dict[bscan], 'outfile': self.outfile,
                            'chunk_size': mb_chunksize, 'linkdap': 1 if parsed_args.linkdap is True else 0}
        id_code = check_int(scan_chain[device_index * 2])
        if id_code == 0x5ba00477:
            if cpu_index <= 3:
                self.arch = 'a64' if exec_mode == 'a64' else 'a32'
                self.cpu_type = 'a53'
                self.dbgbase = self.A53_DBGBASE + cpu_index * 0x100000
                self.ctibase = self.A53_CTIBASE + cpu_index * 0x100000
            elif cpu_index <= 5:
                self.arch = 'armv7'
                self.cpu_type = 'r5'
                self.dbgbase = self.R5_DBGBASE + ((cpu_index - 4) * 0x2000)
            else:
                raise Exception(f'cpu_index should be between 0 to 5') from None
        elif id_code == 0x4ba00477:
            if cpu_index > 1:
                raise Exception(f'cpu-index should be 0 or 1') from None
            self.arch = 'armv7'
            self.cpu_type = 'a9'
            self.dbgbase = self.A9_DBGBASE + cpu_index * 0x2000
        else:
            self.arch = 'mb'
            self.cpu_type = 'mb'
        self.fileptr = open(self.outfile, 'a')
        self.__writesvf(f'// Generating SVF for {self.arch} ')
        open_cmd = self.cmd_dict[self.arch]['open']
        if self.cpu_type == 'r5':
            open_cmd = self.__zynqmp_open
        open_cmd()

    add_function_metadata('svf config', 'Configure options for SVF file.', 'svf', 'SVF')

    def con(self):
        """
con:
    Record resuming the execution of active target to SVF file.

Prototype:
    svf.con()

Returns:
    None

Examples:
    svf.con()

Interactive mode examples:
    svf con
        """

        self.__writesvf('// continue')
        con_cmd = self.cmd_dict[self.arch]['con']
        con_cmd()

    add_function_metadata('svf con', 'Record resuming the execution of active target to SVF file.', 'svf', 'SVF')

    def delay(self, tcks):
        """
delay:
    Record delay in tcks to SVF file.

Prototype:
    svf.delay(tcks = <delay>)

Required Arguments:
    tcks = <delay>

Returns:
    None

Examples:
    svf.delay(tcks=1000)

Interactive mode examples:
    svf delay 1000
        """

        self.__writesvf(f'RUNTEST {tcks} TCK;')

    add_function_metadata('svf delay', 'Record delay in tcks to SVF file.', 'svf', 'SVF')

    def dow(self, *args, **kwargs):
        """
dow:
    Record elf download to SVF file.

Prototype:
    svf.dow(*args,**kwargs)

Options:
    --data
Set to record downloading of binary file <file> to the memory.

Optional Arguments:
    kwargs:
        file = <binary_file/ elf file>
            Binary file/ elf file to be downloaded.

        addr = <address>
            Address at which file is to be downloaded.

Returns:
    None if successful, else exception is raised.

Examples:
    svf.dow("--data" , file = "data.bin", addr =0x1000)
    svf.dow(file = "test.elf")

Interactive mode examples:
    svf dow -data -file data.bin -addr 0x1000
    svf dow -file test.elf
        """

        parser = argparse.ArgumentParser(description='svf download')
        parser.add_argument('--data', '-d', action='store_true',
                            help='Record downloading of binary file to the memory.')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        file = kwargs.pop('file')
        addr = 0
        entryaddr = 0
        data = 1 if parsed_args.data is True else 0
        if parsed_args.data is True:
            addr = kwargs.pop("addr")
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        self.__writesvf("// download file")
        if data == 0:
            f = ElfParse()
            f.open(file)
            entryaddr = f.get_elf_header()['e_entry']
            f.close()
        dow_cmd = self.cmd_dict[self.arch]['dow']
        dow_cmd(file, data, addr)
        if data == 0:
            setpc_cmd = self.cmd_dict[self.arch]['setpc']
            setpc_cmd(entryaddr)

    add_function_metadata('svf dow', 'Record elf download to SVF file.', 'svf', 'SVF')

    def generate(self):
        """
generate:
    Generate recorded SVF file.

Prototype:
    svf.generate()

Returns:
    None if successful, else exception is raised.

Examples:
    svf.generate()

Interactive mode examples:
    svf generate
        """
        if self.outfile is None:
            raise Exception('SVF not configured') from None
        self.fileptr.close()

    add_function_metadata('svf generate', 'Generate recorded SVF file.', 'svf', 'SVF')

    def mwr(self, addr, val):
        """
mwr:
    Record memory write to SVF file.

Prototype:
    svf.mwr(addr = <address>, val = <value>)

Required Arguments:
    addr
        Address on which value is to be written.
    val
        Value of the memory address.

Returns:
    None if successful, else exception is raised.

Examples:
    svf.mwr(0xffff0000,0xffff0000)

Interactive mode examples:
    svf mwr 0xffff0000 0xffff0000
        """
        self.__writesvf(f'// write to mem - value-{val} @ addr-{addr}')
        write_cmd = self.cmd_dict[self.arch]['mwr']
        write_cmd(addr, val)

    add_function_metadata('svf mwr', 'Record memory write to SVF file.', 'svf', 'SVF')

    def rst(self, *args):
        """
rst:
    System reset.

Prototype:
    svf.rst(*args)

Options:
    -processor (-p)
        Set for resentting processor.

    -system (-s)
        Set for resetting system.

Returns:
    None if successful, else exception is raised.

Examples:
    svf.rst("--processor")

Interactive mode examples:
    svf rst --processor
        """
        parser = argparse.ArgumentParser(description='svf reset')
        parser.add_argument('--processor', '-p', action='store_true', help='Processor reset')
        parser.add_argument('--system', '-s', action='store_true', help='System reset')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        processor = 1 if parsed_args.processor is True else 0

        device_index = self.config_dict['device_index']
        dapname = f'dap{device_index}'
        cpu_index = self.config_dict['cpu_index']
        self.__writesvf('// reset')
        if processor == 1:
            if self.cpu_type == 'a53':
                rst_ctrl = 1 << (cpu_index + 10)
                rst_ctrl = rst_ctrl | (1 << 8)
                rst_ctrl = rst_ctrl | (1 << cpu_index)
                # Bootloop
                self.__cmd_memwrite(dapname, self.AHB, 0xffff0000, 0x14000000)
                # Activate reset
                self.__cmd_memwrite(dapname, self.AHB, 0xfd1a0104, rst_ctrl)
                # Write the reset address to RVBARADDR
                self.__cmd_memwrite(dapname, self.AHB, 0xfd5c0040 + (8 * cpu_index), 0xffff0000)
                self.__cmd_memwrite(dapname, self.AHB, 0xfd5c0044 + (8 * cpu_index), 0x0)
                # Clear reset
                rst_ctrl = rst_ctrl & ~(0x1 << 8)
                rst_ctrl = rst_ctrl & ~(1 << (cpu_index + 10))
                rst_ctrl = rst_ctrl & ~(1 << cpu_index)
                self.__cmd_memwrite(dapname, self.AHB, 0xfd1a0104, rst_ctrl)
                # Stop the core
                self.__armv8_stop()
            if self.cpu_type == 'r5':
                r5_cpu_index = cpu_index - 0x4
                rst_ctrl = 0x188fc0 | (0x1 << r5_cpu_index)
                # Bootloop
                self.__cmd_memwrite(dapname, self.AHB, 0xffff0000, 0xeafffffe)
                # Activate reset
                self.__cmd_memwrite(dapname, self.AHB, 0xff5e023c, rst_ctrl)
                # Start from OCM after reset
                self.__cmd_memwrite(dapname, self.AHB, 0xff9a0100, 0x5)
                # Clear reset
                rst_ctrl = rst_ctrl & ~(1 << r5_cpu_index)
                self.__cmd_memwrite(dapname, self.AHB, 0xff5e023c, rst_ctrl)
                # Stop the core
                self.__armv7_stop()
            if self.cpu_type == 'a9':
                rst_ctrl = 0x1 << cpu_index
                # Bootloop
                self.__cmd_memwrite(dapname, self.AHB, 0x0, 0xeafffffe)
                # Unlock SLCR
                self.__cmd_memwrite(dapname, self.AHB, 0xf8000008, 0xdf0d)
                # Activate reset
                self.__cmd_memwrite(dapname, self.AHB, 0xf8000244, rst_ctrl)
                # Stop clock
                self.__cmd_memwrite(dapname, self.AHB, 0xf8000244, 0x11)
                # Start clock
                self.__cmd_memwrite(dapname, self.AHB, 0xf8000244, 0x10)
                # Clear reset
                rst_ctrl = rst_ctrl & ~(1 << cpu_index)
                self.__cmd_memwrite(dapname, self.AHB, 0xf8000244, rst_ctrl)
                # Stop the core
                self.__armv7_stop()
        else:
            self.__cmd_reset(dapname)
        self.__cmd_run(dapname)

    add_function_metadata('svf rst', 'System reset.', 'svf', 'SVF')

    def stop(self):
        """
stop:
    Record suspending execution of current target to SVF file.

Prototype:
    svf.stop()

Returns:
    None

Examples:
    svf.stop()

Interactive mode examples:
    svf stop
        """
        self.__writesvf('// stop')
        stop_cmd = self.cmd_dict[self.arch]['stop']
        stop_cmd()

    add_function_metadata('svf stop', 'Record suspending execution of current target to SVF file.', 'svf', 'SVF')

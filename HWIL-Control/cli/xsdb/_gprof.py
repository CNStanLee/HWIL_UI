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

from xsdb._elf import *


class Gprof(object):
    def __init__(self, session):
        self.session = session
        self.gmonparamstruct = list()
        self.profile_enabled = 0
        self.prof_addr = dict()
        self.elf = None
        self.bigendian = 0
        self.ngmonsections = None
        self.histbinsize = 4
        self.gmonparamoffsets = {'GPARAM_START': 0, 'GPARAM_HIST_O': 4, 'GPARAM_HISTSIZE_O': 8, 'GPARAM_CG_FROM_O': 12,
                                 'GPARAM_CG_FROMSIZE_O': 16, 'GPARAM_CG_TO_O': 20, 'GPARAM_CG_TOSIZE_O': 24,
                                 'GPARAM_LOWPC_O': 28, 'GPARAM_HIGHPC_O': 32, 'GPARAM_TEXTSIZE_O': 36,
                                 'GPARAM_SIZE': 40}

    def get_gmonparam_offsets(self):
        return self.gmonparamoffsets

    def get_gmonparamstruct(self):
        return self.gmonparamstruct

    def enable_profiling(self):
        self.profile_enabled = 1

    def is_profiling_enabled(self):
        return self.profile_enabled

    def set_profile_elf(self, file):
        self.elf = ElfParse()
        self.elf.open(file)
        self.ngmonsections = 0
        self.gmonparamstruct = list()
        self.prof_addr = dict()
        self.bigendian = None

    def set_prof_endianness(self, val):
        self.bigendian = val

    def get_prof_endianness(self):
        return self.bigendian

    def is_elf_prof_enabled(self, file):
        f = ElfParse()
        f.open(file)
        ret = 0
        if f.get_sym_addr('__gnu_mcount_nc') is not None or f.get_sym_addr('_mcount') is not None:
            ret = 1
        f.close()
        return ret

    def get_prof_version(self):
        value = self.elf.get_sym_val('profile_version', self.bigendian)
        if value == 0:
            return 0
        return 1

    def get_prof_addresses(self):
        self.prof_addr['sampfreq'] = self.elf.get_sym_addr('sample_freq_hz')
        self.prof_addr['binsize'] = self.elf.get_sym_addr('binsize')
        self.prof_addr['timerticks'] = self.elf.get_sym_addr('timer_clk_ticks')
        self.prof_addr['cpufreq'] = self.elf.get_sym_addr('cpu_clk_freq')
        self.prof_addr['ngmonsecs'] = self.elf.get_sym_addr('n_gmon_sections')
        self.prof_addr['gmonparam'] = self.elf.get_sym_addr('_gmonparam')
        return self.prof_addr

    def get_prof_cpufreq(self):
        return self.elf.get_sym_val('cpu_clk_freq', self.bigendian)

    def get_no_of_gmon_sections(self):
        return self.ngmonsections

    def get_sorted_exec_sections(self):
        sortedsec = list()
        exec_sections = self.elf.get_exec_sections()
        for exsec in exec_sections:
            retsec = self.sort_sections(exsec)
            if retsec is not None:
                sortedsec.append(retsec)
        if self.ngmonsections == 0:
            raise Exception('program cannot be profiled - no code sections found') from None
        code_highpc = sortedsec[self.ngmonsections - 1]['highpc']
        code_lowpc = sortedsec[0]['lowpc']
        code_size = code_highpc - code_lowpc
        if code_size > 0x100000:
            raise Exception('code sections are located far apart, which results in huge profile output file') from None
        return sortedsec

    def sort_sections(self, sec):
        discard_sections = [".vectors.reset", ".vectors.sw_exception", ".vectors.interrupt", ".vectors.hw_exception",
                            ".init", ".fini"]
        lowpc = sec.get('sh_addr')
        size = sec.get('sh_size')
        secname = sec.get('sh_name')
        highpc = lowpc + size

        # If section is very small (< 10 instructions), do not profile
        # Min profile section size = 10 inst * 4 bytes per inst
        if size < 10 * 4:
            return None
        for dissec in discard_sections:
            if secname == dissec:
                return None

        t_down = self.rounddown(highpc, self.histbinsize * 4)
        t_up = self.roundup(highpc, self.histbinsize * 4)
        t_highpc = t_down
        t_down = self.rounddown(lowpc, self.histbinsize * 4)
        t_lowpc = t_down
        retdict = {'secname': secname, 'lowpc': t_lowpc, 'highpc': t_highpc}
        self.ngmonsections = self.ngmonsections + 1
        return retdict

    def get_prof_cg_hist_details(self, secdict, cputype):
        sname = secdict['secname']
        cgsize = self.calc_cg_size(sname, cputype)
        highpc = secdict['highpc']
        lowpc = secdict['lowpc']
        histcount = int((highpc - lowpc) / (self.histbinsize * 4))
        histsize = self.roundup(histcount * 2, 4)
        retdict = {'secname': sname, 'lowpc': lowpc, 'highpc': highpc, 'cgsize': cgsize, 'histcount': histcount,
                   'histsize': histsize}
        self.gmonparamstruct.append(retdict)
        return retdict

    def calc_cg_size(self, sname, cputype):
        calltype = 0
        fc_cnt = 0
        fpc_cnt = 0
        inst = list()
        secdata = self.elf.get_elf_section_data(sname)
        bindata = secdata[sname]['secbin']
        len_bindata = len(bindata)
        for i in range(0, len(bindata), 4):
            inst.append(int.from_bytes(bindata[i:i + 4], byteorder='little', signed=False))
        for i in range(0, len(inst)):
            if cputype == 'Cortex-A9':
                calltype = self.is_func_call_instr_a9(inst[i])
            elif cputype == 'MicroBlaze':
                calltype = self.is_func_call_instr_mb(inst[i])
            if calltype == 1:
                fc_cnt = fc_cnt + 1
            elif calltype == 2:
                fpc_cnt += 1
        # Call Graph Mem Size 	= Size for FromStruct + Size for TosStruct
        # = (Total Num of Calls * FromStructSize) +
        # ((Num of Func Calls + (Num of FuncPtr Calls * ~Num of Target Calls)) * TosStructSize)
        # cgmemsize = [ {(fc + fpc)*12} + {(fc + fpc*5)*12} ]
        cgmemsize = ((fc_cnt + fpc_cnt) * 12) + ((fc_cnt + (fpc_cnt * 5)) * 12)
        return self.roundup(cgmemsize, 4)

    def is_func_call_instr_a9(self, instr):
        calltype = instr & 0x0F000000
        if calltype == 0x01000000:
            if instr & 0x002FFF30 == 0x002FFF30:
                # Func pointer call type
                return 2
        elif calltype == 0x0B000000:
            # func call type
            return 1
        return 0

    def is_func_call_instr_mb(self, instr):
        calltype = instr >> 26
        brtype = (instr >> 16) & 0x1F
        if calltype == 0x26:
            if brtype == 0x14 or brtype == 0x1C:
                return 2
        elif calltype == 0x2E:
            if brtype == 0x14 or brtype == 0x1C:
                return 1
        return 0

    def rounddown(self, x, y):
        return int(x / y) * y

    def roundup(self, x, y):
        return int((x + y - 1) / y) * y

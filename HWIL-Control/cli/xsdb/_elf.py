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

from collections import UserDict
from elftools.elf.elffile import ELFFile


class ElfParse(object):
    def __init__(self):
        self.__file = None
        self.__file_ptr = None
        self.__elf_file = None

    def open(self, file):
        self.__file = file
        self.__file_ptr = open(file, "rb")
        self.__elf_file = ELFFile(self.__file_ptr)
        return self.__file_ptr

    def get_program_header(self):
        self.__ph_table = []
        for n_sec, segment in enumerate(self.__elf_file.iter_segments()):
            self.__ph_table.append(UserDict(segment.header))
        return self.__ph_table

    def get_section_header(self):
        self.__sh_table = []
        for n_sec, segment in enumerate(self.__elf_file.iter_sections()):
            header = UserDict(segment.header)
            header['sh_name'] = segment.name
            self.__sh_table.append(header)
        return self.__sh_table

    def get_elf_header(self):
        return UserDict(self.__elf_file.header)

    def get_sym_table(self):
        self.__symbols = []
        for sec in self.__elf_file.iter_sections():
            if sec['sh_type'] == 'SHT_SYMTAB':
                self.__symbols = sorted(sec.iter_symbols(), key=lambda sym: sym.name)
                return self.__symbols

    def get_sym_addr(self, symbol):
        symtab = self.get_sym_table()
        for sym in symtab:
            if sym.name == symbol:
                return sym.entry.st_value
        return None

    def get_sym_val(self, symbol, endian):
        symtab = self.get_sym_table()
        sym = None
        found = 0
        for sym in symtab:
            if sym.name == symbol:
                found = 1
                break
        if found == 0:
            raise Exception(f'symbol {symbol} not found') from None
        sym_addr = sym.entry.st_value
        sym_size = sym.entry.st_size
        shdrlist = self.get_section_header()
        for sh in shdrlist:
            loadaddr = sh.get('sh_addr')
            datasize = sh.get('sh_size')
            secoff = sh.get('sh_offset')
            symoff = secoff + sym_addr - loadaddr
            highadd = loadaddr + datasize
            if loadaddr <= sym_addr < highadd:
                value = self.read_at(symoff, sym_size)
                return int.from_bytes(value, byteorder='little' if endian == 0 else 'big', signed=False)
        return None

    def read_at(self, pos, length):
        f = self.__file_ptr
        f.seek(pos, 0)
        data = f.read(length)
        if len(data) != length:
            raise Exception('Incomplete ELF file read') from None
        return data

    def close(self):
        if self.__file is not None and self.__file_ptr is not None:
            self.__file_ptr.close()

    def get_elf_section_headers(self):
        sh_info = ''
        shl = self.get_section_header()
        for sh in shl:
            if sh.get('sh_flags') & 0x7:
                sh_info += '{0:4s}{1}{2}{3}{4}{5}{6}{7}'. \
                    format('', 'section, ', sh.get('sh_name'), ': ',
                           '{0:#0{1}x}'.format(sh.get('sh_addr'), 10), ' - ',
                           '{0:#0{1}x}'.format(sh.get('sh_addr') + sh.get('sh_size') - 1, 10),
                           '\n')
        return sh_info

    def get_exec_sections(self):
        execseclist = list()
        shdrlist = self.get_section_header()
        for sh in shdrlist:
            flag = sh.get('sh_flags')
            if flag & 0x04 and flag & 0x02:
                if sh.get('sh_size') == 0:
                    continue
                execseclist.append(sh)
        return execseclist

    def get_elf_section_data(self, sectionname):
        shdrlist = self.get_section_header()
        secdata = dict()
        for sh in shdrlist:
            if 'sh_name' in sh.keys():
                name = sh.get('sh_name')
                if name == sectionname:
                    loadaddr = sh.get('sh_addr')
                    datasize = sh.get('sh_size')
                    secoff = sh.get('sh_offset')
                    secbin = self.read_at(secoff, datasize)
                    secdata[sectionname] = {'loadaddr': loadaddr, 'datasize': datasize, 'secbin': secbin}
                    break
        return secdata



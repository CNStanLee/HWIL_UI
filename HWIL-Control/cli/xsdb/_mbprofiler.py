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
import subprocess
from subprocess import PIPE
from math import log, ceil
from xsdb._utils import *
import string


class MbProfiler(object):
    def __init__(self, session):
        self.session = session
        self.profile_dict = dict()

    def mbprof_start(self):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        self.__mbprof_clear_mem()
        profile_dict['clear_mem'] = 1
        if dict_get_value_or_error_out(profile_dict, 'cumulate'):
            profile_dict['clear_mem'] = 0
        profile_dict['dirty_data'] = 1
        self.__mbprof_write('c', (profile_dict['ctrl_reg'] & 0x3F) | 0x80)

    def mbprof_gmonout(self, outfile):
        profile_dict = self.profile_dict
        nr_runs = 1
        accuracy = 1000000
        self.__mbprof_checkinit()
        freq = dict_get_value_or_error_out(profile_dict, 'freq')
        mem_words = dict_get_value_or_error_out(profile_dict, 'mem_words')
        real_low_addr = dict_get_value_or_error_out(profile_dict, 'real_low_addr')
        real_high_addr = dict_get_value_or_error_out(profile_dict, 'real_high_addr')
        cnt_instr = dict_get_value_or_error_out(profile_dict, 'cnt_instr')

        # Stop profiling before reading data
        self.__mbprof_stop()

        # Read out all profiling data (36 bits/item)
        self.__read_prof_data()
        prof_list_unscaled = profile_dict['raw_data']
        needs_accuracy = 0
        prof_list = list()
        largest = find_largest_in_list(prof_list_unscaled)
        if largest > nr_runs * 65536:
            print(f"Info: A bin has a value higher than {nr_runs * 65536}. Scaling to fit.")
            print('Info: To improve accuraccy when using command line gprof increase number of runs.')
            needs_accuracy = 1
            scaler = int((nr_runs * 65536 * accuracy) / largest)
            scaled_hertz = int(scaler * freq / accuracy)
            prof_list = list()
            for old_value in prof_list_unscaled:
                old_value = int(old_value, 16)
                new_val = hex(old_value * scaler)
                prof_list.append(new_val)
        else:
            # If we do not need to scale, the used variables still get updated to clarify code further down
            scaled_hertz = freq
            prof_list = prof_list_unscaled.copy()

        f = open(outfile, 'wb')
        # Create Header Format
        f.write('gmon'.encode())
        # Version
        f.write(to_bytes(1, 4))
        # Trailing space
        for i in range(0, 12):
            f.write(to_bytes(0))
        # Create histogram
        # 00 is Histogram
        f.write(to_bytes(0))
        # Output address range
        f.write(to_bytes(real_low_addr, 4))
        f.write(to_bytes(real_high_addr + 1, 4))
        f.write(to_bytes(mem_words, 4))
        # Output frequency in Hz
        f.write(to_bytes(scaled_hertz, 4))
        # Output dimension which uses 15 chars
        f.write('seconds'.encode())
        for i in range(0, 8):
            f.write(to_bytes(0))
        # Output abbreviation for dimension
        f.write('s'.encode())
        # Used to handle overcarry values
        cindex = list()
        cvalue = list()

        # write our values
        for i in range(0, mem_words):
            value = int(prof_list[i], 16)
            if needs_accuracy == 1:
                value = int(value / accuracy)
            # If a value is larger than 16 bits, we fill it with 0xffff and reduce it by 0xffff
            if value > 65535:
                cindex.append(i)
                cvalue.append(value - 65535)
                f.write(to_bytes(65535, 2))
            else:
                f.write(to_bytes(value, 2))

        run_count = 0
        run_append_hist = 1
        # If a single value > 0xFFFF we need to append several new histograms with the difference
        # We only do this a maximum of $run_count times to stop infinite loops and keep filesize reasonable
        while run_append_hist != 0 and run_count < nr_runs and len(cindex) > 0 and len(cvalue) > 0:
            run_count = run_count + 1
            # Unless there is further carry over this is the last time we run the while loop
            run_append_hist = 0

            # Create histogram
            # 00 is Histogram
            f.write(to_bytes(0))
            # Output address range
            f.write(to_bytes(real_low_addr, 4))
            f.write(to_bytes(real_high_addr + 1, 4))
            f.write(to_bytes(mem_words, 4))

            # Output frequency in Hz
            f.write(to_bytes(scaled_hertz, 4))
            # Output dimension which uses 15 chars
            f.write('seconds'.encode())
            for i in range(0, 8):
                f.write(to_bytes(0))
            # Output abbreviation for dimension
            f.write('s'.encode())
            # Output the profiling data
            for i in range(0, mem_words):
                idx = 0 if i in cindex else -1
                # If the adress hasn't carried over, we keep it at 0x0000
                if idx == -1:
                    f.write(to_bytes(0, 2))
                else:
                    if cvalue[idx] > 65535:
                        # There is further carry over, and we need to append another histogram
                        f.write(to_bytes(65535, 2))
                        run_append_hist = 1
                        cvalue[idx] = cvalue[idx] - 65535
                    else:
                        # This is last time address carried over, therefore we delete the elements from our lists
                        f.write(to_bytes(cvalue[idx], 2))
                        del (cvalue[idx])
                        del (cindex[idx])
        f.close()

    def mbprof_disassembly_annotate(self, filename, usetime=1, source=1):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        elf_file = profile_dict['elf'] if 'elf' in profile_dict else ''
        mem_words = dict_get_value_or_error_out(profile_dict, 'mem_words')
        low_addr = dict_get_value_or_error_out(profile_dict, 'low_addr')
        high_addr = dict_get_value_or_error_out(profile_dict, 'high_addr')
        real_low_addr = dict_get_value_or_error_out(profile_dict, 'real_low_addr')
        profiler_bin = dict_get_value_or_error_out(profile_dict, 'profiler_bin')
        cnt_instr = dict_get_value_or_error_out(profile_dict, 'cnt_instr')
        freq = dict_get_value_or_error_out(profile_dict, 'freq')

        dump_opt = '-S' if source == 1 else '-d'
        if elf_file == '':
            raise Exception('elf-file is undefined') from None
        p = subprocess.run([f'mb-objdump {dump_opt} {elf_file}'], shell=True, stdout=PIPE, stderr=PIPE)
        err = p.stderr.decode()
        if err:
            raise Exception("mb-objdump returned with error code")
        dis_line = p.stdout.decode().split("\n")
        f = open(filename, 'w')

        # Must stop profiling in order to read data
        self.__mbprof_stop()
        self.__read_prof_data()
        raw_data = profile_dict['raw_data']
        data = list()
        pc_data = list()
        total = 0
        for i in range(0, mem_words):
            val = int(raw_data[i], 16)
            total = total + val
            firstaddr = hex(real_low_addr + i * (1 << profiler_bin) * 4)
            secondaddr = hex(real_low_addr + (i + 1) * (1 << profiler_bin) * 4 - 4)
            dataitem = [firstaddr, secondaddr, val]
            data.append(dataitem)
            pc_data.append(firstaddr)

        nsec_per_clock = 1.0E9 / freq
        for line in dis_line:
            temp = line.split(':')[0].strip()
            if len(temp) and all(c in string.hexdigits for c in temp) is True:
                pcaddr = int(f'0x{temp}', 16)
                if low_addr <= pcaddr <= high_addr:
                    found = 1 if hex(pcaddr) in pc_data else 0
                    if found == 1:
                        index = [i for i, x in enumerate(pc_data) if x == hex(pcaddr)][0]
                        value = data[index][2]
                        if usetime == 0:
                            f.write('{:12d}'.format(value))
                        else:
                            exectime = nsec_per_clock * value
                            if exectime < 1000.0:
                                f.write(f'{"{:07.3f}".format(exectime)} ns  ')
                            elif exectime < 1000000.0:
                                f.write(f'{"{:07.3f}".format(exectime / 1000.0)} us  ')
                            elif exectime < 1000000000.0:
                                f.write(f'{"{:07.3f}".format(exectime / 1000000.0)} ms  ')
                            else:
                                f.write(f'{"{:07.3f}".format(exectime / 1000000000.0)} s   ')
                    else:
                        pcrangeaddr = pcaddr & ~(((1 << profiler_bin) * 4) - 1)
                        pcrangeaddr_found = 1 if hex(pcrangeaddr) in pc_data else 0
                        f.write("||          ") if pcrangeaddr_found == 1 else f.write("            ")
                    f.writelines(line + '\n')
                else:
                    # outside profiling address range, just copy the line
                    f.writelines(line + '\n')
            else:
                # no pc address so just copy the line
                f.writelines(line + '\n')

        if cnt_instr == 0:
            millisec_scale = int(freq / 1000)
            freq_mhz = int(freq / 1000000)
            exec_time = int(total / millisec_scale)
            print(f'Total cycles {total} - Total execution time {exec_time} msec at {freq_mhz} MHz')
        else:
            print(f'Total instructions: {total}')
        f.close()

    def mbprof_set_config(self, mb_profile_config):
        self.profile_dict = mb_profile_config

    def mbprof_init(self, props):
        profile_dict = self.profile_dict
        profile_dict['bscan'] = ''
        if 'JtagChain' in props:
            profile_dict['bscan'] = props['JtagChain'][4:]
        if 'MBCore' in props and props['MBCore'] >= 0:
            profile_dict['which'] = props['MBCore']
        else:
            raise Exception('Invalid target. Only supported for MicroBlaze targets') from None
        profile_dict['mdmaddr'] = ''
        if 'MDMAddr' in props:
            profile_dict['mdmaddr'] = props['MDMAddr']
        profile_dict['mdmconfig'] = props['MDMConfig']
        # Determine MDM property: dbg_ports
        config_mdm = profile_dict['mdmconfig'] & 0xffffffff
        config_mdm_mb_dbg_ports = (((config_mdm >> 8) & 0xFF) > 1)  # TODO check why > 1
        profile_dict['dbg_ports'] = config_mdm_mb_dbg_ports

        # Configuration Register Read
        config_extended_debug = self.__mb_get_config(161)
        config_profile_size = self.__mb_get_config(272, 274)
        config_addr_size = self.__mb_get_config(276, 281)
        config_data_size_64 = self.__mb_get_config(282)

        if config_extended_debug == 0:
            raise Exception('Profiling is not enabled in the design. Enable Extended Debug in '
                            'MicroBlaze configuration') from None
        elif config_profile_size == 0:
            raise Exception('Profiling is not enabled in the design. Set Profile Size in '
                            'MicroBlaze configuration') from None
        else:
            mem_bits = config_profile_size + 9
            mem_words = 1 << mem_bits
            addr_bits = config_addr_size + 32 if config_data_size_64 else 32
            profile_dict['mem_bits'] = mem_bits
            profile_dict['mem_words'] = mem_words
            profile_dict['addr_bits'] = addr_bits
            profile_dict['init_done'] = 1
            profile_dict['ctrl_reg'] = 0
            profile_dict['clear_mem'] = 1
            if dict_get_value_or_error_out(profile_dict, 'cumulate'):
                profile_dict['clear_mem'] = 0
            self.__mbprof_clear_mem()
            self.__mbprof_set()

    def __mbprof_set(self):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        low_addr = dict_get_value_or_error_out(profile_dict, 'low_addr')
        high_addr = dict_get_value_or_error_out(profile_dict, 'high_addr')
        mem_words = dict_get_value_or_error_out(profile_dict, 'mem_words')
        cnt_instr = dict_get_value_or_error_out(profile_dict, 'cnt_instr')
        use_cycles = 0
        if low_addr >= high_addr:
            raise Exception('High address cannot be same or smaller than low address') from None
        profile_dict['dirty_data'] = 1
        offset = int((high_addr - low_addr + ((4 * mem_words) - 1)) / (4 * mem_words))
        bindata = int(ceil(log(offset) / log(2)))
        mem_add_bits = 2 + int(ceil(log(mem_words) / log(2)))

        # Need to calculate the actual low_addr that plist will be using for
        # getting correct offsets into the BRAM
        if bindata > 20:
            real_low_addr = 0
            real_low_addrmask = 0xffffffff
        else:
            real_low_addrmask = (1 << (mem_add_bits + bindata)) - 1
            real_low_addr = low_addr & ~real_low_addrmask
            # Need to detect if there is a rounding error if low addr start very close to end of offset
            while (real_low_addr + (mem_words * (1 << bindata) * 4)) < high_addr:
                bindata = bindata + 1
                real_low_addrmask = (1 << (mem_add_bits + bindata)) - 1
                real_low_addr = low_addr & ~real_low_addrmask
        profile_dict['profiler_bin'] = bindata
        self.__mbprof_write('l', low_addr)
        self.__mbprof_write('h', high_addr)
        if cnt_instr == 0:
            use_cycles = 1
        self.__mbprof_write('c', ((bindata & 0x1f) + (use_cycles << 5)))
        real_high_addr = real_low_addr + real_low_addrmask
        binsize = 1 << bindata
        if cnt_instr == 0:
            print(f'Profiler: \n\tFull range  = {"{0:#0{1}x}".format(real_low_addr, 10)}-'
                  f'{"{0:#0{1}x}".format(real_high_addr, 10)}\n\tTrace range = {"{0:#0{1}x}".format(low_addr, 10)}-'
                  f'{"{0:#0{1}x}".format(high_addr, 10)}\n\tBin size    = {binsize} instructions\n\tCounting Cycles')
        else:
            print(f'Profiler: \n\tFull range  = {"{0:#0{1}x}".format(real_low_addr, 10)}-'
                  f'{"{0:#0{1}x}".format(real_high_addr, 10)}\n\tTrace range = {"{0:#0{1}x}".format(low_addr, 10)}-'
                  f'{"{0:#0{1}x}".format(high_addr, 10)}\n\tBin size    = {binsize} instructions\n\tCounting '
                  f'Instructions')
        profile_dict['real_low_addr'] = real_low_addr
        profile_dict['real_high_addr'] = real_high_addr

    def __mbprof_clear_mem(self):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        if 'clear_mem' in profile_dict and profile_dict['clear_mem'] == 0:
            return
        # Must stop profiling in order to write data
        self.__mbprof_write('c', ((dict_get_value_or_error_out(profile_dict, 'ctrl_reg') & 0x3F) | 0x40))

        # Set ram to 0
        self.__mbprof_write('b', 0)

        mdmaddr = profile_dict['mdmaddr'] if 'mdmaddr' in profile_dict else ''
        mem_words = dict_get_value_or_error_out(profile_dict, 'mem_words')
        if mdmaddr == '':
            bscan = dict_get_value_or_error_out(profile_dict, 'bscan')
            dbg_ports = dict_get_value_or_error_out(profile_dict, 'dbg_ports')
            which = dict_get_value_or_error_out(profile_dict, 'which')
            command = 0x77
            length = 32
            res = to_bits(0x0, length)
            if self.session.cur_jtag_target is None:
                raise Exception("Select jtag target using jtag_targets command.")
            jtag_tgt = self.session.cur_jtag_target.id
            jt = self.session.jtag_targets(jtag_tgt)
            jseq = jt.sequence()
            jseq.irshift(state='IRUPDATE', register='bypass')
            jseq.irshift(state='IDLE', register=f'user{bscan}')
            jseq.drshift(state="DRUPDATE", bit_len=4, data=1)
            if dbg_ports > 1:
                length = dbg_ports if dbg_ports > 8 else 8
                jseq.drshift(state="DRUPDATE", bit_len=8, data=0x0D)
                jseq.drshift(state="DRUPDATE", bit_len=length, data=1 << which)
            for i in range(0, mem_words - 1):
                jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
                jseq.drshift(state="DRUPDATE", bit_len=length, data=res)
            jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
            jseq.drshift(state="IDLE", bit_len=length, data=res)
            jseq.run()
            jseq.clear()
            del jseq
        else:
            for i in range(0, mem_words):
                self.session.mwr(mdmaddr + 0x5DC0, 0)
        profile_dict['clear_mem'] = 0

    def __mbprof_write(self, reg: str, value=0):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        if reg.startswith('c'):
            # control register
            self.__mb_prof_write_control(value)
            profile_dict['ctrl_reg'] = value
        if reg.startswith('l'):
            # profiling low address register
            addr_bits = dict_get_value_or_error_out(profile_dict, 'addr_bits')
            self.__mb_prof_write_low_addr(value >> 2, addr_bits - 2)
        if reg.startswith('h'):
            # profiling high address register
            addr_bits = dict_get_value_or_error_out(profile_dict, 'addr_bits')
            self.__mb_prof_write_high_addr(value >> 2, addr_bits - 2)
        if reg.startswith('b'):
            # profiling buffer address register
            self.__mb_prof_write_buf_addr(value, dict_get_value_or_error_out(profile_dict, 'mem_bits'))

    def __mb_prof_write_control(self, value):
        mdmaddr = self.profile_dict['mdmaddr'] if 'mdmaddr' in self.profile_dict else ''
        if mdmaddr == '':
            bscan = self.profile_dict['bscan']
            which = self.profile_dict['which']
            self.session.mb_drwr(0x71, value, 8, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5C40, value)

    def __mb_prof_write_buf_addr(self, value, length=16):
        mdmaddr = self.profile_dict['mdmaddr'] if 'mdmaddr' in self.profile_dict else ''
        if mdmaddr == '':
            bscan = self.profile_dict['bscan']
            which = self.profile_dict['which']
            self.session.mb_drwr(0x74, value, length, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5D00, value)

    def __mb_prof_write_low_addr(self, value, length=30):
        mdmaddr = self.profile_dict['mdmaddr'] if 'mdmaddr' in self.profile_dict else ''
        if mdmaddr == '':
            bscan = self.profile_dict['bscan']
            which = self.profile_dict['which']
            self.session.mb_drwr(0x72, value, length, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5C80, value & 0x7FFFFFFF)
            if length > 30:
                self.session.mwr(mdmaddr + 0x5C84, value >> 30)

    def __mb_prof_write_high_addr(self, value, length=30):
        mdmaddr = self.profile_dict['mdmaddr'] if 'mdmaddr' in self.profile_dict else ''
        if mdmaddr == '':
            bscan = self.profile_dict['bscan']
            which = self.profile_dict['which']
            self.session.mb_drwr(0x73, value, length, user=bscan, which=which)
        else:
            self.session.mwr(mdmaddr + 0x5CC0, value & 0x7FFFFFFF)
            if length > 30:
                self.session.mwr(mdmaddr + 0x5CC4, value >> 30)

    def __mbprof_checkinit(self):
        if 'init_done' in self.profile_dict and self.profile_dict['init_done'] == 1:
            return 1
        raise Exception('Profiling not configured, please configure using command mbprofile') from None

    def __mb_get_config(self, frm, to=-1):
        profile_dict = self.profile_dict
        if to == -1:
            to = frm
        mdmaddr = profile_dict['mdmaddr'] if 'mdmaddr' in profile_dict else ''
        if mdmaddr == '':
            bscan = dict_get_value_or_error_out(profile_dict, 'bscan')
            which = dict_get_value_or_error_out(profile_dict, 'which')
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

    def __mbprof_stop(self):
        profile_dict = self.profile_dict
        self.__mbprof_checkinit()
        self.__mbprof_write('c', ((dict_get_value_or_error_out(profile_dict, 'ctrl_reg') & 0x3F) | 0x40))

    def __read_prof_data(self):
        profile_dict = self.profile_dict
        dirty_data = dict_get_value_or_error_out(profile_dict, 'dirty_data')
        if dirty_data == 0:
            return dict_get_safe(profile_dict, 'raw_data')  # TODO check if raw_data is initialized somewhere
        else:
            self.__mbprof_write('b', 0)
            prof_list_raw = list()
            mdmaddr = profile_dict['mdmaddr'] if 'mdmaddr' in profile_dict else ''
            mem_words = dict_get_value_or_error_out(profile_dict, 'mem_words')
            if mdmaddr == '':
                bscan = dict_get_value_or_error_out(profile_dict, 'bscan')
                dbg_ports = dict_get_value_or_error_out(profile_dict, 'dbg_ports')
                which = dict_get_value_or_error_out(profile_dict, 'which')
                command = 0x76
                length = 36
                if self.session.cur_jtag_target is None:
                    raise Exception("Select jtag target using jtag_targets command.")
                jtag_tgt = self.session.cur_jtag_target.id
                jt = self.session.jtag_targets(jtag_tgt)
                jseq = jt.sequence()
                jseq.irshift(state='IRUPDATE', register='bypass')
                jseq.irshift(state='IDLE', register=f'user{bscan}')
                jseq.drshift(state="DRUPDATE", bit_len=4, data=0x1)
                if dbg_ports > 1:
                    length = dbg_ports if dbg_ports > 8 else 8
                    jseq.drshift(state="DRUPDATE", bit_len=8, data=0x0D)
                    jseq.drshift(state="DRUPDATE", bit_len=length, data=1 << which)
                for i in range(0, mem_words - 1):
                    jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
                    jseq.drshift(capture=True, state="DRUPDATE", bit_len=length, tdi=0)
                jseq.drshift(state="DRUPDATE", bit_len=8, data=command)
                jseq.drshift(capture=True, state="IDLE", tdi=0, bit_len=length)
                res = jseq.run('--bits')
                jseq.clear()
                del jseq
                for r in res:
                    r = "{0:#0{1}x}".format(int(r, 2), int(ceil(length / 4)) + 2)
                    prof_list_raw.append(r)
            else:
                for i in range(0, mem_words):
                    datalow = self.session.mrd('-v', mdmaddr + 0x5D80)
                    datahigh = self.session.mrd('-v', mdmaddr + 0x5D84)
                    val = (datahigh << 32) | datalow
                    prof_list_raw.append("{0:#0{1}x}".format(val, 11))

            profile_dict['raw_data'] = prof_list_raw
            profile_dict['dirty_data'] = 0

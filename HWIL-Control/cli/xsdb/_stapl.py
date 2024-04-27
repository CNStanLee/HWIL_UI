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
import time

from tcf.services import svf as svf_service
from xsdb._tcf_stapl import TcfStapl
from xsdb._tcf_xicom import TcfXicom
from xsdb._tcf_svf import TcfSVF
from xsdb._utils import *


class Stapl(object):
    def __init__(self, chan, session):
        self.session = session
        self.channel = chan
        self.__stapltable = {}
        self.__tcf_stapl = TcfStapl(session)
        self.__tcf_xicom = TcfXicom(session)
        self.__tcf_svf = TcfSVF(session)

        # The Following Table (__crc_ccitt_table) is generated from https://pycrc.org/ with the following options
        # crc = Crc(width=16, poly=0x1021, reflect_in=True, xor_in=0x8408, reflect_out=True, xor_out=0x0000)
        # crc_table = crc.gen_table()[0]
        self.__crc_ccitt_table = \
            [0, 4489, 8978, 12955, 17956, 22445, 25910, 29887, 35912, 40385, 44890, 48851, 51820, 56293, 59774, 63735,
             4225, 264, 13203, 8730, 22181, 18220, 30135, 25662, 40137, 36160, 49115, 44626, 56045, 52068, 63999, 59510,
             8450, 12427, 528, 5017, 26406, 30383, 17460, 21949, 44362, 48323, 36440, 40913, 60270, 64231, 51324, 55797,
             12675, 8202, 4753, 792, 30631, 26158, 21685, 17724, 48587, 44098, 40665, 36688, 64495, 60006, 55549, 51572,
             16900, 21389, 24854, 28831, 1056, 5545, 10034, 14011, 52812, 57285, 60766, 64727, 34920, 39393, 43898,
             47859, 21125, 17164, 29079, 24606, 5281, 1320, 14259, 9786, 57037, 53060, 64991, 60502, 39145, 35168,
             48123, 43634, 25350, 29327, 16404, 20893, 9506, 13483, 1584, 6073, 61262, 65223, 52316, 56789, 43370,
             47331, 35448, 39921, 29575, 25102, 20629, 16668, 13731, 9258, 5809, 1848, 65487, 60998, 56541, 52564,
             47595, 43106, 39673, 35696, 33800, 38273, 42778, 46739, 49708, 54181, 57662, 61623, 2112, 6601, 11090,
             15067, 20068, 24557, 28022, 31999, 38025, 34048, 47003, 42514, 53933, 49956, 61887, 57398, 6337, 2376,
             15315, 10842, 24293, 20332, 32247, 27774, 42250, 46211, 34328, 38801, 58158, 62119, 49212, 53685, 10562,
             14539, 2640, 7129, 28518, 32495, 19572, 24061, 46475, 41986, 38553, 34576, 62383, 57894, 53437, 49460,
             14787, 10314, 6865, 2904, 32743, 28270, 23797, 19836, 50700, 55173, 58654, 62615, 32808, 37281, 41786,
             45747, 19012, 23501, 26966, 30943, 3168, 7657, 12146, 16123, 54925, 50948, 62879, 58390, 37033, 33056,
             46011, 41522, 23237, 19276, 31191, 26718, 7393, 3432, 16371, 11898, 59150, 63111, 50204, 54677, 41258,
             45219, 33336, 37809, 27462, 31439, 18516, 23005, 11618, 15595, 3696, 8185, 63375, 58886, 54429, 50452,
             45483, 40994, 37561, 33584, 31687, 27214, 22741, 18780, 15843, 11370, 7921, 3960]

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(Stapl) if callable(getattr(Stapl, method)) if
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

    def config(self, *args, **kwargs):
        """
config:
    Configure stapl target.

Prototype:
    stapl_target.config(self, **kwargs)
        Create a hw_target (jtag chain) and add all the hw_devices given in
        the scan-chain list to the hw_target. It also configures the stapl
        output file where the stapl data is recorded.

Arguments:

    :param kwargs:
        out=<filepath>
        Output file path. Only one of the -out and -handle options should be
        used. If the -out option is provided, the file will be explicitly opened
        in w+b mode.

        handle=<filehandle>
        File handle returned by open command for output. Only one of the
        -out and -handle options should be used.

        scan_chain=<list-of-dicts>
        List of devices in the scan-chain. Each list element must be a dict of
        device properties in the format {name <string> idcode <int> irlen <int>
        idcode2 <int> mask <int>}. For example:
            scan_chain=[{'name': 'xcvc1902'}, {'name': 'xcvm1802'}]
        The order of devices specified with scan-chain option should match the
        order of devices on the physical hardware where the stapl file is played
        back.
        Only one of the scan_chain and part options should be used.

        part=<device-name list>
        List of part names of the Xilinx devices to add to the scan-chain.
        This option works only with Xilinx devices. This option can be
        used instead of the -scan-chain option.

Note:
    For Xilinx devices, if the device_name or idcode is specified in the
    scan-chain information, the other parameters are optional. All the JTAG
    TAPs are added automatically to the scan-chain for Xilinx devices.

Returns:
    None

Examples:
    This example demonstrates the correct order of creating a stapl file
    for a single device on a stapl target.
        st = self.session.stapl()
        st.config(out="xsdpy_tests/data/pystapl.stapl",
            scan_chain=[{'name': 'xcvc1902'}])
        self.session.targets('-s', filter='jtag_device_name == xcvc1902')
        self.session.jtag_targets('-s', filter='name == xcvc1902')
        st.start()
        self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        st.stop()
    This example demonstrates the correct order of creating a stapl file
    for multiple devices on a stapl target.
        st = self.session.stapl()
        st.config(out="xsdpy_tests/data/pystapl.stapl",
            part=['xcvc1902', 'xcvm1802'])
        self.session.targets('-s', filter='jtag_device_name == xcvc1902')
        self.session.jtag_targets('-s', filter='name == xcvc1902')
        st.start()
        self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        self.session.targets('-s', filter='jtag_device_name == xcvm1802')
        self.session.jtag_targets('-s', filter='name == xcvm1802')
        st.start()
        self.session.device_program("xsdpy_tests/elfs/versal/vck190.pdi")
        st.stop()

Interactive mode examples:
    stapl config -out xsdb.stapl -part [xcvc1902, xcvm1802]
    stapl config -out "pystapl.stapl" -scan_chain [{'name': 'xcvc1902'}, {'name': 'xcvm1802'}]
        """

        parser = argparse.ArgumentParser(description='Jtag terminal options')
        parser.add_argument('-c', '--checksum', action='store_true', help='Calculates checksum of stapl file')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        self.__stapltable['checksum'] = 1 if parsed_args.checksum is True else 0

        if (('scan_chain' in kwargs and 'part' in kwargs) or ('scan_chain' not in kwargs and 'part' not in kwargs) or
                ('handle' in kwargs and 'out' in kwargs) or ('handle' not in kwargs and 'out' not in kwargs)):
            raise Exception('Invalid arguments, specify -scan-chain/-part and -handle/-out options.') from None

        if 'scan_chain' in kwargs:
            devices = kwargs.get('scan_chain')
            if not isinstance(devices, list):
                raise Exception('\'scan_chain\' must be sent in list of dicts format.') from None
            for dev in devices:
                if not isinstance(dev, dict):
                    raise Exception('\'scan_chain\' must be sent in list of dicts format.') from None
                if 'name' not in dev and 'idcode' not in dev:
                    raise Exception('Missing device parameters, specify name or idcode for all devices') from None

        if 'out' in kwargs:
            self.__stapltable.update({'out': kwargs.pop('out')})
        else:
            self.__stapltable.update({'handle': kwargs.pop('handle')})

        tgt = 'target' + '{0:>03s}'.format(self.session.curchan.split("#")[1])
        exec_in_dispatch_thread(self.__tcf_svf.add_target, tgt)
        tgt_ctx = list(self.session.jtag_targets('-t', filter=f"name == Xilinx Null Cable {tgt}").keys())[0]
        devices = list()
        scan_chain = 0
        if 'scan_chain' in kwargs:
            devices = kwargs.pop('scan_chain')
            scan_chain = 1
        elif 'part' in kwargs:
            devices = kwargs.pop('part')
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if not isinstance(devices, list):
            raise Exception('\'part\' must be in the list format.') from None
        if scan_chain == 1:
            for dev in devices:
                if 'name' in dev:
                    if 'idcode' not in dev:
                        dev['idcode'] = 0
                else:
                    dev['name'] = ''
                if 'irlen' not in dev:
                    dev['irlen'] = 0
                if 'idcode2' not in dev:
                    dev['idcode2'] = 0
                if 'mask' not in dev:
                    dev['mask'] = 0
                exec_in_dispatch_thread(self.__tcf_svf.add_device, tgt_ctx, dev['name'], dev['idcode'], dev['irlen'],
                                        dev['idcode2'], dev['mask'])

        else:
            for device in devices:
                exec_in_dispatch_thread(self.__tcf_svf.add_device, tgt_ctx, device, 0, 0, 0, 0)

    add_function_metadata('stapl config', 'Configure stapl target.', 'stapl', 'Stapl')

    def start(self):
        """
start:
    start stapl recording.

Prototype:
    stapl.start()
        start stapl recording.

Note:
    It is mandatory to call 'stapl start' before each 'device program', and
    'stapl stop' after programming all devices to generate stapl data properly.

Returns:
    None

Example:
    stapl.start()

Interactive mode examples:
    stapl start
        """

        if len(self.__stapltable) == 0:
            raise Exception('Run stapl config prior to this command.') from None
        if 'out' in self.__stapltable and 'handle' not in self.__stapltable:
            self.__stapltable['handle'] = open(self.__stapltable['out'], "w+b")
        self.__stapltable['done'] = 0
        if self.session.cur_jtag_target is None:
            raise Exception('Please select the jtag target using \'jtag_targets command\'.') from None
        exec_in_dispatch_thread(self.__tcf_stapl.stapl_start, self.session.cur_jtag_target.ctx)
        self.__stapltable['started'] = 1
        exec_in_dispatch_thread(self.__tcf_xicom.xicom_config_reset, self.session.cur_jtag_target.ctx, {})

    add_function_metadata('stapl start', 'start stapl recording.', 'stapl', 'Stapl')

    def stop(self):
        """
stop:
    stop stapl recording.

Prototype:
    stapl.stop()
        stop stapl recording.

Note:
    It is mandatory to call 'stapl start' before each 'device program', and
    'stapl stop' after programming all devices to generate stapl data properly.

Returns:
    None

Example:
    stapl.stop()

Interactive mode examples:
    stapl stop
        """

        if len(self.__stapltable) == 0:
            raise Exception('Run stapl config prior to this command.') from None
        if 'started' not in self.__stapltable or self.__stapltable['started'] == 0:
            raise Exception('Run stapl start prior to this command.') from None
        self.__stapltable['started'] = 0
        exec_in_dispatch_thread(self.__tcf_stapl.stapl_stop, self.session.cur_jtag_target.ctx)
        exec_in_dispatch_thread(self.__tcf_stapl.stapl_close, self.session.cur_jtag_target.ctx)
        while self.__stapltable['done'] == 0:
            time.sleep(0.05)
        if 'out' in self.__stapltable:
            self.__stapltable['handle'].close()

    add_function_metadata('stapl stop', 'stop stapl recording.', 'stapl', 'Stapl')

    def on_stapl_data_event(self, size, data):
        handle = self.__stapltable['handle']
        if handle is not None:
            handle.seek(0, 2)
            handle.write(data)

    def crc16_ccitt(self, data):
        crc = 0xFFFF
        for in_byte in data:
            if in_byte != '\r':
                crc = (self.__crc_ccitt_table[(crc ^ ord(in_byte)) & 0xFF] ^ (crc >> 8)) & 0xFFFF
        return ~crc & 0xFFFF

    def on_stapl_notes_event(self, size, data):
        handle = self.__stapltable['handle']
        if handle is not None:
            handle.seek(0, 0)
            content = handle.read()
            data += content
            handle.seek(0, 0)
            handle.write(data)
            if self.__stapltable['checksum'] == 1:
                crc_field = 'CRC ' + '{0:0{1}x}'.format(self.crc16_ccitt(data.decode()), 4) + ';'
            else:
                crc_field = 'CRC 0;'
            handle.write(crc_field.encode())
            self.__stapltable['done'] = 1

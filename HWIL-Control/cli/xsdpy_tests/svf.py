import xsdb
import os

core = 0
apu_reset_a53 = ['0x380e', '0x340d', '0x2c0b', '0x1c07']

session = xsdb.start_debug_session()
svf = session.svf()
with open('/tmp/output.svf', 'w') as fp:
    pass
with open('/tmp/fsbl_hello.svf', 'w') as fp:
    pass
svf.config('--linkdap', device_index = 1, out = '/tmp/output.svf', scan_chain = ['0x14738093','12', '0x5ba00477','4'])
svf.generate()
svf.config('--linkdap', cpu_index = core, delay = 10,out = '/tmp/fsbl_hello.svf', scan_chain = ['0x14738093', '12', '0x5ba00477', '4'])
svf.mwr(addr = '0xffff0000', val = '0x14000000')
svf.mwr(addr = '0xfd1a0104', val = apu_reset_a53[core])
svf.stop()
dir_path = os.path.dirname(os.path.realpath(__file__))
svf.dow(elf = dir_path+"/elf/fsbl_a53.elf")
svf.con()
svf.delay(tcks = 100000)
svf.stop()
svf.dow(elf = dir_path+"/elf/hello_a53.elf")
svf.con()
svf.generate()
print('Generated svf files /tmp/output.svf and /tmp/fsbl_hello.svf ')
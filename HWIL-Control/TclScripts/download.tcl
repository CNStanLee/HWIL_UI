connect -url tcp:127.0.0.1:3121
targets -set -filter {jtag_cable_name =~ "Digilent Nexys Video 210276B81712B" && level==0 && jtag_device_ctx=="jsn-Nexys Video-210276B81712B-13636093-0"}
#fpga -file /home/lic9/workspace/mb0_ctr_node/_ide/bitstream/bd1_wrapper.bit
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
loadhw -hw /home/lic9/workspace/nvb1/export/nvb1/hw/bd1_wrapper.xsa -regs
configparams mdm-detect-bscan-mask 2
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
rst -system
after 3000
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
dow TclScripts/DestCode/mb_dos_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#4" && bscan=="USER2" }
dow TclScripts/DestCode/mb_finn_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#0" && bscan=="USER2" }
dow TclScripts/DestCode/mb0_ctr_node.elf
targets -set -nocase -filter {name =~ "*microblaze*#1" && bscan=="USER2" }
dow TclScripts/DestCode/mb1_ecu1_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#2" && bscan=="USER2" }
dow TclScripts/DestCode/mb2_ecu2_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#3" && bscan=="USER2" }
dow TclScripts/DestCode/mb3_ecu3_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
con
targets -set -nocase -filter {name =~ "*microblaze*#4" && bscan=="USER2" }
con
targets -set -nocase -filter {name =~ "*microblaze*#0" && bscan=="USER2" }
con
targets -set -nocase -filter {name =~ "*microblaze*#1" && bscan=="USER2" }
con
targets -set -nocase -filter {name =~ "*microblaze*#2" && bscan=="USER2" }
con
targets -set -nocase -filter {name =~ "*microblaze*#3" && bscan=="USER2" }
con
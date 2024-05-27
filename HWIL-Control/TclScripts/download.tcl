connect -url tcp:127.0.0.1:3121
configparams mdm-detect-bscan-mask 2
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
rst -system
after 1000
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
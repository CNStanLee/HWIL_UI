connect -url tcp:127.0.0.1:3121
configparams mdm-detect-bscan-mask 2
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
rst -system
after 1000
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
dow TclScripts/DestCode/dos.elf
targets -set -nocase -filter {name =~ "*microblaze*#4" && bscan=="USER2" }
dow TclScripts/DestCode/finn.elf
targets -set -nocase -filter {name =~ "*microblaze*#0" && bscan=="USER2" }
dow TclScripts/DestCode/hwil_app.elf
targets -set -nocase -filter {name =~ "*microblaze*#1" && bscan=="USER2" }
dow TclScripts/DestCode/ecu1.elf
targets -set -nocase -filter {name =~ "*microblaze*#2" && bscan=="USER2" }
dow TclScripts/DestCode/ecu2.elf
targets -set -nocase -filter {name =~ "*microblaze*#3" && bscan=="USER2" }
dow TclScripts/DestCode/ecu3.elf
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
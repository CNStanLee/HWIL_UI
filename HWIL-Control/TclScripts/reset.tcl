connect -url tcp:127.0.0.1:3121
configparams mdm-detect-bscan-mask 2
after 100
targets -set -nocase -filter {name =~ "*microblaze*#0" && bscan=="USER2" }
rst
targets -set -nocase -filter {name =~ "*microblaze*#1" && bscan=="USER2" }
rst
targets -set -nocase -filter {name =~ "*microblaze*#2" && bscan=="USER2" }
rst
targets -set -nocase -filter {name =~ "*microblaze*#3" && bscan=="USER2" }
rst
targets -set -nocase -filter {name =~ "*microblaze*#4" && bscan=="USER2" }
rst
targets -set -nocase -filter {name =~ "*microblaze*#5" && bscan=="USER2" }
rst
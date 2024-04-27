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
import os
import socket
import sys
import threading
import time


def recv_thread(s):
    while True:
        data = s.recv(4096).decode()
        if data == 'xsdb_exit':
            s.close()
            os.system('kill %d' % os.getpid())
            sys.exit(1)
        print(data, end='')


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])
s.connect(('localhost', port))
threading.Thread(target=recv_thread, name="async_thread", args=(s,), daemon=True).start()

for line in sys.stdin:
    if 'terminal_exit' == line.rstrip():
        s.send(line.encode())
        time.sleep(0.2)
        s.close()
        sys.exit()
    s.send(line.encode())
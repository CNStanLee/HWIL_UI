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

port = int(sys.argv[1])
code_block = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', port))

if code_block == 1:
    def recv_thread(s):
        while True:
            data = s.recv(4096).decode()
            if data == 'xsdb_exit':
                s.close()
                os.system('kill %d' % os.getpid())
                sys.exit(1)
            print(data, end='')

    print("JTAG-based Hyperterminal.\n"
          f"Connected to JTAG-based Hyperterminal over TCP port : {port}\n"
          f"(using socket : {s})\n"
          "Help :\n"
          "Terminal requirements :\n"
          "  (i) Processor's STDOUT is redirected to the ARM DCC/MDM UART\n"
          "  (ii) Processor's STDIN is redirected to the ARM DCC/MDM UART.\n"
          "       Then, text input from this console will be sent to DCC/MDM's UART port.\n"
          "   NOTE: This is a line-buffered console and you have to press \"Enter\"\n"
          "      to send a string of characters to DCC/MDM.\n")

    threading.Thread(target=recv_thread, name="recv_thread", args=(s,), daemon=True).start()

    for line in sys.stdin:
        s.send(line.encode())
        if 'terminal_exit' == line.rstrip():
            time.sleep(0.2)
            s.close()
            sys.exit()

else:
    s.send('terminal_exit\n'.encode())
    time.sleep(0.2)
    s.close()

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

import time
import os
from tkinter import *

interp = None
running = False

def cmd(c: str):
    global interp
    r = interp.eval(c)
    # HACK: update() should be called from background thread, but tkinter can be
    # used only from main thread. mtTkinter supports multiple threds but it's
    # licensed under LGPL, which is not compatible with proprietary license :(
    # update() can only process the immediate events resulting from the command,
    # but not other background events (for example, core stopped because of a
    # breakpoint)
    interp.update()
    return r

def start():
    global running
    global interp

    if (running == True):
        return

    env = os.getenv("MYVIVADO")
    if env == None:
        env = os.getenv("XILINX_VITIS")
    if env == None:
        raise Exception("Cannot load XSDB packages, XILINX_VITIS is not set") from None
    try:
        interp = Tcl()
        path = env + '/scripts/xsdb'
        interp.eval(f'lappend ::auto_path {path}')
        # TODO: Set this flag only in interactive mode
        interp.eval('set ::tcl_interactive 1')
        interp.eval('package require tcf')
        interp.eval('package require xsdb')
        interp.eval('namespace import ::xsdb::*')
    except Exception as e:
        raise Exception(f"Cannot load XSDB packages, " + str(e)) from None
    running = True

def stop():
    global running

    if running == False:
        return
    running = False

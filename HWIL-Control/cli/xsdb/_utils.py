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

# !/usr/bin/env python3
import sys
import tkinter
import threading
import struct
from tcf import protocol, channel
from typing import List

function_metadata = {}


class SyncRequest(object):
    def __init__(self):
        self.cond = threading.Condition()
        self.error = None
        self.result = None

    def done(self, error=None, result=None):
        self.error = error
        self.result = result
        with self.cond:
            self.cond.notify()


class Runnable(object):
    def __init__(self, callable_function, arg=None):
        self.callable = callable_function
        self.arg = arg
        self.sync = SyncRequest()

    def __call__(self):
        return self.callable(self)


def flatten(t):
    return [item for sublist in t for item in sublist]


def words_from_bytes(buf, word_size=4):
    words = []
    s = struct.Struct("<I")
    l = len(buf)
    for i in range(0, l, word_size):
        words.append(s.unpack(buf[i: i + word_size])[0])
    return words


def bytes_from_words(words, word_count=0, word_size=4):
    if not word_count:
        word_count = len(words)
    buf = bytearray(word_count * word_size)
    count = min(len(words), word_count)
    s = struct.Struct("<I")
    start = 0
    for i in range(count):
        buf[start: start + word_size] = s.pack(words[i])
        start += word_size

    word_count -= count
    while word_count > 0:
        buf[start: start + word_size] = s.pack(words[-1])
        start += word_size
        word_count -= 1

    return buf


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def check_int(val):
    try:
        return int(val)
    except ValueError:
        raise TypeError(f"Expected integer but got '{val}'") from None


def is_ss(s, ss):
    try:
        if s.index(ss) == 0:
            return True
        else:
            return False
    except ValueError:
        return False


def to_tcl(py_list):
    if type(py_list) == list:
        out_str = "{"
        for item in py_list:
            if (out_str != "{"):
                out_str += " "
            out_str += to_tcl(item)
        out_str += "}"
        return out_str
    else:
        out_str = str(py_list)
        for c in ["\\", "{", "}", "[", "]", "$"]:
            out_str = out_str.replace(c, "\\" + c)
        return out_str


def to_dict(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct


def to_list(dct):
    lst = "{"
    for d in dct:
        lst = lst + " " + str(d)
        lst = lst + " " + str(dct[d])
    lst += "}"
    return lst


def to_bits(value, length):
    res = bin(value)
    ln = len(res) - 2
    res = res[2:].zfill(length) if ln <= length else res[2:][(ln - length):]
    return res


def split_addr(addr):
    res = list()
    res.append(((addr >> 32) & 0xFFFFFFFF))
    res.append(addr & 0xFFFFFFFF)
    return res


def to_bytes(data: int, length=1, order=sys.byteorder):
    data_bytes = data.to_bytes(length, order)
    return data_bytes


def _add_element(cache, element):
    if element != '':
        cache[-1].append(element)
    return ''


def find_largest_in_list(arr):
    max = arr[0]
    for i in range(0, len(arr)):
        if isinstance(arr[i], int):
            arr[i] = hex(arr[i])
        if arr[i] > max:
            max = arr[i]
    return int(max, 16)


def to_py(tcl_list, interp):
    out = []
    cache = [out]
    element = ''
    escape = False
    level = 0
    for char in tcl_list:
        if escape:
            element += char
            escape = False
        elif char == "\\":
            escape = True
        # elif char in [" ", "\t", "\r", "\n"]:
        #     element = _add_element(cache, element)
        elif char == "{":
            level += 1
            if level == 1:
                a = []
                cache[-1].append(a)
                cache.append(a)
            else:
                element += char
        elif char == "}":
            level -= 1
            if level == 0:
                element = _add_element(cache, tkinter._splitdict(interp, element))
                cache.pop()
            else:
                element += char
        else:
            if (element == '' and char == ' '):
                pass
            else:
                element += char
    py_list = []
    for l in out:
        py_list.append(l[0])
    return py_list


# Helper function to add function name, brief description, class and module to
# a global dict, which can be used to get list of functions, brief description
# for each function, and more importantly doc-string.
# Function names should be unique across all classes.
def add_function_metadata(fn: str, brief: str, category: str, cls: str, mod: str = None):
    global function_metadata

    function_metadata[fn] = {}
    function_metadata[fn]['brief'] = brief
    function_metadata[fn]['category'] = category
    function_metadata[fn]['class'] = cls
    function_metadata[fn]['module'] = mod


def exec_as_runnable(callable_function, arg=None):
    if threading.currentThread().name == 'TCF Event Dispatcher':
        raise Exception("exec_as_runnable cannot be called from dispatch thread.") from None
    run = Runnable(callable_function, arg)
    protocol.invokeLater(run)
    with run.sync.cond:
        run.sync.cond.wait()
    if run.sync.error is not None:
        raise Exception(f"{run.sync.error}") from None
    result = run.sync.result
    del run
    return result


def exec_in_dispatch_thread(callable_function, *args):
    if threading.currentThread().name == 'TCF Event Dispatcher':
        raise Exception("exec_in_dispatch_thread cannot be called from dispatch thread.") from None
    sync = SyncRequest()
    protocol.invokeAndWait(callable_function, *args, sync=sync)
    with sync.cond:
        sync.cond.wait()
    if sync.error is not None:
        raise Exception(f"{sync.error}") from None
    return sync.result


def dict_get_safe(dict_name, key):
    if key in dict_name:
        return dict_name.get(key)
    else:
        return None


def dict_get_value_or_error_out(dict_name, key):
    if key in dict_name:
        return dict_name.get(key)
    else:
        raise Exception(f"{key} not found in {dict_name}")


def get_cache_data(run):
    node = run.arg
    if not node.validate(run):
        return False
    else:
        run.sync.done(error=node.getError(), result=node.getData())


class TraceListener(channel.TraceListener):
    # debug purpose only. Modify the code with what you wish to see
    def onMessageReceived(self, msgType, token, service, name, data):
        if msgType == 'E' and service != "Locator" and (service == "Jtag" or service == "JtagCable"):
            print("<<< ", msgType, service, name, data[:150])

    #
    # def onMessageSent(self, msgType, token, service, name, data):
    #     if msgType == 'C' and service != "Locator" and service == 'JtagDevice':
    #         print("<<< ", msgType, service, name, data[:100])

    def onChannelClosed(self, error):
        pass

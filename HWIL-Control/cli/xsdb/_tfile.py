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

from tcf.services import filesystem as fs
from xsdb._tcf_tfile import TcfTFile
from xsdb._utils import *


class TFile(object):
    files = {}

    def __init__(self, session):
        self.session = session
        self.__tcf_tfile = TcfTFile(session)

    # Support partial functions
    def __getattr__(self, name):

        def unknown(*args, **kwargs):
            matches = []
            public_methods = [method for method in dir(TFile) if callable(getattr(TFile, method)) if
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

    def open(self, path: str = None, *args, **kwargs):
        """
open:
    Open specified file.

Prototype:
    file_handle = tfile.open(path = <file_path>)

Arguments:
    path = <file_path>

Optional:
    flags = <flags>
        read mode = 0x00000001
        write mode = 0x00000002
        append mode = 0x00000004
        create mode= 0x00000008
        trunc mode = 0x00000010
        excl mode= 0x00000020

Returns:
    File handle.
    Exception
        Failed to open the file.

Examples:
    handle = tfile.open("/tmp/file1.txt", 0x0F)

Interactive mode examples:
    tfile open /tmp/file1.txt -flags 0x0F
        """
        parser = argparse.ArgumentParser(description='TFile open')
        parser.add_argument('path', nargs='?', type=str, help='path of the file')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.path is None and path is None:
            raise Exception("File path is not specified.") from None
        elif parsed_args.path is not None:
            path = parsed_args.path

        flags = check_int(kwargs.pop('flags')) if 'flags' in kwargs else 0
        attrs = kwargs.pop('attrs') if 'attrs' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        handle = exec_in_dispatch_thread(self.__tcf_tfile.open, path, flags, attrs)
        if handle is None:
            raise Exception('Error opening file') from None
        TFile.files[handle] = 0
        return handle

    add_function_metadata('tfile open', 'Open specified file.', 'tfile', 'TFile')

    def write(self, handle=None, data=None, **kwargs):
        """
write:
    Write on the specified file handle.

Prototype:
    tfile.write(handle = <file_handle>, data)

Arguments:
    :param handle:
        file handle return by open
    :param data:
        Data to be written in the file. Data must be in string format.

Optional kwargs:
    offset=<offset>
        The offset (in bytes) relative to the beginning of the
        file from where to start writing. Default is 0.
    pos=<pos>
        Offset in *data* to write. Default is 0.
    size=<size>
        Number of bytes to write.Default is length of *data*
Returns:
    Exception
        Failed to write on the file handle.
    Else None

Examples:
    tfile.write(handle, "Hi, this is test.")

Interactive mode examples:
    tfile write -offset 0 'Hi , this is test'
        Note: It uses current file handle
        """
        if handle is None or handle not in TFile.files.keys():
            raise Exception(f'Invalid file handle: {handle}') from None
        if data is None:
            raise Exception(f'\'data\' not specified') from None
        offset = kwargs.pop('offset') if 'offset' in kwargs else TFile.files[handle]
        data_pos = kwargs.pop('pos') if 'pos' in kwargs else 0
        data_size = kwargs.pop('size') if 'size' in kwargs else len(data)
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if data_pos > len(data):
            raise Exception(f'Invalid data_pos: {data_pos}. Must be less than or equal to length of \'data\'') from None
        if isinstance(data, str):
            exec_in_dispatch_thread(self.__tcf_tfile.write, handle, offset, [ord(c) for c in data], data_pos, data_size)
        else:
            exec_in_dispatch_thread(self.__tcf_tfile.write, handle, offset, data, data_pos, data_size)
        TFile.files[handle] = offset + data_size

    add_function_metadata('tfile write', 'Write on the specified file handle.', 'tfile', 'TFile')

    def read(self, handle=None, size: int = 0, **kwargs):
        """
read:
    Read from the specified file handle.

Prototype:
    data = tfile.read(handle, size)

Arguments:
    handle:  file handle return by open
    size:  size of bytes to read from file

Optional kwargs:
    offset=<offset>
        Is the offset (in bytes) relative to the beginning of
        the file from where to start reading. Default value is 0

Returns:
    File content
    Exception
        Failed to read from the file handle.

Examples:
    tfile.read(handle, 20)

Interactive mode examples:
    tfile read -offset 0 -size 3
        Note: It uses current file handle
        """
        if handle is None or handle not in TFile.files.keys():
            raise Exception(f'Invalid file handle: {handle}') from None
        offset = kwargs.pop('offset') if 'offset' in kwargs else TFile.files[handle]
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        size = check_int(size)
        data = exec_in_dispatch_thread(self.__tcf_tfile.read, handle, offset, size)
        TFile.files[handle] = offset + size if data['eof'] is False else offset + len(data['data'])
        return data['data']

    add_function_metadata('tfile read', 'Read from the specified file handle.', 'tfile', 'TFile')

    def close(self, handle):
        """
close:
    Close the specified file handle.

Prototype:
    tfile.close(handle = <file_handle>)

Arguments:
    handle = <file_handle>

Returns:
    Exception
        Failed to close the file.
    else None

Examples:
    tfile.close(handle)

Interactive mode examples:
    tfile close
        Note: It uses current file handle
        """
        if handle not in TFile.files.keys():
            raise Exception(f'Invalid file handle: {handle}') from None
        exec_in_dispatch_thread(self.__tcf_tfile.close, handle)
        del TFile.files[handle]

    add_function_metadata('tfile close', 'Close the specified file handle.', 'tfile', 'TFile')

    def ls(self, path: str = None):
        """
ls:
    List directory content.

Prototype:
    tfile.ls(path = <dir_path>)

Arguments:
    path = <dir_path>

Returns:
    Directory content.
    Exception
        Failed to retrieve the directory content.

Examples:
    tfile.ls(path = "/tmp/dir1")

Interactive mode examples:
    tfile ls -path /tmp
        """
        ls_list = list()
        if path is None:
            roots = exec_in_dispatch_thread(self.__tcf_tfile.roots)
            if len(roots) == 1:
                path = roots[0].filename
            else:
                ls_list = roots
        if path is not None:
            fhandle = exec_in_dispatch_thread(self.__tcf_tfile.opendir, path)
            while True:
                v = exec_in_dispatch_thread(self.__tcf_tfile.readdir, fhandle)
                ls_list += v['entries']
                if v['eof'] is True:
                    break
            exec_in_dispatch_thread(self.__tcf_tfile.close, fhandle)
        result = ''
        for item in ls_list:
            result += '{0:10d}{1}{2}{3}'.format(0 if item.attrs is None else item.attrs.size, ' ' * 2,
                                                item.filename, '\n')

        print(result)

    add_function_metadata('tfile ls', 'List directory content.', 'tfile', 'TFile')

    def remove(self, path: str = None):
        """
remove:
    Remove the specified path.

Prototype:
    tfile.remove(path = <file_path>)

Arguments:
    path = <file_path>

Returns:
    Exception
        Failed to remove the path.
    else None

Examples:
    tfile.remove("/tmp/file2.txt")

Interactive mode examples:
    tfile remove /tmp/file2.txt
        """
        if path is None:
            raise Exception(f'\'path\' is not specified') from None
        exec_in_dispatch_thread(self.__tcf_tfile.remove, path)

    add_function_metadata('tfile remove', 'Remove the specified path.', 'tfile', 'TFile')

    def mkdir(self, path: str = None, *args, **kwargs):
        """
mkdir:
    Make directory.

Prototype:
    stat_dict = tfile.mkdir(path = <dir_path>)

Arguments:
    path = <dir_path>

Returns:
    Exception
        Failed to make the directory.
    else None

Examples:
    tfile.mkdir(path = <dir_path>)

Interactive mode examples:
    tfile mkdir /tmp/dir1
        """
        parser = argparse.ArgumentParser(description='TFile mkdir')
        parser.add_argument('path', nargs='?', type=str, help='path of the file')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.path is None and path is None:
            raise Exception("Path is not specified.") from None
        elif parsed_args.path is not None:
            path = parsed_args.path

        attrs = kwargs.pop('attrs') if 'attrs' in kwargs else None
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        exec_in_dispatch_thread(self.__tcf_tfile.mkdir, path, attrs)

    add_function_metadata('tfile mkdir', 'Make directory.', 'tfile', 'TFile')

    def rmdir(self, path: str = None):
        """
rmdir:
    Remove the specified directory.

Prototype:
    tfile.rmdir(path = <dir_path>)

Arguments:
    path = <dir_path>

Returns:
    Exception
        Failed to remove the directory.
    else None

Examples:
    tfile.rmdir(path = "/tmp/dir1")

Interactive mode examples:
    tfile rmdir /tmp/dir1
        """
        if path is None:
            raise Exception(f'\'path\' is not specified') from None
        exec_in_dispatch_thread(self.__tcf_tfile.rmdir, path)

    add_function_metadata('tfile rmdir', 'Remove the specified directory.', 'tfile', 'TFile')

    def roots(self):
        """
roots:
    Get file system roots.

Prototype:
    root_list = tfile.roots()

Arguments:
    None

Returns:
    Root list.
    Exception
        Failed to get the file system roots.

Examples:
    root_list = tfile.roots()

Interactive mode examples:
    tfile roots
        """
        roots = exec_in_dispatch_thread(self.__tcf_tfile.roots)
        out = []
        for item in roots:
            out.append({'FileName': item.filename,
                        'Attrs': {'Size': item.attrs.size, 'UID': item.attrs.uid,
                                  'GID': item.attrs.gid, 'Permissions': hex(item.attrs.permissions),
                                  'ATime': item.attrs.atime, 'MTime': item.attrs.mtime, 'Flags': item.attrs.flags,
                                  'Attributes': item.attrs.attributes}})
        return out

    add_function_metadata('tfile roots', 'Get file system roots.', 'tfile', 'TFile')

    def opendir(self, path: str):
        """
opendir:
    Open specified directory.

Prototype:
    dir_handle = tfile.open(path = <dir_path>)

Arguments:
    path = <dir_path>

Returns:
    Directory handle.
    Exception
        Failed to open the directory.

Examples:
    handle = tfile.opendir("/tmp/dir1")

Interactive mode examples:
    tfile opendir /tmp/dir1
        """
        if path is None:
            raise Exception(f'\'path\' is not specified') from None
        fhandle = exec_in_dispatch_thread(self.__tcf_tfile.opendir, path)
        TFile.files[fhandle] = 0
        return fhandle

    add_function_metadata('tfile opendir', 'Open specified directory.', 'tfile', 'TFile')

    def readdir(self, handle):
        """
readdir:
    Get directory attributes for the handle.

Prototype:
    dir_attr = tfile.readdir(handle = <dir_handle>)

Arguments:
    handle = <dir_handle>

Returns:
    Directory attributes in dictionary format.
    Exception
        Failed to get the directory attributes.

Examples:
    dir_attr = tfile.readdir(handle)

Interactive mode examples:
    tfile readdir
        Note: it uses current opendir handle
        """
        if handle not in TFile.files.keys():
            raise Exception(f'Invalid file handle: {handle}') from None
        data = exec_in_dispatch_thread(self.__tcf_tfile.readdir, handle)['entries']
        out = []
        for item in data:
            if item.attrs is None:
                out.append({'FileName': item.filename, 'Attrs': None})
            else:
                out.append({'FileName': item.filename,
                            'Attrs': {'Size': item.attrs.size, 'UID': item.attrs.uid,
                                      'GID': item.attrs.gid, 'Permissions': hex(item.attrs.permissions),
                                      'ATime': item.attrs.atime, 'MTime': item.attrs.mtime, 'Flags': item.attrs.flags,
                                      'Attributes': item.attrs.attributes}})
        return out

    add_function_metadata('tfile readdir', 'Get directory attributes for the handle.', 'tfile', 'TFile')

    def rename(self, old: str = None, new: str = None):
        """
rename:
    Rename file or directory.

Prototype:
    tfile.ls(old_path , new_path)

Arguments:
    old
        Current path of the file/directory.
    new
        New path for the file/directory.

Returns:
    Exception
        Failed to rename the file or directory.
    else None

Examples:
    tfile.rename(old_path = "/tmp/dir1", new_path = "/tmp/dir2")

Interactive mode examples:
    tfile rename /tmp/dir1 /tmp/dir2
        """
        if old is None or new is None:
            raise Exception('Invalid paths of old, new') from None
        exec_in_dispatch_thread(self.__tcf_tfile.rename, old, new)

    add_function_metadata('tfile rename', 'Rename file or directory.', 'tfile', 'TFile')

    def stat(self, path: str = None):
        """
stat:
    Get file attributes from path.

Prototype:
    stat_dict = tfile.stat(path = <file_path>)

Arguments:
    path = <file_path>

Returns:
    File attributes
    Exception
        Failed to get file attributes.

Examples:
    stat_dict = tfile.stat(path = "/tmp/file1.txt")

Interactive mode examples:
    tfile stat -path /tmp/file1.txt
        """
        if path is None:
            raise Exception('path is not specified') from None
        return exec_in_dispatch_thread(self.__tcf_tfile.stat, path)

    add_function_metadata('tfile stat', 'Get file attributes from path.', 'tfile', 'TFile')

    def lstat(self, path):
        """
lstat:
    Get link attributes from the path.

Prototype:
    path = tfile.lstat(path = <link>)

Arguments:
    path = <link>

Returns:
    Link file attributes.
    Exception
        Failed to get the link attributes.

Examples:
    path = tfile.lstat("/tmp/link1")

Interactive mode examples:
    tfile lstat /tmp/link1
        """
        if path is None:
            raise Exception('path is not specified') from None
        return exec_in_dispatch_thread(self.__tcf_tfile.lstat, path)

    add_function_metadata('tfile lstat', 'Get link attributes from the path.', 'tfile', 'TFile')

    def fstat(self, handle=None):
        """
fstat:
    Get file attributes for handle.

Prototype:
    stat_dict = tfile.fstat(handle = <file_handle>)

Arguments:
    handle = <file_handle>

Returns:
    File attributes.
    Exception
        Failed to get the file attributes.

Examples:
    stat_dict = tfile.fstat(handle)

Interactive mode examples:
    tfile fstat
        Note : It uses current opened file handle as input
        """
        if handle is None or handle not in TFile.files.keys():
            raise Exception('Invalid handle') from None
        return exec_in_dispatch_thread(self.__tcf_tfile.fstat, handle)

    add_function_metadata('tfile fstat', 'Get file attributes for handle.', 'tfile', 'TFile')

    def realpath(self, path: str = None):
        """
realpath:
    Get real path of specified path.

Prototype:
    real_path = tfile.realpath(path = <file_path>)

Arguments:
    path = <file_path>

Returns:
    Real path of the specified path.
    Exception
        Failed to get the real path.

Examples:
    real_path = tfile.realpath("/tmp/file1.txt")

Interactive mode examples:
    tfile realpath /tmp/text1.txt
        """
        if path is None:
            raise Exception('path is not specified') from None
        return exec_in_dispatch_thread(self.__tcf_tfile.realpath, path)

    add_function_metadata('tfile realpath', 'Get real path of specified path.', 'tfile', 'TFile')

    def user(self):
        """
user:
    Get user attributes.

Prototype:
    user_attr = tfile.user()

Arguments:
    None

Returns:
    User attributes.
    Exception
        Failed to get the user attributes.

Examples:
    user_attr = tfile.user()

Interactive mode examples:
    tfile user
        """
        return exec_in_dispatch_thread(self.__tcf_tfile.user)

    add_function_metadata('tfile user', 'Get user attributes.', 'tfile', 'TFile')

    def symlink(self, link: str = None, target: str = None):
        """
symlink:
    Create symbolic link for the specified path.

Prototype:
    tfile.symlink(link = <link_path>, target = <target_path>)

Arguments:
    link = <link_path>
    target = <target_path>

Returns:
    Exception
        Failed to create the symbolic link.
    Else None

Examples:
    tfile.symlink("tmp/link1","tmp/dir1/file1.txt")

Interactive mode examples:
    tfile symlink /tmp/link1 tmp/dir1/file1.txt
        """
        if link is None or target is None:
            raise Exception('Invalid inputs link/target') from None
        exec_in_dispatch_thread(self.__tcf_tfile.symlink, link, target)

    add_function_metadata('tfile symlink', 'Create symbolic link for the specified path.', 'tfile', 'TFile')

    def readlink(self, path: str = None):
        """
readlink:
    Read symbolic link.

Prototype:
    path = tfile.readlink(path = <link>)

Arguments:
    path = <link>
        Read link file.

Returns:
    Target path.
    Exception
        Failed to read the symbolic link.

Examples:
    path = tfile.readlink("tmp/link1")

Interactive mode examples:
    tfile readlink /tmp/link1
        """
        if path is None:
            raise Exception('Invalid path') from None
        return exec_in_dispatch_thread(self.__tcf_tfile.readlink, path)

    add_function_metadata('tfile readlink', 'Read symbolic link.', 'tfile', 'TFile')

    def setstat(self, path: str = None, attr=None):
        """
setstat:
    Set file attributes.

Prototype:
    tfile.setstat(path = <file_path>, attr = <file_attr>)

Arguments:
    path = <file_path>
    attr = <file_attr>
        File attributes in FileAttrs format.( which is a
        return type from tfile.stat)

Returns:
    Exception
        Failed to set the file attributes.
    Else None

Examples:
    tfile.setstat("/tmp/file1.txt" , {'permissions':33119})

Interactive mode examples:
    tfile setstat /tmp/file1.txt -attr {'permissions':33119}

        """
        if path is None:
            raise Exception('path is not specified') from None
        file_attrs = self.stat(path)
        if not isinstance(attr, dict):
            raise Exception('specify attrs in dict format') from None
        for key, value in attr.items():
            if hasattr(file_attrs, key):
                setattr(file_attrs, key, value)
            else:
                raise Exception(f'Invalid key \'{key}\' in attr dictionary') from None
        exec_in_dispatch_thread(self.__tcf_tfile.setstat, path, file_attrs)

    add_function_metadata('tfile setstat', 'Set file attributes.', 'tfile', 'TFile')

    def fsetstat(self, handle=None, attr=None):
        """
fsetstat:
    Set file attributes for the handle.

Prototype:
    tfile.fsetstat(handle = <file_handle>, file_attr)

Arguments:
    handle  <file_handle>
        file handle
    attr
        File attributes in dictionary format.

Returns:
    Exception
        Failed to set the file attributes.
    Else None

Examples:
    tfile.fsetstat(handle , {'permissions':33119})

Interactive mode examples:
    tfile fsetstat -attr {'permissions':33119}
        Note: handle is current file handler
        """
        if handle is None:
            raise Exception('handle is not specified') from None
        file_attrs = self.fstat(handle)
        if not isinstance(attr, dict):
            raise Exception('specify attrs in dict format') from None
        for key, value in attr.items():
            if hasattr(file_attrs, key):
                setattr(file_attrs, key, value)
            else:
                raise Exception(f'Invalid key \'{key}\' in attr dictionary') from None
        exec_in_dispatch_thread(self.__tcf_tfile.fsetstat, handle, file_attrs)

    add_function_metadata('tfile fsetstat', 'Set file attributes for the handle.', 'tfile', 'TFile')

    def copy(self, *args, src: str = None, dest: str = None, **kwargs):
        """
copy:
    Copy the target file.

Prototype:
    tfile.copy(src = <src_file>, dest = <dest_file>)

Arguments:
    src = <src_file>
    dest = <dest_file>

Options:
    --owner (-o)
        Copy owner information.
    --permissions (-p)
        Copy permissions.

Returns:
    Exception
        Failed to copy the target file.
    else None

Examples:
    tfile.copy(src = "/tmp/file1.txt",dest = "/tmp/file1.txt")

Interactive mode examples:
    tfile copy -src f1.txt -dest f2.txt
        """

        parser = argparse.ArgumentParser(description='TFile copy')
        parser.add_argument('-f', '--from_host', action='store_true', help='Copy data from host')
        parser.add_argument('-t', '--to_host', action='store_true', help='Copy data to host')
        parser.add_argument('-o', '--owner', action='store_true', help='Copy owner information')
        parser.add_argument('-p', '--permissions', action='store_true', help='Copy permissions')
        parser.add_argument('src', nargs='?', type=str, help='source file path')
        parser.add_argument('dest', nargs='?', type=str, help='destination file path')
        parsed_args = parser.parse_args(tuple(str(arg) for arg in args))

        if parsed_args.src is not None:
            if src is not None:
                raise TypeError(f"Conflicting args: Specify src name either as positional arg or keyword arg")
            src = parsed_args.src

        if parsed_args.dest is not None:
            if dest is not None:
                raise TypeError(f"Conflicting args: Specify dest name either as positional arg or keyword arg")
            dest = parsed_args.dest

        from_host = 1 if parsed_args.from_host is True else 0
        to_host = 1 if parsed_args.to_host is True else 0

        if from_host + to_host > 1:
            raise Exception("Data cannot be copied to host and from host on the same time.") from None

        chunk_size = kwargs.pop('chunk_size') if 'chunk_size' in kwargs else 16384
        if kwargs:
            raise TypeError(f"Invalid args: {list(kwargs.keys())}") from None
        if from_host == 1 or to_host == 1:
            if from_host == 1:
                fsrc = open(src, 'rb')
            else:
                fsrc = self.open(src, flags=0x01)
            if to_host == 1:
                fdest = open(dest, 'wb')
            else:
                fdest = self.open(dest, flags=0x01A)
            while True:
                if from_host == 1:
                    data = fsrc.read(chunk_size)
                else:
                    data = self.read(fsrc, chunk_size)
                if len(data) == 0:
                    break
                if to_host == 1:
                    fdest.write(data)
                else:
                    self.write(fdest, data)
            if from_host == 1:
                fsrc.close()
            else:
                self.close(fsrc)
            if to_host == 1:
                fdest.close()
            else:
                self.close(fdest)
        else:
            exec_in_dispatch_thread(self.__tcf_tfile.copy, src, dest, parsed_args.permissions, parsed_args.owner)

    add_function_metadata('tfile copy', 'Copy the target file.', 'tfile', 'TFile')

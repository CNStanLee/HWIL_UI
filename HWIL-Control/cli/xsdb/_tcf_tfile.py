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

from tcf.services import filesystem as fs
from xsdb._utils import *


class TcfTFile(object):
    def __init__(self, session):
        self.fsn = protocol.invokeAndWait(session._curchan_obj.getRemoteService, fs.NAME)

    class DoneStat(fs.DoneStat):
        def __init__(self, sync):
            self.sync = sync

        def doneStat(self, token, error, attrs):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error, result=attrs)

    class DoneSetStat(fs.DoneSetStat):
        def __init__(self, sync):
            self.sync = sync

        def doneSetStat(self, token, error):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error)

    class DoneOpen(fs.DoneOpen):
        def __init__(self, sync):
            self.sync = sync

        def doneOpen(self, token, error, handle):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error, result=handle)

    class DoneRemove(fs.DoneRemove):
        def __init__(self, sync):
            self.sync = sync

        def doneRemove(self, token, error):
            if error is not None:
                error = error if isinstance(error, OSError) else error.getAttributes()['Format']
            self.sync.done(error=error)

    def opendir(self, path, sync):
        self.fsn.opendir(path, self.DoneOpen(sync))

    def rmdir(self, path, sync):
        self.fsn.rmdir(path, self.DoneRemove(sync))

    def open(self, file_name, flags, attrs, sync):
        self.fsn.open(file_name, flags, attrs, self.DoneOpen(sync))

    def remove(self, file_name, sync):
        self.fsn.remove(file_name, self.DoneRemove(sync))

    def stat(self, path, sync):
        self.fsn.stat(path, self.DoneStat(sync))

    def fstat(self, handle, sync):
        self.fsn.fstat(handle, self.DoneStat(sync))

    def lstat(self, path, sync):
        self.fsn.lstat(path, self.DoneStat(sync))

    def setstat(self, path, attrs, sync):
        self.fsn.setstat(path, attrs, self.DoneSetStat(sync))

    def fsetstat(self, handle, attrs, sync):
        self.fsn.fsetstat(handle, attrs, self.DoneSetStat(sync))

    def roots(self, sync):
        class DoneRoots(fs.DoneRoots):
            def __init__(self, sync):
                self.sync = sync

            def doneRoots(self, token, error, entries):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result=entries)

        self.fsn.roots(DoneRoots(sync))

    def readdir(self, handle, sync):
        class DoneReadDir(fs.DoneReadDir):
            def __init__(self, sync):
                self.sync = sync

            def doneReadDir(self, token, error, entries, eof):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result={'entries': entries, 'eof': eof})

        self.fsn.readdir(handle, DoneReadDir(sync))

    def mkdir(self, path, attrs, sync):
        class DoneMkDir(fs.DoneMkDir):
            def __init__(self, sync):
                self.sync = sync

            def doneMkDir(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.mkdir(path, attrs, DoneMkDir(sync))

    def close(self, handle, sync):
        class DoneClose(fs.DoneClose):
            def __init__(self, sync):
                self.sync = sync

            def doneClose(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.close(handle, DoneClose(sync))

    def read(self, handle, offset, length, sync):
        class DoneRead(fs.DoneRead):
            def __init__(self, sync):
                self.sync = sync

            def doneRead(self, token, error, data, eof):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result={'data': data, 'eof': eof})

        self.fsn.read(handle, offset, length, DoneRead(sync))

    def write(self, handle, offset, data, data_pos, data_size, sync):
        class DoneWrite(fs.DoneWrite):
            def __init__(self, sync):
                self.sync = sync

            def doneWrite(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.write(handle, offset, data, data_pos, data_size, DoneWrite(sync))

    def copy(self, src_path, dst_path, copy_permissions, copy_ownership, sync):
        class DoneCopy(fs.DoneCopy):
            def __init__(self, sync):
                self.sync = sync

            def doneCopy(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.copy(src_path, dst_path, copy_permissions, copy_ownership, DoneCopy(sync))

    def rename(self, old_path, new_path, sync):
        class DoneRename(fs.DoneRename):
            def __init__(self, sync):
                self.sync = sync

            def doneRename(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.rename(old_path, new_path, DoneRename(sync))

    def readlink(self, path, sync):
        class DoneReadLink(fs.DoneReadLink):
            def __init__(self, sync):
                self.sync = sync

            def doneReadLink(self, token, error, path):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result=path)

        self.fsn.readlink(path, DoneReadLink(sync))

    def realpath(self, path, sync):
        class DoneRealPath(fs.DoneRealPath):
            def __init__(self, sync):
                self.sync = sync

            def doneRealPath(self, token, error, path):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result=path)

        self.fsn.realpath(path, DoneRealPath(sync))

    def symlink(self, link_path, target_path, sync):
        class DoneSymLink(fs.DoneSymLink):
            def __init__(self, sync):
                self.sync = sync

            def doneSymLink(self, token, error):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error)

        self.fsn.symlink(link_path, target_path, DoneSymLink(sync))

    def user(self, sync):
        class DoneUser(fs.DoneUser):
            def __init__(self, sync):
                self.sync = sync

            def doneUser(self, token, error, real_uid, effective_uid, real_gid, effective_gid, home):
                if error is not None:
                    error = error if isinstance(error, OSError) else error.getAttributes()['Format']
                self.sync.done(error=error, result={'real_uid': real_uid, 'effective_uid': effective_uid,
                                                    'real_gid': real_gid, 'effective_gid': effective_gid, 'home': home})

        self.fsn.user(DoneUser(sync))
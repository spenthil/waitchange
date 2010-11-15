#!/usr/bin/env python

# Licensed under the MIT License.
#
# Copyright (c) 2010 Senthil Palanisami
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import os
import select
from optparse import OptionParser

version = "0.1"

def watch_files(filenames):
    def _watch_file(kq, filename, flags = select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT, fflags = select.KQ_NOTE_WRITE | select.KQ_NOTE_DELETE | select.KQ_NOTE_EXTEND | select.KQ_NOTE_RENAME):
        fd = os.open(filename, os.O_RDONLY)
        event = [select.kevent(fd, filter=select.KQ_FILTER_VNODE, flags=flags, fflags=fflags)]
        kq.control(event, 0, 0)
        return fd
    kq = select.kqueue()
    # filedescriptors -> filename
    fds = {}
    for filename in filenames:
        # expand out '~/' nonsense if its their
        filename = os.path.expanduser(filename)
        # get absolute path if its relative
        filename = os.path.abspath(filename)
        fds[_watch_file(kq, filename)] = filename
    try:
        events = kq.control([], 1, None)
    finally:
        kq.close()
        for fd in fds:
            os.close(fd)

    changed_files = set()
    for event in events:
        changed_files.add(fds[event.ident])

    return changed_files

if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] filename1 filename2 ...", version="%prog " + version)
    #parser.add_option("-r", "--recursive", action="store_true", default=False, dest="recursive", help="Watch subfolders as well. Default is to not.")
    (options, args) = parser.parse_args()
    if args == []:
        parser.error("must supply at least one file to wait on")
    results = watch_files(args)
    print ", ".join(("'" + x + "'" for x in results))
    # if got files return 0, if not return 1
    sys.exit(results == False)

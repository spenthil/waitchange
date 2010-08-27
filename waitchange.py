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

def main():

    parser = OptionParser(usage="usage: %prog [options] filename1 filename2 ...", version="%prog " + version)
    parser.add_option("-r", "--recursive", action="store_true", default=False, dest="recursive", help="Watch subfolders as well. Default is to not.")
    (options, args) = parser.parse_args()

    if args == []:
        args = [os.getcwd(),]
    def watch_file(kq, filename):
        fd = os.open(filename, os.O_RDONLY)
        event = [select.kevent(fd, filter=select.KQ_FILTER_VNODE, flags=select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_ONESHOT, fflags=select.KQ_NOTE_WRITE | select.KQ_NOTE_DELETE | select.KQ_NOTE_EXTEND)]
        kq.control(event, 0, 0)
        return fd
    kq = select.kqueue()
    fds = []
    for filename in args:
        fds.append(watch_file(kq, filename))
        if options.recursive and os.path.isdir(filename):
            for subdir in [x[0] for x in os.walk(filename)]:
                fds.append(watch_file(kq, subdir))
    try:
        events = kq.control([], 1, None)
    except KeyboardInterrupt:
        # keyboard killed, return 1 (fail)
        return 1
    else:
        # something changed, return 0 (success)
        kq.close()
        for fd in fds:
            os.close(fd)
        return 0

if __name__ == '__main__':
    sys.exit(main())

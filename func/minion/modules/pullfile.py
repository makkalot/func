#!/usr/bin/env python
#
# pullfile.py
#
# Copyright 2009, Stone-IT
# L.S. Keijser <keijser@stone-it.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA


from func.minion import codes
import func_module, os
from urllib2 import Request, urlopen, URLError

class PullFile(func_module.FuncModule):

    version = "0.0.2"
    api_version = "0.0.1"
    description = "Download remote file and save locally"

    def update(self, args):
        for inFile, outFile in args.iteritems():
            try:
                req = Request(inFile)
                webFile = urlopen(req)
            except URLError:
                raise codes.FuncException("Error retrieving file")
            try:
                f = open(outFile, 'w')
            except IOError:
                raise codes.FuncException("Error opening local file")
            f.write(webFile.read())
            f.close()
            webFile.close()
        return 0

    def get(self, inFile, outFile):
        try:
            req = Request(inFile)
            webFile = urlopen(req)
        except URLError:
            raise codes.FuncException("Error retrieving file")
        try:
            f = open(outFile, 'w')
        except IOError:
            raise codes.FuncException("Error opening local file")
        f.write(webFile.read())
        f.close()
        webFile.close()
        return 0


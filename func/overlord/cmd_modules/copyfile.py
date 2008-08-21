"""
copyfile command line

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


import optparse
import os
import pprint
import stat
import xmlrpclib

from func.overlord import base_command
from func.overlord import client


class CopyFile(base_command.BaseCommand):
    name = "copyfile"
    usage = "copy a file to a client"
    summary = "copy a file to a minion"


    def addOptions(self):
        self.parser.add_option("-f", "--file", dest="filename",
                               action="store")
        self.parser.add_option("", "--remotepath", dest="remotepath",
                                action="store")
        self.parser.add_option("", "--force", dest="force",
                               action="store_true")
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")

    def handleOptions(self, options):
        self.verbose = self.options.verbose

    def do(self, args):
        if not self.options.filename or not self.options.remotepath:
            self.outputUsage()
            return
        
        self.server_spec = self.parentCommand.server_spec
        self.getOverlord()

        return self.overlord_obj.local.copyfile.send(self.options.filename, self.options.remotepath)

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

from func.overlord import command
from func.overlord import client

DEFAULT_PORT = 51234

class CopyFile(client.command.Command):
    name = "copyfile"
    usage = "copy a file to a client"


    def addOptions(self):
        self.parser.add_option("-f", "--file", dest="filename",
                               action="store")
        self.parser.add_option("", "--remotepath", dest="remotepath",
                                action="store")
        self.parser.add_option("", "--force", dest="force",
                               action="store_true")
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
        self.parser.add_option("-p", "--port", dest="port")

    def handleOptions(self, options):
        self.port = DEFAULT_PORT
        if self.options.port:
            self.port = self.options.port


    def do(self, args):
        self.server_spec = self.parentCommand.server_spec

        client_obj = client.Client(self.server_spec,
                                   port=self.port,
                                   interactive=False,
                                   verbose=self.options.verbose,
                                   config=self.config)

        
        try:
            fb = open(self.options.filename, "r").read()
        except IOError, e:
            print "Unable to open file: %s: %s" % (self.options.filename, e)
            return

        st = os.stat(self.options.filename)
        mode = stat.S_IMODE(st.st_mode)
        uid = st.st_uid
        gid = st.st_gid

    
        data = xmlrpclib.Binary(fb)
        results = client_obj.run("copyfile", "copyfile", [self.options.remotepath, data,
                                                          mode, uid, gid])

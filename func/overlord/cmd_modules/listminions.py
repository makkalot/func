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

from func.overlord import command
from func.overlord import client
DEFAULT_PORT = 51234

class ListMinions(client.command.Command):
    name = "list_minions"
    usage = "show known minions"

    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")

    def handleOptions(self, options):
        self.port = DEFAULT_PORT
        if options.verbose:
            self.verbose = self.options.verbose
    
    def do(self, args):
        self.server_spec = self.parentCommand.server_spec

        client_obj = client.Client(self.server_spec,
                                   port=self.port,
                                   interactive=False,
                                   verbose=self.options.verbose,
                                   config=self.config)

        servers = client_obj.servers
        print servers
        for server in servers:
            # just cause I hate regex'es -akl
            host = server.split(':')[-2]
            host = host.split('/')[-1]
            print host

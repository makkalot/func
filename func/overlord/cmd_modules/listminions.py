"""
list minions provides a command line way to see what certs are
registered.

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

from func.overlord import client
from func.overlord import base_command

class ListMinions(base_command.BaseCommand):
    name = "list_minions"
    usage = "show known minions"
    summary = usage

    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")

    def handleOptions(self, options):
        if options.verbose:
            self.verbose = self.options.verbose

    
    def do(self, args):

        self.server_spec = self.parentCommand.server_spec

        minion_set = client.Minions(self.server_spec, port=self.port)
        servers = minion_set.get_all_hosts()
        servers.sort()
        for server in servers:
            print server


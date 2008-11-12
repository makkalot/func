"""
ping minions to see whether they are up.

Copyright 2007, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>
also see AUTHORS

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


class Ping(base_command.BaseCommand):
    name = "ping"
    usage = "see what func minions are up/accessible"
    summary = usage

    def addOptions(self):
        """
        Not too many options for you!  (Seriously, it's a simple command ... func "*" ping)
        """
        # FIXME: verbose and port should be added globally to all sub modules
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               default=self.verbose,
                               action="store_true")

    def handleOptions(self, options):
        """
        Nothing to do here...
        """
        self.verbose = self.options.verbose

    def do(self, args):
        self.server_spec = self.parentCommand.server_spec

        # because this is mainly an interactive command, expand the server list and make seperate connections.
        # to make things look more speedy.

        minion_set = client.Minions(self.server_spec, port=self.port)
        servers = minion_set.get_all_hosts()

        for server in servers:

            overlord_obj = client.Overlord(server,port=self.port,
                                           interactive=False,
                                           verbose=self.verbose,
                                           config=self.config,
                                           noglobs=True)

            results = overlord_obj.run("test", "ping", [])
            if results == 1:
                print "[ ok ... ] %s" % server
            else:
                print "[ FAILED ] %s" % server

        return 1

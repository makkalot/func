#!/usr/bin/python

"""
copyfile command line

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

from func.overlord import command
from func.overlord import client

# FIXME: this really should not be in each sub module.
DEFAULT_PORT = 51234

class Ping(client.command.Command):
    name = "ping"
    useage = "see what func minions are up/accessible"


    def addOptions(self):
        """
        Not too many options for you!  (Seriously, it's a simple command ... func "*" ping)
        """
        # FIXME: verbose and port should be added globally to all sub modules
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
        self.parser.add_option("-p", "--port", dest="port",
                               default=DEFAULT_PORT)


    def handleOptions(self, options):
        """
        Nothing to do here...
        """
        pass


    def do(self, args):
        self.server_spec = self.parentCommand.server_spec

        client_obj = client.Client(self.server_spec,
                                   port=self.options.port,
                                   interactive=False,
                                   verbose=self.options.verbose,
                                   config=self.config)

        results = client_obj.run("test", "ping", [])
        for (host,result) in results.iteritems():
            if result == 1:
                print "[ ok ... ] %s" % host
            else:
                print "[ FAILED ] %s" % host
        return 1


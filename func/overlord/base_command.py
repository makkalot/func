#!/usr/bin/python
"""
Copyright 2008, Red Hat, Inc
Adrian Likins <alikins@redhat.com>
also see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import command
import client

DEFAULT_PORT = 51234
DEFAULT_MAPLOC = "/var/lib/func/map"

class BaseCommand(command.Command):
    """ wrapper class for commands with some convience functions, namely
    getOverlord() for getting a overlord client api handle"""

    interactive = False
    verbose=0
    port=DEFAULT_PORT
    async=False
    forks=1
    delegate=False
    mapfile=DEFAULT_MAPLOC
    def getOverlord(self):
        self.overlord_obj = client.Overlord(self.server_spec,
                                            port=self.port,
                                            interactive=self.interactive,
                                            verbose=self.verbose,
                                            config=self.config,
                                            async=self.async,
                                            nforks=self.forks,
                                            delegate=self.delegate,
                                            mapfile=self.mapfile)

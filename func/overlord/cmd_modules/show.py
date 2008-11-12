"""
show introspection commandline

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


import optparse
import pprint
import xmlrpclib

from func.overlord import base_command
import show_hardware



class Show(base_command.BaseCommand):
    name = "show"
    usage = "show reports about minion info"
    summary = usage
    subCommandClasses = [show_hardware.ShowHardware]

    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")

    def handleOptions(self, options):
        self.options = options

        self.verbose = options.verbose


    def parse(self, argv):
        self.argv = argv

        return base_command.BaseCommand.parse(self, argv)
        

    def do(self, args):
        pass

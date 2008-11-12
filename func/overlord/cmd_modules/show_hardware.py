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


class ShowHardware(base_command.BaseCommand):
    name = "hardware"
    usage = "show hardware details"
    summary = usage

    # FIXME: we might as well make verbose be in the subclass
    #      and probably an inc variable while we are at it
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
    

    def handleOptions(self, options):
        pass
    
    def parse(self, argv):
        self.argv = argv
        return base_command.BaseCommand.parse(self,argv)

    def do(self,args):

        self.server_spec = self.parentCommand.parentCommand.server_spec
        self.getOverlord()
        
        results = self.overlord_obj.run("hardware", "info", [])

        # if the user 
        top_options = ["port","verbose"]
        
        for minion in results:
            print "%s:" % minion
            minion_data = results[minion]
            # if user set no args
            if not args:
                pprint.pprint(minion_data)
                continue
            
            for arg in args:
                if arg in minion_data:
                    print minion_data[arg]



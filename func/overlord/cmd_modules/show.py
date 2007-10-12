#!/usr/bin/python

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

from func.overlord import command
from func.overlord import client

DEFAULT_PORT = 51234


class ShowHardware(client.command.Command):
    name = "hardware"
    useage = "show hardware details"

    # FIXME: we might as well make verbose be in the subclass
    #      and probably an inc variable while we are at it
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
        self.parser.add_option("-p", "--port", dest="port")
        self.parser.add_option("", "--platform", dest="platform",
                               action="store_true")
        self.parser.add_option("", "--memory", dest="memory",
                               action="store_true")
        self.parser.add_option("","--os", dest="os",
                               action="store_true")


    def handleOptions(self, options):
        self.port = DEFAULT_PORT
        if self.options.port:
            self.port = self.options.port

    def parse(self, argv):
        self.argv = argv
        return command.Command.parse(self,argv)

    def do(self,args):

        self.server_spec = self.parentCommand.parentCommand.server_spec
        
        client_obj = client.Client(self.server_spec,
                                   port=self.port,
                                   interactive=False,
                                   verbose=self.options.verbose,
                                   config=self.config)
        
        results = client_obj.run("hardware", "info", [])

        # if the user 
        top_options = ["port","verbose"]
        
        # figure out of the user set any options we care about
        options_set = False

        #ugh, cant find a better way to do this. Look for args
        # that specify a "mode", if we set them, then don't
        # do the big dump

        # also, optparse is annoying -akl
        opt_list = ["--platform", "--memory", "--os"]
        for opt in opt_list:
            if self.parser.has_option(opt):
                options_set = True
        

        for minion in results:
            print "%s:" % minion
            minion_data = results[minion]
            if not options_set:
                pprint.pprint(minion_data)
                continue
            
            if self.options.platform:
                print minion_data['platform']

            if self.options.memory:
                print minion_data["systemMemory"]

            if self.options.os:
                print minion_data["os"]

class Show(client.command.Command):
    name = "show"
    useage = "various simple report stuff"
    subCommandClasses = [ShowHardware]
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
        self.parser.add_option("-p", "--port", dest="port",
                               default=DEFAULT_PORT)

    def handleOptions(self, options):
        self.options = options

        self.verbose = options.verbose
        self.port = options.port


    def parse(self, argv):
        self.argv = argv

        return command.Command.parse(self, argv)
        

    def do(self, args):
        pass
    


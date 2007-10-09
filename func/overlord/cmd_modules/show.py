#!/usr/bin/python

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
        self.parser.add_option("-p", "--port", dest="port",
                               default=DEFAULT_PORT)


    def parse(self, argv):
        self.argc = argv
        return command.Command.parse(self.argv)

    def do(self,args):
        client_obj = client.Client(self.server_spec,port=self.port,interactive=True,
                                   verbose=self.verbose, config=self.config)
        


class Show(client.command.Command):
    name = "show"
    useage = "various simple report stuff"
    subCommands = [ShowHardware]
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
        print "do args", args
        return "bar"
#        client_obj = client.Client(self.server_spec,port=self.port,interactive=True,
#            verbose=self.verbose, config=self.config)
#        results = client_obj.run(self.module, self.method, self.method_args)

        # TO DO: add multiplexer support
        # probably as a higher level module.

        # dump the return code stuff atm till we figure out the right place for it
#        return self.format_return(results)


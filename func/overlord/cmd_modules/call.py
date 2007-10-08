#!/usr/bin/python

import optparse

from func.overlord import command
from func.overlord import client

DEFAULT_PORT = 51234

class Call(client.command.Command):
    name = "call"
    useage = "call nodule method name arg1 arg2..."
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true")
        self.parser.add_option("-p", "--port", dest="port",
            default=DEFAULT_PORT)

    def handleOptions(self, options):
        print "self.parentCommand", self.parentCommand
        
        self.options = options

        self.verbose = options.verbose
        self.port = options.port
        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def parse(self, argv):
        self.argv = argv

        print "self.argv,", self.argv

        # FIXME? not sure this is good or bad, but it seems
        # wronky... we try to grab the hostnamegoo from the
        # args to the parentCommand
        self.server_spec = self.argv[0]
        
        return command.Command.parse(self, argv)

    def do(self, args):

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

        print "ARGS", args
        self.module      = args[1]
        self.method      = args[2]
        self.method_args = args[3:]

        client_obj = client.Client(self.server_spec,port=self.port,interactive=True,
            verbose=self.verbose, config=self.config)
        results = client_obj.run(self.module, self.method, self.method_args)

        # TO DO: add multiplexer support
        # probably as a higher level module.

        return client_obj.cli_return(results)

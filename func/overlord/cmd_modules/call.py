#!/usr/bin/python

import optparse
import pprint
import xmlrpclib

from func.overlord import command
from func.overlord import client

DEFAULT_PORT = 51234

class Call(client.command.Command):
    name = "call"
    useage = "call nodule method name arg1 arg2..."
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               action="store_true")
        self.parser.add_option("-x", "--xmlrpc", dest="xmlrpc",
                               action="store_true")
        self.parser.add_option("", "--pprint", dest="pprint",
                               action="store_true")
        self.parser.add_option("-j", "--json", dest="json",
                               action="store_true")
        self.parser.add_option("-p", "--port", dest="port",
                               default=DEFAULT_PORT)

    def handleOptions(self, options):
        self.options = options

        self.verbose = options.verbose
        self.port = options.port

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def parse(self, argv):
        self.argv = argv

        return command.Command.parse(self, argv)
        

    def format_return(self, data):
        if self.options.xmlrpc:
            return xmlrpclib.dumps((data,""))

        if self.options.pprint:
            return pprint.pformat(data)

        if self.options.json:
            try:
                import simplejson
                return simplejson.dumps(data)
            except ImportError:
                print "json support not found"
                return data

        return data

    def do(self, args):

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

        # I kind of feel like we shouldn't be parsing args here, but I'm
        # not sure what the write place is -al;
        self.module      = args[0]
        self.method      = args[1]
        self.method_args = args[2:]

        # this could get weird, sub sub classes might be calling this
        # this with multiple.parentCommand.parentCommands...
        # maybe command.py needs a way to set attrs on subCommands?
        # or some sort of shared datastruct?
        self.server_spec = self.parentCommand.server_spec

        client_obj = client.Client(self.server_spec,port=self.port,interactive=True,
            verbose=self.verbose, config=self.config)
        results = client_obj.run(self.module, self.method, self.method_args)

        # TO DO: add multiplexer support
        # probably as a higher level module.

        # dump the return code stuff atm till we figure out the right place for it
        return self.format_return(results)

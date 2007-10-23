#!/usr/bin/python

import glob
import sys


import command

#FIXME: need a plug-in runtime module loader here
from cmd_modules import call
from cmd_modules import show
from cmd_modules import copyfile

from func.overlord import client

class FuncCommandLine(command.Command):
    name = "func"
    useage = "func is the commandline interface to a func minion"

    subCommandClasses = [call.Call, show.Show,
                         copyfile.CopyFile]

    def __init__(self):

        command.Command.__init__(self)

    def do(self, args):
        pass

    def addOptions(self):
        self.parser.add_option('', '--version', action="store_true",
            help="show version information")
        self.parser.add_option("--list-minions", dest="list_minions",
            action="store_true", help="list all available minions")

    def handleArguments(self, args):
        server_string = args[0]
        # try to be clever about this for now
        if client.isServer(server_string):
            self.server_spec = server_string
            args.pop(0)
        # if it doesn't look like server, assume it
        # is a sub command? that seems wrong, what about
        # typo's and such? How to catch that? -akl
        # maybe a class variable self.data on Command?

    def handleOptions(self, options):
        if options.version:
            #FIXME
            print "version is NOT IMPLEMENTED YET"
        if options.list_minions:
            self.list_minions()

            sys.exit(0) # stop execution

    def list_minions(self):
        print "Minions:"
        gloob = "%s/%s.cert" % (self.config.certroot, "*")
        certs = glob.glob(gloob)
        for cert in certs:
            host = cert.replace(self.config.certroot, "")[1:-5]
            print "   %s" % host

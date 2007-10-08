#!/usr/bin/python

import glob
import sys


import command
from cmd_modules import call

class FuncCommandLine(command.Command):
    name = "client"
    useage = "func is the commandline interface to a func minion"

    subCommandClasses = [call.Call]

    def __init__(self):

        command.Command.__init__(self)

    def do(self, args):
        pass

    def addOptions(self):
        self.parser.add_option('', '--version', action="store_true",
            help="show version information")
        self.parser.add_option("--list-minions", dest="list_minions",
            action="store_true", help="list all available minions")

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

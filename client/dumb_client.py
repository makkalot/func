#!/usr/bin/python


# all the cool kids would use optparse instead
import getopt
import sys
import xmlrpclib


verbose = 0

try:
    opts, args = getopt.getopt(sys.argv, "hvs:",
                               ["help",
                                "verbose",
                                "server="])
except getopt.error, e:
    print _("Error parsing list arguments: %s") % e
    self.print_help()
    # FIXME: error handling
    

server = "http://127.0.0.1:51234"
for (opt, val) in opts:
    if opt in ["-h", "--help"]:
        self.print_help()
        sys.exit()
    if opt in ["-v", "--verbose"]:
        verbose = verbose + 1
    if opt in ["-s", "--server"]:
        server = val

s = xmlrpclib.ServerProxy(server)

args = args[1:]
method = args[0]
print "calling %s with args: %s" % (method, args[1:])

# thats some pretty code right there aint it? -akl
# we can't call "call" on s, since thats a rpc, so
# we call gettatr around it. 
print getattr(s, method)(*args[1:])

#!/usr/bin/python


# all the cool kids would use optparse instead
import getopt
import sys
import xmlrpclib

myname, argv = sys.argv[0], sys.argv[1:]

def usage():
    return "Usage: %s [ --help ] [ --verbose ] [ --server=http://hostname:port ] method arg1 [ ... ]" % myname

verbose = 0
server = "http://127.0.0.1:51234"

try:
    opts, args = getopt.getopt(argv, "hvs:",
                               ["help",
                                "verbose",
                                "server="])
except getopt.error, e:
    print _("Error parsing list arguments: %s") % e
    print usage()
    sys.exit()
    
for (opt, val) in opts:
    print "opt = %s, val = %s" % (opt, val)
    if opt in ["-h", "--help"]:
        print usage()
        sys.exit()
    if opt in ["-v", "--verbose"]:
        verbose = verbose + 1
    if opt in ["-s", "--server"]:
        server = val

if len(args) < 1:
    print usage()
    sys.exit()

s = xmlrpclib.ServerProxy(server)

method = args[0]
print "calling %s with args: %s" % (method, args[1:])

# thats some pretty code right there aint it? -akl
# we can't call "call" on s, since thats a rpc, so
# we call gettatr around it. 
print getattr(s, method)(*args[1:])


#!/usr/bin/python

##
## func command line interface & client lib
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
## +AUTHORS
## 
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import optparse
import sys
import glob
import pprint

from func.commonconfig import CMConfig
from func.config import read_config, CONFIG_FILE
import sslclient

import command

# ===================================
# defaults
# TO DO: some of this may want to come from config later

DEFAULT_PORT = 51234
FUNC_USAGE = "Usage: %s [ --help ] [ --verbose ] target.example.org module method arg1 [...]"

# ===================================

class CommandAutomagic(object):
    """
    This allows a client object to act as if it were one machine, when in
    reality it represents many.
    """

    def __init__(self, clientref, base):
        self.base = base
        self.clientref = clientref

    def __getattr__(self,name):
        base2 = self.base[:]
        base2.append(name)
        return CommandAutomagic(self.clientref, base2)

    def __call__(self, *args):
        if not self.base:
            raise AttributeError("something wrong here")
        if len(self.base) < 2:
            raise AttributeError("no method called: %s" % ".".join(self.base))
        module = self.base[0]
        method = ".".join(self.base[1:])
        return self.clientref.run(module,method,args)

# ===================================

class Client(object):

    def __init__(self, server_spec, port=DEFAULT_PORT, interactive=False,
        verbose=False, noglobs=False, config=None):
        """
        Constructor.
        @server_spec -- something like "*.example.org" or "foosball"
        @port -- is the port where all funcd processes should be contacted
        @verbose -- whether to print unneccessary things
        @noglobs -- specifies server_spec is not a glob, and run should return single values
        @config -- optional config object
        """
        self.config  = config
        if config is None:
            self.config  = read_config(CONFIG_FILE, CMConfig)

        self.server_spec = server_spec
        self.port        = port
        self.verbose     = verbose
        self.interactive = interactive
        self.noglobs     = noglobs
        self.servers     = self.expand_servers(self.server_spec)
       
        # default cert/ca/key is the same as the certmaster ca - need to
        # be able to change that on the cli
        self.key = '%s/funcmaster.key' % self.config.cadir
        self.cert = '%s/funcmaster.crt' % self.config.cadir
        # yes, they're the same, that's the point
        self.ca = '%s/funcmaster.crt' % self.config.cadir

    # -----------------------------------------------

    def expand_servers(self,spec):
        """
        Given a regex/blob of servers, expand to a list
        of server ids.
        """

        if self.noglobs:
            return [ "https://%s:%s" % (spec, self.port) ]

        all_hosts = []
        all_certs = []
        seperate_gloobs = spec.split(";")
        for each_gloob in seperate_gloobs:
            actual_gloob = "%s/%s.cert" % (self.config.certroot, each_gloob)
            certs = glob.glob(actual_gloob)
            for cert in certs:
                all_certs.append(cert)
                host = cert.replace(self.config.certroot,"")[1:-5]
                all_hosts.append(host)

        all_urls = []
        for x in all_hosts:
            all_urls.append("https://%s:%s" % (x, self.port))

        if self.verbose and len(all_urls) == 0:
            sys.stderr.write("no hosts matched\n")

        return all_urls

    # -----------------------------------------------

    def __getattr__(self, name):
        """
        This getattr allows manipulation of the object as if it were
        a XMLRPC handle to a single machine, when in reality it is a handle
        to an unspecified number of machines.

        So, it enables stuff like this:
   
        Client("*.example.org").yum.install("foo")

        # WARNING: any missing values in Client's source will yield
        # strange errors with this engaged.  Be aware of that.
        """
   
        return CommandAutomagic(self, [name])

    # -----------------------------------------------

    def run(self, module, method, args):
        """
        Invoke a remote method on one or more servers.
        Run returns a hash, the keys are server names, the values are the
        returns.

        The returns may include exception objects.
        If Client() was constructed with noglobs=True, the return is instead
        just a single value, not a hash.
        """

        results = {}

        for server in self.servers:

            conn = sslclient.FuncServer(server, self.key, self.cert, self.ca )
            # conn = xmlrpclib.ServerProxy(server)

            if self.interactive:
                sys.stderr.write("on %s running %s %s (%s)\n" % (server,
                    module, method, ",".join(args)))

            # FIXME: support userland command subclassing only if a module
            # is present, otherwise run as follows.  -- MPD

            try:
                # thats some pretty code right there aint it? -akl
                # we can't call "call" on s, since thats a rpc, so
                # we call gettatr around it. 
                meth = "%s.%s" % (module, method)
                retval = getattr(conn, meth)(*args[:])
                if self.interactive:
                    pprint.pprint(retval) 
            except Exception, e:
                retval = e 
                if self.interactive:
                    sys.stderr.write("remote exception on %s: %s\n" %
                        (server, str(e)))

            if self.noglobs:
                return retval
            else:
                left = server.rfind("/")+1
                right = server.rfind(":")
                server_name = server[left:right]
                results[server_name] = retval

        return results

   # ----------------------------------------------- 

    def cli_return(self,results):
        """
        As the return code list could return strings and exceptions
        and all sorts of crazy stuff, reduce it down to a simple
        integer return.  It may not be useful but we need one.
        """
        numbers = []
        for x in results.keys():
            # faults are the most important
            if type(x) == Exception:
                return -911
            # then pay attention to numbers
            if type(x) == int:
                numbers.append(x)

        # if there were no numbers, assume 0
        if len(numbers) == 0:
            return 0

        # if there were numbers, return the highest
        # (presumably the worst error code
        max = -9999
        for x in numbers:
            if x > max:
                max = x
        return max

# ===================================================================

class Call(command.Command):
    name = "call"
    useage = "call nodule method name arg1 arg2..."
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
            action="store_true")
        self.parser.add_option("-p", "--port", dest="port",
            default=DEFAULT_PORT)

    def handleOptions(self, options):
        self.options = options

        self.verbose = options.verbose
        self.port = options.port
        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def do(self, args):

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

        self.server_spec = args[0]
        self.module      = args[1]
        self.method      = args[2]
        self.method_args = args[3:]

        client = Client(self.server_spec,port=self.port,interactive=True,
            verbose=self.verbose, config=self.config)
        results = client.run(self.module, self.method, self.method_args)
    
        # TO DO: add multiplexer support
        # probably as a higher level module.

        return client.cli_return(results)

class FuncCommandLine(command.Command):
    name = "client"
    useage = "func is the commandline interface to a func minion"

    subCommandClasses = [Call]
    
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

    # -----------------------------------------------

    def list_minions(self):
        print "Minions:"
        gloob = "%s/%s.cert" % (self.config.certroot, "*")
        certs = glob.glob(gloob)
        for cert in certs:
            host = cert.replace(self.config.certroot, "")[1:-5]
            print "   %s" % host

# ===================================================================

if __name__ == "__main__":
    # this is what /usr/bin/func will run
    myname, argv = sys.argv[0], sys.argv[1:]
    cli = FuncCommandLine()
    rc = cli.do()
    sys.exit(rc)
#    cli = FuncCommandLine(myname,argv)

#    rc = cli.run()
    sys.exit(rc)



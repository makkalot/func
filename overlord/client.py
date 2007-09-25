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
import xmlrpclib
import traceback

# ===================================
# defaults
# TO DO: some of this may want to come from config later

DEFAULT_PORT = 51234
FUNC_USAGE = "Usage: %s [ --help ] [ --verbose ] target.example.org module method arg1 [...]"

# ===================================

class Client():

   def __init__(self, server_spec, port=DEFAULT_PORT, verbose=False, silent=False):
       """
       Constructor.  
       server_spec is something like "*.example.org" or "foosball"
       everything else optional and mostly self explanatory.
       """

       self.server_spec = server_spec
       self.port        = port
       self.verbose     = verbose
       self.silent      = silent
       self.servers     = self.expand_servers(self.server_spec)

   # ----------------------------------------------- 

   def expand_servers(self,spec):
       """
       Given a regex/blob of servers, expand to a list
       of server ids.
       """

       # FIXME: currently globbing is not supported (yet)
       # needs knowledge of the tree of certs
       # will be done soon

       results = []

       # FIXME: add SSL
       results.append("http://%s:%s" % (spec, self.port))
       return results

   # ----------------------------------------------- 

   def run(self, module, method, args):
       """
       Invoke a remote method on one or more servers.
       """

       count = len(self.servers)
       results = []

       for server in self.servers:

           # FIXME: add SSL

           conn = xmlrpclib.ServerProxy(server)

           if self.verbose:
                sys.stderr.write("on %s running %s %s (%s)\n" % (server, module, method, ",".join(args)))

           # FIXME: support userland command subclassing only if a module
           # is present, otherwise run as follows.  -- MPD

           try:
                # thats some pretty code right there aint it? -akl
                # we can't call "call" on s, since thats a rpc, so
                # we call gettatr around it. 
                meth = "%s.%s" % (module, method)
                retval = getattr(conn, meth)(*args[:])
                if not self.silent:
                    print retval 
           except Exception, e:
                retval = e 
                if not self.silent:
                    sys.stderr.write("remote exception on %s: %s\n" % (server, str(e)))

           results.append(retval)

       return results

   # ----------------------------------------------- 

   def cli_return(self,results):
       """
       As the return code list could return strings and exceptions
       and all sorts of crazy stuff, reduce it down to a simple
       integer return.  It may not be useful but we need one.
       """
       nonzeros = []
       for x in results:         
           # faults are the most important
           if type(x) == Exception:
               return -911
           # then pay attention to non-zeros
           if type(x) == int:
               nonzeros.append(x)    
       if len(nonzeros) > 0:
           return nonzeros[1]          
       return 0

# ===================================================================

class FuncCommandLine():

    def __init__(self,myname,args):
        """
        Constructor.  Takes name of program + arguments.
        """
        self.myname       = myname
        self.args         = args
        self.verbose      = 0
        self.server_spec  = None
        self.port         = DEFAULT_PORT

    # ----------------------------------------------- 

    def usage(self):
        """
        Returns usage string for command line users.
        """
        return FUNC_USAGE % self.myname

    # ----------------------------------------------- 

    def run(self):
        """
        Engages the command line.
        """
        
        rc = self.parse_command_line()
        if rc != 0:
           return rc

        return self.run_command()

    # ----------------------------------------------- 

    def parse_command_line(self):
        """
        Parses the command line and loads up all the variables.
        """

        # parse options
        p = optparse.OptionParser()
        p.add_option("-v","--verbose",dest="verbose",action="store_true")
        p.add_option("-p","--port",dest="port",default=DEFAULT_PORT)
        (options, args) = p.parse_args(self.args)

        self.args    = args
        self.verbose = options.verbose
        self.port    = options.port
        # self.help  = options.help 

        # provided for free:
        # 
        #if self.help:
        #    print self.usage()
        #    return -411

        # process arguments
        # a good Klingon program does not have parameters
        # it has arguments, and it always wins them.

        if len(args) < 3:
            print self.usage()
            return -411

        self.server_spec = self.args[0]
        self.module      = self.args[1] 
        self.method      = self.args[2]
        self.method_args = self.args[3:]

        return 0

    # ----------------------------------------------- 

    def run_command(self):
        """
        Runs the actual command.
        """
        client = Client(self.server_spec,port=self.port,verbose=self.verbose)
        results = client.run(self.module, self.method, self.method_args)
    
        # TO DO: add multiplexer support
        # probably as a higher level module.
 
        return client.cli_return(results)

       
# ===================================================================


if __name__ == "__main__":
    # this is what /usr/bin/func will run
    myname, argv = sys.argv[0], sys.argv[1:]
    cli = FuncCommandLine(myname,argv)
    rc = cli.run()
    sys.exit(rc)



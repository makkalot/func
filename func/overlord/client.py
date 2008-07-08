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

import sys
import glob
import os
import yaml

from certmaster.commonconfig import CMConfig
from func.config import read_config, CONFIG_FILE

import sslclient

import command
import groups
import delegation_tools as dtools
import func.forkbomb as forkbomb
import func.jobthing as jobthing
import func.utils as utils
from func.CommonErrors import *

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

    def __init__(self, clientref, base, nforks=1):
        self.base = base
        self.clientref = clientref
        self.nforks = nforks

    def __getattr__(self,name):
        base2 = self.base[:]
        base2.append(name)
        return CommandAutomagic(self.clientref, base2, self.nforks)

    def __call__(self, *args):
        if not self.base:
            raise AttributeError("something wrong here")
        if len(self.base) < 2:
            raise AttributeError("no method called: %s" % ".".join(self.base))
        module = self.base[0]
        method = ".".join(self.base[1:])
        return self.clientref.run(module,method,args,nforks=self.nforks)


#def get_groups():    
#    group_class = groups.Groups()
#    return group_class.get_groups()


#def get_hosts_by_groupgoo(groups, groupgoo):
#    group_gloobs = groupgoo.split(':')
#    hosts = []
#    for group_gloob in group_gloobs:
#        if not group_gloob[0] == "@":
#            continue
#        if groups.has_key(group_gloob[1:]):
#            hosts = hosts + groups[group_gloob[1:]]
#        else:            
#            print "group %s not defined" % group_gloob
#    return hosts

# ===================================
# this is a module level def so we can use it and isServer() from
# other modules with a Overlord class

class Minions(object):
    def __init__(self, spec, port=51234, 
                 noglobs=None, verbose=None,
                 just_fqdns=False, groups_file=None,
                 delegate=False, minionmap={}):

        self.spec = spec
        self.port = port
        self.noglobs = noglobs
        self.verbose = verbose
        self.just_fqdns = just_fqdns
        self.delegate = delegate
        self.minionmap = minionmap

        self.config = read_config(CONFIG_FILE, CMConfig)
        self.group_class = groups.Groups(filename=groups_file)
        
        self.all_hosts = []
        self.all_certs = []
        self.all_urls = []

    def _get_new_hosts(self):
        self.new_hosts = self.group_class.get_hosts_by_groupgoo(self.spec)
        return self.new_hosts

    def _get_all_hosts(self):
        seperate_gloobs = self.spec.split(";")
        seperate_gloobs = seperate_gloobs + self.new_hosts
        for each_gloob in seperate_gloobs:
            actual_gloob = "%s/%s.cert" % (self.config.certroot, each_gloob)
            certs = glob.glob(actual_gloob)
            for cert in certs:
                self.all_certs.append(cert)
                host = cert.replace(self.config.certroot,"")[1:-5]
                self.all_hosts.append(host)
        return self.all_hosts

    def get_all_hosts(self):
        self._get_new_hosts()
        self._get_all_hosts()
        return self.all_hosts

    def get_urls(self):
        self._get_new_hosts()
        self._get_all_hosts()
        for host in self.all_hosts:
            if not self.just_fqdns:
                self.all_urls.append("https://%s:%s" % (host, self.port))
            else:
                self.all_urls.append(host)  
        
        if self.verbose and len(self.all_urls) == 0:
            sys.stderr.write("no hosts matched\n")

        return self.all_urls

    # FIXME: hmm, dont like this bit of the api... -al;
    def is_minion(self):
        self.get_urls()
        if len(self.all_urls) > 0:
            return True
        return False



# does the hostnamegoo actually expand to anything?
def is_minion(minion_string):
    minions = Minions(minion_string)
    return minions.is_minion()




class Overlord(object):

    def __init__(self, server_spec, port=DEFAULT_PORT, interactive=False,
        verbose=False, noglobs=False, nforks=1, config=None, async=False, init_ssl=True,
        delegate=True, mapfile="/var/lib/func/inventory/map"):
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
        self.nforks      = nforks
        self.async       = async
        self.delegate    = delegate
        self.mapfile     = mapfile
        
        self.minions_class = Minions(self.server_spec, port=self.port, noglobs=self.noglobs,verbose=self.verbose)
        self.minions = self.minions_class.get_urls()
        
        if self.delegate:
            try:
                mapstream = file(self.mapfile, 'r')
                self.minionmap = yaml.load(mapstream)
            except e:
                sys.stderr.write("mapfile load failed, switching delegation off")
                self.delegate = False
    
        if init_ssl:
            self.setup_ssl()
            
    def setup_ssl(self, client_key=None, client_cert=None, ca=None):
        # defaults go:
          # certmaster key, cert, ca
          # funcd key, cert, ca
          # raise FuncClientError
        ol_key = '%s/certmaster.key' % self.config.cadir
        ol_crt = '%s/certmaster.crt' % self.config.cadir
        myname = utils.get_hostname()

        # FIXME: should be config -akl?
        # maybe /etc/pki/func is a variable somewhere?
        fd_key = '/etc/pki/certmaster/%s.pem' % myname
        fd_crt = '/etc/pki/certmaster/%s.cert' % myname
        self.ca = '%s/certmaster.crt' % self.config.cadir
        if client_key and client_cert and ca:        
            if (os.access(client_key, os.R_OK) and os.access(client_cert, os.R_OK)
                            and os.access(ca, os.R_OK)):
                self.key = client_key
                self.cert = client_cert
                self.ca = ca
        # otherwise fall through our defaults
        elif os.access(ol_key, os.R_OK) and os.access(ol_crt, os.R_OK):
            self.key = ol_key
            self.cert = ol_crt
        elif os.access(fd_key, os.R_OK) and os.access(fd_crt, os.R_OK):
            self.key = fd_key
            self.cert = fd_crt
        else:
            raise Func_Client_Exception, 'Cannot read ssl credentials: ssl, cert, ca'
            

        
    
    def __getattr__(self, name):
        """
        This getattr allows manipulation of the object as if it were
        a XMLRPC handle to a single machine, when in reality it is a handle
        to an unspecified number of machines.

        So, it enables stuff like this:

        Overlord("*.example.org").yum.install("foo")

        # WARNING: any missing values in Overlord's source will yield
        # strange errors with this engaged.  Be aware of that.
        """

        return CommandAutomagic(self, [name], self.nforks)

    # -----------------------------------------------

    def job_status(self, jobid):
        """
        Use this to acquire status from jobs when using run with async client handles
        """
        return jobthing.job_status(jobid, client_class=Overlord)

    # -----------------------------------------------

    def run(self, module, method, args, nforks=1, *extraargs, **kwargs):
        """
        Invoke a remote method on one or more servers.
        Run returns a hash, the keys are server names, the values are the
        returns.

        The returns may include exception objects.
        If Overlord() was constructed with noglobs=True, the return is instead
        just a single value, not a hash.
        """
        
        #if not self.delegate: #delegation is turned off
        #    return self.run_nodelegate(module, method, args, nforks)
        #print self.minionmap
        return self.run_nodelegate(module,method,args,nforks)
        
        
    # -----------------------------------------------

    def run_nodelegate(self, module, method, args, nforks=1):
        """
        Invoke a remote method on one or more servers.
        Run returns a hash, the keys are server names, the values are the
        returns.

        The returns may include exception objects.
        If Overlord() was constructed with noglobs=True, the return is instead
        just a single value, not a hash.
        """

        results = {}

        def process_server(bucketnumber, buckets, server):
            
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

                # async calling signature has an "imaginary" prefix
                # so async.abc.def does abc.def as a background task.
                # see Wiki docs for details
                if self.async:
                    meth = "async.%s" % meth

                # this is the point at which we make the remote call.
                retval = getattr(conn, meth)(*args[:])

                if self.interactive:
                    print retval
            except Exception, e:
                (t, v, tb) = sys.exc_info()
                retval = utils.nice_exception(t,v,tb)
                if self.interactive:
                    sys.stderr.write("remote exception on %s: %s\n" %
                        (server, str(e)))

            if self.noglobs:
                return retval
            else:
                left = server.rfind("/")+1
                right = server.rfind(":")
                server_name = server[left:right]
                return (server_name, retval)
        
        if not self.noglobs:
            if self.nforks > 1 or self.async:
                # using forkbomb module to distribute job over multiple threads
                if not self.async:
                    results = forkbomb.batch_run(self.minions, process_server, nforks)
                else:
                    results = jobthing.batch_run(self.minions, process_server, nforks)
            else:
                # no need to go through the fork code, we can do this directly
                results = {}
                for x in self.minions:
                    (nkey,nvalue) = process_server(0, 0, x)
                    results[nkey] = nvalue    
        else:
            # globbing is not being used, but still need to make sure
            # URI is well formed.
#            expanded = expand_servers(self.server_spec, port=self.port, noglobs=True, verbose=self.verbose)[0]
            expanded_minions = Minions(self.server_spec, port=self.port, noglobs=True, verbose=self.verbose)
            minions = expanded_minions.get_urls()[0]
#            print minions
            results = process_server(0, 0, minions)

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


class Client(Overlord):
    def __init__(self, *args, **kwargs):
        Overlord.__init__(self, *args, **kwargs)
        # we can remove this if folks want -akl 
        print "Client() class is deprecated, please use the Overlord() class."
        

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
import time
import func.yaml as yaml

from certmaster.commonconfig import CMConfig
from certmaster import utils
from certmaster.config import read_config, CONFIG_FILE

import sslclient

import command
import groups
import delegation_tools as dtools
import func.forkbomb as forkbomb
import func.jobthing as jobthing
from func.CommonErrors import *
import func.module_loader as module_loader
from func.overlord import overlord_module

# ===================================
# defaults
# TO DO: some of this may want to come from config later

DEFAULT_PORT = 51234
FUNC_USAGE = "Usage: %s [ --help ] [ --verbose ] target.example.org module method arg1 [...]"
DEFAULT_MAPLOC = "/var/lib/func/map"
DELEGATION_METH = "delegation.run"

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
        self.new_hosts = self.group_class.get_hosts_by_group_glob(self.spec)
        return self.new_hosts

    def _get_all_hosts(self):
        seperate_gloobs = self.spec.split(";")
        seperate_gloobs = seperate_gloobs + self.new_hosts
        for each_gloob in seperate_gloobs:
            #if there is some string from group glob just skip it
            if each_gloob.startswith('@'):
                continue
            actual_gloob = "%s/%s.%s" % (self.config.certroot, each_gloob, self.config.cert_extension)
            certs = glob.glob(actual_gloob)
            for cert in certs:
                #if the spec includes some groups and also it includes some *
                #may cause some duplicates so should check that
                #For example spec = "@home_group;*" will give lots of duplicates as a result
                if not cert in self.all_certs:
                    self.all_certs.append(cert)
		    # use basename to trim off any excess /'s, fix
		    # ticket #53 "Trailing slash in certmaster.conf confuses glob function
                    certname = os.path.basename(cert.replace(self.config.certroot, ""))
                    host = certname[:-(len(self.config.cert_extension) + 1)]
                    self.all_hosts.append(host)

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
        delegate=False, mapfile=DEFAULT_MAPLOC):
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
        if len(self.minions) == 0:
            raise Func_Client_Exception, 'Can\'t find any minions matching \"%s\". ' % self.server_spec
        
        if self.delegate:
            try:
                mapstream = file(self.mapfile, 'r').read()
                self.minionmap = yaml.load(mapstream).next()
            except e:
                sys.stderr.write("mapfile load failed, switching delegation off")
                self.delegate = False
    
        if init_ssl:
            self.setup_ssl()

        self.methods = module_loader.load_methods('func/overlord/modules/', overlord_module.BaseModule, self)
            
    def setup_ssl(self, client_key=None, client_cert=None, ca=None):
        # defaults go:
          # certmaster key, cert, ca
          # funcd key, cert, ca
          # raise FuncClientError
        ol_key = '%s/certmaster.key' % self.config.cadir
        ol_crt = '%s/certmaster.crt' % self.config.cadir
        myname = utils.get_hostname(talk_to_certmaster=False)

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
            raise Func_Client_Exception, 'Cannot read ssl credentials: ssl, cert, ca. '+\
                  'Ensure you have permission to read files in /etc/pki/certmaster/ directory.'
            

        
    
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

    def open_job_ids(self):
        """
        That method can be used by other apps that uses func API
        to get current ids with their short results in the database
        """
        return jobthing.get_open_ids()
    
    def list_minions(self, format='list'):
        """
        Returns a flat list containing the minions this Overlord object currently
        controls
        """
        if self.delegate:
            return dtools.match_glob_in_tree(self.server_spec, self.minionmap)
        minionlist = [] #nasty ugly hack to remove duplicate minions from list
        for minion in self.minions_class.get_all_hosts():
            if minion not in minionlist: #ugh, brute force :(
                minionlist.append(minion)
        return minionlist
        
    # -----------------------------------------------

    def run(self, module, method, args, nforks=1):
        """
        Invoke a remote method on one or more servers.
        Run returns a hash, the keys are server names, the values are the
        returns.

        The returns may include exception objects.
        If Overlord() was constructed with noglobs=True, the return is instead
        just a single value, not a hash.
        """

        if module == "local":
            if method in self.methods.keys():
                return self.methods[method](*args)
            else:
                raise AttributeError("No such local method: %s" % method)

        if not self.delegate: #delegation is turned off, so run normally
            return self.run_direct(module, method, args, nforks)
        
        delegatedhash = {}
        directhash = {}
        completedhash = {}
        
        #First we get all call paths for minions not directly beneath this overlord
        dele_paths = dtools.get_paths_for_glob(self.server_spec, self.minionmap)
        
        #Then we group them together in a dictionary by a common next hop
        (single_paths,grouped_paths) = dtools.group_paths(dele_paths)
        
        for group in grouped_paths.keys():
            delegatedhash.update(self.run_direct(module,
                                              method,
                                              args,
                                              nforks,
                                              call_path=grouped_paths[group],
                                              suboverlord=group))
        
        #Next, we run everything that can be run directly beneath this overlord
        #Why do we do this after delegation calls?  Imagine what happens when
        #reboot is called...
        directhash.update(self.run_direct(module,method,args,nforks))
        
        #poll async results if we've async turned on
        if self.async:
            while (len(delegatedhash) + len(directhash)) > 0:
                for minion in delegatedhash.keys():
                    results = delegatedhash[minion]
                    (return_code, async_results) = self.job_status(results)
                    if return_code == jobthing.JOB_ID_RUNNING:
                        pass
                    elif return_code == jobthing.JOB_ID_PARTIAL:
                        pass
                    else:
                        completedhash.update(async_results[minion])
                        del delegatedhash[minion]
                
                for minion in directhash.keys():
                    results = directhash[minion]
                    (return_code, async_results) = self.job_status(results)
                    if return_code == jobthing.JOB_ID_RUNNING:
                        pass
                    elif return_code == jobthing.JOB_ID_PARTIAL:
                        pass
                    else:
                        completedhash.update(async_results)
                        del directhash[minion]
                time.sleep(0.1) #pause a bit so we don't flood our minions
            return completedhash
        
        #we didn't instantiate this Overlord in async mode, so we just return the
        #result hash
        completedhash.update(delegatedhash)
        completedhash.update(directhash)
        return completedhash
        
        
    # -----------------------------------------------

    def run_direct(self, module, method, args, nforks=1, *extraargs, **kwargs):
        """
        Invoke a remote method on one or more servers.
        Run returns a hash, the keys are server names, the values are the
        returns.

        The returns may include exception objects.
        If Overlord() was constructed with noglobs=True, the return is instead
        just a single value, not a hash.
        """

        results = {}
        spec = ''
        minionurls = []
        use_delegate = False
        delegation_path = []
        
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
                if use_delegate:
                    meth = DELEGATION_METH #call delegation module
                else:
                    meth = "%s.%s" % (module, method)

                # async calling signature has an "imaginary" prefix
                # so async.abc.def does abc.def as a background task.
                # see Wiki docs for details
                if self.async:
                    meth = "async.%s" % meth

                # this is the point at which we make the remote call.
                if use_delegate:
                    retval = getattr(conn, meth)(module,
                                                 method, 
                                                 args,
                                                 delegation_path,
                                                 self.async,
                                                 self.nforks)
                else:
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
        
        if kwargs.has_key('call_path'): #we're delegating if this key exists
            delegation_path = kwargs['call_path']
            spec = kwargs['suboverlord'] #the sub-overlord directly beneath this one
            minionobj = Minions(spec, port=self.port, verbose=self.verbose)
            use_delegate = True #signal to process_server to call delegate method
            minionurls = minionobj.get_urls() #the single-item url list to make async
                                              #tools such as jobthing/forkbomb happy
        else: #we're directly calling minions, so treat everything normally
            spec = self.server_spec
            minionurls = self.minions
            #print "Minion_url is :",minionurls
            #print "Process server is :",process_server
        
        if not self.noglobs:
            if self.nforks > 1 or self.async:
                # using forkbomb module to distribute job over multiple threads
                if not self.async:
                   
                    results = forkbomb.batch_run(minionurls, process_server, nforks)
                else:
                    minion_info =dict(spec=spec,module=module,method=method)
                    results = jobthing.batch_run(minionurls, process_server,nforks,**minion_info)
            else:
                # no need to go through the fork code, we can do this directly
                results = {}
                for x in minionurls:
                    (nkey,nvalue) = process_server(0, 0, x)
                    results[nkey] = nvalue    
        else:
            # globbing is not being used, but still need to make sure
            # URI is well formed.
#            expanded = expand_servers(self.server_spec, port=self.port, noglobs=True, verbose=self.verbose)[0]
            expanded_minions = Minions(spec, port=self.port, noglobs=True, verbose=self.verbose)
            minions = expanded_minions.get_urls()[0]
            results = process_server(0, 0, minions)
        
        if self.delegate and self.async:
            return {spec:results}
        
        if use_delegate:
            if utils.is_error(results[spec]):
                print results
                return results
            return results[spec]
        
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
        # provided for backward compatibility only 

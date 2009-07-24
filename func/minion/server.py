"""
func

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

# standard modules
import SimpleXMLRPCServer
import string
import sys
import traceback
import fnmatch

from gettext import textdomain
I18N_DOMAIN = "func"


from certmaster.config import read_config
from func.commonconfig import FuncdConfig
from certmaster.commonconfig import CMConfig
from func import logger
from certmaster import certs
import func.jobthing as jobthing
from func import utils as func_utils

# our modules
import AuthedXMLRPCServer
import codes
import func.module_loader as module_loader
import func.minion.acls as acls_mod
from func import utils as futils


from certmaster import utils
from certmaster import requester


class XmlRpcInterface(object):

    def __init__(self):

        """
        Constructor.
        """

        cm_config_file = '/etc/certmaster/minion.conf'
        self.cm_config = read_config(cm_config_file, CMConfig)
        config_file = "/etc/func/minion.conf"
        self.config = read_config(config_file, FuncdConfig)

        self.logger = logger.Logger().logger
        self.audit_logger = logger.AuditLogger()
        self.__setup_handlers()


        # need a reference so we can log ip's, certs, etc
        # self.server = server

    def __setup_handlers(self):

        """
        Add RPC functions from each class to the global list so they can be called.
        """

        self.handlers = {}
        for x in self.modules.keys():
            try:
                self.modules[x].register_rpc(self.handlers, x)
                self.logger.debug("adding %s" % x)
            except AttributeError, e:
                self.logger.warning("module %s not loaded, missing register_rpc method" % self.modules[x])

        # internal methods that we do instead of spreading internal goo
        # all over the modules. For now, at lest -akl


        # system.listMethods os a quasi stanard xmlrpc method, so
        # thats why it has a odd looking name
        self.handlers["system.listMethods"] = self.list_methods
        self.handlers["system.list_methods"] = self.list_methods
        self.handlers["system.list_modules"] = self.list_modules
        self.handlers["system.inventory"] = self.inventory
        self.handlers["system.grep"] = self.grep

    def list_modules(self):
        modules = self.modules.keys()
        modules.sort()
        return modules

    def list_methods(self):
        methods = self.handlers.keys()
        methods.sort()
        return methods
    
    
    import func.minion.modules.func_module as fm
    @fm.findout
    def grep(self,word):
        """
        Finding the wanted word
        """

        word = word.strip()
        modules = self.modules.keys()
        methods = self.handlers.keys()
        
        return_dict = {}
        
        #find modules
        for m in modules:
            if m.find(word)!=-1:
                return_dict[self.list_modules]=m

        #find methods
        for m in methods:
            if m.find(word)!=-1:
                return_dict[self.list_methods]=m

        return return_dict


    def inventory(self):
        inventory = {}

        # FIXME: it's kind of dumb that we dont have a real object
        # to represent which methods are in which classes, just a list
        # of modules, and a list of methods. we can match strings to
        # see which are where, but that seems lame -akl
        for module in self.modules.keys():
            inventory[module] = []
            for method in self.handlers.keys():
                # string match, ick. 
                method_bits = method.split('.')
                method_module = string.join(method_bits[:-1], '.')
                method_name = method_bits[-1]
                if method_module == module:
                    inventory[module].append(method_name)

        return inventory



    def get_dispatch_method(self, method):

        if method in self.handlers:
            return FuncApiMethod(self.logger, method, self.handlers[method])

        else:
            self.logger.info("Unhandled method call for method: %s " % method)
            raise codes.InvalidMethodException


class FuncApiMethod:

    """
    Used to hold a reference to all of the registered functions.
    """

    def __init__(self, logger, name, method):

        self.logger = logger
        self.__method = method
        self.__name = name

    def __log_exc(self):

        """
        Log an exception.
        """

        (t, v, tb) = sys.exc_info()
        self.logger.info("Exception occured: %s" % t )
        self.logger.info("Exception value: %s" % v)
        self.logger.info("Exception Info:\n%s" % string.join(traceback.format_list(traceback.extract_tb(tb))))

    def __call__(self, *args):

        self.logger.debug("(X) -------------------------------------------")

        try:
            self.__method = futils.get_fresh_method_instance(self.__method)
            rc = self.__method(*args)
        except codes.FuncException, e:
            self.__log_exc()
            (t, v, tb) = sys.exc_info()
            rc = utils.nice_exception(t,v,tb)
        except:
            self.__log_exc()
            (t, v, tb) = sys.exc_info()
            rc = utils.nice_exception(t,v,tb)
        self.logger.debug("Return code for %s: %s" % (self.__name, rc))

        return rc


def serve():

    """
    Code for starting the XMLRPC service.
    """
    config = read_config("/etc/func/minion.conf", FuncdConfig)
    listen_addr = config.listen_addr
    listen_port = config.listen_port
    if listen_port == '':
        listen_port = 51234
    server =FuncSSLXMLRPCServer((listen_addr, listen_port))
    server.logRequests = 0 # don't print stuff to console
    server.serve_forever()



class FuncXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer, XmlRpcInterface):

    def __init__(self, args):

        self.allow_reuse_address = True

        self.modules = module_loader.load_modules()
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, args)
        XmlRpcInterface.__init__(self)

from func.minion.facts.minion_query import *
class FuncSSLXMLRPCServer(AuthedXMLRPCServer.AuthedSSLXMLRPCServer,
                          XmlRpcInterface):
    def __init__(self, args):
        self.allow_reuse_address = True
        self.modules = module_loader.load_modules()
        
        #load facts methods
        self.fact_methods = load_fact_methods()
        self.minion_query = FactsMinion(method_fact_list=self.fact_methods) 

        XmlRpcInterface.__init__(self)
        hn = func_utils.get_hostname_by_route()

        self.key = "%s/%s.pem" % (self.cm_config.cert_dir, hn)
        self.cert = "%s/%s.cert" % (self.cm_config.cert_dir, hn)
        self.ca = "%s/ca.cert" % self.cm_config.cert_dir
        
        self._our_ca = certs.retrieve_cert_from_file(self.ca)

        self.acls = acls_mod.Acls(config=self.config)
        
        AuthedXMLRPCServer.AuthedSSLXMLRPCServer.__init__(self, args,
                                                          self.key, self.cert,
                                                          self.ca)

    def _dispatch(self, method, params):

        """
        the SimpleXMLRPCServer class will call _dispatch if it doesn't
        find a handler method
        """
        # take _this_request and hand it off to check out the acls of the method
        # being called vs the requesting host
        
        if not hasattr(self, '_this_request'):
            raise codes.InvalidMethodException
            
        r,a = self._this_request
        peer_cert = r.get_peer_certificate()
        ip = a[0]
        

        # generally calling conventions are:  hardware.info
        # async convention is async.hardware.info
        # here we parse out the async to decide how to invoke it.
        # see the async docs on the Wiki for further info.
        async_dispatch = False
        if method.startswith("async."):
            async_dispatch = True
            method = method.replace("async.","",1)

        if not self.acls.check(self._our_ca, peer_cert, ip, method, params):
            raise codes.AccessToMethodDenied
            
        # Recognize ipython's tab completion calls
        if method == 'trait_names' or method == '_getAttributeNames':
            return self.handlers.keys()

        cn = peer_cert.get_subject().CN
        sub_hash = peer_cert.subject_name_hash()
        self.audit_logger.log_call(ip, cn, sub_hash, method, params)

        try:
            if not async_dispatch:
                #check if we send some queries 
                if len(params)>0 and type(params[0]) == dict and params[0].has_key('__fact__'):
                   fact_result = self.minion_query.exec_query(params[0]['__fact__'],True)
                else:
                    return self.get_dispatch_method(method)(*params)

                if fact_result[0]: #that means we have True from query so can go on
                    method_result = self.get_dispatch_method(method)(*params[1:])
                    return [{'__fact__':fact_result},method_result]
                else:
                    return [{'__fact__':fact_result}]
            else:
                return jobthing.minion_async_run(self.get_dispatch_method, method, params,self.minion_query)
        except:
            (t, v, tb) = sys.exc_info()
            rc = utils.nice_exception(t, v, tb)
            return rc

    def auth_cb(self, request, client_address):
        peer_cert = request.get_peer_certificate()
        return peer_cert.get_subject().CN
    

def excepthook(exctype, value, tracebackobj):
    exctype_blurb = "Exception occured: %s" % exctype
    excvalue_blurb = "Exception value: %s" % value
    exctb_blurb = "Exception Info:\n%s" % string.join(traceback.format_list(traceback.extract_tb(tracebackobj)))

    print exctype_blurb
    print excvalue_blurb
    print exctb_blurb

    log = logger.Logger().logger 
    log.info(exctype_blurb)
    log.info(excvalue_blurb)
    log.info(exctb_blurb)


def main(argv):

    """
    Start things up.
    """

    sys.excepthook = excepthook
    if len(sys.argv) > 1 and sys.argv[1] == "--list-modules":
        module_names = module_loader.load_modules().keys()
        module_names.sort()
        print "loaded modules:"
        for foo in module_names:
            print "\t" + foo
        sys.exit(0)

    if "--version" in sys.argv or "-v" in sys.argv:
        print >> sys.stderr, file("/etc/func/version").read().strip()
        sys.exit(0)

    if "daemon" in sys.argv or "--daemon" in sys.argv:
        utils.daemonize("/var/run/funcd.pid")
    else:
        print "serving...\n"

    try:
        hn = futils.get_hostname_by_route()
        requester.request_cert(hn)
        serve()
    except codes.FuncException, e:
        print >> sys.stderr, 'error: %s' % e
        sys.exit(1)


# ======================================================================================
if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)

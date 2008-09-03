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

# our modules
import AuthedXMLRPCServer
import codes
import func.module_loader as module_loader
import func.minion.acls as acls_mod

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

    def list_modules(self):
        modules = self.modules.keys()
        modules.sort()
        return modules

    def list_methods(self):
        methods = self.handlers.keys()
        methods.sort()
        return methods

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
    server =FuncSSLXMLRPCServer(('', 51234))
    server.logRequests = 0 # don't print stuff to console
    server.serve_forever()



class FuncXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer, XmlRpcInterface):

    def __init__(self, args):

        self.allow_reuse_address = True

        self.modules = module_loader.load_modules()
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, args)
        XmlRpcInterface.__init__(self)


class FuncSSLXMLRPCServer(AuthedXMLRPCServer.AuthedSSLXMLRPCServer,
                          XmlRpcInterface):
    def __init__(self, args):
        self.allow_reuse_address = True
        self.modules = module_loader.load_modules()

        XmlRpcInterface.__init__(self)
        hn = utils.get_hostname()
        self.key = "%s/%s.pem" % (self.cm_config.cert_dir, hn)
        self.cert = "%s/%s.cert" % (self.cm_config.cert_dir, hn)
        self.ca = "%s/ca.cert" % self.cm_config.cert_dir
        
        self._our_ca = certs.retrieve_cert_from_file(self.ca)

        self.acls = acls_mod.Acls(config=self.config)
        
        AuthedXMLRPCServer.AuthedSSLXMLRPCServer.__init__(self, ("", 51234),
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
                return self.get_dispatch_method(method)(*params)
            else:
                return jobthing.minion_async_run(self.get_dispatch_method, method, params)
        except:
            (t, v, tb) = sys.exc_info()
            rc = utils.nice_exception(t, v, tb)
            return rc

    def auth_cb(self, request, client_address):
        peer_cert = request.get_peer_certificate()
        return peer_cert.get_subject().CN
    

def main(argv):

    """
    Start things up.
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--list-modules":
        module_names = module_loader.load_modules().keys()
        module_names.sort()
        print "loaded modules:"
        for foo in module_names:
            print "\t" + foo
        sys.exit(0)

    if "daemon" in sys.argv or "--daemon" in sys.argv:
        utils.daemonize("/var/run/funcd.pid")
    else:
        print "serving...\n"

    try:
        requester.request_cert()
        serve()
    except codes.FuncException, e:
        print >> sys.stderr, 'error: %s' % e
        sys.exit(1)


# ======================================================================================
if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)

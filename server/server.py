#!/usr/bin/python

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
import socket
import sys
import traceback

from rhpl.translate import _, N_, textdomain, utf8
I18N_DOMAIN = "func"

# our modules
import codes
import config_data
import logger
import module_loader
import utils

# ======================================================================================

class XmlRpcInterface(object):

    def __init__(self, modules={}, server=None):

        """
        Constructor.
        """

        config_obj = config_data.Config()
        self.config = config_obj.get()
        self.modules = modules
        self.logger = logger.Logger().logger
        self.audit_logger = logger.AuditLogger()
        self.__setup_handlers()

        # need a reference so we can log ip's, certs, etc
        self.server = server
        
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

        self.handlers["system.listMethods"] = self.list_methods

    
    def list_methods(self):
        return self.handlers.keys()



    def get_dispatch_method(self, method):

        if method in self.handlers:
            return FuncApiMethod(self.logger, method, self.handlers[method])
      
        else:
            self.logger.info("Unhandled method call for method: %s " % method)
            raise codes.InvalidMethodException

    def _dispatch(self, method, params):

        """
        the SimpleXMLRPCServer class will call _dispatch if it doesn't
        find a handler method 
        """

        # Recognize ipython's tab completion calls
        if method == 'trait_names' or method == '_getAttributeNames':
            return self.handlers.keys()

        # XXX FIXME - need to figure out how to dig into the server base classes
        # so we can get client ip, and eventually cert id info -akl
        self.audit_logger.log_call(method, params)

        return self.get_dispatch_method(method)(*params)

# ======================================================================================

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
            rc = e
        except:
            self.logger.debug("Not a Func-specific exception")
            self.__log_exc()
            raise
        self.logger.debug("Return code for %s: %s" % (self.__name, rc))

        return rc

# ======================================================================================

def serve():

     """
     Code for starting the XMLRPC service. 
     FIXME:  make this HTTPS (see RRS code) and make accompanying Rails changes..
     """

     modules = module_loader.load_modules()

     server =FuncXMLRPCServer(('', 51234))
     server.logRequests = 0 # don't print stuff to console

     websvc = XmlRpcInterface(modules=modules,server=server)
     
     server.register_instance(websvc)
     server.serve_forever()

# ======================================================================================

class FuncXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):

    def __init__(self, args):

       self.allow_reuse_address = True
       SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, args)

# ======================================================================================
      
def main(argv):

    """
    Start things up.
    """

    modules = module_loader.load_modules()

    print "\n\n\n\n\n"
    print " WARNING WARNING WARNING"
    print "DANGER DANGER DANGER"
    print "\n\n\n\n"
    print "THERE IS NO AUTHENTICATION IN THIS VERSION"
    print "DO NOT RUN ON A MACHINE EXPOSED TO ANYONE YOU DO NOT TRUST"
    print " THEY CAN DO VERY BAD THINGS"
    print "\n\n\n\n\n"
    print "Really, don't do that. It is not at all secure at the moment"
    print "like, at all."
    print ""
    print "Seriously.\n\n"

    try:
        serve()
    except codes.FuncException, e:
        print >> sys.stderr, 'error: %s' % e
        sys.exit(1)

    if "daemon" in sys.argv or "--daemon" in sys.argv:
        utils.daemonize("/var/run/vf_server.pid")
    else:
        print "serving...\n"

       
# ======================================================================================

if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)



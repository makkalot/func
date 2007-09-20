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
import os
import subprocess
import socket
from rhpl.translate import _, N_, textdomain, utf8
I18N_DOMAIN = "vf_server"

# our modules
from codes import *
import config_data
import logger
import module_loader
import utils

# ======================================================================================

class XmlRpcInterface(object):

    def __init__(self, modules={}):

        """
        Constructor.
        """

        config_obj = config_data.Config()
        self.config = config_obj.get()
        self.modules = modules
        self.logger = logger.Logger().logger
        self.__setup_handlers()
        
    def __setup_handlers(self):

        """
        Add RPC functions from each class to the global list so they can be called.
        """

        self.handlers = {}
        for x in self.modules.keys():
            try:
                self.modules[x].register_rpc(self.handlers)
                self.logger.debug("adding %s" % x)
            except AttributeError, e:
                self.logger.warning("module %s not loaded, missing register_rpc method" % modules[x])


    def get_dispatch_method(self, method):

        if method in self.handlers:
            return FuncApiMethod(self.logger, method, self.handlers[method])
      
        else:
            self.logger.info("Unhandled method call for method: %s " % method)
            raise InvalidMethodException

    def _dispatch(self, method, params):

        """
        the SimpleXMLRPCServer class will call _dispatch if it doesn't
        find a handler method 
        """

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
        except FuncException, e:
            self.__log_exc()
            rc = e
        except:
            self.logger.debug("Not a Func-specific exception")
            self.__log_exc()
            raise
        self.logger.debug("Return code for %s: %s" % (self.__name, rc))

        return rc

# ======================================================================================

def serve(websvc):

     """
     Code for starting the XMLRPC service. 
     FIXME:  make this HTTPS (see RRS code) and make accompanying Rails changes..
     """

     server =FuncXMLRPCServer(('', 51234))
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
    print "modules", modules

    try:
        websvc = XmlRpcInterface(modules=modules)
    except FuncException, e:
        print >> sys.stderr, 'error: %s' % e
        sys.exit(1)

    if "daemon" in sys.argv or "--daemon" in sys.argv:
        utils.daemonize("/var/run/vf_server.pid")
    else:
        print "serving...\n"

    serve(websvc)
       
# ======================================================================================

if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)



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

import SimpleXMLRPCServer
import os
import subprocess
import socket

SERVE_ON = (None,None)

# FIXME: logrotate

from codes import *

import config_data
import logger
import module_loader
import utils


#from busrpc.services import RPCDispatcher
#from busrpc.config import DeploymentConfig

from rhpl.translate import _, N_, textdomain, utf8
I18N_DOMAIN = "vf_server"


class XmlRpcInterface(object):

    def __init__(self, modules={}):
        """
        Constructor sets up SQLAlchemy (database ORM) and logging.
        """
        config_obj = config_data.Config()
        self.config = config_obj.get()
       
        self.tables = {}
        self.tokens = []

        self.modules = modules

        self.logger = logger.Logger().logger
        
        self.__setup_handlers()
        
    def __setup_handlers(self):
        """
        Add RPC functions from each class to the global list so they can be called.
        FIXME: eventually calling most functions should go from here through getattr.
        """
        self.handlers = {}
        print "ffffffffffff", self.modules.keys()
        for x in self.modules.keys():
            print "x", x
            try:
                self.modules[x].register_rpc(self.handlers)
                self.logger.debug("adding %s" % x)
            except AttributeError, e:
                self.logger.warning("module %s could not be loaded, it did not have a register_rpc method" % modules[x])


        # FIXME: find some more elegant way to surface the handlers?
        # FIXME: aforementioned login/session token requirement

    def get_dispatch_method(self, method):
        if method in self.handlers:
            return FuncApiMethod(self.logger, method,
                               self.handlers[method])
      
        else:
            self.logger.info("Unhandled method call for method: %s " % method)
            raise InvalidMethodException

    def _dispatch(self, method, params):
        """
        the SimpleXMLRPCServer class will call _dispatch if it doesn't
        find a handler method 
        """
        return self.get_dispatch_method(method)(*params)

class BusRpcWrapper:
    
    def __init__(self, config):
        self.rpc_interface = None

    def __getattr__(self, name):
        if self.rpc_interface == None:
            self.rpc_interface = XmlRpcInterface()
        return self.rpc_interface.get_dispatch_method(name)

    def __repr__(self):
        return ("<BusRpcWrapper>")

class FuncApiMethod:
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
            self.logger.debug("Not a virt-factory specific exception")
            self.__log_exc()
            raise
        rc = rc.to_datastruct()
        self.logger.debug("Return code for %s: %s" % (self.__name, rc))
        return rc


def serve(websvc):
     """
     Code for starting the XMLRPC service. 
     FIXME:  make this HTTPS (see RRS code) and make accompanying Rails changes..
     """
     server =FuncXMLRPCServer(('', 51234))
     server.register_instance(websvc)
     server.serve_forever()

def serve_qpid(config_path, register_with_bridge=False, is_bridge_server=False):
     """
     Code for starting the QPID RPC service. 
     """
     config = DeploymentConfig(config_path)
     dispatcher = RPCDispatcher(config, register_with_bridge, is_bridge_server=is_bridge_server)
     
     try:
         dispatcher.start()
     except KeyboardInterrupt:
         dispatcher.stop()
     print "Exiting..."

class FuncXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self, args):
       self.allow_reuse_address = True
       SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, args)
      
def main(argv):
    """
    Start things up.
    """


    module_path=None
    
    for arg in sys.argv:
        if arg == "import" or arg == "--import":
            prov_obj = provisioning.Provisioning()
            prov_obj.init(None, {})
            return
        elif arg == "sync" or arg == "--sync":
            prov_obj = provisioning.Provisioning()
            prov_obj.sync(None, {}) # just for testing
            return
        elif arg in ["debug", "--debug", "-d"]:
            # basically, run from the src tree instead of
            # using the installed modules
            module_path="modules/"
            mod_path="server/"

    print "module_path_foo", module_path
    modules = module_loader.load_modules(module_path=module_path)
    print "modules", modules


    websvc = XmlRpcInterface(modules=modules)

    if "qpid" in sys.argv or "--qpid" in sys.argv:
        if "daemon" in sys.argv or "--daemon" in sys.argv:
            utils.daemonize("/var/run/vf_server_qpid.pid")
        else:
            print "serving...\n"
        serve_qpid("/etc/virt-factory/qpid.conf")
    else:
        if "daemon" in sys.argv or "--daemon" in sys.argv:
            utils.daemonize("/var/run/vf_server.pid")
        else:
            print "serving...\n"
            # daemonize only if --daemonize, because I forget to type "debug" -- MPD
        serve(websvc)
       
# FIXME: upgrades?  database upgrade logic would be nice to have here, as would general creation (?)
# FIXME: command line way to add a distro would be nice to have in the future, rsync import is a bit heavy handed.
#        (and might not be enough for RHEL, but is good for Fedora/Centos)


if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)



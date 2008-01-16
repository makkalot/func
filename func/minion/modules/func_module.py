##
## Copyright 2007, Red Hat, Inc
## see AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import inspect

from func import logger
from func.config import read_config
from func.commonconfig import FuncdConfig


class FuncModule(object):

    # the version is meant to
    version = "0.0.0"
    api_version = "0.0.0"
    description = "No Description provided"

    def __init__(self):

        config_file = '/etc/func/minion.conf'
        self.config = read_config(config_file, FuncdConfig)
        self.__init_log()
        self.__base_methods = {
            # __'s so we don't clobber useful names
            "module_version" : self.__module_version,
            "module_api_version" : self.__module_api_version,
            "module_description" : self.__module_description,
            "list_methods"       : self.__list_methods
        }

    def __init_log(self):
        log = logger.Logger()
        self.logger = log.logger

    def register_rpc(self, handlers, module_name):
        # add the internal methods, note that this means they
        # can get clobbbered by subclass versions
        for meth in self.__base_methods:
            handlers["%s.%s" % (module_name, meth)] = self.__base_methods[meth]

        # register our module's handlers
        for name, handler in self.__list_handlers().items():
            handlers["%s.%s" % (module_name, name)] = handler

    def __list_handlers(self):
        """ Return a dict of { handler_name, method, ... }.
        All methods that do not being with an underscore will be exposed.
        We also make sure to not expose our register_rpc method.
        """
        handlers = {}
        for attr in dir(self):
            if inspect.ismethod(getattr(self, attr)) and attr[0] != '_' and \
                    attr != 'register_rpc':
                handlers[attr] = getattr(self, attr)
        return handlers

    def __list_methods(self):
        return self.__list_handlers().keys() + self.__base_methods.keys()

    def __module_version(self):
        return self.version

    def __module_api_version(self):
        return self.api_version

    def __module_description(self):
        return self.description

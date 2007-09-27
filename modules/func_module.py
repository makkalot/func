#!/usr/bin/python

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


from func import config_data
from func import logger


class FuncModule(object):

    # the version is meant to
    version = "0.0.0"
    api_version = "0.0.0"
    description = "No Description provided"
    
    def __init__(self):

        config_obj = config_data.Config()
        config_result = config_obj.get()
        self.config = config_result
        self.__init_log()
        self.__base_methods = {
            # __'s so we don't clobber useful names
            "module_version" : self.__module_version,
            "module_api_version" : self.__module_api_version,
            "module_description" : self.__module_description,
            }
        
    def __init_log(self):
        log = logger.Logger()
        self.logger = log.logger
    
    def register_rpc(self, handlers, module_name):
        # add the internal methods, note that this means they
        # can get clobbbered by subclass versions
        for meth in self.__base_methods:
            handlers["%s.%s" % (module_name, meth)] = self.__base_methods[meth]
        for meth in self.methods:
            handlers["%s.%s" % (module_name,meth)] = self.methods[meth]

#    def list_methods(self):
#        return self.methods.keys() + self.__base_methods.keys()

    def __module_version(self):
        return self.version

    def __module_api_version(self):
        return self.api_version

    def __module_description(self):
        return self.description


methods = FuncModule()
register_rpc = methods.register_rpc

#!/usr/bin/python

## Virt-factory backend code.
##
## Copyright 2006, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com
## Adrian Likins <alikins@redhat.com
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##


import logging
import config_data


# from the comments in http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type, *args, **kwargs)
        return type._the_instance

# logging is weird, we don't want to setup multiple handlers
# so make sure we do that mess only once
class Logger(Singleton):
    __no_handlers = True
    def __init__(self, logfilepath ="/var/log/virt-factory/svclog"):

        self.config = config_data.Config().get()     
        if self.config.has_key("loglevel"):
           self.loglevel = logging._levelNames[self.config["loglevel"]]
        else:
           self.loglevel = logging.INFO   
        self.__setup_logging()
        if self.__no_handlers:
            self.__setup_handlers(logfilepath=logfilepath)
        
    def __setup_logging(self):
        self.logger = logging.getLogger("svc")

    def __setup_handlers(self, logfilepath="/var/log/virt-factory/svclog"):
        handler = logging.FileHandler(logfilepath, "a")
        self.logger.setLevel(self.loglevel)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.__no_handlers = False


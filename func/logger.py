## func
##
## Copyright 2007, Red Hat, Inc
## See AUTHORS
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
import os

from certmaster.config import read_config
from func.commonconfig import FuncdConfig


# from the comments in http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
class Singleton(object):
    def __new__(type, *args, **kwargs):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type, *args, **kwargs)
        return type._the_instance

# logging is weird, we don't want to setup multiple handlers
# so make sure we do that mess only once

class Logger(Singleton):
    _no_handlers = True

    def __init__(self, logfilepath ="/var/log/func/func.log"):
        config_file = '/etc/func/minion.conf'
        self.config = read_config(config_file, FuncdConfig)    
        self.loglevel = logging._levelNames[self.config.log_level]
        self._setup_logging()
        if self._no_handlers:
            self._setup_handlers(logfilepath=logfilepath)
        
    def _setup_logging(self):
        self.logger = logging.getLogger("svc")

    def _setup_handlers(self, logfilepath="/var/log/func/func.log"):

        # we try to log module loading and whatnot, even if we aren't
        # root, so if we can't write to the log file, ignore it
        # this lets "--help" work as a user
        # https://fedorahosted.org/func/ticket/75
        if not os.access(logfilepath, os.W_OK):
            return

        handler = logging.FileHandler(logfilepath, "a")
        self.logger.setLevel(self.loglevel)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self._no_handlers = False


class AuditLogger(Singleton):
    _no_handlers = True
    def __init__(self, logfilepath = "/var/log/func/audit.log"):
        self.loglevel = logging.INFO
        self._setup_logging()
        if self._no_handlers:
            self._setup_handlers(logfilepath=logfilepath)

    def log_call(self, ip, CN, cert_hash, method, params):
        # square away a good parseable format at some point -akl
        self.logger.info("%s %s %s %s called with %s" % (ip, CN, cert_hash, method, params))


    def _setup_logging(self):
        self.logger = logging.getLogger("audit")

    def _setup_handlers(self, logfilepath="/var/log/func/audit.log"):
        handler = logging.FileHandler(logfilepath, "a")
        self.logger.setLevel(self.loglevel)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self._no_handlers = False

#some more dynamic logger handlers here
config_file = '/etc/func/minion.conf'
config = read_config(config_file, FuncdConfig)
GLOBAL_LOG_DIR = config.method_log_dir 
class StandartLogger(object):
    """
    It is just a proxy like object to the logging
    module so we control here the stuff
    """

    def __init__(self,handlers,app_name,**kwargs):
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)

        self.handlers = handlers
        self.__setup_handlers()

    def __setup_handlers(self):
        # a default case is to have a FileHandler for all that is what we want
        for handler in self.handlers:
            self.logger.addHandler(handler)
    
    def progress(self,current,all):
        """
        A method to log the progress of the 
        running method ...
        """
        self.logger.debug("Progress report %d/%d completed"%(current,all))
    
    def debug(self,msg):
        self.logger.debug(msg)
    def info(self,msg):
        self.logger.info(msg)
    def critical(self,msg):
        self.logger.critical(msg)
    def error(self,msg):
        self.logger.error(msg)
    def exception(self,msg):
        self.logger.exception(msg)
    def warn(self,msg):
        self.logger.warn(msg)

#----------------------------------HANDLERS------------------------------------------------
class AbstarctHandler(object):
    pass

class StandartHandler(AbstarctHandler):
    """
    Standart one just has a filehandler in it
    """
    def __init__(self,formatter,**kwargs):
        if kwargs.has_key('log_place'):
            self.log_place = "".join([kwargs['log_place']])
        log_f = os.path.join(GLOBAL_LOG_DIR,self.log_place)
        if not os.path.exists(os.path.split(log_f)[0]):
            os.mkdir(os.path.split(log_f)[0])

        self.handler = logging.FileHandler((log_f), "a")
        self.handler.setFormatter(formatter)

    def __getattr__(self,name):
        return getattr(self.handler,name)

#--- some formatters here ---
def standart_formatter():
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def exception_formatter():
    return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s")

#----------------------------------HANDLERS------------------------------------------------
STANDART_LOGGER = 0
EXCEPTION_LOGGER = 1

class LogFactory(object):
    
    @staticmethod
    def get_instance(type=STANDART_LOGGER,app_name="direct_log",log_place=None):
        if type == STANDART_LOGGER:
            if not log_place:
                log_place = "".join([app_name.strip()])
            sh = StandartHandler(standart_formatter(),log_place=log_place)
            logger = StandartLogger([sh.handler],app_name=app_name)
            return logger
        elif type == EXCEPTION_LOGGER:
            #we will add the prefixes here ok
            if not log_place:
                log_place = "".join([app_name.strip()])
            sh = StandartHandler(exception_formatter(),log_place=log_place)
            logger = StandartLogger([sh],app_name=app_name)
            return logger
        else:
            return None

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
from func.config import read_config
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

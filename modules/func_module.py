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

from codes import *

from server import config_data
from server import logger

import os
import threading
import time
import traceback


class FuncModule(object):
    def __init__(self):

        config_obj = config_data.Config()
        config_result = config_obj.get()
        self.config = config_result
        self.__init_log()
        
    def __init_log(self):
        log = logger.Logger()
        self.logger = log.logger
    
    def register_rpc(self, handlers, module_name):
        for meth in self.methods:
            handlers["%s.%s" % (module_name,meth)] = self.methods[meth]
            



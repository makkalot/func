#!/usr/bin/python

# func
#
# Copyright 2006, Red Hat, Inc
# see AUTHORS
#
# This software may be freely redistributed under the terms of the GNU
# general public license.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import codes

import os
import ConfigParser

CONFIG_FILE = "/etc/func/minion.conf"

class Config:

    # this class is a Borg
    __shared_state = {}
    has_read = False

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.ds = {}
        if not self.has_read:
            self.read()
            Config.has_read = True

    def read(self):

        if not os.path.exists(CONFIG_FILE):
            raise codes.FuncException("Missing %s" % CONFIG_FILE)

        cp = ConfigParser.ConfigParser()

        cp.read([CONFIG_FILE])
        
        self.ds["log_level"] = cp.get("general","log_level")
        self.ds["overlord_server"] = cp.get("general","overlord_server")
        self.ds["certmaster"] = cp.get("general", "certmaster")
        self.ds["cert_dir"] = cp.get("general", "cert_dir")
        
    def get(self):
        return self.ds



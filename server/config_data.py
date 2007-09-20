#!/usr/bin/python

# Virt-factory backend code.
#
# Copyright 2006, Red Hat, Inc
# Michael DeHaan <mdehaan@redhat.com>
# Scott Seago <sseago@redhat.com>
# Adrian Likins <alikins@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from codes import *

import os
import yaml

CONFIG_FILE = "/etc/virt-factory/settings"

# from the comments in http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
#class Singleton(object):
#    def __new__(type):
#        if not '_the_instance' in type.__dict__:
#            type._the_instance = object.__new__(type)
#        return type._the_instance


class Config:

    # this class is a Borg
    __shared_state = {}
    has_read = False

    def __init__(self):
        self.__dict__ = self.__shared_state
        if not self.has_read:
            self.read()
            print "***** CONFIG RELOAD *****"
            Config.has_read = True

    def read(self):
        if not os.path.exists(CONFIG_FILE):
            raise MisconfiguredException(comment="Missing %s" % CONFIG_FILE)
        config_file = open(CONFIG_FILE)
        data = config_file.read()
        self.ds = yaml.load(data).next()
   

    def get(self):
        return self.ds



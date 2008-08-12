## -*- coding: utf-8 -*-
##
## Process lister (control TBA)
##
## Copyright 2008, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

# our modules
import func_module
from certmaster import certmaster as certmaster

# =================================

class CertMasterModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Administers certs on an overlord."

    def get_hosts_to_sign(self):
        """
        ...
        """
        cm = certmaster.CertMaster()
        return cm.get_csrs_waiting()
        
    def get_signed_certs(self):
        """
        Returns a list of all signed certs on this minion
        """
        cm = certmaster.CertMaster()
        return cm.get_signed_certs()

    def sign_hosts(self, list_of_hosts):
        """
        ...
        """
        list_of_hosts = self.__listify(list_of_hosts)
        cm = certmaster.CertMaster()
        for x in list_of_hosts:
           cm.sign_this_csr(x)
        return True

    def cleanup_hosts(self, list_of_hosts):
        """
        ...
        """
        list_of_hosts = self.__listify(list_of_hosts)
        cm = certmaster.CertMaster()
        for x in list_of_hosts:
           cm.remove_this_cert(x)
        return True

    def __listify(self, list_of_hosts):
        if type(list_of_hosts) is type([]):
            return list_of_hosts
        else:
            return [ list_of_hosts ]

    def register_method_args(self):
        """
        Export certmaster module 
        """

        list_of_hosts = {
                'type':'list',
                'optional':False,
                'description':'A list of hosts to apply the operation'
                }

        return {
                'get_hosts_to_sign':{
                    'args':{},
                    'description':"Returns a list of hosts to sign"
                    },
                'get_signed_certs':{
                    'args':{},
                    'description':"Get the certs you signed"
                    },
                'sign_hosts':{
                    'args':{
                        'list_of_hosts':list_of_hosts
                        },
                    'description':"Sign a list of hosts"
                    },
                'cleanup_hosts':{
                    'args':{
                        'list_of_hosts':list_of_hosts
                        },
                    'description':"Clean the certs for specified hosts"
                    }
                }

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

# other modules
import sub_process
import codes

# our modules
import func_module
from func import certmaster as certmaster

# =================================

class CertMasterModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Administers certs on an overlord."

    def get_hosts_to_sign(self, list_of_hosts):
        """
        ...
        """
        list_of_hosts = self.__listify(list_of_hosts)
        cm = certmaster.CertMaster()
        return cm.get_csrs_waiting()

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


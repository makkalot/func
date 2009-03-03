# Copyright 2008, Red Hat, Inc
# Steve Salevan <ssalevan@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module
import func.overlord.client as fc
from certmaster import certmaster as certmaster
from certmaster import utils as cm_utils
from func import utils as func_utils

class OverlordModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Module for controlling minions that are also overlords."

    def map_minions(self,get_only_alive=False):
        """
        Builds a recursive map of the minions currently assigned to this
        overlord
        """
        maphash = {}
        current_minions = []
        if get_only_alive:
            ping_results = fc.Overlord("*").test.ping()
            for minion in ping_results.keys():
                if ping_results[minion] == 1: #if minion is alive
                    current_minions.append(minion) #add it to the list
        else:
            cm = certmaster.CertMaster()
            current_minions = cm.get_signed_certs()
        for current_minion in current_minions:
            if current_minion in func_utils.get_hostname_by_route():
                maphash[current_minion] = {} #prevent infinite recursion
            else:
                next_hop = fc.Overlord(current_minion)
                mapresults = next_hop.overlord.map_minions()[current_minion]
                if not cm_utils.is_error(mapresults):
                    maphash[current_minion] = mapresults
                else:
                    maphash[current_minion] = {}
        return maphash

    def register_method_args(self):
        """
        Export overlord
        """
        return {
                'map_minions':{
                    'args':{
                        'get_only_alive':{
                            'type':'boolean',
                            'optional':True,
                            'default':True,
                            'description':"Get only online ones"
                            }
                        },
                    'description':"Builds a recursive map of the minions currently assigned to this minion overlord"
                    }
                }
        
    

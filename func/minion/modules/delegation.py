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
from func import utils

class DelegationModule(func_module.FuncModule):
    
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Minion-side module to support delegation on sub-Overlords."
    
    def run(self,module,method,args,delegation_path):
        """
        Delegates commands down the path of delegation
        supplied as an argument
        """
        
        next_hop = delegation_path[0]
        overlord = fc.Overlord(next_hop)
        if len(delegation_path) == 1: #minion exists under this overlord
            meth = "%s.%s" % (module, method)
            return getattr(overlord,meth)(*args[:])
        
        stripped_list = delegation_path[1:len(delegation_path)]
        delegation_results = overlord.delegation.run(module,method,args,stripped_list)
        return delegation_results[next_hop] #strip away nested hash data from results

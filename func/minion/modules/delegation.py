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
from func.overlord import delegation_tools as dtools

class DelegationModule(func_module.FuncModule):
    
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Minion-side module to support delegation on sub-Overlords."
    
    def run(self,module,method,args,delegation_list):
        """
        Delegates commands down the path of delegation
        supplied as an argument
        """
        result_dict = {}
        
        #separate list passed to us into minions we can call directly and 
        #further delegation paths
        (single_paths, grouped_paths) = dtools.group_paths(delegation_list)
        
        #run delegated calls
        for group in grouped_paths.keys():
            overlord = fc.Overlord(group)
            path_list = grouped_paths[group]
            delegation_results = overlord.delegation.run(module,method,args,path_list)
            result_dict.update(delegation_results[group]) #strip away nesting hash
        
        #run direct calls
        for minion in single_paths:
            overlord = fc.Overlord(minion)
            overlord_module = getattr(overlord,module)
            result_dict.update(getattr(overlord_module,method)(*args[:]))
        
        return result_dict 

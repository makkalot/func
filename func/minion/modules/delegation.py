# Copyright 2008, Red Hat, Inc
# Steve Salevan <ssalevan@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import time
import func_module
import func.overlord.client as fc
import func.jobthing as jobthing

from func import utils
from func.overlord import delegation_tools as dtools

#boolean value appended to job id list to denote direct/delegated calls
DIRECT = False
DELEGATED = True

class DelegationModule(func_module.FuncModule):
    
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Minion-side module to support delegation on sub-Overlords."
    
    def run(self,module,method,args,delegation_list,async,nforks):
        """
        Delegates commands down the path of delegation
        supplied as an argument
        """
        result_dict = {}
        job_id_list = []
        
        #separate list passed to us into minions we can call directly and 
        #further delegation paths
        (single_paths, grouped_paths) = dtools.group_paths(delegation_list)
        
        #run delegated calls
        for group in grouped_paths.keys():
            overlord = fc.Overlord(group,
                                   async=async,
                                   nforks=nforks)
            path_list = grouped_paths[group]
            delegation_results = overlord.delegation.run(module,
                                                         method,
                                                         args,
                                                         path_list,
                                                         async,
                                                         nforks)
            if async:
                job_id_list.append([overlord, 
                                    delegation_results,
                                    group,
                                    True])
            else:
                #These are delegated calls, so we need to strip away the
                #hash that surrounds the results
                if utils.is_error(delegation_results[group]):
                    result_dict.update(delegation_results)
                else:
                    result_dict.update(delegation_results[group])
        
        #run direct calls
        for minion in single_paths:
            overlord = fc.Overlord(minion, 
                                   async=async,
                                   nforks=nforks)
            overlord_module = getattr(overlord,module)
            results = getattr(overlord_module,method)(*args[:])
            if async:
                job_id_list.append([overlord,
                                    results,
                                    minion,
                                    False])
            else:
                result_dict.update(results)
        
        #poll async calls
        while len(job_id_list) > 0:
            for job in job_id_list:
                (return_code, async_results) = job[0].job_status(job[1])
                if return_code == jobthing.JOB_ID_RUNNING:
                    pass #it's still going, ignore it this cycle
                elif return_code == jobthing.JOB_ID_PARTIAL:
                    pass #yep, it's still rolling
                elif return_code == jobthing.JOB_ID_REMOTE_ERROR:
                    result_dict.update(async_results)
                    job_id_list.remove(job)
                else: #it's done or it's had an error, pass it up
                    if job[3] == DIRECT:
                        #this is a direct call, so we only need to
                        #update the hash with the pertinent results
                        results = async_results
                    elif job[3] == DELEGATED:
                        #this is a delegated call, so we need to strip
                        #away the nesting hash
                        results = async_results[job[2]]
                    else:
                        #and this code should never be reached
                        results = {}
                    result_dict.update(results)
                    job_id_list.remove(job)
            time.sleep(0.1) #pause a bit so that we don't flood our minions
        
        return result_dict 

##
## NetApp Filer 'vol.clone' Module
##
## Copyright 2008, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import re
from func.minion.modules import func_module
from func.minion.modules.netapp.common import *

class Clone(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'vol' command"

    def create(self, filer, vol, parent, snap):
        """
        TODO: Document me ...
        """
        regex = """Creation of clone volume .* has completed."""
        cmd_opts = ['vol', 'clone', 'create', vol, '-b', parent, snap]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)
    
    def split(self, filer, vol):
        """
        TODO: Document me ...
        """
        # only worry about 'start' now, I don't terribly care to automate the rest
        regex = """Clone volume .* will be split from its parent."""
        cmd_opts = ['vol', 'clone', 'split', 'start', vol]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    
    def register_method_args(self):
        """
        Implementing netapp.clone export
        """
        vol = {
                'type':'string',
                'optional':False,
                'description':"The name of the volume"
                }
        
        filer = {
                'type':'string',
                'optional':False,
                'description':"Resolvable name of the target filer"
                }
        
        snap = {
                'type':'string',
                'optional':False,
                'description':"The name of the snapshot"
                }

        return {
                'create':{
                    'args':{
                        'filer':filer,
                        'vol':vol,
                        'snap':snap,
                        'parent':{
                            'type':'string',
                            'optional':False,
                            'description':"The parent to clone"
                            }
                        },
                    'description':"Create a clone"
                    },
                'split':{
                    'args':{
                        'filer':filer,
                        'vol':vol
                        },
                    'description':"Split the vol"
                    }   
                }

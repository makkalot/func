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

    def create(self, filer, args):
        """
        TODO: Document me ...
        """
        regex = """Creation of clone volume .* has completed."""
        param_check(args, ['name', 'parent', 'snapshot'])
        
        cmd_opts = ['vol', 'clone', 'create']
        cmd_opts.extend([args['name'], '-b', args['parent'], args['snapshot']])

        output = ssh(filer, cmd_opts)
        return check_output(regex, output)
    
    def split(self, filer, args):
        """
        TODO: Document me ...
        """
        # only worry about 'start' now, I don't terribly care to automate the rest
        regex = """Clone volume .* will be split from its parent."""
        param_check(args, ['name'])

        cmd_opts = ['vol', 'clone', 'split', 'start', args['name']]

        output = ssh(filer, cmd_opts)
        return check_output(regex, output)




##
## NetApp Filer 'vol.clone' Module
##
## Copyright 2007, Red Hat, Inc
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
        return True
        regex = """Creation of volume .* has completed."""
        param_check(args, ['name', 'aggr', 'size'])
        
        cmd_opts = ['vol', 'create']
        cmd_opts.extend([args['name'], args['aggr'], args['size']])

        output = ssh('root', filer, cmd_opts)
        return check_output(regex, output)
    
    def split(self, filer, args):
        """
        TODO: Document me ...
        """
        return True


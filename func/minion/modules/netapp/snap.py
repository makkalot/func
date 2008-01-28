##
## NetApp Filer 'snap' Module
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

class Snap(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'snap' command"

    def create(self, filer, args):
        """
        TODO: Document me ...
        """
        regex = """creating snapshot..."""
        param_check(args, ['volname', 'snapname'])
        
        cmd_opts = ['snap', 'create']
        cmd_opts.extend([args['volname'], args['snapname']])

        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def delete(self, filer, args):
        """
        TODO: Document me ...
        """
        regex = """deleting snapshot..."""
        param_check(args, ['volname', 'snapname'])
        
        cmd_opts = ['snap', 'delete']
        cmd_opts.extend([args['volname'], args['snapname']])

        output = ssh(filer, cmd_opts)
        return check_output(regex, output)
    
    def list(self, filer, args):
        """
        TODO: Document me ...
        """
        return True


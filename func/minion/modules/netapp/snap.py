##
## NetApp Filer 'snap' Module
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

class Snap(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'snap' command"

    def create(self, filer, vol, snap):
        """
        TODO: Document me ...
        """
        regex = """creating snapshot..."""
        cmd_opts = ['snap', 'create', vol, snap]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)

    def delete(self, filer, vol, snap):
        """
        TODO: Document me ...
        """
        regex = """deleting snapshot..."""
        cmd_opts = ['snap', 'delete', vol, snap]
        output = ssh(filer, cmd_opts)
        return check_output(regex, output)
    
    def list(self, filer, vol):
        """
        TODO: Document me ...
        """
        return True


##
## NetApp Filer 'options' Module
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

from func.minion.modules import func_module
from func.minion.modules.netapp.common import *

class Options(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'options' command"

    def get(self, filer, filter=''):
        """
        TODO: Document me ...
        """
        cmd_opts = ['options', filter]
        output = ssh(filer, cmd_opts)
        if 'No such option' in output:
            return output.strip()

        result = {}
        for line in output.split('\n'):
            if not line: continue
            tokens = line.split()
            try:
                result[tokens[0]] = tokens[1]
            except:
                result[tokens[0]] = ''

        return result

    def set(self, filer, option, value):
        """
        TODO: Document me ...
        """
        cmd_opts = ['options', option, value]
        output = ssh(filer, cmd_opts)
        # should return no output (maybe a space or newline)
        return check_output("^\s*$", output)


    

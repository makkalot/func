# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
# Seth Vidal modified command.py to be nagios-check.py
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
Abitrary command execution module for func.
"""

from modules import func_module

import sub_process

class Nagios(func_module.FuncModule):

    def __init__(self):
        self.methods = {
                "run" : self.run
        }
        func_module.FuncModule.__init__(self)

    def run(self, check_name):
        """
        Runs a nagios check returning the return code, stdout, and stderr as a tuple.
        """
        nagios_path='/usr/lib/nagios/plugins'
        command = '%s/%s' % (nagios_path, check_name)
        
        cmdref = sub_process.Popen(command.split(),stdout=sub_process.PIPE,stderr=sub_process.PIPE, shell=False)
        data = cmdref.communicate()
        return (cmdref.returncode, data[0], data[1])

methods = Nagios()
register_rpc = methods.register_rpc



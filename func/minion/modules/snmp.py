# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
# Seth Vidal modified command.py to be snmp.py
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

import func_module
import sub_process
base_snmp_command = '/usr/bin/snmpget -v2c -Ov -OQ'

class Snmp(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "SNMP related calls through func."

    def get(self, oid, rocommunity, hostname='localhost'):
        """
        Runs an snmpget on a specific oid returns the output of the call.
        """
        command = '%s -c %s %s %s' % (base_snmp_command, rocommunity, hostname, oid)
        
        cmdref = sub_process.Popen(command.split(),stdout=sub_process.PIPE,stderr=sub_process.PIPE, shell=False)
        data = cmdref.communicate()
        return (cmdref.returncode, data[0], data[1])
        
    #def walk(self, oid, rocommunity):

    #def table(self, oid, rocommunity):

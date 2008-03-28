#
# Copyright 2008
# Krzysztof A. Adamski <krzysztofa@gmail.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# our modules
from func.minion.modules import func_module
from func.minion.modules.iptables.common import *

IPTABLES_SAVE_FILE = "/etc/sysconfig/iptables"

class Iptables(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "iptables module"

    def run(self, args):
        """
        Run 'iptables' command with arguments given. For example:
          > func '*' call iptables run "-L INPUT"
        """
        return run_iptables(args)

    def policy(self, chain="INPUT", policy=None):
        """
        Check/set default policy for the chain. Examples:
          * Check default policy for INPUT chain:
            > func '*' call iptables policy
            or
            > func '*' call iptables policy INPUT
          * Set default policy for OUTPUT:
            > func '*' call iptables policy OUTPUT DROP
        """
        if policy==None:
            return check_policy(chain)
        else:
            return set_policy(chain, policy)

    def flush(self, chain="INPUT"):
        """
        Flush the selected chain (or INPUT if none given).
        """
        return call_iptables("-F %s" % chain)

    def zero(self, chain="INPUT"):
        """
        Zero counters in selected chain (or INPUT if none given).
        """
        return call_iptables("-Z %s" % chain)

    def drop_from(self, ip):
        """
        Drop all incomming traffic from IP. Example:
          > func '*' call iptables drop_from 192.168.0.10
        """
        clear_all("-D INPUT -s %s -j ACCEPT" % ip)
        clear_all("-D INPUT -s %s -j REJECT" % ip)
        return call_if_policy("INPUT", "ACCEPT", "-I INPUT -s %s -j DROP" % ip)

    def reject_from(self, ip):
        """
        Reject all incoming traffic from IP. Example:
          > func '*' call iptables reject_from 192.168.0.10
        """
        clear_all("-D INPUT -s %s -j ACCEPT" % ip)
        clear_all("-D INPUT -s %s -j DROP" % ip)
        return call_iptables("-I INPUT -s %s -j REJECT" % ip)

    def accept_from(self, ip):
        """
        Accept all incoming traffic from IP. Example:
          > func '*' call iptables accept_from 192.168.0.10
        """
        clear_all("-D INPUT -s %s -j DROP" % ip)
        clear_all("-D INPUT -s %s -j REJECT" % ip)
        return call_if_policy("INPUT", "DROP", "-I INPUT -s %s -j ACCEPT" % ip)

    def drop_to(self, ip):
        """
        Drop all outgoing traffic to IP. Example:
          > func '*' call iptables drop_to 192.168.0.10
        """
        clear_all("-D OUTPUT -d %s -j ACCEPT" % ip)
        clear_all("-D OUTPUT -d %s -j REJECT" % ip)
        return call_if_policy("INPUT", "ACCEPT", "-I OUTPUT -d %s -j DROP" % ip)

    def reject_to(self, ip):
        """
        Drop all outgoing traffic to IP. Example:
          > func '*' call iptables reject_to 192.168.0.10
        """
        clear_all("-D OUTPUT -d %s -j ACCEPT" % ip)
        clear_all("-D OUTPUT -d %s -j DROP" % ip)
        return call_iptables("-I OUTPUT -d %s -j REJECT" % ip)

    def accept_to(self, ip):
        """
        Accept all outgoing traffic to IP. Example:
          > func '*' call iptables accept_to 192.168.0.10
        """
        clear_all("-D OUTPUT -d %s -j DROP" % ip)
        clear_all("-D OUTPUT -d %s -j REJECT" % ip)
        return call_if_policy("INPUT", "DROP", "-I OUTPUT -d %s -j ACCEPT" % ip)

    def inventory(self):
        return self.dump()

    def dump(self, counters=False):
        """
        Dump iptables configuration in iptables-save format.
        """
        args = []
        if counters:
            args.append("-c")

        cmd = sub_process.Popen(["/sbin/iptables-save"] + args,
                                executable="/sbin/iptables-save",
                                stdout=sub_process.PIPE,
                                stderr=sub_process.PIPE,
                                shell=False)

        data, error = cmd.communicate()

        return data

    def save(self, counters=False):
        """
        Save iptables state using '/sbin/iptables-save'. If counters=True,
        save counters too.
        TODO: maybe some locking?
        """
        f=open(IPTABLES_SAVE_FILE, 'w')
        f.write(self.dump(counters))
        f.close
        return True

    def panic(self):
        self.flush("")
        self.policy("INPUT", "DROP")
        self.policy("OUTPUT", "DROP")
        self.policy("FORWARD", "DROP")

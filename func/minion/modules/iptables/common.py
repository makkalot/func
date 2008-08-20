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

# other modules
from func.minion import sub_process

def run_iptables(args):
    cmd = sub_process.Popen(["/sbin/iptables"] + args.split(),
                            executable="/sbin/iptables",
                            stdout=sub_process.PIPE,
                            stderr=sub_process.PIPE,
                            shell=False)

    data, error = cmd.communicate()

    results = []
    for line in data.split("\n"):
        tokens = line.split()
        results.append(tokens)

    return results

def call_iptables(args):
    return sub_process.call(["/sbin/iptables"] + args.split(),
                            executable="/sbin/iptables",
                            shell=False)

def check_policy(chain):
    ret = run_iptables("-L %s" % chain)
    try:
        if ret[0][2] == "(policy":
            return ret[0][3][:-1]
        else:
            return False
    except:
        return False
        
def set_policy(chain, policy):
    return call_iptables("-P %s %s" % (chain, policy) )

def clear_all(arg):
    while not call_iptables(arg): pass

def call_if_policy(chain, policy, arg):
    if check_policy(chain) == policy:
        return call_iptables(arg)
    else:
        return 0

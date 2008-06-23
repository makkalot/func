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

class Port(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "iptables 'port' submodule"

    def drop_from(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Drop all incomming traffic from/to selected port. Arguments:
         * port - destination/source port
         * ip - source IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Drop all incoming traffic to local TCP port 80:
           > func '*' call iptables.port drop_from 80
         * Drop all incomming traffic to local UDP port 53 from 192.168.0.0/24:
           > func '*' call iptables.port drop_from 80 192.168.0.0/24 udp 
        """
        dir=parse_dir(dir)
        clear_all("-D INPUT -p %s --%sport %s -s %s -j ACCEPT" % (prot, dir, port, ip) )
        clear_all("-D INPUT -p %s --%sport %s -s %s -j REJECT" % (prot, dir, port, ip) )
        return call_if_policy("INPUT", "ACCEPT", "-I INPUT -p %s --%sport %s -s %s -j DROP" % (prot, dir, port, ip) )

    def reject_from(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Reject all outgoing traffic from/to port. Arguments:
         * port - destination/source port
         * ip - source IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Reject all incoming traffic to local TCP port 80:
           > func '*' call iptables.port reject_from 80
         * Reject incomming traffic to local UDP port 53 from 192.168.0.0/24:
           > func '*' call iptables.port reject_from 80 192.168.0.0/24 udp 
        """
        dir=parse_dir(dir)
        clear_all("-D INPUT -p %s --%sport %s -s %s -j ACCEPT" % (prot, dir, port, ip) )
        clear_all("-D INPUT -p %s --%sport %s -s %s -j DROP" % (prot, dir, port, ip) )
        return call_iptables("-I INPUT -p %s --%sport %s -s %s -j REJECT" % (prot, dir, port, ip) )

    def accept_from(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Accept all incomming traffic from/to port. Arguments:
         * port - destination/source port
         * ip - source IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Accept all incoming traffic to local TCP port 80:
           > func '*' call iptables.port accept_from 80
         * Accept incomming traffic to local UDP port 53 from 192.168.0.0/24:
           > func '*' call iptables.port accept_from 80 192.168.0.0/24 udp 
        """
        dir=parse_dir(dir)
        clear_all("-D INPUT -p %s --%sport %s -s %s -j DROP" % (prot, dir, port, ip) )
        clear_all("-D INPUT -p %s --%sport %s -s %s -j REJECT" % (prot, dir, port, ip) )
        return call_if_policy("INPUT", "DROP", "-I INPUT -p %s --%sport %s -s %s -j ACCEPT" % (prot, dir, port, ip) )

    def drop_to(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Drop all outgoing traffic going from/to port. Arguments:
         * port - destination/source port
         * ip - destination IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Drop outgoing traffic to TCP port 80 on 192.168.0.1:
           > func '*' call iptables.port drop_to 80 192.168.0.1
         * Drop outgoing traffic from UDP port 53 to 192.168.0.0/24:
           > func '*' call iptables.port drop_to 53 192.168.0.0/24 udp src
        """
        dir=parse_dir(dir)
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j ACCEPT" % (prot, dir, port, ip) )
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j REJECT" % (prot, dir, port, ip) )
        return call_if_policy("OUTPUT", "ACCEPT", "-I OUTPUT -p %s --%sport %s -d %s -j DROP" % (prot, dir, port, ip) )

    def reject_to(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Reject all outgoing traffic going from/to PORT. Arguments:
         * port - destination/source port
         * ip - destination IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Reject outgoing traffic to TCP port 80 on 192.168.0.1:
           > func '*' call iptables.port reject_to 80 192.168.0.1
         * Reject outgoing traffic from UDP port 53 to 192.168.0.0/24:
           > func '*' call iptables.port reject_to 53 192.168.0.0/24 udp src
        """
        dir=parse_dir(dir)
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j ACCEPT" % (prot, dir, port, ip) )
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j DROP" % (prot, dir, port, ip) )
        return call_iptables("-I OUTPUT -p %s --%sport %s -d %s -j REJECT" % (prot, dir, port, ip) )

    def accept_to(self, port, ip="0.0.0.0", prot="tcp", dir="dst"):
        """
        Accept all outgoing traffic going from/to PORT. Arguments:
         * port - destination/source port
         * ip - destination IP
         * prot - protocol (e.g. tcp/udp)
         * dir - direction, "dst" for matching destination port or "src" for matching source port
        Examples:
         * Accept outgoing traffic to TCP port 80 on 192.168.0.1:
           > func '*' call iptables.port accept_to 80 192.168.0.1
         * Accept outgoing traffic from UDP port 53 to 192.168.0.0/24:
           > func '*' call iptables.port accept_to 53 192.168.0.0/24 udp src
        """
        dir=parse_dir(dir)
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j DROP" % (prot, dir, port, ip) )
        clear_all("-D OUTPUT -p %s --%sport %s -d %s -j REJECT" % (prot, dir, port, ip) )
        return call_if_policy("OUTPUT", "DROP", "-I OUTPUT -p %s --%sport %s -d %s -j ACCEPT" % (prot, dir, port, ip) )

    def register_method_args(self):
        """
        Export the methods and their definitons
        """
        #they are all same so just declare here
        port={
                'type':'string',
                'optional':False,

                }
        ip={
                'type':'string',
                'optional':False,
                'default':'0.0.0.0'
                }
        prot={
                'type':'string',
                'options':['tcp','udp','icmp','sctp'],
                'default':'tcp',
                'optional':False
                }
        dir={
                'type':'string',
                'default':'dst',
                'options':['src','dst'],
                'optional':False
                }

        return {
                'drop_from':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        }
                    },
                'reject_from':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        
                        }
                    },
                'accept_from':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        
                        }
                    },
                'drop_to':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        
                        }
                    },
                 'reject_to':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        
                        }
                    },
                  'accept_to':{'args':
                    {
                        'ip':ip,
                        'prot':prot,
                        'dir':dir,
                        'port':port
                        
                        }
                    },
               
                }

def parse_dir(dir):
    if (dir == "dst"):
        return "d"
    elif (dir == "src"):
        return "s"
    else:
        raise exceptions.Exception("Wrong direction!")

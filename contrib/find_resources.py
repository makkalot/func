##
## Func cloud availability application.
## Given machine requirements, returns the best
## location in the cloud to run koan.
## Depends on the storage and virt modules.
##
## Copyright 2008, Red Hat, Inc
## Matt Hicks <mhicks@redhat.com>
## +AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import os.path
import optparse
import sys
import random
import func.overlord.client as func_client
import func.utils as utils

class FindResources(object):

    def __init__(self):
        pass 

    def run(self,args): 

        p = optparse.OptionParser()
        p.add_option("-v", "--verbose",
                     dest="verbose",
                     action="store_true",
                     help="provide extra output")
        p.add_option("-s", "--server-spec",
                     dest="server_spec",
                     default="*",
                     help="run against specific servers, default: '*'")
        p.add_option("-m", "--memory",
                     dest="memory",
                     default="512",
                     help="the memory requirements in megabytes, default: '512'")
        p.add_option("-d", "--disk",
                     dest="disk",
                     default="20",
                     help="the disk storage requirements in gigabytes, default: '20'")

        (options, args) = p.parse_args(args)
        self.options = options

        # convert the memory and storage to integers for later comparisons
        memory = int(options.memory)
        storage = int(options.disk)

        # see what hosts have enough RAM
        avail_hosts = {}
        host_freemem = func_client.Client(options.server_spec).virt.freemem()
        for (host, freemem) in host_freemem.iteritems():
            if utils.is_error(freemem):
                print "-- connection refused: %s" % host 
                continue 

            # Take an additional 256M off the freemem to keep
            # Domain-0 stable (shrinking it to 256M can cause
            # it to crash under load)
            if (freemem-256) >= memory:
                avail_hosts[host] = {'memory': freemem}

        # figure out which of these machines have enough storage
        for avail_host in avail_hosts.keys():
            # see what hosts have the required storage
            host_volume_groups = func_client.Client(avail_host).storage.vgs()
           
            for (host, vol_groups) in host_volume_groups.iteritems():
                if utils.is_error(vol_groups):
                    print "-- connection refused: %s" % host 
                    continue

                avail_vol_groups = []
                for vol_group, attrs in vol_groups.iteritems():
                    free_space = int(float(attrs['free'][:-1]))
                    if free_space >= storage:
                        avail_vol_groups.append((vol_group, free_space))
                
                if len(avail_vol_groups) > 0:
                    avail_hosts[host]['space'] = dict(avail_vol_groups)
                else:
                    avail_hosts.pop(host)

        # Default the dest_host to nothing
        dest_host = None

        if len(avail_hosts) > 0:
            # Find the host that is the closest memory match
            for (host, attrs) in avail_hosts.iteritems():
                # Use a random volume group
                vol_group = random.choice(attrs['space'].keys())

                if not dest_host:
                    dest_host = [host, vol_group, attrs['memory']]
                else:
                    if attrs['memory'] < dest_host[2]:
                        # Use the better match
                        dest_host = [host, vol_group, attrs['memory']]

        return dest_host

if __name__ == "__main__":
    inv = FindResources()
    inv.run(sys.argv)

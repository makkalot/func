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
        p.add_option("-a", "--arch",
                     dest="arch",
                     default="i386",
                     help="the architecture requirements, default: 'i386'")

        (options, args) = p.parse_args(args)
        self.options = options

        # convert the memory and storage to integers for later comparisons
        memory = int(options.memory)
        arch = options.arch

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

        # Default the dest_host to nothing
        dest_host = None

        # see what hosts have the right architecture
        arch_hosts = {}
        host_arch = func_client.Client(options.server_spec).command.run('uname -i')
        for (host, output) in host_arch.iteritems():
            if utils.is_error(output):
                print "-- connection refused: %s" % host
                continue

            host_arch = output[1].rstrip()

            # If the host_arch is 64 bit, allow 32 bit machines on it
            if host_arch == arch or (host_arch == "x86_64" and arch == "i386"):
                arch_hosts[host] = host

        if len(avail_hosts) > 0:
            # Find the host that is the closest memory match
            # and matching architecture
            for (host, attrs) in avail_hosts.iteritems():
                if arch_hosts.has_key(host):
                    if not dest_host:
                        dest_host = [host, attrs['memory']]
                    else:
                        if attrs['memory'] < dest_host[1]:
                            # Use the better match
                            dest_host = [host, attrs['memory']]

        return dest_host

if __name__ == "__main__":
    inv = FindResources()
    inv.run(sys.argv)

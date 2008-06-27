##
## func topology map-building tool
## If you've got a giant, tangled, complex web of func overlords
## and minions, this tool will help you construct or augment a map
## of your func network topology so that delegating commands to 
## minions and overlords becomes a simple matter.
##
## Copyright 2008, Red Hat, Inc.
## Steve Salevan <ssalevan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import optparse
import sys
import yaml
import func.overlord.client as func_client

DEFAULT_TREE = "/var/lib/func/inventory/map"

class MapperTool(object):

    def __init__(self):
        pass
    
    def run(self,args):
    
        p = optparse.OptionParser()
        #currently not implemented
        p.add_option("-a", "--append",
                     dest="append",
                     action="store_true",
                     help="append new map to current map")
        p.add_option("-r", "--rebuild",
                     dest="rebuild",
                     action="store_true",
                     help="rebuild map from scratch")
        p.add_option("-o", "--onlyalive",
                     dest="only_alive",
                     action="store_true",
                     help="gather only currently-living minions")
        p.add_option("-v", "--verbose",
                     dest="verbose",
                     action="store_true",
                     help="provide extra output")
                     
        (options, args) = p.parse_args(args)
        self.options = options
        
        if options.verbose:
            print "- recursively calling map function"
        
        self.build_map()
        
        return 1
        
    def build_map(self):
        
        minion_hash = func_client.Overlord("*").overlord.map_minions(self.options.only_alive==True)
        
        if self.options.verbose:
            print "- built the following map:"
            print minion_hash
            print "- writing to %s" % DEFAULT_TREE
        
        if not self.options.append:
            mapfile = file(DEFAULT_TREE, 'w')
            yaml.dump(minion_hash,mapfile)
        

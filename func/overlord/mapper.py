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
import func.yaml as yaml
import func.overlord.client as func_client

from func import utils

DEFAULT_TREE = "/var/lib/func/map"

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
        
        for minion in minion_hash.keys(): #clean hash of any top-level errors
            if utils.is_error(minion_hash[minion]):
                minion_hash[minion] = {}        

        if self.options.verbose:
            print "- built the following map:"
            print minion_hash
        
        if self.options.append:
            try:
                oldmap = file(DEFAULT_TREE, 'r').read()
                old_hash = yaml.load(oldmap).next()
                oldmap.close()
            except e:
                sys.stderr.write("ERROR: old map could not be read, append failed\n")
                sys.exit(-1)
                
            merged_map = {}
            merged_map.update(old_hash)
            merged_map.update(minion_hash)
            
            if self.options.verbose:
                print "- appended new map to the following map:"
                print old_hash
                print "  resulting in:"
                print merged_map
            
            minion_hash = merged_map
        
        if self.options.verbose:
            print "- writing to %s" % DEFAULT_TREE
        
        mapfile = file(DEFAULT_TREE, 'w')
        data = yaml.dump(minion_hash)
        mapfile.write(data)
         

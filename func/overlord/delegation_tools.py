##
## func delegation tools
## These are some helper methods to make dealing with delegation
## dictionary trees a little more sane when dealing with delegation
## and related functions.
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

import fnmatch

class groupby(object):
    """
    Borrowing the groupby iterator class directly 
    from the Python API as it does not exist in Pythons < 2.4
    """
    
    def __init__(self, iterable, key=None):
        if key is None:
            key = lambda x: x
        self.keyfunc = key
        self.it = iter(iterable)
        self.tgtkey = self.currkey = self.currvalue = xrange(0)
    def __iter__(self):
        return self
    def next(self): 
        while self.currkey == self.tgtkey:
            self.currvalue = self.it.next() # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)
        self.tgtkey = self.currkey
        return (self.currkey, self._grouper(self.tgtkey))
    def _grouper(self, tgtkey):
        while self.currkey == tgtkey:
            yield self.currvalue
            self.currvalue = self.it.next() # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)

def group_paths(ungrouped_list):
    """
    Given a list of multi-element path lists, 
    groups them together into a list of single-element paths (which
    exist directly under the current overlord) and a dictionary of paths
    to send to next hops in the delegation chain, containing a list of lists
    keyed by their common next hop.
    """
    
    single_paths = [path[0] for path in ungrouped_list if len(path) == 1]
    non_single_paths = [path for path in ungrouped_list if len(path) > 1]
    path_group = dict([(key,[path[1:len(path)] for path in list(gen)]) 
                       for key, gen in groupby(non_single_paths,
                                               key=lambda x:x[0])])
    
    return (single_paths,path_group)
                                          
def get_paths_for_glob(glob, minionmap):
    """
    Given a glob, returns shortest path to all minions
    matching it in the delegation dictionary tree
    """
    
    pathlist = []
    for elem in match_glob_in_tree(glob,minionmap):
        result = get_shortest_path(elem,minionmap)
        if result not in pathlist: #prevents duplicates
            pathlist.append(result)
    return pathlist

def list_all_minions(minionmap):
    """
    Given a minion map, returns a flat list of all minions
    contained within it
    """
    minionlist = []
    for minion in minionmap.keys():
        if minion not in minionlist:
            minionlist.append(minion)
        for minion in list_all_minions(minionmap[minion]):
            if minion not in minionlist:
                minionlist.append(minion)
    return minionlist

def flatten_list(bumpy_list):
    """
    Flattens gnarly nested lists into much
    nicer, flat lists
    """
    
    flat_list = []
    for item in bumpy_list:
        if isinstance(item, list):
            for elem in flatten_list(item):
                flat_list.append(elem)
        else:
            flat_list.append(item)
    return flat_list

def match_glob_on_toplevel(pattern, minionmap):
    """
    Searches through the top level of a dictionary
    for all keys (minion FQDNs) matching the given
    glob, returns matches
    """
    
    matched = []
    for k,v in minionmap.iteritems():
        if fnmatch.fnmatch(k,pattern):
            matched.append(k)
    return matched
    
def match_glob_in_tree(pattern, minionmap):
    """
    Searches through given tree dictionary for all
    keys (minion FQDNs) matching the given glob,
    returns matches
    """
    
    matched = []
    for k,v in minionmap.iteritems():
        for result in match_glob_in_tree(pattern, v):
            matched.append(result)
        if fnmatch.fnmatch(k,pattern):
            matched.append(k)
    return matched

def minion_exists_under_node(minion, minionmap):
    """
    A little wrapper around the match_glob_on_toplevel
    method that you can use if you want to get a boolean
    result denoting minion existence under your current
    node
    """
    
    return len(match_glob_on_toplevel(minion,minionmap)) > 0

def get_shortest_path(minion, minionmap):
    """
    Given a minion that exists in the given tree,
    this method returns all paths from the top
    node to the minion in the form of a flat list
    """
    
    def lensort(a,b):
        if len(a) > len(b):
            return 1
        return -1
    
    results = get_all_paths(minion,minionmap)
    results.sort(lensort)
    return results[0]

def get_all_paths(minion, minionmap):
    """
    Given a minion that exists in the given tree,
    this method returns all paths that exist from the top
    node to the minion in the delegation dictionary tree
    """
    
    #This is an ugly kludge of franken-code.  If someone with
    #more knowledge of graph theory than myself can improve this
    #module, please, please do so. - ssalevan 7/2/08
    seq_list = []
    
    if minion_exists_under_node(minion, minionmap):
        return [[minion]] #minion found, terminate branch
    
    if minionmap == {}:
        return [[]] #no minion found, terminate branch
        
    for k,v in minionmap.iteritems():
        branch_list = []
        branch_list.append(k)
        
        for branchlet in get_all_paths(minion, v):
            branch_list.append(branchlet)
        
        single_branch = flatten_list(branch_list)
        if minion in single_branch:
            seq_list.append(single_branch)
    
    return seq_list

if __name__ == "__main__":   
    mymap = {'anthony':{'longpath1':{'longpath2':{'longpath3':{}}}},
             'phil':{'steve':{'longpath3':{}}},
             'tony':{'mike':{'anthony':{}}},
             'just_a_minion':{}
            }
    
    print "- Testing an element that exists in multiple lists of varying length:"
    for elem in match_glob_in_tree('*path3',mymap):    
        print "Element: %s, all paths: %s" % (elem, get_all_paths(elem,mymap))
        print "best path: %s" % get_shortest_path(elem, mymap)
    
    print "- Testing an element that is simply a minion and has no sub-nodes:"
    for elem in match_glob_in_tree('*minion',mymap):
        print "Element: %s, best path: %s" % (elem, get_shortest_path(elem,mymap))
        
    print "- OK, now the whole thing:"
    for elem in match_glob_in_tree('*',mymap):
        print "Element: %s, best path: %s" % (elem, get_shortest_path(elem,mymap))
        
    print "- And finally, with all duplicates removed:"
    for elem in get_paths_for_glob('*',mymap):
        print "Valid Path: %s" % elem
        
    print "- And grouped together:"
    print group_paths(get_paths_for_glob('*',mymap))

# forkbomb is a module that partitions arbitrary workloads
# among N seperate forks, for a configurable N, and
# collates results upon return, as if it never forked.
#
# Copyright 2007, Red Hat, Inc
# Michael DeHaan <mdehaan@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import random # for testing only
import time   # for testing only
import shelve
import bsddb
import sys
import tempfile
import fcntl
import utils
import xmlrpclib

DEFAULT_FORKS = 4
DEFAULT_CACHE_DIR = "/var/lib/func"

def __get_storage(dir):
    """
    Return a tempfile we can use for storing data.
    """
    dir = os.path.expanduser(dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return tempfile.mktemp(suffix='', prefix='asynctmp', dir=dir)

def __access_buckets(filename,clear,new_key=None,new_value=None):
    """
    Access data in forkbomb cache, potentially clearing or
    modifying it as required.
    """

    internal_db = bsddb.btopen(filename, 'c', 0644 )
    handle = open(filename,"r")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    storage = shelve.BsdDbShelf(internal_db)

    if clear:
        storage.clear()
        storage.close()
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return {}

    if not storage.has_key("data"):
        storage["data"] = {}
    else: 
        pass

    if new_key is not None:
        # bsdb is a bit weird about this
        newish = storage["data"].copy()
        newish[new_key] = new_value
        storage["data"] = newish

    rc = storage["data"].copy()
    storage.close()
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    return rc

def __bucketize(pool, slots):
    """
    Given a pre-existing list of X number of tasks, partition
    them into a hash of Y number of slots.
    """
    buckets = {}
    count = 0
    for key in pool:
        count = count + 1
        slot = count % slots
        if not buckets.has_key(slot):
            buckets[slot] = [] 
        buckets[slot].append(key)
    return buckets

def __with_my_bucket(bucket_number,buckets,what_to_do,filename):
    """
    Process all tasks assigned to a given fork, and save
    them in the shelf.
    """
    things_in_my_bucket = buckets[bucket_number]
    results = {}
    for thing in things_in_my_bucket:
        (nkey,nvalue) = what_to_do(bucket_number,buckets,thing)
        __access_buckets(filename,False,nkey,nvalue)

def __forkbomb(mybucket,buckets,what_to_do,filename):
    """
    Recursive function to spawn of a lot of worker forks.
    """
    nbuckets = len(buckets)
    pid = os.fork()
    if pid != 0:
        if mybucket < (nbuckets-1):
            __forkbomb(mybucket+1,buckets,what_to_do,filename)
        try:
            os.waitpid(pid,0)
        except OSError, ose:
            if ose.errno == 10:
                pass
            else:
                raise ose
    else:
        __with_my_bucket(mybucket,buckets,what_to_do,filename)    
        sys.exit(0)

def __demo(bucket_number, buckets, my_item):
    """ 
    This is a demo handler for test purposes.
    It just multiplies all numbers by 1000, but slowly.
    """
    # print ">> I am fork (%s) and I am processing item (%s)" % (bucket_number, my_item)
    # just to verify forks are not sequential
    sleep = random.randrange(0,4)
    time.sleep(sleep)
    return (my_item, my_item * 1000)

def batch_run(pool,callback,nforks=DEFAULT_FORKS,cachedir=DEFAULT_CACHE_DIR):
    """
    Given an array of items (pool), call callback in each one, but divide
    the workload over nfork forks.  Temporary files used during the
    operation will be created in cachedir and subsequently deleted.    
    """
    if nforks <= 1:
       # modulus voodoo gets crazy otherwise and bad things happen
       nforks = 2
    shelf_file = __get_storage(cachedir)
    __access_buckets(shelf_file,True,None)
    buckets = __bucketize(pool, nforks)
    __forkbomb(1,buckets,callback,shelf_file)
    rc = __access_buckets(shelf_file,False,None)
    os.remove(shelf_file)
    return rc

def __test(nforks=4,sample_size=20):
    pool = xrange(0,sample_size)
    print batch_run(pool,__demo,nforks=nforks)

if __name__ == "__main__":
    __test()



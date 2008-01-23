# jobthing is a module that allows for background execution of a task, and
# getting status of that task.  The ultimate goal is to allow ajaxyness
# of GUI apps using Func, and also for extremely long running tasks that
# we don't want to block on as called by scripts using the FunC API.  The
# CLI should not use this.
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
import forkbomb

JOB_ID_RUNNING = 0
JOB_ID_FINISHED = 1
JOB_ID_LOST_IN_SPACE = 2

# how long to retain old job records in the job id database
RETAIN_INTERVAL = 60 * 60    

# where to store the internal job id database
CACHE_DIR = "/var/lib/func"

def __update_status(jobid, status, results, clear=False):
    return __access_status(jobid=jobid, status=status, results=results, write=True)

def __get_status(jobid):
    return __access_status(jobid=jobid, write=False)


def __purge_old_jobs(storage):
    """
    Deletes jobs older than RETAIN_INTERVAL seconds.  
    MINOR FIXME: this probably should be a more intelligent algorithm that only
    deletes jobs if the database is too big and then only the oldest jobs
    but this will work just as well.
    """
    nowtime = time.time()
    for x in storage.keys():
        create_time = float(x)
        if nowtime - create_time > RETAIN_INTERVAL:
            del storage[x]

def __access_status(jobid=0, status=0, results=0, clear=False, write=False):

    dir = os.path.expanduser(CACHE_DIR)
    if not os.path.exists(dir):
        os.makedirs(dir)
    filename = os.path.join(dir,"status-%s" % os.getuid()) 

    internal_db = bsddb.btopen(filename, 'c', 0644 )
    handle = open(filename,"r")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    storage = shelve.BsdDbShelf(internal_db)

    if clear:
        storage.clear()
        storage.close()
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        return {}

    if write:
        __purge_old_jobs(storage)
        storage[str(jobid)] = (status, results)
        rc = jobid
    else:
        if storage.has_key(str(jobid)):
            # tuple of (status, results)
            rc = storage[str(jobid)]
        else:
            rc = (JOB_ID_LOST_IN_SPACE, 0)

    storage.close()
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    return rc

def batch_run(server, process_server, nforks):
    """
    This is the method used by the overlord side usage of jobthing.
    It likely makes little sense for the minion async usage (yet).

    Given an array of items (pool), call callback in each one, but divide
    the workload over nfork forks.  Temporary files used during the
    operation will be created in cachedir and subsequently deleted.    
    """
   
    job_id = time.time()
    pid = os.fork()
    if pid != 0:
        #print "DEBUG: UPDATE STATUS: r1: %s" % job_id
        __update_status(job_id, JOB_ID_RUNNING, -1)
        return job_id
    else:
        #print "DEBUG: UPDATE STATUS: r2: %s" % job_id
        __update_status(job_id, JOB_ID_RUNNING,  -1)
        results = forkbomb.batch_run(server, process_server, nforks)
        #print "DEBUG: UPDATE STATUS: f1: %s" % job_id
        __update_status(job_id, JOB_ID_FINISHED, results)
        sys.exit(0)

def job_status(jobid):
    return __get_status(jobid)

if __name__ == "__main__":
    __test()



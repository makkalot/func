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
import utils
import traceback

JOB_ID_RUNNING = 0
JOB_ID_FINISHED = 1
JOB_ID_LOST_IN_SPACE = 2
JOB_ID_ASYNC_PARTIAL = 3
JOB_ID_ASYNC_FINISHED = 4

# how long to retain old job records in the job id database
RETAIN_INTERVAL = 60 * 60    

# where to store the internal job id database
CACHE_DIR = "/var/lib/func"

def __update_status(jobid, status, results, clear=False):
    return __access_status(jobid=jobid, status=status, results=results, write=True)

def __get_status(jobid):
    return __access_status(jobid=jobid, write=False)

def purge_old_jobs():
    return __access_status(purge=True)

def __purge_old_jobs(storage):
    """
    Deletes jobs older than RETAIN_INTERVAL seconds.  
    MINOR FIXME: this probably should be a more intelligent algorithm that only
    deletes jobs if the database is too big and then only the oldest jobs
    but this will work just as well.
    """
    nowtime = time.time()
    for x in storage.keys():
        # minion jobs have "-minion" in the job id so disambiguation so we need to remove that
        jobkey = x.replace("-","").replace("minion","")
        create_time = float(jobkey)
        if nowtime - create_time > RETAIN_INTERVAL:
            del storage[x]

def __access_status(jobid=0, status=0, results=0, clear=False, write=False, purge=False):

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
    
    if purge or write:
        __purge_old_jobs(storage)

    if write:
        storage[str(jobid)] = (status, results)
        rc = jobid
    elif not purge:
        if storage.has_key(str(jobid)):
            # tuple of (status, results)

            rc = storage[str(jobid)]
        else:
            rc = (JOB_ID_LOST_IN_SPACE, 0)
    else:
        rc = 0

    storage.close()
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    return rc

def batch_run(server, process_server, nforks):
    """
    This is the method used by the overlord side usage of jobthing.
    Minion side usage will use minion_async_run instead.

    Given an array of items (pool), call callback in each one, but divide
    the workload over nfork forks.  Temporary files used during the
    operation will be created in cachedir and subsequently deleted.    
    """
   
    job_id = time.time()
    pid = os.fork()
    if pid != 0:
        __update_status(job_id, JOB_ID_RUNNING, -1)
        return job_id
    else:
        # kick off the job
        __update_status(job_id, JOB_ID_RUNNING,  -1)
        results = forkbomb.batch_run(server, process_server, nforks)
        
        # we now have a list of job id's for each minion, kill the task
        __update_status(job_id, JOB_ID_ASYNC_PARTIAL, results)
        sys.exit(0)

def minion_async_run(retriever, method, args):
    """
    This is a simpler invocation for minion side async usage.
    """
    # to avoid confusion of job id's (we use the same job database)
    # minion jobs contain the string "minion".  


    job_id = "%s-minion" % time.time()
    pid = os.fork()
    if pid != 0:
        __update_status(job_id, JOB_ID_RUNNING, -1)
        return job_id
    else:
        __update_status(job_id, JOB_ID_RUNNING,  -1)
        try:
            function_ref = retriever(method)
            rc = function_ref(*args)
        except Exception, e:
            (t, v, tb) = sys.exc_info()
            rc = utils.nice_exception(t,v,tb)

        __update_status(job_id, JOB_ID_FINISHED, rc)
        sys.exit(0)

def job_status(jobid, client_class=None):
 
    # NOTE: client_class is here to get around some evil circular reference
    # type stuff.  This is intended to be called by minions (who can leave it None)
    # or by the Client module code (which does not need to be worried about it).  API
    # users should not be calling jobthing.py methods directly.
   
    got_status = __get_status(jobid)

    # if the status comes back as JOB_ID_ASYNC_PARTIAL what we have is actually a hash
    # of hostname/minion-jobid pairs.  Instantiate a client handle for each and poll them
    # for their actual status, filling in only the ones that are actually done.

    (interim_rc, interim_results) = got_status

    if interim_rc == JOB_ID_ASYNC_PARTIAL:

        partial_results = {}


        some_missing = False
        for host in interim_results.keys():

            minion_job = interim_results[host]
            client = client_class(host, noglobs=True, async=False)
            minion_result = client.jobs.job_status(minion_job)

            (minion_interim_rc, minion_interim_result) = minion_result

            if minion_interim_rc not in [ JOB_ID_RUNNING ]:
                if minion_interim_rc in [ JOB_ID_LOST_IN_SPACE ]:
                    partial_results[host] = [ utils.REMOTE_ERROR, "lost job" ]
                else:
                    partial_results[host] = minion_interim_result
            else: 
                some_missing = True

        if some_missing:
            return (JOB_ID_ASYNC_PARTIAL, partial_results)
        else:
            return (JOB_ID_ASYNC_FINISHED, partial_results)

    else:
        return got_status
   
    # of job id's on the minion in results.

if __name__ == "__main__":
    __test()



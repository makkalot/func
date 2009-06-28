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

import dbm
import fcntl
import os
import pprint
import shelve
import sys
import time

import forkbomb
from func.CommonErrors import *
from func import utils
from certmaster import utils as cm_utils

JOB_ID_RUNNING = 0
JOB_ID_FINISHED = 1
JOB_ID_LOST_IN_SPACE = 2
JOB_ID_PARTIAL = 3
JOB_ID_REMOTE_ERROR = 4

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

def clear_db():
    return __access_status(clear=True)

def __purge_old_jobs(storage):
    """
    Deletes jobs older than RETAIN_INTERVAL seconds.  
    MINOR FIXME: this probably should be a more intelligent algorithm that only
    deletes jobs if the database is too big and then only the oldest jobs
    but this will work just as well.
    """
    nowtime = time.time()
    for x in storage.keys():
        jobkey = x.strip().split('-')
        #if the jobkey's lenght is smaller than 4 it means that
        #that id maybe a minion id that is in timestap-minion format
        #or maybe a an old id which is in timestap format that handles
        #both situations
        if len(jobkey)<4: #the minion part job_ids
            jobkey = jobkey[0]
        #if the job is equal or bigger than 4 that means that it is a new type id
        #which is in glob-module-method-timestamp format, in a perfect world the lenght
        #of the jobkey should be exactly 4 but in some situations we have bigger lenghts
        #anyway that control will hande all situation because only we need is the timestamp
        #member which is the last one
        else:
            jobkey = jobkey[len(jobkey)-1]

        create_time = float(jobkey)
        if nowtime - create_time > RETAIN_INTERVAL:
            del storage[x]

def get_open_ids():
    return __access_status(write=False,get_all=True)

def __get_open_ids(storage):
    """
    That method is needes from other language/API/UI/GUI parts that uses 
    func's async methods to know the status of the results.
    """
    result_hash_pack = {}
    #print storage
    for job_id,result in storage.iteritems():
        #TOBE REMOVED that control is for old job_ids 
        #some users who will upgrade to new version will have errors
        #if we dont have that control here :)
        if len(job_id.split("-"))>=4: #ignore the old job_ids the overlord part 
            result_hash_pack[job_id]=result[0]
        elif len(job_id.split("-"))==2: #it seems to be a minion side id and also ignores old ids
            result_hash_pack[job_id]=result[0]

    return result_hash_pack

        

def __access_status(jobid=0, status=0, results=0, clear=False, write=False, purge=False,get_all=False):

    dir = os.path.expanduser(CACHE_DIR)
    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except IOError:
            raise Func_Client_Exception, 'Cannot create directory for status files. '+\
                  'Ensure you have permission to create %s directory' % dir
    filename = os.path.join(dir,"status-%s" % os.getuid()) 

    try:
        handle = open(filename,"w")
    except IOError, e:
        raise Func_Client_Exception, 'Cannot create status file. Ensure you have permission to write in %s directory' % dir
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    internal_db = dbm.open(filename, 'c', 0644 )
    storage = shelve.Shelf(internal_db)


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
    elif get_all:
        rc=__get_open_ids(storage)
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

def batch_run(pool, callback, nforks,**extra_args):
    """
    This is the method used by the overlord side usage of jobthing.
    Minion side usage will use minion_async_run instead.

    Given an array of items (pool), call callback in each one, but divide
    the workload over nfork forks.  Temporary files used during the
    operation will be created in cachedir and subsequently deleted.    
    """
   
    job_id = utils.get_formated_jobid(**extra_args)
    
    __update_status(job_id, JOB_ID_RUNNING, -1)
    pid = os.fork()
    if pid != 0:
        return job_id
    else:
        # kick off the job
        results = forkbomb.batch_run(pool, callback, nforks)
        
        # write job IDs to the state file on overlord 
        __update_status(job_id, JOB_ID_PARTIAL, results)
        # we now have a list of job id's for each minion, kill the task
        os._exit(0)

def minion_async_run(retriever, method, args,minion_query=None):
    """
    This is a simpler invocation for minion side async usage.
    """
    # to avoid confusion of job id's (we use the same job database)
    # minion jobs contain the string "minion".  


    job_id = "%s-minion" % pprint.pformat(time.time())
    __update_status(job_id, JOB_ID_RUNNING, -1)
    pid = os.fork()
    if pid != 0:
        os.waitpid(pid, 0)
        return job_id
    else:
        # daemonize!
        os.umask(077)
        os.chdir('/')
        os.setsid()
        if os.fork():
            os._exit(0)

        try:
            fact_result = None
            if args and type(args[0]) == dict and args[0].has_key('__fact__'):
                fact_result = minion_query.exec_query(args[0]['__fact__'],True)
            else:
                function_ref = retriever(method)
                rc = function_ref(*args)
                
            if fact_result and fact_result[0]: #that means we have True from query so can go on
                function_ref = retriever(method)
                rc = function_ref(*args[1:])
                rc = [{'__fact__':fact_result},rc]
            elif fact_result and not fact_result[0]:
                rc =  [{'__fact__':fact_result}]
        
        except Exception, e:
            (t, v, tb) = sys.exc_info()
            rc = cm_utils.nice_exception(t,v,tb)

        __update_status(job_id, JOB_ID_FINISHED, rc)
        os._exit(0)

def job_status(jobid, client_class=None):
 
    # NOTE: client_class is here to get around some evil circular reference
    # type stuff.  This is intended to be called by minions (who can leave it None)
    # or by the Client module code (which does not need to be worried about it).  API
    # users should not be calling jobthing.py methods directly.
   
    got_status = __get_status(jobid)
    # if the status comes back as JOB_ID_PARTIAL what we have is actually a hash
    # of hostname/minion-jobid pairs.  Instantiate a client handle for each and poll them
    # for their actual status, filling in only the ones that are actually done.

    (interim_rc, interim_results) = got_status

    if interim_rc == JOB_ID_PARTIAL:

        partial_results = {}


        some_missing = False
        for host in interim_results.keys():

            minion_job = interim_results[host]
            client = client_class(host, noglobs=True, async=False)
            minion_result = client.jobs.job_status(minion_job)

            if type(minion_result) != list or len(minion_result)!=2:
                minion_interim_rc = JOB_ID_REMOTE_ERROR
                minion_interim_result = minion_result[:3]
            else:
                (minion_interim_rc, minion_interim_result) = minion_result

            if minion_interim_rc != JOB_ID_RUNNING :
                if minion_interim_rc == JOB_ID_LOST_IN_SPACE:
                    partial_results[host] = [ utils.REMOTE_ERROR, "lost job" ]
                else:
                    partial_results[host] = minion_interim_result
            else: 
                some_missing = True

        if some_missing or not interim_results:
            return (JOB_ID_PARTIAL, partial_results)
        
        else:
            # Save partial results in state file so next time we don't
            # call minions to get status.
            if partial_results:
                __update_status(jobid,JOB_ID_FINISHED, partial_results)
            return (JOB_ID_FINISHED, partial_results)

    else:
        return got_status
   
    # of job id's on the minion in results.

if __name__ == "__main__":
    __test()



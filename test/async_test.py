from func.overlord.client import Client
import func.jobthing as jobthing
import time
import sys

TEST_SLEEP = 5
EXTRA_SLEEP = 5

def __tester(async):
   if async:
       client = Client("*",nforks=10,async=True)
       oldtime = time.time()
       print "asking minion to sleep for %s seconds" % TEST_SLEEP
       job_id = client.test.sleep(TEST_SLEEP)
       print "job_id = %s" % job_id
       while True:
           status = client.job_status(job_id)
           (code, results) = status
           nowtime = time.time()
           delta = int(nowtime - oldtime)
           if nowtime > oldtime + TEST_SLEEP + EXTRA_SLEEP:
               print "time expired, test failed"
               sys.exit(1)
           if code == jobthing.JOB_ID_RUNNING:  
               print "task is still running, %s elapsed ..." % delta
           if code == jobthing.JOB_ID_PARTIAL:
               print "task reports partial status, %s elapsed, results = %s" % (delta, results)
                   
           elif code == jobthing.JOB_ID_FINISHED:
               print "task complete, %s elapsed, results = %s" % (delta, results)
               sys.exit(0)
           else:
               print "job not found: %s, %s elapased" % (code, delta)
           time.sleep(1)
   else:
       print Client("*",nforks=10,async=False).test.sleep(5)

# __tester(False)
__tester(True)



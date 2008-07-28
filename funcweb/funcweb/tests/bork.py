from func.overlord.client import Overlord
from func.jobthing import *
import time


print "Now running one with getattr "
module = "echo"
method = "run_int"

fc_new = Overlord("*",async = True)
new_job_id = getattr(getattr(fc_new,module),method)(500)
code_status = fc_new.job_status(new_job_id)[0]

print "The code status is : ",code_status

while code_status != JOB_ID_FINISHED:
    print "Waiting the run_int to finish "
    code_status = fc_new.job_status(new_job_id)[0]
    time.sleep(2)
print "The int operation is  finished"



print "Creating the object"
fc = Overlord("*",async = True)
job_id = fc.echo.run_string("Merhaba")
code_status = fc.job_status(job_id)[0]

print "The code status is : ",code_status

while code_status != JOB_ID_FINISHED:
    print "Waiting the run_string to finish "
    code_status = fc.job_status(job_id)[0]
    time.sleep(2)
print "The run_string was finished"



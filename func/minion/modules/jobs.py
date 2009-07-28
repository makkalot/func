## (Largely internal) module for access to asynchoronously dispatched
## module job ID's.  The Func Overlord() module wraps most of this usage
## so it's not entirely relevant to folks using the CLI or Func API
## directly.
##
## Copyright 2008, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

from func import jobthing
import func_module
NUM_OF_LINES = 50
# =================================

class JobsModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Internal module for tracking background minion tasks."

    def job_status(self, job_id):
        """
        Returns job status in the form of (status, datastruct).
        Datastruct is undefined for unfinished jobs.  See jobthing.py and
        Wiki details on async invocation for more information.
        """
        return jobthing.job_status(job_id)
    
    def tail_output(self,minion_job_id):
        """
        A tail method which will tail the log files
        that will track their output ....
        """
        
        from func.minion import sub_process
        from certmaster.config import read_config
        from func.commonconfig import FuncdConfig
        from func.logger import config_file
        import os
        import subprocess

        
        
        config = read_config(config_file, FuncdConfig)
        method_log_dir = config.method_log_dir
        method_log_file = os.path.join(method_log_dir,minion_job_id)
        cmd= subprocess.Popen(
                args=["tail","-n",str(NUM_OF_LINES),method_log_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell = False,
                )
        
        return cmd.communicate()


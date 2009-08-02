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

# copyright 2004 Michael D. Stenner <mstenner@ece.arizona.edu>
# license: LGPL

class xreverse:
    def __init__(self, file_object, buf_size=1024*8):
        self.fo = fo = file_object
        fo.seek(0, 2)        # go to the end of the file
        self.pos = fo.tell() # where we are 
        self.buffer = ''     # data buffer
        self.lbuf = []       # buffer for parsed lines
        self.done = 0        # we've read the last line
        self.jump = -1 * buf_size
        
        while 1:
            try:            fo.seek(self.jump, 1)
            except IOError: fo.seek(0)
            new_position = fo.tell()
            new = fo.read(self.pos - new_position)
            fo.seek(new_position)
            self.pos = new_position

            self.buffer = new + self.buffer
            if '\n' in new: break
            if self.pos == 0: return self.buffer

        nl = self.buffer.split('\n')
        nlb = [ i + '\n' for i in nl[1:-1] ]
        if not self.buffer[-1] == '\n': nlb.append(nl[-1])
        self.buffer = nl[0]
        self.lbuf = nlb

    def __iter__(self): return self

    def next(self):
        try:
            return self.lbuf.pop()
        except IndexError:
            fo = self.fo
            while 1:
                #get the next chunk of data
                try:            fo.seek(self.jump, 1)
                except IOError: fo.seek(0)
                new_position = fo.tell()
                new = fo.read(self.pos - new_position)
                fo.seek(new_position)
                self.pos = new_position

                nl = (new + self.buffer).split('\n')
                self.buffer = nl.pop(0)
                self.lbuf = [ i + '\n' for i in nl ]

                if self.lbuf: return self.lbuf.pop()
                elif self.pos == 0:
                    if self.done:
                        raise StopIteration
                    else:
                        self.done = 1
                        return self.buffer + '\n'

   

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

    
    def get_progress(self,minion_job_id):
        """
        Get the log file and parse the progress part 
        to be polled on overlord
        """
        from certmaster.config import read_config
        from func.commonconfig import FuncdConfig
        from func.logger import config_file
        import os
        import re

        config = read_config(config_file, FuncdConfig)
        method_log_dir = config.method_log_dir
        method_log_file = os.path.join(method_log_dir,minion_job_id)
        
        reco=re.compile("Progress report (\d+)/(\d+) completed")
        fo = file(method_log_file)
        for line in xreverse(fo):
            tmp = re.search(reco,line)
            if tmp:
                current = tmp.group(1)
                all = tmp.group(2)
                return (int(current),int(all))

        #that tells that we couldnt found any report there
        return(0,0)


## (Largely internal) module for access to asynchoronously dispatched
## module job ID's.  The Func Client() module wraps most of this usage
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

import codes
from func import jobthing
import func_module

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


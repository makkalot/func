#!/usr/bin/python

## 
## Process lister (control TBA)
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

# other modules
import subprocess

# our modules
from codes import *
from modules import func_module

# =================================

class ProcessModule(func_module.FuncModule):
    def __init__(self):
        self.methods = {
            "info"    : self.info,
            "kill"    : self.kill,
            "pkill"   : self.pkill
        }
        func_module.FuncModule.__init__(self)

    def info(self,flags="-auxh"):
        """
        Returns a struct of hardware information.  By default, this pulls down
        all of the devices.  If you don't care about them, set with_devices to
        False.
        """

        flags.replace(";","") # prevent stupidity

        cmd = subprocess.Popen("ps %s" % flags,stdout=subprocess.PIPE,shell=True)
        data = cmd.communicate()[0]

        results = []       

        for x in data.split("\n"):
            tokens = x.split()
            results.append(tokens)

        return results

    def kill(self,pid,level=""):
        rc = subprocess.call("/bin/kill %s %s" % (pid, level), shell=True)
        return rc

    def pkill(self,name,level=""):
        # example killall("thunderbird","-9")
        rc = subprocess.call("/usr/bin/pkill %s %s" % (name, level), shell=True)
        return rc

methods = ProcessModule()
register_rpc = methods.register_rpc




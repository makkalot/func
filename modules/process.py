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
import sub_process
import codes

# our modules
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


        #FIXME: we need to swallow stdout/stderr as well, right now it spews to the console
        cmd = sub_process.Popen(["/bin/ps", flags] ,executable="/bin/ps", stdout=sub_process.PIPE,shell=False)
        data = cmd.communicate()[0]

        results = []       

        for x in data.split("\n"):
            tokens = x.split()
            results.append(tokens)

        return results


    def kill(self,pid,signal="TERM"):
        if pid == "0":
            raise codes.FuncException("Killing pid group 0 not permitted")
        if signal == "":
            # this is default /bin/kill behaviour, it claims, but enfore it anyway
            signal = "-TERM"
        if signal[0] != "-":
            signal = "-%s" % signal
        rc = sub_process.call(["/bin/kill",signal, pid], executable="/bin/kill", shell=False)
        print rc
        return rc

    def pkill(self,name,level=""):
        # example killall("thunderbird","-9")
        rc = sub_process.call(["/usr/bin/pkill", name, level], executable="/usr/bin/pkill", shell=False)
        return rc

methods = ProcessModule()
register_rpc = methods.register_rpc




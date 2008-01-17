##
## Grabs status from SMART to see if your hard drives are ok
## Returns in the format of (return code, [line1, line2, line3,...])
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

# our modules
import func_module

# =================================

class SmartModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Grabs status from SMART to see if your hard drives are ok."

    def info(self,flags="-q onecheck"):
        """
        Returns a struct of hardware information.  By default, this pulls down
        all of the devices.  If you don't care about them, set with_devices to
        False.
        """

        flags.replace(";","") # prevent stupidity

        cmd = sub_process.Popen("/usr/sbin/smartd %s" % flags,stdout=sub_process.PIPE,shell=True)
        data = cmd.communicate()[0]

        results = []

        for x in data.split("\n"):
            results.append(x)

        return (cmd.returncode, results)

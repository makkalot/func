# Copyright 2008, Red Hat, Inc
# Luke Macken <lmacken@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module
import sub_process

class SysctlModule(func_module.FuncModule):

    version = "0.0.1"
    description = "Configure kernel parameters at runtime"

    def __run(self, cmd):
        cmd = sub_process.Popen(cmd.split(), stdout=sub_process.PIPE,
                                stderr=sub_process.PIPE, shell=False)
        return [line for line in cmd.communicate()[0].strip().split('\n')]

    def list(self):
        return self.__run("/sbin/sysctl -a")

    def get(self, name):
        return self.__run("/sbin/sysctl -n %s" % name)

    def set(self, name, value):
        return self.__run("/sbin/sysctl -w %s=%s" % (name, value))

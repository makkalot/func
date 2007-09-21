# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from modules import web_svc

import subprocess

class Reboot(web_svc.WebSvc):

    def __init__(self):
        self.methods = {
                "reboot_reboot" : self.reboot
        }
        web_svc.WebSvc.__init__(self)

    def reboot(self, when='now', message=''):
        return subprocess.call(["/sbin/shutdown", '-r', when, message])


methods = Reboot()
register_rpc = methods.register_rpc

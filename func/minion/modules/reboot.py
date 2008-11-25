# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module
from func.minion import sub_process

class Reboot(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Reboots a machine."

    def reboot(self, when='now', message=''):
        return sub_process.call(["/sbin/shutdown", '-r', when, message], close_fds=True)

    def register_method_args(self):
        """
        Implementing method getter part
        """

        return {
                'reboot':{
                    'args':{
                        'when':{
                            'type':'string',
                            'optional':True,
                            'default':'now',
                            'description':"When to reboot (optional)"
                            },
                        'message':{
                            'type':'string',
                            'optional':True,
                            'description':"The shutdown message"
                            }
                        },
                    'description':"Rebooting the minions"
                    }
                }


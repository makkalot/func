# Copyright 2008, Red Hat, Inc
# Steve Salevan <ssalevan@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module
import func.overlord.client as fc
from func import utils

class OverlordModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Module for controlling minions that are also overlords."

    def get_minions(self,current_minions):
        """
        Builds a recursive map of the minions currently assigned to this
        overlord
        """
        maphash = {}
        for current_minion in current_minions:
            minionhash = {}
            minions_directly_below = fc.Overlord(current_minion).certmaster.get_signed_certs()
            for (minion,subminions) in minions_directly_below:
                if len(subminions) == 0:
                    minionhash[minion] = {}
                else:
                    minionhash[minion] = fc.Overlord(minion).overlord.get_minions(subminions)
            maphash[current_minion] = minionhash
        return {utils.get_hostname():maphash}

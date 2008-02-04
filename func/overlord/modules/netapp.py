##
## Overlord library to interface with minion-side netapp operations
##
## Most of this is just wrappers to create some cleaner, earier to use
## interfaces.  Also allows users to get function signatures and use
## nice things like kwargs client side, for those of us who can't live
## without ipython introspection.
##
## Copyright 2008, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

from func.overlord.client import Client

class RemoteError(Exception): pass

def _(res):
    if type(res) == type([]) and res[0] == 'REMOTE_ERROR':
        raise RemoteError, res[2]
    else:
        return res

class Filer(Client):
    def __init__(self, filer, admin_host):
        Client.__init__(self, admin_host)
        self.filer = filer
        self.admin_host = admin_host

    def create_volume(self, vol, aggr, size):
        return _(self.netapp.vol.create(self.filer, vol, aggr, size)[self.admin_host])

    def destroy_volume(self, vol):
        # offline it first
        try:
            self.netapp.vol.offline(self.filer, vol)
        except:
            pass
        return _(self.netapp.vol.destroy(self.filer, vol)[self.admin_host])

    def offline_volume(self, vol):
        return _(self.netapp.vol.offline(self.filer, vol)[self.admin_host])                 

    def online_volume(self, vol):
        return _(self.netapp.vol.online(self.filer, vol)[self.admin_host])                 

    def get_volume_size(self, vol):
        return _(self.netapp.vol.size(self.filer, vol)[self.admin_host])

    def resize_volume(self, vol, delta):
        return _(self.netapp.vol.size(self.filer, vol, delta)[self.admin_host])

    def create_snapshot(self, vol, snap):
        return _(self.netapp.snap.create(self.filer, vol, snap)[self.admin_host])

    def delete_snapshot(self, vol, snap):
        return _(self.netapp.snap.delete(self.filer, vol, snap)[self.admin_host])

    def create_clone_volume(self, vol, parent, snap):
        return _(self.netapp.vol.clone.create(self.filer, vol, parent, snap)[self.admin_host])

    def split_clone_volume(self, vol):
        return _(self.netapp.vol.clone.split(self.filer, vol)[self.admin_host])

    def list_volumes(self):
        vols = _(self.netapp.vol.status(self.filer))
        return_list = []
        for vol in vols:
            return_list.append(vol['name'])
        return return_list

    def volume_details(self, vol=None):
        if vol:
            return _(self.netapp.vol.status(self.filer, vol)[self.admin_host])
        else:
            return _(self.netapp.vol.status(self.filer)[self.admin_host])

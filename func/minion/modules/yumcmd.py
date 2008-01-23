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

import yum

# XXX Use internal yum callback or write a useful one.
class DummyCallback(object):

    def event(self, state, data=None):
        pass

class Yum(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Package updates through yum."

    def update(self):
        # XXX support updating specific rpms
        ayum = yum.YumBase()
        ayum.doGenericSetup()
        ayum.doRepoSetup()
        try:
            ayum.doLock()
            ayum.update()
            ayum.buildTransaction()
            ayum.processTransaction(
                    callback=DummyCallback())
        finally:
            ayum.closeRpmDB()
            ayum.doUnlock()
        return True

    def check_update(self, repo=None):
        """Returns a list of packages due to be updated"""
        ayum = yum.YumBase()
        ayum.doConfigSetup()
        ayum.doTsSetup()
        if repo is not None:
            ayum.repos.enableRepo(repo)
        return map(str, ayum.doPackageLists('updates').updates)

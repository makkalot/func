# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
# Alex Wood <awood@redhat.com>
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
    api_version = "0.1.0"
    description = "Package updates through yum."

    def update(self, pkg=None):
        ayum = yum.YumBase()
        ayum.doGenericSetup()
        ayum.doRepoSetup()
        try:
            ayum.doLock()
            if pkg != None:
                tx_result = ayum.update(pattern=pkg)
            else:
                tx_result = ayum.update()

            ayum.buildTransaction()
            ayum.processTransaction(
                    callback=DummyCallback())
        finally:
            ayum.closeRpmDB()
            ayum.doUnlock()
        return map(str, tx_result)

    def check_update(self, filter=[], repo=None):
        """Returns a list of packages due to be updated
           You can specify a filter using the standard yum wildcards
        """
        # parsePackages expects a list and doesn't react well if you send in a plain string with a wildcard in it
        # (the string is broken into a list and one of the list elements is "*" which matches every package)
        if type(filter) not in [list, tuple]:
            filter = [filter]

        ayum = yum.YumBase()
        ayum.doConfigSetup()
        ayum.doTsSetup()
        if repo is not None:
            ayum.repos.enableRepo(repo)

        pkg_list = ayum.doPackageLists('updates').updates

        if filter:
            # exactmatch are all the packages with exactly the same name as one in the filter list
            # matched are all the packages that matched under any wildcards
            # unmatched are all the items in the filter list that didn't match anything
            exactmatch, matched, unmatched = yum.packages.parsePackages(pkg_list, filter)
            pkg_list = exactmatch + matched

        return map(str, pkg_list)

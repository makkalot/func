##
## NetApp Filer 'Vol' Module
##
## Copyright 2007, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

from func.minion.modules import func_module
class Vol(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'vol' command"

    def create(self, *args):
        """
        TODO: Document me ...
        """
        pass

    def clone(self, *args):
        """
        TODO: Document me ...
        """
        pass

    def destroy(self):
        """
        TODO: Document me ...
        """
        pass

    def offline(self):
        """
        TODO: Document me ...
        """
        pass

    def status(self):
        """
        TODO: Document me ...
        """
        pass

    def size(self):
        """
        TODO: Document me ...
        """
        pass

    def options(self):
        """
        TODO: Document me ...
        """
        pass

    def rename(self):
        """
        TODO: Document me ...
        """
        pass

    def restrict(self):
        """
        TODO: Document me ...
        """
        pass

    def split(self):
        """
        TODO: Document me ...
        """
        pass

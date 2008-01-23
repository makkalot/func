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

import re
from func.minion.modules import func_module
from common import *

class Vol(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Interface to the 'vol' command"

    def create(self, filer, *args):
        """
        TODO: Document me ...
        """
        regex = """Creation of volume .* has completed."""

        output = ssh('root', filer, ' '.join(args))
        if re.search(regex, output):
            return True
        else:
            raise NetappCommandError, output

    def clone(self, filer, *args):
        """
        TODO: Document me ...
        """
        if len(args)==1:
            args = args[0].split()

        if subcmd == 'create':
            regex = """Creation of clone volume .* has completed."""
        elif subcmd == 'split':
            if args[1] == 'start':
                regex = """Clone volume .* will be split from its parent."""
            else:
                raise NetappNotImplemented
        else:
            raise NetappNotImplemented

        output = ssh('root', filer, ' '.join(args))
        if re.search(regex, output):
            return True
        else:
            raise NetappCommandError, output

    def destroy(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def offline(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def status(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def size(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def options(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def rename(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def restrict(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

    def split(self, filer, *args):
        """
        TODO: Document me ...
        """
        pass

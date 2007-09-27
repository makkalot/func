#!/usr/bin/python

## func module for PackageKit
##
## Copyright 2007, Red Hat, Inc
## Robin Norwood <rnorwood@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##


from codes import *
from modules import func_module

from packagekit import PackageKit


class PackageKitInterface(PackageKit):

    def __init__(self):
        PackageKit.__init__(self)
        self.packages = []
        
    def Percentage(self, progress):
        pass
        
    def JobStatus(self, type):
        pass
	
    def Package(self, package_name, package_summary):
        self.packages.append( {
            "name"    : "%s" % package_name,
            "summary" : "%s" % package_summary,
            } )

    def Description(self, package_name, package_group, package_description, package_url):
        self.packages.append( {
            "name"        : "%s" % package_name,
            "group"       : "%s" % package_group,
            "description" : "%s" % package_description,
            "url"         : "%s" % package_url,
            } )

class PackageKitController(func_module.FuncModule):

    def __init__(self):
        try:
            self.pkt_interface = PackageKitInterface()
        except PackageKitNotStarted:
            func_module.FuncModule.__init__(self)
            return

        self.methods = {
            "SearchName"     : self.SearchName,
            "GetDescription" : self.GetDescription,
            "RefreshCache"   : self.RefreshCache,
        }
        func_module.FuncModule.__init__(self)

    def SearchName(self, pattern):
        if len(pattern)==0:
            return

        self.pkt_interface.job = self.pkt_interface.SearchName(pattern)
        self.pkt_interface.run()

        return self.pkt_interface.packages

    def GetDescription(self, packageName):
        if len(packageName) == 0:
            return

        self.pkt_interface.job = self.pkt_interface.GetDescription(packageName)
        self.pkt_interface.run()

        return self.pkt_interface.packages

    def RefreshCache(self):
        self.pkt_interface.job = self.pkt_interface.RefreshCache()
        self.pkt_interface.run()

        return "Done"

methods = PackageKitController()
register_rpc = methods.register_rpc

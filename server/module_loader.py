#!/usr/bin/python

## func
##
## Copyright 2007, Red Hat, Inc
## See AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##


import distutils.sysconfig
import os
import sys
import glob
from rhpl.translate import _, N_, textdomain, utf8

module_file_path="modules/"
mod_path="server/"
sys.path.insert(0, mod_path)

def load_modules(module_path=module_file_path, blacklist=None):
    filenames = glob.glob("%s/*.py" % module_file_path)
    filenames = filenames + glob.glob("%s/*.pyc" % module_file_path)
    filesnames = filenames + glob.glob("%s/*.pyo" % module_file_path)

    mods = {}

    print sys.path

    for fn in filenames:
        basename = os.path.basename(fn)
        if basename == "__init__.py":
            continue
        if basename[-3:] == ".py":
            modname = basename[:-3]
        elif basename[-4:] in [".pyc", ".pyo"]:
            modname = basename[:-4]

        
        try:
            blip =  __import__("modules.%s" % ( modname), globals(), locals(), [modname])
            if not hasattr(blip, "register_rpc"):
		errmsg = _("%(module_path)s/%(modname)s module not a proper module")
                print errmsg % {'module_path': module_path, 'modname':modname} 
                continue
            mods[modname] = blip
        except ImportError, e:
            # shouldn't this be fatal?
            print e
            raise

    return mods




if __name__ == "__main__":
    print load_modules(module_path)

    

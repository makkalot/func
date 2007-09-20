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


def load_modules(blacklist=None):

    module_file_path="%s/func/server/modules/" % distutils.sysconfig.get_python_lib()
    mod_path="%s/func/server/"  % distutils.sysconfig.get_python_lib()

    sys.path.insert(0, mod_path)
    mods = {}

    filenames = glob.glob("%s/*.py" % module_file_path)
    filenames = filenames + glob.glob("%s/*.pyc" % module_file_path)
    filesnames = filenames + glob.glob("%s/*.pyo" % module_file_path)

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
                print errmsg % {'module_path': module_file_path, 'modname':modname} 
                continue
            mods[modname] = blip
        except ImportError, e:
            # shouldn't this be fatal?
            print e
            raise

    return mods



    

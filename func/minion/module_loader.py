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
from gettext import gettext
_ = gettext


from func import logger
logger = logger.Logger().logger


def module_walker(topdir):
    module_files = []
    for root, dirs, files in os.walk(topdir):
        # we should get here for each subdir
        for filename in files:
            # ASSUMPTION: all module files will end with .py, .pyc, .pyo
            if filename[-3:] == ".py" or filename[-4:] == ".pyc" or filename[-4:] == ".pyo":
                # we don't really care about __init__ files, though we do requure them
                if filename[:8] == "__init__":
                    continue
                # the normpath is important, since we eventually replace /'s with .'s
                # in the module name, and foo..bar doesnt work -akl
                module_files.append(os.path.normpath("%s/%s" % (root, filename)))


    return module_files

def load_modules(blacklist=None):

    module_file_path="%s/func/minion/modules/" % distutils.sysconfig.get_python_lib()
    mod_path="%s/func/minion/"  % distutils.sysconfig.get_python_lib()

    sys.path.insert(0, mod_path)
    mods = {}
    bad_mods = {}

    filenames = module_walker(module_file_path)

    # FIXME: this is probably more complicated than it needs to be -akl
    for fn in filenames:
        # aka, everything after the module_file_path
        module_name_part = fn[len(module_file_path):]
        dirname, basename = os.path.split(module_name_part)

        if basename == "__init__.py":
            continue
        if basename[-3:] == ".py":
            modname = basename[:-3]
        elif basename[-4:] in [".pyc", ".pyo"]:
            modname = basename[:-4]

        pathname = modname
        if dirname != "":
            pathname = "%s/%s" % (dirname, modname)

        mod_imp_name = pathname.replace("/", ".")

        if mods.has_key(mod_imp_name):
            # If we've already imported mod_imp_name, don't import it again
            continue

        # ignore modules that we've already determined aren't valid modules
        if bad_mods.has_key(mod_imp_name):
            continue

        try:
            blip =  __import__("modules.%s" % ( mod_imp_name), globals(), locals(), [mod_imp_name])
            if not hasattr(blip, "register_rpc"):
		errmsg = _("%(module_path)s%(modname)s module not a proper module")
                logger.warning(errmsg % {'module_path': module_file_path, 'modname':mod_imp_name})
                bad_mods[mod_imp_name] = True
                continue
            mods[mod_imp_name] = blip
        except ImportError, e:
            # A module that raises an ImportError is (for now) simply not loaded.
            errmsg = _("Could not load %s module: %s")
            logger.warning(errmsg % (mod_imp_name, e))
            bad_mods[mod_imp_name] = True
            continue
        except:
            errmsg = _("Could not load %s module")
            logger.warning(errmsg % (mod_imp_name))
            bad_mods[mod_imp_name] = True
            continue

    return mods


if __name__ == "__main__":

    module_file_path = "/usr/lib/python2.5/site-packages/func/minion/modules/"
    bar = module_walker(module_file_path)
    print bar
    for f in bar:
        print f
        print os.path.basename(f)
        print os.path.split(f)
        g = f[len(module_file_path):]
        print g
        print os.path.split(g)

    print load_modules()

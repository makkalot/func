# Copyright 2007, Red Hat, Inc
# Michael DeHaan <mdehaan@redhat.com>
# Copyright 2009
# Milton Paiva Neto <milton.paiva@gmail.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module

class RpmModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "RPM related commands."

    def inventory(self, flatten=True):
        """
        Returns information on all installed packages.
        By default, 'flatten' is passed in as True, which makes printouts very
        clean in diffs for use by func-inventory.  If you are writting another
        software application, using flatten=False will prevent the need to 
        parse the returns.
        """
        # I have not been able to get flatten=False to work if there 
        # is more than 491 entries in the dict -- ashcrow
        import rpm
        ts = rpm.TransactionSet()
        mi = ts.dbMatch()
        results = []
        for hdr in mi:
            name = hdr['name']
            epoch = (hdr['epoch'] or 0)
            version = hdr['version']
            release = hdr['release']
            arch = hdr['arch']
            if flatten:
                results.append("%s %s %s %s %s" % (name, epoch, version, 
                                                   release, arch))
            else:
                results.append([name, epoch, version, release, arch])
        return results

    @func_module.findout
    def grep(self, word):
        """
        Grep some info from packages we got from
        inventory especially 
        """
        results = {self.inventory:[]}
        inventory_res = self.inventory()
        
        for res in inventory_res:
            if res.lower().find(word)!= -1:
                results[self.inventory].append(res)
        
        return results

    def verify(self, pattern='', flatten=True):
        """
        Returns information on the verified package(s).
        """        
        import rpm
        import yum
        from re import split
        ts = rpm.TransactionSet()
        mi = (ts.dbMatch() if pattern == '' else self.glob(pattern))
        results = []
        for hdr in mi:
            name = hdr['name'] if pattern == '' else split("\s",hdr)[0]
            if flatten:                
                yb = yum.YumBase()
                pkgs = yb.rpmdb.searchNevra(name)
                for pkg in pkgs:
                    errors = pkg.verify()
                    for fn in errors.keys():
                        for prob in errors[fn]:
                            results.append('%s %s %s' % (name, fn, prob.message))
            else:
                results.append("%s-%s-%s.%s" % (name, version, release, arch))
        return results

    def glob(self, pattern, flatten=True):
        """
        Return a list of installed packages that match a pattern
        """
        import rpm
        ts = rpm.TransactionSet()
        mi = ts.dbMatch()
        results = []
        if not mi:
            return
        mi.pattern('name', rpm.RPMMIRE_GLOB, pattern)
        for hdr in mi:
            name = hdr['name']
            epoch = (hdr['epoch'] or 0)
            version = hdr['version']
            release = hdr['release']
            # gpg-pubkeys have no arch
            arch = (hdr['arch'] or "")

            if flatten:
                results.append("%s %s %s %s %s" % (name, epoch, version,
                                                       release, arch))
            else:
                results.append([name, epoch, version, release, arch])
        return results

    def register_method_args(self):
        """
        Implementing the method argument getter
        """
        return {
                'inventory':{
                    'args':{
                        'flatten':{
                            'type':'boolean',
                            'optional':True,
                            'default':True,
                            'description':"Print clean in difss"
                            }
                        },
                    'description':"Returns information on all installed packages"
                    },
                'verify':{
                    'args':{
                        'flatten':{
                            'type':'boolean',
                            'optional':True,
                            'default':True,
                            'description':"Print clean in difss"
                            }
                        },
                    'description':"Returns information on the verified package(s)"
                    },
                'glob':{
                    'args':{
                        'pattern':{
                            'type':'string',
                            'optional':False,
                            'description':"The glob packet pattern"
                            },
                        'flatten':{
                            'type':'boolean',
                            'optional':True,
                            'default':True,
                            'description':"Print clean in difss"
                                }
                        },
                    'description':"Return a list of installed packages that match a pattern"
                    }
                }

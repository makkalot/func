"""
Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import fnmatch
import glob
import os
import sys

from func import logger


# TODO: need to track which file got which config from

class Acls(object):
    def __init__(self, config=None):
        self.config = config
        
        self.acldir = self.config.acl_dir
        self.acls = {}
        self.logger = logger.Logger().logger
        self.certmaster_overrides_acls = self.config.certmaster_overrides_acls
        self.load()

    def load(self): 
        """
        takes a dir of .acl files
        returns a dict of hostname+hash =  [methods, to, run]
        
        """
    
        if not os.path.exists(self.acldir):
            sys.stderr.write('acl dir does not exist: %s\n' % self.acldir)
            return self.acls
    
        # get the set of files
        acl_glob = '%s/*.acl' % self.acldir
        files = glob.glob(acl_glob)
    
        for acl_file in files:
            self.logger.debug("acl_file", acl_file)
            try:
                fo = open(acl_file, 'r')
            except (IOError, OSError), e:
                sys.stderr.write('cannot open acl config file: %s - %s\n' % (acl_file, e))
                continue
    
            for line in fo.readlines():
                if line.startswith('#'): continue
                if line.strip() == '': continue
                line = line.replace('\n', '')
                (host, methods) = line.split('=')
                host = host.strip().lower()
                methods = methods.strip()
                methods = methods.replace(',',' ')
                methods = methods.split()
                if not self.acls.has_key(host):
                    self.acls[host] = []
                self.acls[host].extend(methods)

        self.logger.debug("acls %s" % self.acls)

        return self.acls

    def check(self, cm_cert, cert, ip, method, params):

        # certmaster always gets to run things
        # unless we are testing, and need to turn it off.. -al;
        
 
        if self.config.certmaster_overrides_acls:
            ca_cn = cm_cert.get_subject().CN
            ca_hash = cm_cert.subject_name_hash()
            ca_key = '%s-%s' % (ca_cn, ca_hash)
            self.acls[ca_key] = ['*']

        cn = cert.get_subject().CN
        sub_hash = cert.subject_name_hash()
        self.logger.debug("cn: %s sub_hash: %s" % (cn, sub_hash))
        self.logger.debug("acls %s" % self.acls)
        if self.acls:
            allow_list = []
            hostkey = '%s-%s' % (cn, sub_hash)
            self.logger.debug("hostkey %s" % hostkey)
            # search all the keys, match to 'cn-subhash'
            for hostmatch in self.acls.keys():
                if fnmatch.fnmatch(hostkey, hostmatch):
                    allow_list.extend(self.acls[hostmatch])
            # go through the allow_list and make sure this method is in there
            for methodmatch in allow_list:
                if fnmatch.fnmatch(method, methodmatch):
                    return True
                    
        return False

    def save(self):
        pass

    def add(self, acl, host):
        pass

    def delete(self, acl, host):
        pass

    def update(self, acl, host):
        pass



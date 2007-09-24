#!/usr/bin/python

"""
cert master listener

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

# standard modules
import SimpleXMLRPCServer
import string
import socket
import sys
import os
import os.path
import traceback
from OpenSSL import crypto

#from func.server import codes
import func
import func.certs


class SimpleConfigFile(object):
    """simple config file object:
       reads in key=value pairs from a file and stores each as an attribute"""
       
    def __init__(self, filename):
        self.fn = filename
        fo = open(filename, 'r')
        for line in fo.readlines():
            if line.startswith('#'): continue
            if line.strip() == '': continue
            (key, val) = line.split('=')
            key = key.strip().lower()
            val = val.strip()
            setattr(self, key, val)
        fo.close()


class CertMaster(object):
    def __init__(self, conf_file):
        self.cfg = SimpleConfigFile(conf_file)
        self.listen_addr = 'localhost'
        self.listen_port =  '51235'
        self.cadir = '/etc/pki/func/ca'
        self.certroot = '/etc/pki/func/ca/certs'
        self.csrroot = '/etc/pki/func/ca/csrs'
        self.autosign = True
        for attr in ['listen_addr', 'listen_port', 'cadir', 'certroot',
                     'csrroot']:
            if hasattr(self.cfg, attr):
                setattr(self, attr, getattr(self.cfg, attr))
        if hasattr(self.cfg, 'autosign'):
            if getattr(self.cfg, 'autosign').lower() in ['yes', 'true', 1, 'on']:
                self.autosign = True
            elif getattr(self.cfg, 'autosign').lower() in ['no', 'false', 0, 'off']:
                self.autosign = False
        # open up the cakey and cacert so we have them available
        ca_key_file = '%s/funcmaster.key' % self.cadir
        ca_cert_file = '%s/funcmaster.crt' % self.cadir
        self.cakey = func.certs.retrieve_key_from_file(ca_key_file)
        self.cacert = func.certs.retrieve_cert_from_file(ca_cert_file)
        
        for dirpath in [self.cadir, self.certroot, self.csrroot]:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

        # setup handlers
        self.handlers = {
                 'wait_for_cert': self.wait_for_cert,
                 }
        
    def _dispatch(self, method, params):
        if method == 'trait_names' or method == '_getAttributeNames':
            return self.handlers.keys()
        
        if method in self.handlers.keys():
            return self.handlers[method](*params)
        else:
            pass
            #raise codes.InvalidMethodException
    

    def wait_for_cert(self, csrbuf):
        """
           takes csr as a string
           returns True, caller_cert, ca_cert
           returns False, '', ''
        """
        try:
            csrreq = crypto.load_certificate_request(crypto.FILETYPE_PEM, csrbuf)
        except crypto.Error, e:
            #XXX need to raise a fault here and document it - but false is just as good
            return False, '', ''
        requesting_host = csrreq.get_subject().CN

        if self.autosign:
            # XXX need to have it check for existing cert instead of making a new one
            slavecert = func.certs.create_slave_certificate(csrreq,
                          self.cakey, self.cacert, self.cadir)
            destfile = '%s/%s.pem' % (self.certroot, requesting_host)
            destfo = open(destfile, 'w')
            destfo.write(crypto.dump_certificate(crypto.FILETYPE_PEM, slavecert))
            destfo.close()
            del destfo
            cert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, slavecert)
            cacert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, self.cacert)
            return True, cert_buf, cacert_buf
        else:
            # check for existing csr first
            # write the csr out to a file to be dealt with by the admin
            destfile = '%s/%s.csr' % (self.csrroot, requesting_host)
            destfo = open(destfile, 'w')
            destfo.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csrreq))
            destfo.close()
            del destfo
            return False, '', ''

        return False, '', ''
        




cm = CertMaster('/etc/func/certmaster.conf')
server = SimpleXMLRPCServer.SimpleXMLRPCServer((cm.cfg.listen_addr, int(cm.cfg.listen_port)))
server.logRequests = 0
server.register_instance(cm)
server.serve_forever()



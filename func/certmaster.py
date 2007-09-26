#!/usr/bin/python

# FIXME: Perms checked and okayed on all csr, certs and keys, everywhere
# FIXME: picky about bogus CN names ../ ../ ./ etc, etc to avoid stupid attacks
# FIXME: more intelligent fault raises

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
import sha
import glob

#from func.server import codes
import func
import func.certs
import func.codes
import func.utils

class SimpleConfigFile(object):
    """simple config file object:
       reads in key=value pairs from a file and stores each as an attribute"""
       
    def __init__(self, filename, defaults={}):
        self.fn = filename
        fo = open(filename, 'r')
        for line in fo.readlines():
            if line.startswith('#'): continue
            if line.strip() == '': continue
            (key, val) = line.split('=')
            key = key.strip().lower()
            val = val.strip()
            setattr(self, key, val)
        for k,v in defaults.items():
            if not hasattr(self, k):
                setattr(self, k, v)
        fo.close()


class CertMaster(object):
    def __init__(self, conf_file, defaults={}):
        self.cfg = SimpleConfigFile(conf_file, defaults)
        if hasattr(self.cfg, 'autosign'):
            if getattr(self.cfg, 'autosign').lower() in ['yes', 'true', 1, 'on']:
                self.cfg.autosign = True
            elif getattr(self.cfg, 'autosign').lower() in ['no', 'false', 0, 'off']:
                self.cfg.autosign = False
        else:
            self.cfg.autosign = False
        self.cfg.listen_port = int(self.cfg.listen_port)
        self.ca_key_file = '%s/funcmaster.key' % self.cfg.cadir
        self.ca_cert_file = '%s/funcmaster.crt' % self.cfg.cadir
        try:
            if not os.path.exists(self.cfg.cadir):
                os.makedirs(self.cfg.cadir)
            # fixme - should we creating these separately?
            if not os.path.exists(self.ca_key_file) and not os.path.exists(self.ca_cert_file):
                func.certs.create_ca(ca_key_file=self.ca_key_file, ca_cert_file=self.ca_cert_file)
        except (IOError, OSError), e:
            print 'Cannot make certmaster certificate authority keys/certs, aborting: %s' % e
            sys.exit(1)

            
        # open up the cakey and cacert so we have them available
        self.cakey = func.certs.retrieve_key_from_file(self.ca_key_file)
        self.cacert = func.certs.retrieve_cert_from_file(self.ca_cert_file)
        
        for dirpath in [self.cfg.cadir, self.cfg.certroot, self.cfg.csrroot]:
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
            raise func.codes.InvalidMethodException
    

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
        certfile = '%s/%s.cert' % (self.cfg.certroot, requesting_host)
        csrfile = '%s/%s.csr' % (self.cfg.csrroot, requesting_host)

        # check for old csr on disk
        # if we have it - compare the two - if they are not the same - raise a fault
        if os.path.exists(csrfile):
            oldfo = open(csrfile)
            oldcsrbuf = oldfo.read()
            oldsha = sha.new()
            oldsha.update(oldcsrbuf)
            olddig = oldsha.hexdigest()
            newsha = sha.new()
            newsha.update(csrbuf)
            newdig = newsha.hexdigest()
            if not newdig == olddig:
                # XXX raise a proper fault
                return False, '', ''

        # look for a cert:
        # if we have it, then return True, etc, etc
        if os.path.exists(certfile):
            slavecert = func.certs.retrieve_cert_from_file(certfile)
            cert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, slavecert)
            cacert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, self.cacert)
            return True, cert_buf, cacert_buf
        
        # if we don't have a cert then:
        # if we're autosign then sign it, write out the cert and return True, etc, etc
        # else write out the csr
        
        if self.cfg.autosign:
            cert_fn = self.sign_this_csr(csrreq)
            cert = func.certs.retrieve_cert_from_file(cert_fn)            
            cert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            cacert_buf = crypto.dump_certificate(crypto.FILETYPE_PEM, self.cacert)
            return True, cert_buf, cacert_buf
        
        else:
            # write the csr out to a file to be dealt with by the admin
            destfo = open(csrfile, 'w')
            destfo.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, csrreq))
            destfo.close()
            del destfo
            return False, '', ''

        return False, '', ''

    def get_csrs_waiting(self):
        hosts = [] 
        csrglob = '%s/*.csr' % self.cfg.csrroot
        csr_list = glob.glob(csrglob)
        for f in csr_list:
            hn = os.path.basename(f)
            hn = hn[:-4]
            hosts.append(hn)
        return hosts
    
            
    def sign_this_csr(self, csr):
        """returns the path to the signed cert file"""
        csr_unlink_file = None

        if type(csr) is type(''): 
            if csr.startswith('/') and os.path.exists(csr):  # we have a full path to the file
                csrfo = open(csr)
                csr_buf = csrfo.read()
                csr_unlink_file = csr
                
            elif os.path.exists('%s/%s' % (self.cfg.csrroot, csr)): # we have a partial path?
                csrfo = open('%s/%s' % (self.cfg.csrroot, csr))
                csr_buf = csrfo.read()
                csr_unlink_file = '%s/%s' % (self.cfg.csrroot, csr)
                
            # we have a string of some kind
            else:
                csr_buf = csr

            try:
                csrreq = crypto.load_certificate_request(crypto.FILETYPE_PEM, csr_buf)                
            except crypto.Error, e:
               print 'Bad CSR: %s' % csr
                
        else: # assume we got a bare csr req
            csrreq = csr
        requesting_host = csrreq.get_subject().CN
        certfile = '%s/%s.cert' % (self.cfg.certroot, requesting_host)
        thiscert = func.certs.create_slave_certificate(csrreq, self.cakey, self.cacert, self.cfg.cadir)
        destfo = open(certfile, 'w')
        destfo.write(crypto.dump_certificate(crypto.FILETYPE_PEM, thiscert))
        destfo.close()
        del destfo
        if csr_unlink_file and os.path.exists(csr_unlink_file):
            os.unlink(csr_unlink_file)
            
        return certfile
        

class CertmasterXMLRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
    def __init__(self, args):
       self.allow_reuse_address = True
       SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, args)
        

def serve(xmlrpcinstance):

     """
     Code for starting the XMLRPC service. 
     """

     server = CertmasterXMLRPCServer((xmlrpcinstance.cfg.listen_addr, xmlrpcinstance.cfg.listen_port))
     server.logRequests = 0 # don't print stuff to console
     server.register_instance(xmlrpcinstance)
     server.serve_forever()


def main(argv):
    
    defaults = { 'listen_addr': 'localhost',
                 'listen_port': '51235',
                 'cadir': '/etc/pki/func/ca',
                 'certroot': '/var/lib/func/certmaster/certs',
                 'csrroot': '/var/lib/func/certmaster/csrs',
                 'autosign': 'false'
                 }


    cm = CertMaster('/etc/func/certmaster.conf', defaults)

    if "daemon" in argv or "--daemon" in argv:
        func.utils.daemonize("/var/run/certmaster.pid")
    else:
        print "serving...\n"


    # just let exceptions bubble up for now
    serve(cm)

 

if __name__ == "__main__":
    textdomain(I18N_DOMAIN)
    main(sys.argv)


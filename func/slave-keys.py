#!/usr/bin/python -tt

import sys
import os
import os.path
from OpenSSL import crypto
import socket


def_country = 'UN'
def_state = 'FC'
def_local = 'Func-ytown'
def_org = 'func'
def_ou = 'slave-key'

cert_dir = '/home/skvidal/tmp/t'
key_file = '%s/slave.pem' % cert_dir
csr_file = '%s/slave.csr' % cert_dir


def make_cert(dest=None):
    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 2048)
    if dest:
        destfo = open(dest, 'w')
        destfo.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        destfo.close()
    
    return pkey

def make_csr(pkey, dest=None, cn=None):
    req = crypto.X509Req()
    req.get_subject()
    subj  = req.get_subject()
    subj.C = def_country
    subj.ST = def_state
    subj.L = def_local
    subj.O = def_org
    subj.OU = def_ou
    if cn:
        subj.CN = cn
    else:
        subj.CN = socket.getfqdn()
    subj.emailAddress = 'root@%s' % subj.CN       
        
    req.set_pubkey(pkey)
    req.sign(pkey, 'md5')
    if dest:
        destfo = open(dest, 'w')
        destfo.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req))
        destfo.close()

    return req

def retrieve_key_from_file(keyfile):
    fo = open(keyfile, 'r')
    buf = fo.read()
    keypair = crypto.load_privatekey(crypto.FILETYPE_PEM, buf)
    return keypair
    
def main():
    keypair = None
    try:
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        if not os.path.exists(key_file):
            keypair = make_cert(dest=key_file)
        if not os.path.exists(csr_file):
            if not keypair:
                keypair = retrieve_key_from_file(key_file)
            csr = make_csr(keypair, dest=csr_file)
    except:
        return 1
        
    return 0


if __name__ == "__main__":
   sys.exit(main())
       
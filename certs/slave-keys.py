#!/usr/bin/python -tt
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Copyright (c) 2007 Red Hat, inc 
#- Written by Seth Vidal skvidal @ fedoraproject.org

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

cert_dir = '/etc/pki/func'
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
    
def retrieve_csr_from_file(csrfile)
    fo = open(csrfile, 'r')
    buf = fo.read()
    csrreq = crypto.load_certificate_request(crypto.FILETYPE_PEM, buf)
    return csrreq
    
def submit_csr_to_master(csrfile, master):
    # stuff happens here - I can just cram the csr in a POST if need be
    pass

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
       

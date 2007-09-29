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
import xmlrpclib
import time

from  exceptions import Exception

import func.certs


def submit_csr_to_master(csr_file, master_uri):
    # get csr_file
    # submit buffer of file content to master_uri.wait_for_cert()
    # wait for response and return
    fo = open(csr_file)
    csr = fo.read()
    s = xmlrpclib.ServerProxy(master_uri)
    
    return s.wait_for_cert(csr)
    
    

def main(cert_dir, master_uri):
    keypair = None
    key_file = '%s/slave.pem' % cert_dir
    csr_file = '%s/slave.csr' % cert_dir
    cert_file = '%s/slave.cert' % cert_dir
    ca_cert_file = '%s/ca.cert' % cert_dir
    
    try:
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
        if not os.path.exists(key_file):
            keypair = func.certs.make_keypair(dest=key_file)
        if not os.path.exists(csr_file):
            if not keypair:
                keypair = func.certs.retrieve_key_from_file(key_file)
            csr = func.certs.make_csr(keypair, dest=csr_file)
    except Exception, e: # need a little more specificity here
        print e
        return 1
    
    result = False
    while not result:
        result, cert_string, ca_cert_string = submit_csr_to_master(csr_file, master_uri)
        print 'looping'
        time.sleep(10)    
    
    
    if result:
        cert_fo = open(cert_file, 'w')
        cert_fo.write(cert_string)
        cert_fo.close()

        ca_cert_fo = open(ca_cert_file, 'w')
        ca_cert_fo.write(ca_cert_string)
        ca_cert_fo.close()
    
    return 0


if __name__ == "__main__":
    if len(sys.argv[1:]) > 0: 
        cert_dir = sys.argv[1]
    else:
        cert_dir = '/etc/pki/func'
    
    if len(sys.argv[1:]) > 1:
        master_uri = sys.argv[2]
    else:
        master_uri = 'http://localhost:51235/'

    sys.exit(main(cert_dir, master_uri))
       

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
import func.certs 


cadir = '/etc/pki/func/ca'
ca_key_file = '%s/funcmaster.key' % cadir
ca_cert_file = '%s/funcmaster.crt' % cadir


def main():
    keypair = None
    try:
        if not os.path.exists(cadir):
            os.makedirs(cadir)
        if not os.path.exists(ca_key_file):
            func.certs.create_ca(ca_key_file=ca_key_file, ca_cert_file=ca_cert_file)
    except:
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
       

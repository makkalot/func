"""
Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import os
import socket
import string
import sys
import time
import traceback
import xmlrpclib
import glob

import codes
from func import certs
from func.config import read_config
from certmaster.commonconfig import MinionConfig
from func import logger

# "localhost" is a lame hostname to use for a key, so try to get
# a more meaningful hostname. We do this by connecting to the certmaster
# and seeing what interface/ip it uses to make that connection, and looking
# up the hostname for that. 
def get_hostname():

    # FIXME: this code ignores http proxies (which granted, we don't
    #      support elsewhere either. It also hardcodes the port number
    #      for the certmaster for now
    hostname = None
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except:
        return hostname
    if ip != "127.0.0.1":
        return hostname


    config_file = '/etc/certmaster/minion.conf'
    minion_config = read_config(config_file, MinionConfig)

    server = minion_config.certmaster
    port = 51235

    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((server, port))
        (intf, port) = s.getsockname()
        hostname = socket.gethostbyaddr(intf)[0]
        s.close()
    except:
        s.close()
        raise

    return hostname
    


# this is kind of handy, so keep it around for now
# but we really need to fix out server side logging and error
# reporting so we don't need it
def trace_me():
    x = traceback.extract_stack()
    bar = string.join(traceback.format_list(x))
    return bar


def daemonize(pidfile=None):
    """
    Daemonize this process with the UNIX double-fork trick.
    Writes the new PID to the provided file name if not None.
    """

    print pidfile
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    os.setsid()
    os.umask(0)
    pid = os.fork()


    if pid > 0:
        if pidfile is not None:
            open(pidfile, "w").write(str(pid))
        sys.exit(0)

def get_acls_from_config(acldir='/etc/func/minion-acl.d'):
    """
    takes a dir of .acl files
    returns a dict of hostname+hash =  [methods, to, run]
    
    """
    
    acls = {}
    if not os.path.exists(acldir):
        print 'acl dir does not exist: %s' % acldir
        return acls
    
    # get the set of files
    acl_glob = '%s/*.acl' % acldir
    files = glob.glob(acl_glob)
    
    for acl_file in files:
        
        try:
            fo = open(acl_file, 'r')
        except (IOError, OSError), e:
            print 'cannot open acl config file: %s - %s' % (acl_file, e)
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
            if not acls.has_key(host):
                acls[host] = []
            acls[host].extend(methods)
    
    return acls

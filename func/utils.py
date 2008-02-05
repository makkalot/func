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
import string
import sys
import traceback
import xmlrpclib
import socket

REMOTE_ERROR = "REMOTE_ERROR"

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

def nice_exception(etype, evalue, etb):
    etype = str(etype)
    lefti = etype.index("'") + 1
    righti = etype.rindex("'")
    nicetype = etype[lefti:righti]
    nicestack = string.join(traceback.format_list(traceback.extract_tb(etb)))
    return [ REMOTE_ERROR, nicetype, str(evalue), nicestack ] 

def get_hostname():
    fqdn = socket.getfqdn()
    host = socket.gethostname()
    if fqdn.find(host) != -1:
        return fqdn
    else:
        return host


def is_error(result):
    if type(result) != list:
        return False
    if len(result) == 0:
        return False
    if result[0] == REMOTE_ERROR:
        return True
    return False


              

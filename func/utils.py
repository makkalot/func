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

REMOTE_CANARY = "***REMOTE_ERROR***"

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

def remove_exceptions(results):
    """
    Used by forkbomb/jobthing to avoid storing exceptions in database
    because you know those don't serialize so well :)
    # FIXME: this needs cleanup
    """

    if results is None:
        return REMOTE_CANARY

    if str(results).startswith("<Fault"):
        return REMOTE_CANARY

    if type(results) == xmlrpclib.Fault:
        return REMOTE_CANARY
    
    if type(results) == dict:
        new_results = {}
        for x in results.keys():
            value = results[x]
            if str(value).find("<Fault") == -1:
                # there are interesting issues with the way it is imported and type()
                # so that is why this hack is here.  type(x) != xmlrpclib.Fault appears to miss some things
                new_results[x] = value
            else:
                new_results[x] = REMOTE_CANARY
        return new_results

    return results




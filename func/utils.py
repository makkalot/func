"""
Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import inspect
import os
import socket
import string

from certmaster.config import read_config
from certmaster.commonconfig import MinionConfig
from commonconfig import FuncdConfig


REMOTE_ERROR = "REMOTE_ERROR"


def is_error(result):
    if type(result) != list:
        return False
    if len(result) == 0:
        return False
    if result[0] == REMOTE_ERROR:
        return True
    return False


def remove_weird_chars(dirty_word):
    """
    That method will be used to clean some
    glob adress expressions because async stuff
    depends on that part
    
    @param dirty_word : word to be cleaned
    """
    from copy import copy
    copy_word = copy(dirty_word)
    copy_word = copy_word.replace("-","_")
    return copy_word

def get_formated_jobid(**id_pack):
    import time
    import pprint

    glob = remove_weird_chars(id_pack['spec'])
    module = remove_weird_chars(id_pack['module'])
    method = remove_weird_chars(id_pack['method'])
    job_id = "".join([glob,"-",module,"-",method,"-",pprint.pformat(time.time())])
    return job_id

def is_public_valid_method(obj, attr, blacklist=[]):
    if inspect.ismethod(getattr(obj, attr)) and attr[0] != '_':
        for b in blacklist:
            if attr==b:
                return False
        return True
    return False

def get_hostname_by_route():
    """
    "localhost" is a lame hostname to use for a key, so try to get
    a more meaningful hostname. We do this by connecting to the certmaster
    and seeing what interface/ip it uses to make that connection, and looking
    up the hostname for that. 
    """
    # FIXME: this code ignores http proxies (which granted, we don't
    #      support elsewhere either. 
    hostname = None
  
    minion_config_file = '/etc/func/minion.conf'
    minion_config = read_config(minion_config_file, FuncdConfig)

    # don't bother guessing a hostname if they specify it in the config file
    if minion_config.minion_name:
        return minion_config.minion_name

    # try to find the hostname attached to the ip of the interface that we use
    # to talk to the certmaster
    cm_config_file = '/etc/certmaster/minion.conf'
    cm_config = read_config(cm_config_file, MinionConfig)

    server = cm_config.certmaster
    port = cm_config.certmaster_port

    try:
        s = socket.socket()
        s.settimeout(5)
        s.connect((server, port))
        (intf, port) = s.getsockname()
         # this can fail if there is no reverse DNS available
        intf_hostname = socket.gethostbyaddr(intf)[0]
        ip = socket.gethostbyname(intf_hostname)
        # not talking via localhost? good enough...
        if ip != '127.0.0.1':
            s.close()
            return intf_hostname
    except:
        s.close()
        # something failed, reverse dns, etc

    # try to find the hostname of the ip we're listening on
    if minion_config.listen_addr:
        try:
            (hostname, aliases, ips) = socket.gethostbyaddr(minion_config.listen_addr)
        except:
            hostname = None
     
    # in an ideal world, this would return exactly what we want: the most meaningful hostname
    # for a system, but that is often not that case
    if hostname is None:
        hostname = socket.gethostname()

    # "localhost" is a really crappy hostname, so is pretty much anything attached
    # to 127.0.0.1, so try for something better
    try:
        ip = socket.gethostbyname(hostname)
    except:
        hostname = None

    # non loopback is about as good as we can do for a guess
    if ip != "127.0.0.1" and hostname is not None:
        return hostname
            
  

    # all else has failed to get a good hostname, so just return
    # an ip address
    return socket.gethostbyname(socket.gethostname())


def get_fresh_method_instance(function_ref):
    """
    That method is kind of workaround to not break the
    current api in order to add logging capabilities per
    method level. When methods are executed during xmlrpc
    calls we have a pool of references with module methods
    and overlord call them. If we want to pass those methods
    different logger instances in order to have log call per
    job_ids we shouldnt have the same method reference to be 
    called,we need fresh ones so that is how we solve that
    kind of hacky ...
    """
    
    #CAUTION HACKY IF STATEMNETS AROUND :)
    # we dont want private methods and system
    #modules around ,we should change system
    #module though ....
    if function_ref.__name__.startswith("_"):
        return function_ref
    else:
        try:
            fresh_instance = function_ref.im_self.__class__()
        except Exception,e:
            #something went wrong so we return the normal reference value
            return function_ref
        return getattr(fresh_instance,function_ref.__name__)

def should_log(args):
    if args and type(args[len(args)-1]) == dict and args[len(args)-1].has_key('__logger__') and args[len(args)-1]['__logger__'] == True:
        return True
    return False

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
import socket
import inspect

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

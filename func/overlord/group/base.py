class BaseBackend(object):
    """
    A base class for others that will
    implement a backend for groups api
    """

    def add_host_to_group(self,group,host,save=True):
        """
        Adds a host to a group
        """
        raise NotImplementedError

   
    def add_group(self,group,save=True):
        """
        Adds a group
        """
        raise NotImplementedError

    def remove_group(self,group,save=True):
        """
        Removes a group
        """
        raise NotImplementedError

    def remove_host(self,group,host,save=True):
        """
        Remove a host from groups
        """
        raise NotImplementedError

        
    def save_changes(self):
        """
        Push the stuff that is in memory
        """
        raise NotImplementedError

    def get_groups(self,pattern=None,exact=True,exclude=None):
        """
        Get a set of groups
        """
        raise NotImplementedError

    def get_hosts(self,pattern=None,group=None,exact=True,exclude=NotImplementedError):

        """
        Get a set of groups
        """
        raise NotImplementedError
    
from func.commonconfig import OVERLORD_CONFIG_FILE,OverlordConfig
from certmaster.config import read_config
CONF_FILE = OVERLORD_CONFIG_FILE

def choose_backend(backend=None,conf_file=None,db_file=None):
    """
    Chooses a backend accoding to params or what is
    supplied ...
    """

    config = read_config(CONF_FILE,OverlordConfig)
    backend = backend or config.backend or "conf"

    if backend == "sqlite":
        from func.overlord.group.sqlite_backend import SqliteBackend
        return SqliteBackend(db_file=db_file)
    elif backend == "conf":
        from func.overlord.group.conf_backend import ConfBackend
        return ConfBackend(conf_file=conf_file)
    else:
        raise Exception("No valid backend options supplied")

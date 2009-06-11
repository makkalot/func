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
    
    

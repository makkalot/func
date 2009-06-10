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

    def add_subgroup_to_group(self,group,subgroup,save=True):
        """
        Here you can add more than one subgroup to a given group
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

    def remove_subgroup(self,group,subgroup,save=True):
        """
        Remove a subgroup
        """
        raise NotImplementedError
    
    def save_changes(self):
        """
        Push the stuff that is in memory
        """
        raise NotImplementedError

    def get_groups(self,pattern=None,exact=True):
        """
        Get a set of groups
        """
        raise NotImplementedError

    def get_hosts(self,pattern=None,group=None,exact=True):

        """
        Get a set of groups
        """
        raise NotImplementedError
    
    def get_subgroups(self,pattern=None,group=None,exact=True):
        """
        Simple getter
        """
        raise NotImplementedError


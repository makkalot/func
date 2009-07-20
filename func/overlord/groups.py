from func.overlord.group.base import choose_backend
import sys
import fnmatch

def get_hosts_spec(spec):
    """
    A simple call to Minions class to be
    able to use globbing in groups when
    querying ...
    """
    from func.overlord.client import Minions

    m = Minions(spec)
    return m.get_hosts_for_spec(spec)

class Groups(object):

    def __init__(self,*args,**kwargs):
        """
        Initialize the backend you are going to use
        """
        #initialize here the backend
        self.backend = choose_backend(**kwargs)


    def show(self):
        """
        Prints some info about current structure
        """
        groups = self.get_groups()
        for g in groups:
            print "Group : %s"%g
            hosts = self.get_hosts(group=g)
            if hosts:
                for h in hosts:
                    print "\t Host : %s "%h
        

            

    def __parse_strings(self, hoststring):
        """
        the host string maybe in 2 forms
        the first one is i it can be comma separated into the
        configuration file the second one 
        is it can be ; separated and entered from
        commandline so should consider both situations

        @param hoststring : String to be parsed
        """
        hosts = []
       
        if hoststring.find(';') != -1:
            bits = hoststring.split(';')
        elif hoststring.find(',') != -1:
            bits = hoststring.split(',')
        else:
            #sometimes we have only one entry there so that will be a problem if dont have
            #a control for it will be missed otherwise :)
            if len(hoststring)!=0:
                hosts.append(hoststring)
            return hosts

        return list(set(bits))

    
    def add_group(self,group_name,save=True):
        """
        Adding a new group

        @param group_name : Group to be added
        @param save       : Save now or keep in memory and save later
        """

        return self.backend.add_group(group_name,save) 

   
    def add_hosts_to_group_glob(self,group,hoststring,exclude_string=None):
        """
        With that method we will be able add lots of machines by single
        glob string ...

        @param group : Group name that will add the hosts
        @param hoststring : Glob string to be added you can
                            add something like "www*" easy and fast
        @param save       : Save now or keep in memory and save later
        @param exclude_string :Glob string to be excluded you can
                            add something like "www*" easy and fast
        """
        hoststring = get_hosts_spec(hoststring)
        if exclude_string :
            e_s = get_hosts_spec(exclude_string)
            hoststring = hoststring.difference(e_s)

        #add them to backend
        self.add_host_list(group,list(hoststring))

    def add_hosts_to_group(self, group, hoststring):
        """
        Here you can add more than one hosts to a given group
        
        @param group : Group name that will add the hosts
        @param hoststring : A string in form of "host1;host2" or comma
                            separated one (will be parsed) ...
        
        """
        hosts = self.__parse_strings(hoststring)
        for host in hosts:
            self.add_host_to_group(group, host,save=False)
        self.save_changes()

    def add_host_to_group(self, group, host, save =True):
        """
        Add a single host to group

        @param group : Group name that will add the hosts
        @param save  : Save now or keep in memory and save later
        @param host  : Host to be added
        """
        return self.backend.add_host_to_group(group,host,save)

    def add_host_list(self,group,host_list):
        """
        Similar as other add methods but accepts a list of hosts
        instead of some strings
        
        @param group : Group name that will add the hosts
        @param host_list  : Host list

        """
        if type(host_list) != list and type(host_list)!=set:
            sys.stderr.write("We accept only lists for for add_host_list method we got %s : %s "%(host_list,type(host_list)))
            return

        for host in host_list:
            self.add_host_to_group(group, host)
        
        self.save_changes()
    
    
    def get_groups(self,pattern=None,exact=True,exclude=None):
        """
        Get a list fo groups according to args

        @param pattern : A string to match name of the group
        @param exact   : When true pattern matching is exact
                        else it gets the ones that are related
        @param exclude : A list of excluded groups useful in globbing
        """
        return self.backend.get_groups(pattern,exact,exclude)

    def get_groups_glob(self,group_string,exclude_string=None):
        """
        Get groups via glob strings

        @param group_string   : The ones that we want to pull
        @param exclude_string : The ones we dont want
        """
        all_groups = self.get_groups()
        match_groups = fnmatch.filter(all_groups,group_string)

        if exclude_string:
            exclude_groups = fnmatch.filter(all_groups,exclude_string)
            return list(set(match_groups).difference(set(exclude_groups)))
        else:
            return match_groups

    def get_hosts(self,pattern=None,group=None,exact=True,exclude=None):
        """
        Getting the list of hosts according to args
        
        @param pattern : A string to match name of the host
        @param exact   : When true pattern matching is exact
                        else it gets the ones that are related
        @param exclude : A list of excluded hosts useful in globbing
        """
        
        return self.backend.get_hosts(pattern,group,exact,exclude)

    def get_group_names(self):
        """
        Getting the groups names
        HERE ONLY FOR API COMPATIBILITY
        use get_groups() instead of that one
        """
        return self.get_groups()

    
    def _get_host_list_from_glob(self,group_globs,include_host):
        """
        A private util method that is responsible for
        extracting a list of hosts from a glob str
        """
        for group_glob in group_globs:
            if group_glob[0] != "@":
                continue
            group_glob = group_glob[1:]
            #we seek for @group:ww* thing here
            if group_glob.find(":")!=-1:
                group_str,host_str = group_glob.split(":")
                hosts = get_hosts_spec(host_str)
                #print "The hosts are ",hosts
                include_host=include_host.union(set(self.get_hosts(pattern=hosts,group=group_str,exact=True)))
            else:
                include_host=include_host.union(set(self.get_hosts(group=group_glob)))
                #print "The include host is like ",include_host
        
        return include_host

    def get_hosts_glob(self,host_string,exclude_string=None):
        """
        Get hosts via globbing

        @param host_string : The string that includes the hosts we
                             want.Example @grname:ww*;@gr2
        @param exclude_string :The string that includes the hosts we
                             dont want.Example @grname:ww*;@gr2
        """

        group_globs = host_string.split(';')
        include_host = set()
        include_host = self._get_host_list_from_glob(group_globs,include_host)
        
        #if you have a list to exclude
        if exclude_string:
            exclude_globs = exclude_string.split(';')
            exclude_host = set()
            exclude_host = self._get_host_list_from_glob(exclude_globs,exclude_host)
            return list(include_host.difference(exclude_host))
        else:
            return list(include_host)


    def get_hosts_by_group_glob(self, group_glob_str):
        """
        Here only for API COMPATIBILITY ...
        use more advanced one get_hosts_glob() method
        """
        return self.get_hosts_glob(group_glob_str)
          
    def remove_group(self,group,save=True):
        """
        Removing a group if needed
        
        @param group : Group to be removed
        @param save  : Save now or keep in memory and save later
        """
        
        return self.backend.remove_group(group,save)

    def remove_group_glob(self,group_str):
        """
        Removing group via a glob
        """
        #firstly get all groups availible
        all_groups = self.get_groups()
        remove_groups = fnmatch.filter(all_groups,group_str)
        #remove them
        self.remove_group_list(remove_groups)

    def remove_group_list(self,group_list):
        """
        Removes a group of list
        """

        if type(group_list) != list:
            sys.stderr.write("We accept only lists for for remove_group_list method")
            return False
        
        for g in group_list:
            self.remove_group(g,save=False)
        self.save_changes()


    def remove_host(self,group_name,host,save=True):
        """
        Removes a proper host from the conf file
        """
        return self.backend.remove_host(group_name,host,save)
    
    
    def remove_host_glob(self,group_name,host_str,exclude_string=None):
        copy_host_str = host_str
        host_str = get_hosts_spec(host_str)
        if exclude_string:
            e_s = get_hosts_spec(exclude_string)
            host_str = host_str.difference(e_s)

        #remove the list completely
        if not host_str: #sometimes we may have some old entries into db so 
            #that will not make a match in that case
            self.remove_host_list(group_name,[copy_host_str])    
        else:
            self.remove_host_list(group_name,host_str)    

    def remove_host_list(self,group,host_list):
        """
        Remove a whole list from the conf file of hosts
        """

        if type(host_list) != list and type(host_list) != set :
            sys.stderr.write("We accept only lists for for remove_host_list method")
            return False

        for host in host_list:
            self.remove_host(group,host,save=False)

        self.save_changes()


    def save_changes(self):
        """
        Write changes to disk
        """
        self.backend.save_changes()

    

if __name__ == "__main__":
    pass

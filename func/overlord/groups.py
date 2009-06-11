from func.overlord.client import Minions
import fnmatch

def get_hosts_spec(spec):
    m = Minions(spec)
    return m.get_hosts_for_spec(spec)

class Groups(object):

    def __init__(self, filename=None):
        """
        Get the file into the memory
        """
        #initialize here the backend
        self.backend = None


    def show(self):
        """
        Prints some info about current structure
        """
        pass

    def __parse_strings(self, hoststring):
        hosts = []
        #the host string maybe in 2 forms
        #the first one is i it can be comma separated into the
        #configuration file
        #the second one is it can be ; separated and entered from
        #commandline so should consider both situations
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

        #now append the good ones
        for bit in bits:
            bit = bit.strip().split(' ')
            for host in bit:
                if host not in hosts:
                    hosts.append(host.strip())

        return hosts
    
    def add_group(self,group_name,save=False):
        """
        Adding a new group
        """
        return self.backend.add_group(group_name,save) 

   
    def add_hosts_to_group_glob(self,group,hoststring,save=True,exclude_string=None):
        """
        With that method we will be able add lots of machines by single
        glob string ...
        """
        hoststring = get_hosts_spec(hoststring)
        if exclude_string :
            e_s = get_hosts_spec(exclude_string)
            hoststring = hoststring.difference(e_s)

        #add them to backend
        self.add_host_list(group,hoststring,save)

    def add_hosts_to_group(self, group, hoststring, save = False):
        """
        Here you can add more than one hosts to a given group
        """
        hosts = self.__parse_strings(hoststring)


        for host in hosts:
            self.add_host_to_group(group, host,save)
        self.save_changes()

    def add_host_to_group(self, group, host, save = False):
        """
        Add a single host to group
        """
        return self.backend.add_host_to_group(group,host,save)

    def add_host_list(self,group,host_list, save = False):
        """
        Similar as other add methods but accepts a list of hosts
        instead of some strings
        """
        if type(host_list) != list:
            sys.stderr.write("We accept only lists for for add_host_list method")
            return

        for host in host_list:
            self.add_host_to_group(group, host)
        
        self.save_changes()

    def add_subgroup_to_group(self, group, subgroup, save = False):
        """
        Add a single subgroup to group
        """
        self.backend.add_subgroup_to_group(group,subgroup,save)
    
    def add_subgroup_list(self,group,subgroup_list, save = False):
        """
        Similar as other add methods but accepts a list of subgroups
        instead of some strings
        """
        if type(subgroup_list) != list:
            sys.stderr.write("We accept only lists for for add_subgroup_list method")
            return

        for subgroup in subgroup_list:
            self.add_subgroup_to_group(group, subgroup)

        if save:
            self.save_changes()

    def get_groups(self,pattern=None,exact=True,exclude=None):
        """
        Simple getter
        """
        return self.backend.get_groups

    def get_hosts(self,pattern=None,group=None,exact=True,exclude=None):
        """
        Getting the hosts in a proper pattern or what is
        """
        pass

    def get_group_names(self):
        """
        Getting the groups names
        """
        return self.__groups.keys()

    def get_hosts_by_group_glob(self, group_glob_str):
        """
        What is that one ?
        """
        #split it if we have more than one
        group_gloobs = group_glob_str.split(';')
        hosts = []
        for group_gloob in group_gloobs:
            #the group globs are signed by @
            if not group_gloob[0] == "@":
                continue
            if self.__groups.has_key(group_gloob[1:]):
                hosts.extend(self.__groups[group_gloob[1:]])
                if group_gloob[1:] in self.__subgroups:
                    for subgroup in self.__subgroups[group_gloob[1:]]:
                        hosts.extend(self.__groups[subgroup])
            else:
                sys.stderr.write("group %s not defined\n" % group_gloob)

        # Because of subgroups, there is a possibility to get duplicates.
        # Remove them in Python 2.3 compatible way (by not using sets).
        unique_hosts = []
        for item in hosts:
            if not item in unique_hosts:
                unique_hosts.append(item)

        return unique_hosts

   
    def remove_group(self,group_name,save=False):
        """
        Removing a group if needed
        """
        return self.backend.remove_group(group_name,save)

    def remove_group_glob(self,group_str,save=False):
        """
        Removing group via a glob
        """
        #firstly get all groups availible
        all_groups = self.get_groups()
        remove_groups = fnmatch.filter(all_groups,group_str)

    def remove_group_list(self,group_list,save = False):
        """
        Removes a group of list
        """

        if type(host_list) != list:
            sys.stderr.write("We accept only lists for for remove_group_list method")
            return False
        
        for g in group_list:
            self.remove_group(g)
        self.save_changes()


    def remove_host(self,group_name,host,save=False):
        """
        Removes a proper host from the conf file
        """
        return self.backend.remove_group(group_name,host,save)
    
    
    def remove_host_glob(self,group_name,host_str,save=False,exclude_string=None):
        host_str = get_hosts_spec(host_str)
        if exclude_string:
            e_s = get_hosts_spec(exclude_string)
            host_str = host_str.difference(e_s)

        #remove the list completely
        self.remove_host_list(group_name,host_str,save)    

    def remove_host_list(self,group,host_list,save = False):
        """
        Remove a whole list from the conf file of hosts
        """

        if type(host_list) != list or type(host_list) != set :
            sys.stderr.write("We accept only lists for for remove_host_list method")
            return False

        for host in host_list:
            self.remove_host(group,host)

        self.save_changes()


    def save_changes(self):
        """
        Write changes to disk
        """
        self.backend.save_changes()

    
def main():
    Groups("/tmp/testgroups").show()

if __name__ == "__main__":
    main()

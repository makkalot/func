## func command line interface & client lib
##
## Copyright 2007,2008 Red Hat, Inc
## Adrian Likins <alikins@redhat.com>
## +AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##


# this module lets you define groups of systems to work with from the
# commandline. It uses an "ini" style config parser like:

#[groupname]
#host = foobar, baz, blip
#subgroup = blippy


import ConfigParser
import sys
GROUP_FILE = "/etc/func/groups"

class Groups(object):

    def __init__(self, filename=None):
        """
        Get the file into the memory
        """
        if filename:
            self.__filename = filename
        else:
            self.__filename = GROUP_FILE

        self.__groups = {}
        self.__parse()

    def __parse(self):
        
        self.cp = ConfigParser.SafeConfigParser()
        self.cp.read(self.__filename)
        
        #loop through the group_names
        for section in self.cp.sections():
            options = self.cp.options(section)
            for option in options:
                if option == "host":
                    self.add_hosts_to_group(section, self.cp.get(section, option))
                #not implemented yet do we need it ?
                if option == "subgroup":
                    continue
        
 
    def show(self):
        print self.cp.sections()
        print self.__groups

    def __parse_hoststrings(self, hoststring):
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

        #now append the god ones
        for bit in bits:
            bit = bit.strip().split(' ')
            for host in bit:
                if host not in hosts:
                    hosts.append(host.strip())

        return hosts

    def add_hosts_to_group(self, group, hoststring,save = False):
        """
        Here you can add more than one hosts to a given group
        """
        hosts = self.__parse_hoststrings(hoststring)

        #the user may left the host = empty at the beginning
        if not hosts:
            self.__groups[group] = []
            return

        for host in hosts:
            self.add_host_to_group(group, host)        

    def add_host_to_group(self, group, host,save = False):
        """
        Add a single host to group
        """
        if not self.__groups.has_key(group):
            self.__groups[group] = []
        
        #dont want duplicates
        if not host in self.__groups[group]:
            self.__groups[group].append(host) 

    def add_host_list(self,group,host_list,save = False):
        """
        Similar as other add methods but accepts a list of hosts
        instead of some strings
        """
        if type(host_list) != list:
            sys.stderr.write("We accept only lists for for add_host_list method")
            return

        for host in host_list:
            self.add_host_to_group(group,host)

        if save:
            self.save_changes()


    def get_groups(self):
        """
        Simple getter
        """
        return self.__groups

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
            else:            
                sys.stderr.write("group %s not defined\n" % group_gloob)
        #get the hosts
        return hosts

    def save_changes(self):
        """
        Write changes to disk
        """
        for group_name,group_hosts in self.__groups.iteritems():
            #if we have added a new group add it to config object
            if not group_name in self.cp.sections():
                self.cp.add_section(group_name)
            self.cp.set(group_name,"host",",".join(group_hosts))
            #print "Im in save changes and here i have : ",self.cp.get(group_name,"host")
        
        #store tha changes
        conf_file = open(self.__filename, "w")
        self.cp.write(conf_file)
        conf_file.close()


    def remove_group(self,group_name,save=False):
        """
        Removing a group if needed
        """
        if not self.__groups.has_key(group_name):
            return False
        #delete that entry
        if group_name in self.cp.sections():
            #if we have it also here should remove it
            if self.cp.has_section(group_name):
                self.cp.remove_section(group_name)
        #delete the entry
        del self.__groups[group_name]
        
        #Do you want to store it ?
        if save:
            self.save_changes()
        return True

    def remove_host(self,group_name,host,save=False):
        """
        Removes a proper host from the conf file
        """
        if not self.__groups.has_key(group_name) or not host in self.__groups[group_name]:
            return False
        
        #remove the machine from there
        self.__groups[group_name].remove(host)
        #save to config file
        if save:
            self.save_changes()

        return True

    def remove_host_list(self,group,host_list,save = False):
        """
        Remove a whole list from the conf file of hosts
        """

        if type(host_list) != list:
            sys.stderr.write("We accept only lists for for add_host_list method")
            return False

        for host in host_list:
            self.remove_host(group,host,save = False)
            
        if save:
            self.save_changes()




    def add_group(self,group_name,save=False):
        """
        Adding a new group
        """
        if self.__groups.has_key(group_name):
            return False
        #create with an empty list
        self.__groups[group_name] = []
        if save:
            self.save_changes()

        return True #success


def main():
    g = Groups("/tmp/testgroups")
    print g.show()
    


if __name__ == "__main__":
    main()

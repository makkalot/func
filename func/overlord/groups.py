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
#subgroup = blippy; flozzy

# Subgrouping is supported only one level down, but group can have both
# hosts and many subgroups with other hosts

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
        self.__subgroups = {}
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
                if option == "subgroup":
                    self.add_subgroups_to_group(section, self.cp.get(section, option))


    def show(self):
        print self.cp.sections()
        print self.__groups
        print self.__subgroups
        for group in self.get_group_names():
            print group, '=>', self.get_hosts_by_group_glob('@' + group)

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

    def add_hosts_to_group(self, group, hoststring, save = False):
        """
        Here you can add more than one hosts to a given group
        """
        hosts = self.__parse_strings(hoststring)

        #the user may left the host = empty at the beginning
        if not hosts:
            self.__groups[group] = []

        for host in hosts:
            self.add_host_to_group(group, host)

        if save:
            self.save_changes()

    def add_host_to_group(self, group, host, save = False):
        """
        Add a single host to group
        """
        if not self.__groups.has_key(group):
            self.__groups[group] = []

        #dont want duplicates
        if not host in self.__groups[group]:
            self.__groups[group].append(host)

        if save:
            self.save_changes()

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

        if save:
            self.save_changes()

    def add_subgroups_to_group(self, group, subgroupstring, save = False):
        """
        Here you can add more than one subgroup to a given group
        """
        subgroups = self.__parse_strings(subgroupstring)

        if not subgroups and group not in self.__subgroups:
            self.__subgroups[group] = []

        # Add empty group when subgroup is not empty to also have groups without
        # in groups dict.
        if subgroups and group not in self.__groups:
            self.__groups[group] = []

        for subgroup in subgroups:
            self.add_subgroup_to_group(group, subgroup)

        if save:
            self.save_changes()

    def add_subgroup_to_group(self, group, subgroup, save = False):
        """
        Add a single subgroup to group
        """
        if group not in self.__groups:
            self.__groups[group] = []

        if group not in self.__subgroups:
            self.__subgroups[group] = []

        #dont want duplicates
        if subgroup not in self.__subgroups[group]:
            self.__subgroups[group].append(subgroup)

        if save:
            self.save_changes()

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

    def get_groups(self):
        """
        Simple getter
        """
        return self.__groups

    def get_subgroups(self):
        """
        Simple getter
        """
        return self.__subgroups

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

    def save_changes(self):
        """
        Write changes to disk
        """
        for group_name,group_hosts in self.__groups.iteritems():
            #if we have added a new group add it to config object
            if not group_name in self.cp.sections():
                self.cp.add_section(group_name)
            self.cp.set(group_name,"host",",".join(group_hosts))
            if group_name in self.__subgroups:
                self.cp.set(group_name,"subgroup",",".join(self.__subgroups[group_name]))
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

        if group_name in self.__subgroups:
            del self.__subgroups[group_name]

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

    def remove_subgroup(self, group_name, subgroup, save=False):
        """
        Removes a proper subgroup from the conf file
        """
        if not self.__subgroups.has_key(group_name) or not subgroup in self.__subgroups[group_name]:
            return False

        #remove the machine from there
        self.__subgroups[group_name].remove(subgroup)

        # remove subgroup if it is empty
        if not self.__subgroups[group_name]:
            del self.__subgroups[group_name]

        #save to config file
        if save:
            self.save_changes()

        return True

    def remove_host_list(self,group,host_list,save = False):
        """
        Remove a whole list from the conf file of hosts
        """

        if type(host_list) != list:
            sys.stderr.write("We accept only lists for for remove_host_list method")
            return False

        for host in host_list:
            self.remove_host(group,host,save = False)

        if save:
            self.save_changes()

    def remove_subgroup_list(self, group, subgroup_list, save = False):
        """
        Remove a whole list from the conf file of subgroups
        """

        if type(subgroup_list) != list:
            sys.stderr.write("We accept only lists for for remove_subgroup_list method")
            return False

        for subgroup in subgroup_list:
            self.remove_subgroup(group, subgroup)

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
    Groups("/tmp/testgroups").show()

if __name__ == "__main__":
    main()

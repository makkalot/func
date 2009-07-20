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


from func.overlord.group.base import BaseBackend

class ConfBackend(BaseBackend):
    """
    That backend uses a configuraton file for 
    keeping the stuff
    """
    def __init__(self,conf_file = None,*args,**kwargs):
        """
        Initializing the database if it doesnt exists it is created and
        connection opened for serving nothing special

        @param conf_file : Configuration file
        """
        self.config = conf_file or GROUP_FILE
        self.__groups = {}
        self.__parse()


    
    def __parse(self):

        self.cp = ConfigParser.SafeConfigParser()
        self.cp.read(self.config)

        #loop through the group_names
        for section in self.cp.sections():
            options = self.cp.options(section)
            for option in options:
                if option == "host":
                    hosts = self.cp.get(section,option)
                    hosts = hosts.split(",")
                    for h in hosts:
                        self.add_host_to_group(section,h,save=False)
                        
    def add_host_to_group(self,group,host,save=True):
        """
        Adds a host to a group
        """
        if not self.__groups.has_key(group):
            self.__groups[group] = []

        #dont want duplicates
        if not host in self.__groups[group]:
            if host:
                self.__groups[group].append(host)
        else:
            return (False,"Host is already in database : %s"%host)

        if save:
            self.save_changes()
        return (True,"")
    
    def add_group(self,group,save=True):
        """
        Adds a group
        """
        if self.__groups.has_key(group):
            return (False,"Group name : %s already exists"%group)
        #create with an empty list
        self.__groups[group] = []
        if save:
            self.save_changes()

        return (True,'') #success

    def remove_group(self,group,save=True):
        """
        Removes a group
        """
        if not self.__groups.has_key(group):
            return (False,"Group name : %s doesnt exist"%group)
        #delete that entry
        if group in self.cp.sections():
            #if we have it also here should remove it
            if self.cp.has_section(group):
                self.cp.remove_section(group)
        #delete the entry
        del self.__groups[group]

        #Do you want to store it ?
        if save:
            self.save_changes()
        return (True,'')

    def remove_host(self,group,host,save=True):
        """
        Remove a host from groups
        """
        if not self.__groups.has_key(group) or not host in self.__groups[group]:
            return (False,"Non existing group or name")
        
        #remove the machine from there
        self.__groups[group].remove(host)
        #save to config file
        if save:
            self.save_changes()

        return (True,'')

    
    def save_changes(self):
        """
        Write changes to disk
        """
        for group_name,group_hosts in self.__groups.iteritems():
            #if we have added a new group add it to config object
            if not group_name in self.cp.sections():
                self.cp.add_section(group_name)
            self.cp.set(group_name,"host",",".join(group_hosts))

        #store tha changes
        conf_file = open(self.config, "w")
        self.cp.write(conf_file)

    
    def get_groups(self,pattern=None,exact=True,exclude=None):
        """
        Get a list of groups

        @param pattern : You may request to get an exact host or
                         a one in proper pattern .
        @param exact   : Related to pattern if you should do exact 
                         matching or related one.
        @param exclude : A list to be excluded from final set

        """
        if not pattern:
            #return all of them
            if not exclude:
                return self.__groups.keys()
            else:
                #get the difference of 2 sets 
                return list(set(self.__groups.keys()).difference(set(exclude)))
        else:
            #it seems there is a pattern
            if exact:
                #there is no mean to check here for
                #exclude list ...
                for g in self.__groups.keys():
                    if g == pattern:
                        return [g]
                return []

            else:#not exact match
                if not exclude:#there is no list to exclude
                    tmp_l = set()
                    for g in self.__groups.keys():
                        if pattern.lower() in g.lower():
                            tmp_l.add(g)
                    return list(tmp_l)
                else:
                    tmp_l = set()
                    for g in self.__groups.keys():
                        if pattern.lower() in g.lower():
                            tmp_l.add(g)
                    #get the difference of 2 sets
                    return list(tmp_l.difference(set(exclude)))

            #shouldnt come here actually
            return []


    def get_hosts(self,pattern=None,group=None,exact=True,exclude=None):

        """
        Get a set of hosts
        
        @param pattern : You may request to get an exact host or
                         a one in proper pattern .
        @param exact   : Related to pattern if you should do exact 
                         matching or related one.
        @param exclude : A list to be excluded from final set
        """
        #print "Caling %s:%s"%(pattern,group)
        group = self.get_groups(pattern=group,exact=True)
        #print "The group we got is : ",group
        if not group or len(group)>1:
            return []

        hosts = self.__groups[group[0]]
        #print "The hosts we got are ",hosts 

        if not pattern:
            #return all of them
            if not exclude:
                #print "Returning back the hosts ",hosts
                return hosts
            else:
                #get the difference of 2 sets 
                return list(set(hosts()).difference(set(exclude)))
        else:
            #it seems there is a pattern
            if exact:
                #there is no mean to check here for exclude list ...
                if type(pattern)==str:
                    for g in hosts:
                        if g == pattern:
                            return [g]
                else:
                    #sometimes we pass all list to compare em
                    tmp = []
                    for p in pattern:
                        if p in hosts:
                            tmp.append(p)
                    return tmp
                return []

            else:#not exact match
                if not exclude:#there is no list to exclude
                    tmp_l = set()
                    for g in hosts:
                        if pattern.lower() in g.lower():
                            tmp_l.add(g)
                    return list(tmp_l)
                else:
                    tmp_l = set()
                    for g in hosts:
                        if pattern.lower() in g.lower():
                            tmp_l.add(g)
                    #get the difference of 2 sets
                    return list(tmp_l.difference(set(exclude)))

            #shouldnt come here actually
            return []


    

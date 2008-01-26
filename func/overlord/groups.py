#!/usr/bin/python

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
import os


class Groups(object):

    def __init__(self, filename="/etc/func/groups"):
        self.filename = filename
        self.group_names = {}
        self.groups = {}
        self.__parse()

    def __parse(self):
        
        self.cp = ConfigParser.SafeConfigParser()
        self.cp.read(self.filename)

        for section in self.cp.sections():
            self.add_group(section)
            options = self.cp.options(section)
            for option in options:
                if option == "host":
                    self.add_hosts_to_group(section, self.cp.get(section, option))
                if option == "subgroup":
                    pass
        
 
    def show(self):
        print self.cp.sections()
        print self.groups

    def add_group(self, group):
        pass

    def __parse_hoststrings(self, hoststring):
        hosts = []
        bits = hoststring.split(';')
        for bit in bits:
            blip = bit.strip().split(' ')
            for host in blip:
                if host not in hosts:
                    hosts.append(host.strip())

        return hosts

    def add_hosts_to_group(self, group, hoststring):
        hosts = self.__parse_hoststrings(hoststring)
        for host in hosts:
            self.add_host_to_group(group, host)

        

    def add_host_to_group(self, group, host):
        if not self.groups.has_key(group):
            self.groups[group] = []
        self.groups[group].append(host) 

    def get_groups(self):
        return self.groups



def main():
    g = Groups("/tmp/testgroups")
    print g.show()
    


if __name__ == "__main__":
    main()

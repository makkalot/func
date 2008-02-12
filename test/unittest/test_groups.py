#!/usr/bin/python

# unit tests for group functionality in func

import os
import func.overlord.client as fc

import ConfigParser

GROUP_TEST="/tmp/func.test.groups"

class GroupFileBuilder(object):
    def __init__(self, filename=GROUP_TEST):
        self.filename = filename
        if os.access(self.filename, os.R_OK):
            os.unlink(self.filename)
        self.cp = ConfigParser.SafeConfigParser()
        
    def create(self, dict):
        # dict is a dict of section names, whose values
        # are a list of tuples of key=value
        # aka foo = {'section1':[(key1, value1), (key2, value2)],
        #            "section2":[(key3, value3)]}
        for section in dict.keys():
            self.cp.add_section(section)
            for (option, value) in dict[section]:
                self.cp.set(section, option, value)

        fo = open(self.filename, "a+")
        self.cp.write(fo)


class GroupsBase(object):
    def __init__(self):
        self.minions = fc.Minions("*", groups_file=GROUP_TEST)


    def test_expand_servers(self):
        result = self.minions.get_urls()
        print result

    def test_get_groups(self):
        result = self.minions.group_class.get_groups()
        print result


class Groups(GroupsBase):
    def get_hosts_by_group_goo(self, group_goo):
        group_dict = fc.get_groups()
        hosts = fc.get_hosts_by_groupgoo(group_dict, group_goo)
        print hosts

class TestGroups(Groups):
    def __init__(self):
        self.minions = fc.Minions("@blippy", groups_file=GROUP_TEST)

    def setUp(self):
        self.gfb = GroupFileBuilder()
        self.gfb.create({'blippy':[('host', 'localhost')]})

    def test_get_host_by_group_goo(self):
        results = self.minions.get_urls()
        print results

        

        
# FIXME: comment this out till I setup a way to test with a speciic
#        test config -akl

#    def test_get_hosts_by_groupgoo(self):
#        group_dict = fc.get_groups()
#        hosts = fc.get_hosts_by_groupgoo(group_dict, "@blippy")
#        print hosts

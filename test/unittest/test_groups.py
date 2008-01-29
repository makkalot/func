#!/usr/bin/python

# unit tests for group functionality in func

import func.overlord.client as fc



class TestGroups(object):

    def test_expand_servers(self):
        result = fc.expand_servers("*")
        print result

    def test_get_groups(self):
        result = fc.get_groups()
        print result

    def test_get_hosts_by_groupgoo(self):
        group_dict = fc.get_groups()
        hosts = fc.get_hosts_by_groupgoo(group_dict, "@blippy")
        print hosts

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
        
    def create(self, group_dict):
        # dict is a dict of section names, whose values
        # are a list of tuples of key=value
        #the dict should be : {'groupname':{'option':(values),'option2':(values)}}
        for section,section_value in group_dict.iteritems():
            self.cp.add_section(section)
            for host_option,hosts in section_value.iteritems():
                self.cp.set(section,host_option,",".join(hosts))
        
        #save the changes
        fo = open(self.filename, "w")
        self.cp.write(fo)


class TestGroupsBase(object):

    def setUp(self):
        self.minions = fc.Minions("*", groups_file=GROUP_TEST)
        import os
        
        #we want a fresh copy :)
        if os.path.exists(GROUP_TEST):
            os.remove(GROUP_TEST)

        self.gfb = GroupFileBuilder()
        self.the_groups_dict = {
            "home_group":{'host':['first','second','third']},
            }

        self.test_dict = {
            "home_group":['first','second','third']
            }
            
       
        #create the file
        self.gfb.create(self.the_groups_dict)
   

    def test_get_groups(self):
        #will reset on every test
        self.setUp()
        result = self.minions.group_class.get_groups()
        assert self.test_dict == result

    def test_get_group_names(self):
        self.setUp()
        result = self.minions.group_class.get_group_names()
        assert self.test_dict.keys() == result


    def test_add_hosts_to_group(self):
        self.setUp()
        self.minions.group_class.add_hosts_to_group("home_group","fourth,sixth")
        result = self.minions.group_class.get_groups()
        self.test_dict["home_group"].append("fourth")
        self.test_dict["home_group"].append("sixth")
        
        #print "The result we got is : ",result
        #print "The current into memory is : ",self.test_dict
        assert self.test_dict == result
        
        self.minions.group_class.add_hosts_to_group("home_group","wormy;troll")
        self.test_dict["home_group"].append("wormy")
        self.test_dict["home_group"].append("troll")
        assert self.test_dict == result
        

    def test_add_host_to_group(self):
        self.setUp()
        
        self.minions.group_class.add_host_to_group("home_group","bloop")
        result = self.minions.group_class.get_groups()
        self.test_dict["home_group"].append("bloop")
        assert self.test_dict == result
        
    def test_add_host_list(self):
        
        self.setUp()
        self.minions.group_class.add_host_list("home_group",["bloop","woop","zoo"])
        self.test_dict["home_group"].extend(["bloop","woop","zoo"])
        result = self.minions.group_class.get_groups()
        assert self.test_dict == result
       #add one for save 
        self.minions.group_class.add_host_list("home_group",["hey.com"],save = True)
        result = self.minions.group_class.get_groups()
        assert result == self.util_save_change()


    def test_save_changes(self):
        self.setUp()
        self.minions.group_class.add_host_to_group("home_group","bloop")
        self.minions.group_class.save_changes()
        result = self.minions.group_class.get_groups()
        
        assert result == self.util_save_change()

    def test_remove_group(self):
        self.setUp()
        self.minions.group_class.add_group("lab_group")
        self.minions.group_class.add_host_to_group("lab_group","bloop")
        result = self.minions.group_class.get_groups()
        self.test_dict["lab_group"]=[]
        self.test_dict["lab_group"].append("bloop")

        assert self.test_dict == result
        
        self.minions.group_class.remove_group("lab_group")
        result = self.minions.group_class.get_groups()
        del self.test_dict["lab_group"]
        assert self.test_dict == result
            
        #what if activated the save changes
        self.minions.group_class.add_group("lab_group")
        self.minions.group_class.add_host_to_group("lab_group","bloop")
        self.minions.group_class.save_changes()
        self.minions.group_class.remove_group("lab_group",save = True)
        result = self.minions.group_class.get_groups()
        assert result == self.util_save_change()
       


    def test_remove_host(self):
        self.setUp()
        self.minions.group_class.remove_host("home_group","first")
        self.test_dict["home_group"].remove("first")
        result = self.minions.group_class.get_groups()
        assert self.test_dict == result

        #if activated the save changes ON
        self.minions.group_class.remove_host("home_group","second",save = True)
        result = self.minions.group_class.get_groups()
        
        #print "The result we got is : ",result
        #print "The data from file is :i ",self.util_save_change()
        assert result == self.util_save_change()

    def test_remove_host_list(self):
        self.setUp()
        self.minions.group_class.remove_host_list("home_group",["first","second"])
        self.test_dict["home_group"].remove("first")
        self.test_dict["home_group"].remove("second")
        result = self.minions.group_class.get_groups()
        assert self.test_dict == result
        
        #also check the save situation
        self.minions.group_class.add_host_to_group("home_group","bloop")
        self.minions.group_class.remove_host_list("home_group",["bloop"],save = True)
        result = self.minions.group_class.get_groups()
        assert result == self.util_save_change()


    def test_add_group(self):
        self.setUp()
        self.minions.group_class.add_group("lab_group")
        self.test_dict["lab_group"]=[]
        result = self.minions.group_class.get_groups()
        
        #print "The result after adding the group is : ",result
        #print "The current test dict is : ",self.test_dict
        #if you have chosen to save the changes ?
        assert self.test_dict == result
        
        self.minions.group_class.add_group("data_group",save = True)
        self.test_dict["data_group"]=[]
        result = self.minions.group_class.get_groups()
        #print "The result we got is : ",result
        #print "The data from file is :i ",self.util_save_change()
        assert result == self.util_save_change()

    def util_save_change(self):
        """
        Will create a tmp object of groups to pull
        current changes from conf file

        """
        tmp_minions = fc.Minions("*", groups_file=GROUP_TEST)
        result = tmp_minions.group_class.get_groups()
        del tmp_minions

        #result tobe tested
        return result

    def test_get_hosts_by_group_glob(self):
        
        self.setUp()
        spec = "@home_group;some*.com"
        tmp_minions = fc.Minions(spec, groups_file=GROUP_TEST)
        result = tmp_minions.group_class.get_hosts_by_group_glob(spec)
        #print "test_get_hosts_by_group_glob result is : ",result
        assert result == self.test_dict["home_group"]


class TestMinionGroups(object):
    """
    Test the minion methods that wraps the group classes
    """
    def setUp(self):
        from certmaster.certmaster import CertMaster
        cm = CertMaster()
       
        #firstly create a group of some real ones
        self.signed_certs = cm.get_signed_certs()
        
        #we want a fresh copy :)
        if os.path.exists(GROUP_TEST):
            os.remove(GROUP_TEST)

        self.gfb = GroupFileBuilder()
        self.the_groups_dict = {
            "home_group":{'host':self.signed_certs},
            }

        self.test_dict = {
            "home_group":self.signed_certs
            }
            
       
        #create the file
        self.gfb.create(self.the_groups_dict)
   

        #print "The signet certs are : ",cm.get_signed_certs()
        #self.spec = "@home_group;some*.com"
        self.spec = "*"
        self.test_minions = fc.Minions(self.spec, groups_file=GROUP_TEST)


    def test_get_urls(self):
        the_urls = self.test_minions.get_urls()
        print the_urls

    def test_get_all_hosts(self):
        self.setUp()
        result = self.test_minions.get_all_hosts()
        #print "The result is : ",result
        #print "The home group is : ",self.test_dict["home_group"]
        assert result == self.test_dict["home_group"]

from func.overlord.groups import Groups,get_hosts_spec
from certmaster.config import read_config, CONFIG_FILE
from certmaster.commonconfig import CMConfig
import os
import fnmatch

from func.overlord.group.conf_backend import ConfBackend
from func.overlord.group.sqlite_backend import SqliteBackend
       

TEST_DB_FILE = "/tmp/test_sqlite.db"
TEST_CONF_FILE = "/tmp/test_conf.conf"


class BaseMinions(object):
    
    def create_dummy_minions(self,howmany=None):
        """
        Creates a lots of minions so we can query
        with different minion names cool isnt it
        """

        cm_config = read_config(CONFIG_FILE, CMConfig)
        howmany = howmany or 100 #it is a good default number
        
        final_list = []
        for m in xrange(howmany):
            tmp_f = open("%s/%s.%s" % (cm_config.certroot,str(m),cm_config.cert_extension),"w")
            tmp_f.close()
            final_list.append(str(m))
        print "%d dummy minions created "%howmany
        return final_list

    def clean_dummy_minions(self,howmany=None):
        """
        Deletes a lots of minions garbage
        """

        cm_config = read_config(CONFIG_FILE, CMConfig)
        howmany = howmany or 100 #it is a good default number

        for m in xrange(howmany):
            tmp_f = "%s/%s.%s" % (cm_config.certroot,str(m), cm_config.cert_extension)
            if os.path.exists(tmp_f):
                os.remove(tmp_f)

        print "%d dummy minions cleaned "%howmany


class BaseGroupT(object):
    
    backends = [
                {'backend':'sqlite','db_file':TEST_DB_FILE},
                {'backend':'conf','conf_file':TEST_CONF_FILE}
                ]
    
    def refresh_backend(self,g_object):
        """
        Here you should add your object in if statements
        """
        from func.overlord.group.conf_backend import ConfBackend
        from func.overlord.group.sqlite_backend import SqliteBackend
       
        if isinstance(g_object.backend,ConfBackend):
            return Groups(**self.backends[1])
        elif isinstance(g_object.backend,SqliteBackend):
            return Groups(**self.backends[0])
        else:
            return None

    def get_group_objects(self):
        """
        Initializer
        """
        
        gr_list = []
        for b in self.backends:
            gr_list.append(Groups(**b))

        return gr_list
    
    def clean_t_files(self,path):
        """
        Clean the initialized stuff
        """
        if os.path.exists(path):
            os.remove(path)


class TestGroupApi(BaseGroupT,BaseMinions):

    def setUp(self):
        """
        Will be called after every
        """
        #clean current files
        self.clean_t_files(TEST_DB_FILE)
        self.clean_t_files(TEST_CONF_FILE)
        
        #destroy and create minions
        self.clean_dummy_minions()
        self.current_minions = self.create_dummy_minions()
        #get groups
        self.groups = self.get_group_objects()
    
    def teardown(self):
        """
        Clean the stuff
        """
        self.clean_dummy_minions()
        self.clean_t_files(TEST_DB_FILE)
        self.clean_t_files(TEST_CONF_FILE)
        
    def test_add_group(self):
        """
        adds a single group item
        """
        for g in self.groups:
            assert g.add_group("group1",save=True)[0]== True
            g = self.refresh_backend(g)
            assert g.add_group("group1")[0] == False

    
    
    def test_add_host_to_group(self):
        """
        adds a host test
        """
        g_name = "group1"

        for g in self.groups:
            g.add_group(g_name)
            assert g.add_host_to_group(g_name,"host1")[0] == True
            g = self.refresh_backend(g)
            assert g.add_host_to_group(g_name,"host1")[0] == False
            
            
    def test_add_hostst_to_group(self):
        """
        Test adding hosts via string
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_hosts_to_group(g_name,"host1,host2,host3")
            g = self.refresh_backend(g)
            g.add_hosts_to_group(g_name,"host5;host7;host8")
    
    def test_add_host_list(self):
        """
        Test adding hosts via list
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host1","host2","host3"])
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host1","host2","host3"])
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host4","host5","host6"])

    def test_add_hosts_to_group_glob(self):
        """
        Test globbing addition
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_hosts_to_group_glob(g_name,"*") #add all of them
            g = self.refresh_backend(g)

        self.groups = self.get_group_objects()        
        for g in self.groups:
            for h in self.current_minions:
                if self.current_minions.index(h) %10 == 0:
                    print "Tests completed : ",self.current_minions.index(h)
                assert g.add_host_to_group(g_name,h)[0] == False
                #print "Let see IT ",g.add_host_to_group(g_name,h)[0]
                g = self.refresh_backend(g)
       
        #clear again so we can test exclude thing
        self.teardown()
        self.setUp()
        
        #print "Testing exclude string ...."

        self.groups = self.get_group_objects()        
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_hosts_to_group_glob(g_name,"*",exclude_string="*[1,3,5,7,9]")
            g = self.refresh_backend(g)
            #add all of them
            for h in self.current_minions:
                #print "Checking for : ",h
                if int(h)%2==0:
                    assert g.add_host_to_group(g_name,h)[0] == False
                    g = self.refresh_backend(g)
                else:
                    assert g.add_host_to_group(g_name,h)[0] == True
                    g = self.refresh_backend(g)

    
    def test_get_groups(self):
        """
        test get groups
        """
        for g in self.groups:
            g.add_group("group1")
            g = self.refresh_backend(g)
            g.add_group("group2")
            g = self.refresh_backend(g)
            #get all groups
            grs = g.get_groups()
            assert self._t_compare_arrays(grs,["group1","group2"]) == True
            
            #get one
            tmg = g.get_groups(pattern="group1")
            assert tmg==["group1"]
            
            tmg = g.get_groups(pattern="gr",exact=False)
            assert self._t_compare_arrays(tmg,["group1","group2"])==True
            
            tmg = g.get_groups(pattern="gr",exact=False,exclude=["group2"])
            assert tmg == ["group1"]
            
            #test also an empty one
            tmg = g.get_groups(pattern="group3")
            assert tmg == []
            
   
    def test_get_groups_glob(self):
       """
       Globbing in groups
       """
       for g in self.groups:
            g.add_group("group1")
            g = self.refresh_backend(g)
            g.add_group("group2")
            g = self.refresh_backend(g)
            #get all groups
            grs = g.get_groups_glob("*")
            assert self._t_compare_arrays(grs,["group1","group2"]) == True
            
            #get one
            tmg = g.get_groups_glob("*[1]")
            assert tmg == ["group1"]
            
            tmg = g.get_groups_glob("*",exclude_string="*[2]")
            assert tmg == ["group1"]
            
            #test also an empty one
            tmg = g.get_groups_glob("*[3]")
            assert tmg == []
    
    def test_get_hosts(self):
        """
        Get hosts tests
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host1","host2","host3"])
            g = self.refresh_backend(g)
            
            hosts = g.get_hosts(group=g_name)
            assert self._t_compare_arrays(hosts,["host1","host2","host3"]) == True

            #get only one
            host = g.get_hosts(pattern="host1",group=g_name)
            assert host == ["host1"]
            
            #get pattern
            host = g.get_hosts(pattern="ho",group=g_name,exact=False)
            assert self._t_compare_arrays(host,["host1","host2","host3"]) == True

            host = g.get_hosts(pattern="ho",group=g_name,exact=False,exclude=["host1","host2"])
            assert host==["host3"]

            #an empty test also
            host = g.get_hosts(pattern="host4")
            assert host==[]

    def test_get_hosts_glob(self):
        """
        test hosts for glob strings
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_hosts_to_group_glob(g_name,"*") #add all of them
            g = self.refresh_backend(g)
            
            hosts = g.get_hosts_glob("@group1")
            assert self._t_compare_arrays(hosts,self.current_minions) == True
            
            #try subgroupping thing on the fly
            hosts = g.get_hosts_glob("@group1:[0-9]")
            assert self._t_compare_arrays(hosts,list(range(10))) == True

            #try the exclude string
            hosts = g.get_hosts_glob("@group1",exclude_string="@group1:[0-9][0-9]")
            assert self._t_compare_arrays(hosts,list(range(10))) == True
            hosts = g.get_hosts_glob("@group1:[1-5][0-9];@group1:[6-9][0-9]",exclude_string="@group1:[1-8][0-9];@group1:[9][0-9]")
            assert self._t_compare_arrays(hosts,[]) == True

    def test_remove_group(self):
        """
        remove group test
        """
        for g in self.groups:
            g.add_group("group1")
            g = self.refresh_backend(g)
            #removing the group
            assert g.remove_group("group1")[0] == True
            g = self.refresh_backend(g)
            assert g.remove_group("group1")[0] == False
            g = self.refresh_backend(g)
            grs = g.get_groups_glob("*")
            assert grs == []

    def test_remove_group_list(self):
        """
        remove a list of groups
        """

        for g in self.groups:
            g.add_group("group1")
            g = self.refresh_backend(g)
            g.add_group("group2")
            g = self.refresh_backend(g)
            #removing the group
            g.remove_group_list(["group1","group2"])
            g = self.refresh_backend(g)
            grs = g.get_groups_glob("*")
            assert grs == []
    
    def test_remove_group_glob(self):
        """
        Remove groups by glob
        """
        for g in self.groups:
            g.add_group("group1")
            g = self.refresh_backend(g)
            g.add_group("group2")
            g = self.refresh_backend(g)
            #removing the group
            g.remove_group_glob("gr*")
            g = self.refresh_backend(g)
            grs = g.get_groups_glob("*")
            assert grs == []
    
    def test_remove_host(self):
        """
        remove host test
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host1","host2","host3"])
            g = self.refresh_backend(g)
            
            assert g.remove_host(g_name,"host1")[0] == True 
            g = self.refresh_backend(g)
            assert g.remove_host(g_name,"host1")[0] == False 
            g = self.refresh_backend(g)
            hosts = g.get_hosts(group=g_name)
            assert self._t_compare_arrays(hosts,["host2","host3"])
            assert g.remove_host(g_name,"host2")[0] ==True
            g = self.refresh_backend(g)
            hosts = g.get_hosts(group=g_name)
            assert self._t_compare_arrays(hosts,["host3"])

    
    def test_remove_host_list(self):
        """
        Remove the host list
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_host_list(g_name,["host1","host2","host3"])
            g = self.refresh_backend(g)
            g.remove_host_list(g_name,["host1","host2"])
            g = self.refresh_backend(g)
            hosts = g.get_hosts(group=g_name)
            assert hosts == ["host3"]
    
    def test_remove_host_glob(self):
        """
        Remove hosts bu glob
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g = self.refresh_backend(g)
            g.add_hosts_to_group_glob(g_name,"*") #add all of them
            g = self.refresh_backend(g)
            
            g.remove_host_glob("group1","*")
            g = self.refresh_backend(g)
            hosts = g.get_hosts_glob("@group1")
            assert hosts==[]
            
            g.add_hosts_to_group_glob(g_name,"*") #add all of them
            g = self.refresh_backend(g)
            #try subgroupping thing on the fly
            g.remove_host_glob("group1","[0-9][0-9]")
            g = self.refresh_backend(g)
            hosts = g.get_hosts_glob("@group1:*")
            assert self._t_compare_arrays(hosts,list(range(10))) == True
            #try the exclude string
            g.remove_host_glob("group1","*",exclude_string="[0-9][0-9]")
            g = self.refresh_backend(g)
            hosts = g.get_hosts_glob("@group1:*")
            assert self._t_compare_arrays(hosts,[]) == True

    def _t_compare_arrays(self,one,two):
        return compare_arrays(one,two)

def compare_arrays(one,two):
    if not one == two:
        if not one or not two:
            return False
    else:
        return True

    two = [str(i) for i in two]
    for o in one:
        if not o in two:
            return False
    return True


from func.overlord.client import Minions
class TestMinionGroups(BaseMinions):
    """
    Test the minion methods that wraps the group classes
    """
    
    backends = [
                {'groups_backend':'sqlite','db_file':TEST_DB_FILE},
                {'groups_backend':'conf','conf_file':TEST_CONF_FILE}
                ]
    
    def teardown(self):
        for path in [TEST_DB_FILE,TEST_CONF_FILE]:
            if os.path.exists(path):
                os.remove(path)
    
        self.clean_dummy_minions()
    
    def setUp(self):
        #destroy and create minions
        self.clean_dummy_minions()
        self.current_minions = self.create_dummy_minions()
        #get groups

    def test_get_urls(self):
        for backend_dict in self.backends:
            #create a minion with relevant backens
            m = Minions("[0-9]",**backend_dict)
            hosts = m.get_urls()
            print hosts


    def test_get_hosts_for_spec(self):
        """
        Testing the minions just to pull things for a spec
        """
        spec = "*"
        m = Minions(spec)
        minions = m.get_hosts_for_spec(spec)
        assert compare_arrays(minions,self.current_minions) == True

    
    def test_get_all_hosts(self):
        """
        Getting all hosts
        """
        for backend_dict in self.backends:
            #create a minion with relevant backens
            m = Minions("*",**backend_dict)
            #create some groups and hosts into that Minion
            m.group_class.add_group("group1")
            m.group_class.add_hosts_to_group_glob("group1","[0-9]")
            
            hosts = m.get_all_hosts()
            assert compare_arrays(hosts,self.current_minions) == True
            
            #now test with grouping
            m = Minions("[1][0-9];@group1:*",**backend_dict)
            hosts = m.get_all_hosts()
            assert compare_arrays(hosts,range(20)) == True

            m = Minions("[1][0-5];@group1:[5-9]",**backend_dict)
            hosts = m.get_all_hosts()
            assert compare_arrays(hosts,range(5,16)) == True
            
            #do some testing about exclude string
            m = Minions("*",exclude_spec="[1-9][0-9]",**backend_dict)
            hosts = m.get_all_hosts()
            assert compare_arrays(hosts,range(10)) == True

            m = Minions("[1][0-5];@group1:[5-9]",exclude_spec="[1][3-5];@group1:[5-7]",**backend_dict)
            hosts = m.get_all_hosts()
            assert compare_arrays(hosts,range(8,13)) == True




if __name__ == "__main__":
    b = BaseMinions()
    b.create_dummy_minions()
    #b.clean_dummy_minions()

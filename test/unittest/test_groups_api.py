from func.overlord.groups import Groups
from certmaster.config import read_config, CONFIG_FILE
from certmaster.commonconfig import CMConfig
import os
import fnmatch

TEST_DB_FILE = "/tmp/test_sqlite.db"
TEST_CONF_FILE = "/tmp/test_conf.conf"


class BaseMinions(object):
    
    def create_dummy_minions(self,howmany=None):
        """
        Creates a lots of minions so we can query
        with different minion names cool isnt it
        """

        cm_config = read_config(CONFIG_FILE, CMConfig)
        howmany = howmany or 10000 #it is a good default number
        
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
        howmany = howmany or 10000 #it is a good default number

        for m in xrange(howmany):
            tmp_f = "%s/%s.%s" % (cm_config.certroot,str(m), cm_config.cert_extension)
            if os.path.exists(tmp_f):
                os.remove(tmp_f)

        print "%d dummy minions cleaned "%howmany


class BaseGroupT(object):

    def get_group_objects(self):
        """
        Initializer
        """
        backends = [
                {'backend':'sqlite','db_file':TEST_DB_FILE},
                {'backend':'conf','conf_file':TEST_CONF_FILE}
                ]
        gr_list = []
        for b in backends:
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
    
    
    def test_add_group(self):
        """
        adds a single group item
        """
        for g in self.groups:
            assert g.add_group("group1")[0]== True
            assert g.add_group("group1")[0] == False

    
    
    def test_add_host_to_group(self):
        """
        adds a host test
        """
        g_name = "group1"

        for g in self.groups:
            g.add_group(g_name)
            assert g.add_host_to_group(g_name,"host1")[0] == True
            assert g.add_host_to_group(g_name,"host1")[0] == False
            
            
    def test_add_hostst_to_group(self):
        """
        Test adding hosts via string
        """
        g_name = "group1"
        for g in self.groups:
            g.add_group(g_name)
            g.add_hosts_to_group(g_name,"host1,host2,host3")
            g.add_hosts_to_group(g_name,"host5;host7;host8")


from func.overlord.groups import Group
from certmaster.config import read_config, CONFIG_FILE
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
            tmp_f = open("%s/%s.%s" % (self.cm_config.certroot,str(m), self.cm_config.cert_extension,"w"))
            tmp_f.close()
            final_list.append(str(m))
        print "%d dummy minions created "%howmany
        return final_list

    def clean_dummy_minions(self,howmany):
        """
        Deletes a lots of minions garbage
        """

        cm_config = read_config(CONFIG_FILE, CMConfig)
        howmany = howmany or 10000 #it is a good default number

        for m in xrange(howmany):
            tmp_f = "%s/%s.%s" % (self.cm_config.certroot,str(m), self.cm_config.cert_extension)
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
            gr_list.append(Group(**b))

        return gr_list
    
    def clean_test_files(self,path):
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
        self.clean_test_files(TEST_DB_FILE)
        self.clean_test_files(TEST_CONF_FILE)
        
        #destroy and create minions
        self.clean_dummy_minions()
        self.current_minions = self.create_dummy_minions()
        #get groups
        self.groups = self.get_group_objects()
    
    
    def test_add_group(self):
        """
        adds a single group item
        """
        for g in groups:
            assert g.add_group("group1")[0] == True

        for g in groups:
            assert g.add_group("group1")[0] == False



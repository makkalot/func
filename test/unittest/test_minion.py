#That file will include a set of some test to see
#if we can improve the lookup process of minions

NUMBER_OF_TEST_MINIONS = 10000
PICKLE_PLACE = "/tmp/minion.pkl"

   
import pickle
import fnmatch
from func.overlord.client import Minions
from certmaster.config import read_config, CONFIG_FILE
from certmaster.commonconfig import CMConfig
import os

class BaseMinions(object):
    
    def create_dummy_minions(self,howmany=NUMBER_OF_TEST_MINIONS):
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

    def clean_dummy_minions(self,howmany=NUMBER_OF_TEST_MINIONS):
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


class FromPickle(Minions):
    """
    That one will store all of the stuff in a
    pickle and will just load it to main memory
    and get what it needs ...
    """
    def _get_hosts_for_spec(self,each_gloob):
        """
        Pull only for specified spec
        """
        #these will be returned
        tmp_certs = set()
        
        all_minions = self.load_minions()
        hosts = fnmatch.filter(all_minions.keys(),each_gloob)
        
        for h in hosts:
            tmp_certs.add(all_minions[h])
        
        print "ALL DONE"
        return set(hosts),tmp_certs
    
    def prepare_pickle(self):
        final_dict = {}
        for i in xrange(NUMBER_OF_TEST_MINIONS):
            final_dict[str(i)] = "%s/%s.%s" % (self.cm_config.certroot,str(i), self.cm_config.cert_extension)

        p_file = open(PICKLE_PLACE,"wb")
        pickle.dump(final_dict,p_file,-1)
        p_file.close()

    def load_minions(self):
        p_file = open(PICKLE_PLACE,"rb")
        res = pickle.load(p_file)
        p_file.close()
        return res

class FromFile(Minions):
    """
    That one will store all of the stuff in a
    pickle and will just load it to main memory
    and get what it needs ...
    """
    def _get_hosts_for_spec(self,each_gloob):
        """
        Pull only for specified spec
        """
        #these will be returned
        tmp_certs = set()
        
        hosts = self.load_minions()
        hosts = fnmatch.filter(hosts,each_gloob)
        
        for h in hosts:
            tmp_certs.add("%s/%s.%s" % (self.cm_config.certroot,h, self.cm_config.cert_extension))
        
        return set(hosts),tmp_certs
    
    def prepare_pickle(self):
        p_file = open(PICKLE_PLACE,"w")
        final_list = []
        for i in xrange(NUMBER_OF_TEST_MINIONS):
            p_file.write("%s\n"%str(i))
        p_file.close()

    def load_minions(self):
        p_file = open(PICKLE_PLACE,"r")
        res = p_file.read().split("\n")
        p_file.close()
        return res

import dbm
import shelve

class FromDb(Minions):
    """
    That one will store all of the stuff in a
    pickle and will just load it to main memory
    and get what it needs ...
    """
    def _get_hosts_for_spec(self,each_gloob):
        """
        Pull only for specified spec
        """
        #these will be returned
        tmp_certs = set()
        all_minions = self.load_minions()
        hosts = fnmatch.filter(all_minions.keys(),each_gloob)
        
        for h in hosts:
            tmp_certs.add(all_minions[h])
        
        return set(hosts),tmp_certs
    

    def prepare_pickle(self):
        p_file = open(PICKLE_PLACE,"w")
        internal_db = dbm.open(PICKLE_PLACE, 'c', 0644 )
        storage = shelve.Shelf(internal_db)

        for i in xrange(NUMBER_OF_TEST_MINIONS):
            storage[str(i)] = "%s/%s.%s" % (self.cm_config.certroot,str(i), self.cm_config.cert_extension)
        
        storage.close()

    def load_minions(self):
        p_file = open(PICKLE_PLACE,"w")
        internal_db = dbm.open(PICKLE_PLACE, 'c', 0644 )
        storage = shelve.Shelf(internal_db)
        return storage

def get_glob_list():
    final_list = []
    final_list.extend([str(i) for i in xrange(NUMBER_OF_TEST_MINIONS)])
    final_list.append("[1-5][0-9][0-9]")
    final_list.append("[1-5][0-9][0-9][0-9]")
    final_list.append("[5-9][0-9][0-9]")
    final_list.append("[1,3,5,8,9][0-9][0-9][0-9]")
    final_list.append("[2,4,6,8][0-9][0-9][0-9]")
    
    #tottal 10 000 + 5 :)
    return final_list


if __name__ == "__main__":
    b=BaseMinions()
    b.create_dummy_minions()
    fi = FromDb("*")
    fi.prepare_pickle()
    for glob in get_glob_list():
        
        f=FromDb(glob)
        print f.get_all_hosts()
        #f=FromFile(glob)
        #print f.get_all_hosts()
    

    b.clean_dummy_minions()
    
    #fi = FromPickle("*")
    #fi.prepare_pickle()
    #for glob in get_glob_list():
    #f=FromPickle(glob)
    #    print f.get_all_hosts()
    


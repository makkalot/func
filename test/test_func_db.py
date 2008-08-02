from random import randint
from func.utils import remove_weird_chars,get_formated_jobid
from func import jobthing
import pprint
import time
       
def generate_word(type_word,how_many):
    """
    generating some test fuzzy words
    @type_word : is the type fo word it maybe some
    glob word or maybe some module or method thing
    @how_many : stands for how many words we want to pick from
    ALLOWED things and to combine them
    """

    #what you can choose
    ALLOWED_CHARS = ('*','-','_',';','@','.')
    #may add more later 
    ALLOWED_GLOB_WORDS = ("w-e-i-r-d","foo.com","zoom","@group1","g.r.o.u.p.2","some-hey-com","some_hack.org","1212-32323_blippy-zorg","interesting*;o*n*e")
    ALLOWED_MODULE_METHOD_W = ("some_service","s-o-m-e","s_u_m_m_er","FOOO","FoFo","real_stupid-w-e-i-r-d-naME")
    
    final_word = ""
    pickup = []

    for i in xrange(how_many):
        if type_word == "spec":#pick a glob
            pickup.append(ALLOWED_GLOB_WORDS[randint(0,len(ALLOWED_GLOB_WORDS)-1)])
        else:
            pickup.append(ALLOWED_MODULE_METHOD_W[randint(0,len(ALLOWED_MODULE_METHOD_W)-1)])
    for index,word in enumerate(pickup):
        if index!=len(pickup)-1 and type_word == "spec":
            weird_char = ALLOWED_CHARS[randint(0,len(ALLOWED_CHARS)-1)]
            final_word = "".join([final_word,word,weird_char])
        else:
            final_word = "".join([final_word,word])

    #return the final word back 
    return final_word


def test_remove_weird_chars():
    """
    Test the util method
    """
    how_many_test = 1000
    choices = ["spec","method","module"]
    for t in xrange(how_many_test):
        choice = choices[randint(0,len(choices)-1)]
        gw=generate_word(choice,4)
        result = remove_weird_chars(gw)
        #we dont want any weird chars in it
        assert result.find("-") == -1

def test_get_formated_jobid():
    """
    Test formated job id
    """
    pack = {}
    choices = ["spec","module","method"]
    for choice in choices:
        gw=generate_word(choice,4)
        pack[choice] = gw

    get_formated_jobid(**pack)

class BaseFuncDB(object):
    """
    The base class for Overlord and Minion db test cases
    """
    def __init__(self):
        self.new_jobids = []
        self.old_jobids = []
        self.an_old_time = 217675779.842658

    def setUp(self):
        pass

    def test_purge_old_jobs(self):
        #purge_old_jobs()
        self.enter_some_data(self.new_jobids)
        self.enter_some_data(self.old_jobids)
        #delete the olders
        jobthing.purge_old_jobs()
        db_results = jobthing.get_open_ids()
        #print "The lenght of the db result is : ",len(db_results.keys())
        assert len(db_results.keys()) == len(self.new_jobids)

        for job in self.new_jobids:
            for job_id,job_pack in job.iteritems():
                assert db_results.has_key(job_id) == True
                assert db_results[job_id] == job_pack[0]
        self.enter_some_data(self.old_jobids)
        jobthing.purge_old_jobs()
        assert len(db_results.keys()) == len(self.new_jobids)

    def test_get_open_ids(self):
        #get_open_ids()
        #we dont need any test for that all other methods depends on it
        pass

    def test_update_status(self):
        #__update_status(jobid, status, results, clear=False)
        #test the update operation
        self.enter_some_data(self.new_jobids)
        db_results = jobthing.get_open_ids()
        #some assertions
        for job in self.new_jobids:
            for job_id,job_pack in job.iteritems():
                assert db_results.has_key(job_id) == True
                assert db_results[job_id] == job_pack[0]



    def test_get_status(self):
        #__get_status(jobid)
        self.enter_some_data(self.new_jobids)
        
        for job in self.new_jobids:
            for job_id,job_pack in job.iteritems():
                result = jobthing.__dict__['__get_status'](job_id)
                assert job_pack == result

   
    def enter_some_data(self,data):
        """
        We need that one because every func here uses it at the initial stage
        """
        for job in data:
            for job_id,job_pack in job.iteritems():
                #it is an private so have to access it like that
                #print "The current job is : ",job
                jobthing.__dict__['__update_status'](job_id,job_pack[0],job_pack[1])



    def create_an_old_jobid(self):
        #will be overriden
        pass
    
    def create_new_jobid(self):
        #will be overriden
        pass
 

class TestOverlordDB(BaseFuncDB):
    def __init__(self):
        super(TestOverlordDB,self).__init__()
        self.status_opt = [jobthing.JOB_ID_RUNNING,jobthing.JOB_ID_FINISHED,jobthing.JOB_ID_PARTIAL]
        #JOB_ID_LOST_IN_SPACE = 2
        #JOB_ID_REMOTE_ERROR = 4
        self.test_result = "overlord_result"


    def setUp(self):
        #create 5 new ids and 5 old ones
        #firstly clean the db !
        print "Cleaning the database"
        jobthing.clear_db()
        for new_id in xrange(5):
            tmp_hash = {}
            tmp_hash[self.create_new_jobid()] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_new.com":self.test_result})
            self.new_jobids.append(tmp_hash)

        base_time = self.an_old_time
        for old_id in xrange(5):
            tmp_hash = {}
            tmp_hash[self.create_an_old_jobid(base_time)] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_old.com":self.test_result})
            self.old_jobids.append(tmp_hash)
            base_time = base_time + 10

        #print "The new ids i created are : ",self.new_jobids
        #print "The old ids i created are : ",self.old_jobids

    def create_new_jobid(self):
        """
        Generating an old id
        """
        pack = {}
        choices = ["spec","module","method"]
        for choice in choices:
            #the stres words :)
            gw=generate_word(choice,4)
            pack[choice] = gw
            
        return get_formated_jobid(**pack)

    
    def create_an_old_jobid(self,base_time):
        new_time = self.create_new_jobid().split("-")
        new_time[len(new_time)-1]=str(base_time)
        return "-".join(new_time)

        

    def test_old_new_upgrade(self):
        #that will do some control if some users has old_ids and
        #upgrade to new ones so they shouldnt have some weird errors
        old_type_new = []
        old_type_old = []
        #create 5 old type job ids with current time
        for n in xrange(5):
            job_id = pprint.pformat(time.time())
            tmp_hash = {}
            tmp_hash[job_id] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_old_type_new.com":self.test_result})
            old_type_new.append(tmp_hash)
        
        #create 5 old type job ids with older  time
        base_time = self.an_old_time
        for n in xrange(5):
            job_id = str(base_time)
            tmp_hash = {}
            tmp_hash[job_id] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_old_type.com":self.test_result})
            old_type_old.append(tmp_hash)
            base_time = base_time + 10
        
        #print "The old type pack is : ",old_type_new
        #print "The old type pack is : ",old_type_old
        #enter also that ids into database
        self.enter_some_data(old_type_new)
        self.enter_some_data(old_type_old)
        #db_results = jobthing.get_open_ids()
        #print "The current db results are : ",db_results

        self.enter_some_data(self.new_jobids)
        self.enter_some_data(self.old_jobids)
        
        #db_results = jobthing.get_open_ids()
        #print "The current db results are : ",db_results

        #now check for errors or failures
        jobthing.purge_old_jobs()
        db_results = jobthing.get_open_ids()
        #print "The current db results are : ",db_results
        assert len(db_results.keys()) == len(self.new_jobids)
        for job in self.new_jobids:
            for job_id,job_pack in job.iteritems():
                assert db_results.has_key(job_id) == True
                assert db_results[job_id] == job_pack[0]
 

    def access_update_stress(self):
        """
        That stress is about entering lots of data to see the time delay
        the tests will be done for overlord side ...
        """
        how_many = 1000
        self.setUp()
        self.create_lots_of_ids(how_many,self.new_jobids,"new")
        self.create_lots_of_ids(how_many,self.old_jobids,"old")
        self.enter_some_data(self.new_jobids)
        print "Entering data test is over"

    def access_delete_stress(self):
        
        if not self.new_jobids or not self.old_jobids:
            self.create_lots_of_ids(how_many,self.new_jobids,"old")
            self.create_lots_of_ids(how_many,self.old_jobids,"new")
            self.enter_some_data(self.new_jobids)
        jobthing.purge_old_jobs()
        print "Old ids were removed succesfully "

    def create_lots_of_ids(self,how_many,to_object,type_id):
        #generates lots of weird named 
        import time
        base_time = self.an_old_time
        for new_id in xrange(how_many):
            time.sleep(0.1)
            tmp_hash = {}
            if type_id == "new":
                tmp_hash[self.create_new_jobid()] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_new.com":self.test_result})
            else:
                tmp_hash[self.create_an_old_jobid(base_time)] = (self.status_opt[randint(0,len(self.status_opt)-1)],{"some_old.com":self.test_result})
                base_time = base_time + 10

            if new_id%100==0:
                print "The %s of the generation completed "%new_id

            to_object.append(tmp_hash)
        print "Generated the requested ids"




class TestMinionDB(BaseFuncDB):
    
    def __init__(self):
        super(TestMinionDB,self).__init__()
        self.status_opt = [jobthing.JOB_ID_RUNNING,jobthing.JOB_ID_FINISHED,jobthing.JOB_ID_PARTIAL,jobthing.JOB_ID_LOST_IN_SPACE,jobthing.JOB_ID_REMOTE_ERROR]
        self.test_result = "minion_result"

    def setUp(self):
        jobthing.clear_db()
        for new_id in xrange(5):
            tmp_hash = {}
            tmp_hash[self.create_new_jobid()] = (self.status_opt[randint(0,len(self.status_opt)-1)],self.test_result)
            self.new_jobids.append(tmp_hash)

        base_time = self.an_old_time
        for old_id in xrange(5):
            tmp_hash = {}
            tmp_hash[self.create_an_old_jobid(base_time)] = (self.status_opt[randint(0,len(self.status_opt)-1)],self.test_result)
            self.old_jobids.append(tmp_hash)
            base_time = base_time + 10


    def create_new_jobid(self):
        job_id = "%s-minion" % pprint.pformat(time.time())
        return job_id

    def create_an_old_jobid(self,base_time):
        job_id = "%s-minion" % str(base_time)
        return job_id


if __name__ == "__main__":
    #those tests are not run by nosetest only by hand
    #they take longer so if yu dont have time dont run them :)
    t = TestOverlordDB()
    t.access_update_stress()
    t.access_delete_stress()

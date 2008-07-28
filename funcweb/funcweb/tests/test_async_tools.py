from funcweb.async_tools import AsyncResultManager
from func.overlord.client import Overlord
from func.jobthing import *
import unittest

class AsyncResultManagerTest(object):

    def setUp(self):
        self.fc = Overlord("*")
        self.async_manager = AsyncResultManager()

    def get_current_list_test(self):
        #that is tested in test_current_db
        pass

    def update_current_list_test(self):
        pass
        

    def check_for_changes_test(self):
        print "***** Testing check_for_changes *****" 
        self.reset_stuff()
        #now make a new entry into database to have a only one 
        #new entry in the db ...
        #running a new command which is a short one
        new_fc = Overlord("*",async=True)
        new_job_id=new_fc.test.add(1,2)
        #print "The job id we got is :",new_job_id
        changes = self.async_manager.check_for_changes()
        print "The latest Changes for add method are :",changes
        assert len(changes) == 1
        assert changes[0] == new_job_id
        
        #check if that one is finished
        another_test = False
        while new_fc.job_status(new_job_id)[0] != JOB_ID_FINISHED:
            print "Waiting for add command to finish "
            time.sleep(2)
            another_test = True
            
        # that probably may happen so should add it here
        if another_test:
            changes = self.async_manager.check_for_changes()
            assert len(changes) == 1
            assert changes[0] == new_job_id
            print "The changes are for add finish :",changes
        
        #now should run another command that is longer to see what happens
        new_job_id = new_fc.test.sleep(4)
        # we have now one entry in the db what to do ?
        # when now run the check changes should have ne entry in the changes :)
        changes = self.async_manager.check_for_changes()
        print "The changes for sleep are :",changes
        assert len(changes) == 1
        assert changes[0] == new_job_id
        
        #if we already have the finished message we dont have to run the other test after that one
        another_test = False
        while new_fc.job_status(new_job_id)[0] != JOB_ID_FINISHED:
            print "Waiting for sleep command to finish "
            time.sleep(2)
            another_test = True
        
        if another_test:
            changes = self.async_manager.check_for_changes()
            assert len(changes) == 1
            assert changes[0] == new_job_id
            print "The changes for sleep finish are :",changes
        
        
    def select_from_test(self):
        print "****Testing select_from**** "
        #these tests are a little bit tricky so may not have 
        #the exact results all depends on remote machines :)
        self.reset_stuff()
        new_fc = Overlord("*",async=True)
        #new_job_id=new_fc.test.add(1,2)
        new_job_id = new_fc.test.sleep(6)
        
        #insert one running
        #now we have one entry into async_manager 
        result_ids = new_fc.open_job_ids()
        self.async_manager.refresh_list() 
        if result_ids.has_key(new_job_id) and result_ids[new_job_id] == JOB_ID_RUNNING:
            print "Testing for SELECT RUNNING ..."
            select_list = self.async_manager.select_from('RUNNING')
            #print "Result form selct RUNNING :",select_list
            assert len(select_list) == 1
            assert select_list[0].has_key(new_job_id)
            assert select_list[0][new_job_id][0] == JOB_ID_RUNNING
        
        #pull_property_options = ('FINISHED','ERROR','NEW','CHANGED','RUNNING','PARTIAL')
        #insert one that finishes
        #get one NEW
        print "Testing for SELECT NEW ..."
        select_list = self.async_manager.select_from('NEW')
        #print "The select list is :",select_list
        assert len(select_list) == 1
        assert select_list[0].has_key(new_job_id)
        assert select_list[0][new_job_id][1] == self.async_manager.JOB_CODE_NEW
        
        #test the ones that are changed :)
        another_test = False
        current_job_status = new_fc.job_status(new_job_id)[0] 
        while current_job_status != JOB_ID_FINISHED:
            print "Waiting for sleep command to finish "
            time.sleep(1)
            another_test = True
            
            #test also for partial resultst status
            if current_job_status == JOB_ID_PARTIAL:
                #populate the list
                print "Testing for SELECT PARTIAL ..."
                self.async_manager.refresh_list()
                select_list = self.async_manager.select_from('PARTIAL')
                assert select_list[0].has_key(new_job_id)
                assert select_list[0][new_job_id][0] == JOB_ID_PARTIAL
                
            current_job_status = new_fc.job_status(new_job_id)[0] 
                
        
        if another_test:
        
            print "Testing for SELECT CHANGED ..."
            self.async_manager.refresh_list()
            select_list = self.async_manager.select_from('CHANGED')
            #print "current Select list is :",select_list
            assert len(select_list) == 1
            assert select_list[0].has_key(new_job_id)
            assert select_list[0][new_job_id][1] == self.async_manager.JOB_CODE_CHANGED
       
            print "Testing for SELECT FINISHED ..."
            assert select_list[0][new_job_id][0] == JOB_ID_FINISHED

        #didnt test for ERROR and others they are not present in overlord :)

        #insert one raises error
        #insert one another

    def job_id_result_test(self):
        pass

    def current_db_test(self):
        #that test also test the test_get_current_list with no changes option

        result_ids = self.fc.open_job_ids()
        manual_list = {}
        for job_id,code in result_ids.iteritems():
            manual_list[job_id]=[code,self.async_manager.JOB_CODE_NEW]

        real_result =self.async_manager.current_db()
        #print real_result
        assert manual_list ==real_result 
    
    def reset_stuff(self):
        #first reset the database to see what is there
        self.remove_db()
        #all of them are new now
        self.async_manager.reset_current_list()
       

    def remove_db(self):
        import os
        root_dir = "/var/lib/func"
        db_file_list = os.listdir(root_dir)
        for f in db_file_list:
            if not f.startswith("."):
                os.remove("".join([root_dir,"/",f]))

        print "The database is removed"
# we do it that way because when run it from nosetest we hae failings 
tester = AsyncResultManagerTest()
tester.setUp()
#tester.current_db_test()
tester.check_for_changes_test()
tester.select_from_test()

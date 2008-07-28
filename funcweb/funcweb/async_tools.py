from func.overlord.client import Overlord
from func.jobthing import JOB_ID_RUNNING,JOB_ID_FINISHED,JOB_ID_LOST_IN_SPACE,JOB_ID_PARTIAL,JOB_ID_REMOTE_ERROR

class AsyncResultManager(object):
    """
    A class to check the async result updates,changes to
    be able to display on UI
    """

    JOB_CODE_CHANGED = 1
    JOB_CODE_NEW = 2
    JOB_CODE_SAME = 3

    pull_property_options = ('FINISHED','ERROR','NEW','CHANGED','RUNNING','PARTIAL')

    def __init__(self):
        #we keep all the entries in memory it may seems
        #that it will occuppy lots of space but all it has 
        #is job_id:code pairs with some status info : changed,new
        #and etc all other stuff is kept in DB
        #so if someone does 1000 async queries will occupy
        #1000 * (integer*2) not big deal :)
        #the format will be job_id : [code,status]
        self.__current_list = {}

        #create a dummy Overlord object
        self.fc = Overlord("*")

    def __get_current_list(self,check_for_change=False):
        """
        Method returns back the current 
        list of the job_ids : result_code pairs
        """
        changed = []
        tmp_ids = self.fc.open_job_ids()
        for job_id,code in tmp_ids.iteritems():
            #is it a new code ?
            if self.__current_list.has_key(job_id):
                #the code is same no change occured
                if self.__current_list[job_id][0] == code:
                    #print "I have that code %s no change will be reported"%job_id
                    self.__current_list[job_id][1] = self.JOB_CODE_SAME
                else:
                    #we have change i db 
                    #print "That is a change from %d to %d for %s"%(self.__current_list[job_id][0],code,job_id)
                    self.__current_list[job_id]=[code,self.JOB_CODE_CHANGED]
                    if check_for_change:
                        changed.append(job_id)
            else:
                # a new code was added
                #print "A new code was added %s"%job_id
                self.__current_list[job_id] = [code,self.JOB_CODE_NEW]
                if check_for_change:
                    changed.append(job_id)

        #if true the db was updated and ours is outofdate
        if len(self.__current_list.keys()) != len(tmp_ids.keys()):
            self.__update_current_list(tmp_ids.keys())

        #if we want to know if sth has changed
        if check_for_change and changed:
            return changed

        return None

            
    def __update_current_list(self,tmp_db_hash):
        """
        Synch the memory and local db
        """
        for mem_job_id in self.__current_list.keys():
            if mem_job_id not in tmp_db_hash:
                del self.__current_list[mem_job_id]


    def check_for_changes(self):
        """
        Method will be called by js on client side to check if something
        interesting happened in db in "before defined" time interval 
        If have lots of methods running async that may take a while to finish
        but user will not be interrupted about that situation ...
        """
        tmp_ids = self.fc.open_job_ids()
        should_check_change = False
        for job_id,code in tmp_ids.iteritems():
            #check only the partials and others
            if code == JOB_ID_RUNNING or code == JOB_ID_PARTIAL:
                #that operation updates the db at the same time
                try :
                    #print "The status from %s is %s in check_for_changes"%(job_id,self.fc.job_status(job_id)[0])
                    tmp_code = self.fc.job_status(job_id)[0]
                    #should_check_change = True
                except Exception,e:
                    print "Some exception in pulling the job_id_status",e
                    continue
            #else:
            #    print "The job_id is not checked remotely :%s in check_for_changes and the code is %s"%(job_id,code)

        #if you thing there is sth to check interesting send it
        #if should_check_change:
        return self.__get_current_list(check_for_change=True)

            
    
    def select_from(self,pull_property):
        """
        Gets only ones that matches to pull_property_options
        """
        #may have some concurency problems ??? 
        code = None
        status = None
        #get the list of the finished jobs
        if pull_property == self.pull_property_options[0]:
            code = JOB_ID_FINISHED
        #get the jobs that caused error
        elif pull_property == self.pull_property_options[1]:
            code = JOB_ID_REMOTE_ERROR
        #get the jobs which are new
        elif pull_property == self.pull_property_options[2]:
            status = self.JOB_CODE_NEW
        #the changed ones
        elif pull_property == self.pull_property_options[3]:
            status = self.JOB_CODE_CHANGED
        #the running job ids
        elif pull_property == self.pull_property_options[4]:
            code = JOB_ID_RUNNING
        #the partials
        elif pull_property == self.pull_property_options[5]:
            code = JOB_ID_PARTIAL
        else:
            #there is no case like that :)
            return None
        #now pull the list and return it back 
        final_list = []
        #print "The current list in the selct is :",self.__current_list
        for job_id,code_status_pack in self.__current_list.iteritems():
            if code != None and code == code_status_pack[0]:
                tmp_hash = {}
                tmp_hash[job_id]=code_status_pack
            
                #print "To select %s with code %s"%(job_id,code)
                final_list.append(tmp_hash)
            elif status != None  and code_status_pack[1] == status:
                tmp_hash = {}
                tmp_hash[job_id]=code_status_pack
                final_list.append(tmp_hash)
        
        #get the final list here
        return final_list

    def job_id_result(self,job_id):
        """
        A simple wrapper around fc.job_status  to get some to display
        in the Web UI
        """
        try:
            result=self.fc.job_status(job_id)
        except Exception,e:
            print "Some exception in getting job_status"
            return None

        return result

    def current_db(self):
        """
        Just return back the private hash
        """
        if not self.__current_list:
            self.__get_current_list()
        return self.__current_list

    def reset_current_list(self):
        "Reset the list may need it sometimes :)"
        self.__current_list = {}


    def refresh_list(self):
        """
        Simple one to checkout to prepopulate the current memory list
        """
        self.__get_current_list()

  
if __name__ == "__main__":
    pass


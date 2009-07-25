import shelve
import dbm
import fcntl

MY_STORE = "/var/lib/func"
INTERNAL_DB_FILE = "log_matcher"

class IndexDb(object):
    """
    A simple wrapper for index Db,which
    is a kind of pickle ...
    """
    WRITE_MODE = "w"
    READ_MODE = "r"

    def __init__(self,dir=None):
        """
        Load the db when have an instance
        """
        self.__storage = None
        self.__handle = None
        self.__dir = dir

    def __load_index(self):
        """
        Gets the store object for that instance
        """
        import os
        if not self.__dir or not os.path.exists(self.__dir):
            filename=os.path.join(MY_STORE,INTERNAL_DB_FILE)
        else:
            filename=os.path.join(self.__dir,INTERNAL_DB_FILE)
        try:
            self.__handle = open(filename,self.__mode)
        except IOError, e:
            print 'Cannot create status file. Ensure you have permission to write'
            return False

        fcntl.flock(self.__handle.fileno(), fcntl.LOCK_EX)
        internal_db = dbm.open(filename, 'c', 0644 )
        self.__storage = shelve.Shelf(internal_db)
        return True

    def write_to_index(self,write_dict):
        """
        Writes the dictonary into the index
        """
        self.__mode = self.WRITE_MODE
        if not self.__storage:
            self.__load_index()
        try:
            for key,value in write_dict.iteritems():
                self.__storage[key]=value
        except Exception,e:
            print e
            self.__storage = None
            return False

        self.__close_storage()
        return True

    def read_from_index(self):
        """
        Returns back a copy dict of the db
        """
        self.__mode = self.READ_MODE
        if not self.__storage:
            self.__load_index()

        try:
            tmp=dict(self.__storage)
        except Exception,e:
            print e
            self.__storage = None
            return None
        
        self.__close_storage()
        return tmp
        

    def delete_from_index(self,delete_list):
        """
        Deletes a list of items from current store object
        """
        self.__mode = self.WRITE_MODE
        if not self.__storage:
            self.__load_index()
            
        try:
            for to_delete in delete_list:
                if self.__storage.has_key(to_delete):
                    del self.__storage[to_delete]
        except Exception,e:
            print e
            self.__storage = None
            return False
        
        self.__close_storage()
        return True

    def __close_storage(self):
        """
        Close all the stuff
        """
        if not self.__storage:
            return False

        self.__storage.close()
        fcntl.flock(self.__handle.fileno(), fcntl.LOCK_UN)
        self.__storage = None
        return True

#we need some util methods
def get_index_data(dir=None):
    """
    A simple getter method for above structure
    """
    db = IndexDb(dir)
    result = db.read_from_index()
    return result

def write_index_data(data,dir=None):
    """
    A simple setter method for above structure
    """
    db = IndexDb(dir)
    result = db.write_to_index(data) 
    return result

def delete_index_data(data,dir=None):
    """
    A simple deletter method for above structure
    """
    db = IndexDb(dir)
    result = db.delete_from_index(data)
    return result

def key_exists(key,dir=None):
    """
    Checks for a key if is there 
    """
    dict = get_index_data(dir)
    return dict.has_key(key)

if __name__ == "__main__":
    pass


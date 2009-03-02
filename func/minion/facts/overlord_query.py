#That module is going to contain the parts that
#hide (proxies) the Overlord and Minion work

from func.overlord.client import Overlord,CommandAutomagic
from func.minion.facts.query import FuncLogicQuery

class OverlordQueryProxy(object):
    """
    That class will encapsulate the Overlord
    class and do the stuff invisibly to the
    user
    """
    def __init__(self,overlord_obj=None,fact_query=None,*args,**kwargs):
        """
        You can pass progrmatically a overlord object or
        you can construct one as you do normally ...
        """
        #some initialization stuff here ...
        if overlord_obj:
            self.overlord = overlord_obj
        elif kwargs:
            self.overlord = Overlord(*args,**kwargs)
        
        self.fact_query = fact_query or FuncLogicQuery()
        
        #print "These are : ",self.overlord
        #print "These are : ",self.fact_query

    def serialize_query(self):
        """
        That part hides the complexity of internal data
        in self.fact_query and passes it over the silent
        network wire :)
        """
        return [self.fact_query.connector,self.__recurse_traverser(self.fact_query.q)]

    def __recurse_traverser(self,q_object):
        """
        Recuresvily traverse the Q object and return
        back a list like structure which is ready tobe
        sent ...
        """
        results=[] 
        for n in q_object.children:
            if not type(n) == tuple and not type(n) == list:
                results.append([n.connector,self.__recurse_traverser(n)])
            else:
                #here you will do some work
                results.extend(n)

        return results
    
    def __getattribute__(self,name):
        """
        Making it kind of proxy object to the Q object
        """
        try:
            #print "What we get lol ",name
            return object.__getattribute__(self, name)
        except AttributeError:
            #it doesnt have that method so we
            #should send method to another place
            if not self.fact_query:
                try:
                    return object.__getattribute__(self.overlord,name)
                except AttributeError:
                    return self.overlord.__getattr__(name)
            else:
                #create the serialized thing to be sent with all of
                #them as a first argument so other side gateway can
                #take and process it before real method is theree
                return CommandAutomagic(self, [name], self.overlord.nforks)
    
    def filter(self,*args,**kwargs):
        """
        Filter The facts and doesnt call
        the minion directly just gives back a 
        reference to the same object
        """
        self.fact_query=self.fact_query.filter(*args,**kwargs)
        #give back the reference
        return self

    def exclude(self):
        """
        Exclude the things from set
        and give back a reference 
        """
        self.fact_query=self.fact_query.exclude(*args,**kwargs)
        #give back the reference
        return self

    def set_complexq(self,q_object,connector=None):
        self.fact_query=self.fact_query.set_compexq(q_object,connector)
        #give back the reference
        return self
    


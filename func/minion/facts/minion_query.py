from func.minion.facts.query import FuncLogicQuery
from func.minion.facts.query_utils import Q

class FactsMinion(object):
    """
    That class wil be responsible for
    de-seriaqlization of the query by converting
    it to a Q structure and calling the facts modules
    """
    VALID_QUERY_KEYS = ["AND","OR","NOT"]

    def __init__(self,fact_query=None):
        self.fact_query = fact_query or FuncLogicQuery()

    def deserialize(self,q_list):
        """
        Method gets the lists that is sent from overlord
        and converts into a FuncLogicQuery so facts can be
        pulled ...
        """
        return self.__traverse_deserialize(q_list)

    def __traverse_deserialize(self,traverse_object):
        """
        the private part of the action ...
        """
        q_object = None
        #lets try divide and conquer :)
        #assume that it is [NOT,[AND,[a,TRUE,b,FALSE]]]
        
        #print "The traverse object at start is ",traverse_object
        tmp_negated = False
        tmp_connector ="AND"
        if type(traverse_object[0]) == str and  traverse_object[0] == "NOT":
            tmp_negated = True
            #q_object.negated = ~q_object
            traverse_object = traverse_object[1:][0]
            #print "After NOT the traverse_object is ",traverse_object
            #raw_input()
        if type(traverse_object[0]) == str and traverse_object[0] in ["AND","OR"]:
            #q_object.connector = traverse_object[0]
            tmp_connector = traverse_object[0]
            traverse_object = traverse_object[1:][0]
            #print "After CONNETOR the traverse_object is ",traverse_object
            #raw_input()

        if type(traverse_object[0])==str and not traverse_object[0] in self.VALID_QUERY_KEYS:
            #print "In children : ",traverse_object
            for ch in xrange(0,len(traverse_object),2):
                #q_object.add(Q(tuple(traverse_object[ch:ch+2])),q_object.connector)
                #print "We work on ",traverse_object[ch:ch+2]
                if not q_object:
                    q_object = Q(tuple(traverse_object[ch:ch+2]))
                    q_object.connector = tmp_connector
                else:
                    if q_object.connector == "OR":
                        q_object = q_object | Q(tuple(traverse_object[ch:ch+2]))
                    else:
                        q_object = q_object & Q(tuple(traverse_object[ch:ch+2]))
            if tmp_negated:
                q_object =  ~q_object
                

                #print "IN children Q object is ",q_object
            traverse_object = []
            #print "After CHILDREN the traverse_object is ",traverse_object
            #raw_input()

        if traverse_object:
            
            #print "The traverse object at end is ",traverse_object
            #raw_input()
            for t_o in traverse_object:
                #print "The traverse object at end is ",t_o
                #raw_input()
                
                tmp_q = self.__traverse_deserialize(t_o)
                #print "I ADD THAT TO THE ALL ",tmp_q
                #print "WILL BE ADDED TO  ",q_object
                if not q_object:
                    q_object = Q()
                    q_object.connector = tmp_connector
                #q_object.add(tmp_q,q_object.connector)
                if tmp_connector== "OR":
                    q_object = q_object | tmp_q
                else:
                    q_object = q_object & tmp_q
                    #print "AFTER ADDITION ",q_object
            if tmp_negated:
                q_object = ~q_object

        return q_object

        

FACTS_MODULES = "func/minion/facts/modules/"
from func.module_loader import load_modules
from func.minion.facts.modules import fact_module
def load_facts_modules():
    """
    loads the facts modules same way we do with
    minion modules ,keeps the refernces globally
    """
    return load_modules(path=FACTS_MODULES,main_class=fact_module.BaseFactModule)

def load_fact_methods():
    """
    Loads the fact methods
    """
    fact_methods = {}
    loaded_modules = load_facts_modules()
    for module_name,module in loaded_modules.iteritems():
        module.register_facts(fact_methods,module_name)

    #get the fact methods 
    return fact_methods


class QueryKeyword(object):
    """
    That class is for resolving 
    incoming keywords and doing comparison stuff

    Ex: query_ob.filter(uname__contains="f9") the contains
    word will be recognized by that class in will return True if it
    contains that word ,easy and fun stuff, If people need to add more
    fun keywords for FuncQuery that is the right place to do that
    """

    def __init__(self):
        pass

    def resolve(self,keyword,overlord_value,fact_value):
        """
        That method is what will be called from outside
        """
        if not hasattr(self,"keyword_%s"%keyword):
            raise NonExistingQueryKeyword("The keyword %s used in query is not a valid one"%keyword)
        return getattr(self,"keyword_%s"%keyword)(self.__convert_input(overlord_value,fact_value),fact_value)

    def __convert_input(self,overlord_value,fact_value):
        """
        If the overlord value that comes from client is
        not the same as facts we should do some convention ..
        """
        if type(overlord_value) != type(fact_value):
            fact_type = type(fact_value)
            return fact_type(overlord_value)
        else:
            return overlord_value

    def keyword_contains(self,overlord_value,fact_value):
        """
        A simple method for contains, which checks if the 
        fact_value contains the overlord_value
        """

        res = fact_value.find(overlord_value)
        if res == -1:
            return False
        else:
            return True
        
    def keyword_icontains(self,overlord_value,fact_value):
        """
        A simple method for contains, which checks if the 
        fact_value contains the overlord_value (case insensitive)
        """
        res = fact_value.lower().find(overlord_value.lower())
        if res == -1:
            return False
        else:
            return True

    def keyword_iexact(self,overlord_value,fact_value):
        """
        Looks for an iexact match
        """
        if overlord_value.lower() == fact_value.lower():
            return True
        else:
            return False

    def keyword_startswith(self,overlord_value,fact_value):
        """
        A typical python start with keyword implementation
        """
        if fact_value.startswith(overlord_value):
            return True
        else:
            return False

    def keyword_gt(self,overlord_value,fact_value):
        """
        A greater keyword
        """
        if overlord_value > fact_value:
            return True
        else:
            return False

    
    def keyword_gte(self,overlord_value,fact_value):
        """
        A greater keyword
        """
        if overlord_value >= fact_value:
            return True
        else:
            return False
    
    def keyword_lt(self,overlord_value,fact_value):
        """
        A less keyword
        """
        if overlord_value < fact_value:
            return True
        else:
            return False
        
    def keyword_lte(self,overlord_value,fact_value):
        """
        A less equal keyword
        """
        if overlord_value <= fact_value:
            return True
        else:
            return False
    
    def keyword_(self,overlord_value,fact_value):
        """
        A == keyword the default behaviour
        """
        if overlord_value == fact_value:
            return True
        else:
            return False



class NonExistingQueryKeyword(Exception):
    pass

class MinionQueryError(Exception):
    pass

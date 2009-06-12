from func.minion.facts.query import FuncLogicQuery
from func.minion.facts.query_utils import Q

class FactsMinion(object):
    """
    That class wil be responsible for:
        1. De-serialization of the query by converting
        it to a Q structure.
        
        2. Calling the ( prewritten ) 'facts' modules
    """
    VALID_QUERY_KEYS = ["AND","OR","NOT"]

    def __init__(self,fact_query=None,method_fact_list=None):
        """
        Constructor 

        @type  fact_query : FuncLogicQuery
        @param fact_query : FuncLogicQuery that will be produced from that class if
                            not given from constructor as it is here.
        @type  method_fact_list : list
        @param method_fact_list : List of prewritten 'facts' modules you can
                                  find them under facts/modules directory

        @return : None
        """
        self.fact_query = fact_query
        self.keyword_query = QueryKeyword()
        self.method_fact_list = method_fact_list

    def deserialize(self,q_list):
        """
        Method gets the lists that is sent from overlord (pure string or list)
        and converts into a FuncLogicQuery so facts can be pulled from prewritten
        modules...

        @type  q_list : list
        @param q_list : Query list 
        """
        q_result = self.__traverse_deserialize(q_list)
        if not self.fact_query:
            self.fact_query = FuncLogicQuery(q_result,self.pull_facts)
        else:
            if self.fact_query.q.connector == "OR":
                self.fact_query = self.fact_query | FuncLogicQuery(q_result,self.pull_facts)
            else:
                self.fact_query = self.fact_query & FuncLogicQuery(q_result,self.pull_facts)

        return q_result

    def exec_query(self,q_list,include_results=False):
        """
        The magic method which gives the final result of that
        query with values in it if requested. That is why we
        have include_results sometimes.

        @type  q_list : list
        @param q_list : Query list
        @type  include_results : boolean
        @param include_results : As it is known the main purpose 
                                 of facts is to return True or False
                                 but sometimes we need the real result
                                 also included.


        """
        self.deserialize(q_list)
        if not include_results:
            return self.fact_query.result
        else:
            return self.fact_query.exec_query_with_facts()

    def pull_facts(self,overlord_tuple):
        """
        Pull facts is kind of callback method which
        is called by FuncLogicQuery when does the logic
        query operation in its recursive traversing ...
        That way we dont put all the pulling operations in
        FuncLogicQuery but making it pluggable by calling from
        outside. That is the place where we actually call the 'fact'
        modules. If you need change in calling fact methods that is
        the place to go .

        @type  overlord_tuple : Tuple 
        @param overlord_tuple : A tuple in format of (factname__factoperation,compared_value)
        """
        keyword_tuple = overlord_tuple[0].split("__")
        overlord_value = overlord_tuple[1]
     
        if len(keyword_tuple) > 1:
            keyword = keyword_tuple[1]
        else:
            keyword = ""
        fact_name = keyword_tuple[0]
        
        if not self.method_fact_list.has_key(fact_name):
            raise MinionQueryError("None existing Fact method or tag required %s "%fact_name)
       
        fact_value = self.method_fact_list[fact_name]()

        #we have the result with fact now it is time to resolve it
        logic_fact = self.keyword_query.resolve(keyword,overlord_value,fact_value)
       
        #the return part is a tuple (logic_Value which is True or False and fact_name and value dictionary )
        return (logic_fact,{fact_name:fact_value})

    def __traverse_deserialize(self,traverse_object):
        """
        The private recursive part that traverses
        the incoming overlord list (included with facts)
        and produces a Q object query object from it.
        **(heavy recursive code)Caution any change here 
        can make facts not tobe deserialized correctly so
        that will break the facts API.

        @type  : list
        @param : List of overlord incoming facts query
                 something like :[NOT,[AND,[a,TRUE,b,FALSE]]]
 
        @return : Q object returned
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

def load_fact_methods(abort_on_conflict = False):
    """
    Loads the fact methods
    """
    fact_methods = {}
    loaded_modules = load_facts_modules()
    for module_name,module in loaded_modules.iteritems():
        res = module.register_facts(fact_methods,module_name,abort_on_conflict)
        # a control if we have some conflict with loading facts
        if res:
            return {'__conflict__':res}

    #get the fact methods 
    return fact_methods


class QueryKeyword(object):
    """
    That class is for resolving incoming keywords and 
    doing comparison stuff (the core part of the facts)

    Ex: query_ob.filter(uname__contains="f9") the contains
    word will be recognized by that class in will return True if it
    contains that word ,easy and fun stuff, If people need to add more
    fun keywords for FuncQuery that is the right place to do that.
    """

    def __init__(self):
        pass

    def resolve(self,keyword,overlord_value,fact_value):
        """
        That method is what will be called from outside
        and will give back the value True,False that is needed.

        @type  keyword : string
        @param keyword : The name of the method that will be called
                         Ex: contains,icontains ...
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if not hasattr(self,"keyword_%s"%keyword):
            raise NonExistingQueryKeyword("The keyword %s used in query is not a valid one"%keyword)
        return getattr(self,"keyword_%s"%keyword)(self.__convert_input(overlord_value,fact_value),fact_value)

    def __convert_input(self,overlord_value,fact_value):
        """
        If the overlord value that comes from client is
        not the same as facts we should do some convention ..
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
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
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
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
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        res = fact_value.lower().find(overlord_value.lower())
        if res == -1:
            return False
        else:
            return True

    def keyword_iexact(self,overlord_value,fact_value):
        """
        Looks for an iexact match
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value.lower() == fact_value.lower():
            return True
        else:
            return False

    def keyword_startswith(self,overlord_value,fact_value):
        """
        A typical python starts with keyword implementation
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if fact_value.startswith(overlord_value):
            return True
        else:
            return False

    def keyword_gt(self,overlord_value,fact_value):
        """
        A greater keyword
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value < fact_value:
            return True
        else:
            return False

    
    def keyword_gte(self,overlord_value,fact_value):
        """
        A greater keyword
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value <= fact_value:
            #print "Comparing %s -- %s "%(overlord_value,fact_value)
            return True
        else:
            return False
    
    def keyword_lt(self,overlord_value,fact_value):
        """
        A less keyword
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value > fact_value:
            return True
        else:
            return False
        
    def keyword_lte(self,overlord_value,fact_value):
        """
        A less equal keyword
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value >= fact_value:
            return True
        else:
            return False
    
    def keyword_(self,overlord_value,fact_value):
        """
        A == keyword the default behaviour
        
        @type  overlord_value : string
        @param overlord_value : Users value that he compares with system
        
        @type  fact_value : string
        @param fact_value : The system fact value
        """
        if overlord_value == fact_value:
            return True
        else:
            return False



class NonExistingQueryKeyword(Exception):
    """
    When user calls a nonexisting fact keyword
    """
    pass

class MinionQueryError(Exception):
    """
    When we have some Minion Query Error :)
    """
    pass

from func.minion.facts.query_utils import Q
from copy import deepcopy

class BaseFuncQuery(object):
    """
    Is an object that u can pass Q objects to make it fetch
    some results about some variables. FuncQuery is kind of 
    orm but not exactly the exec_query returns True of False
    that is what is all about. For example passing variables
    to FuncQuery like temperature=21,uname="2.6.27.15" will 
    control on target machine if temperature is 21 and uname
    is the expected if 2 of them are true the result will be
    true and u will query the rest of the methods u requested
    """
    def __init__(self,q_object=None,pull_result=None):
        self.q = q_object
        #pull result variable is kind of important
        #it can be an object or a method which will
        #return back a True or False statement
        self.pull_result = pull_result

    def __getattribute__(self,name):
        """
        Making it kind of proxy object to the Q object
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError,e:
            return object.__getattribute__(self.q,name)
    
    def _clone(self,klass=None,q_object=None,pull_result=None):
        """
        When querying filter and other cool methods
        we always return back a object ,it is better
        it tobe a fresh one ...
        """
        if klass is None:
            klass = self.__class__
        c = klass(q_object,pull_result)
        return c
    
    def exec_query(self):
        """
        The part that will say it is True or it is False
        """
        raise Exception("Not implemted method you should subclass and override that method")
    
    result = property(exec_query)


    def __or__(self,other):
        if not isinstance(other,BaseFuncQuery):
            raise IncompatibleTypeOperation("You can not or an object which is not type of FuncQuery")
        tmp_q = self.q | other.q
        fresh_query = self._clone(q_object=tmp_q,pull_result=self.pull_result)
        return fresh_query

    def __and__(self,other):
        if not isinstance(other,BaseFuncQuery):
            raise IncompatibleTypeOperation("You can not or an object which is not type of FuncQuery")
        tmp_q = self.q & other.q
        fresh_query = self._clone(q_object=tmp_q,pull_result=self.pull_result)
        return fresh_query
    
    def __nonzero__(self):
        return bool(self.q)
    
    def __main_filter(self,outside_connector,inside_connector,*args,**kwargs):
        
        temp_q = Q(*args,**kwargs)
        if inside_connector == "OR":
            #because the default is AND
            temp_q.connector = inside_connector
        if self.q:
            current_q = deepcopy(self.q)
        else:
            current_q = None
        
        if not current_q:
            current_q = temp_q
        else:
            if outside_connector == "OR":
                current_q = current_q | temp_q
            else:
                current_q = current_q & temp_q

        fresh_query = self._clone(q_object=current_q,pull_result=self.pull_result)
        return fresh_query
    


    def filter(self,*args,**kwargs):
        """
        The filter method is the one that will be used most
        of the time by end user
        """
        return self.__main_filter("AND","AND",*args,**kwargs)
           
    def filter_or(self,*args,**kwargs):
        """
        The filter method is the one that will be used most
        of the time by end user
        """
        return self.__main_filter("OR","OR",*args,**kwargs)
            
    def and_and(self,*args,**kwargs):
        """
        AND inside and connect with AND
        """
        return self.__main_filter("AND","AND",*args,**kwargs)

    def and_or(self,*args,**kwargs):
        """
        AND inside and connect with AND
        """
        return self.__main_filter("AND","OR",*args,**kwargs)

    
    def or_or(self,*args,**kwargs):
        """
        AND inside and connect with AND
        """
        return self.__main_filter("OR","OR",*args,**kwargs)

    def or_and(self,*args,**kwargs):
        """
        AND inside and connect with AND
        """
        return self.__main_filter("OR","AND",*args,**kwargs)



    def exclude(self,*args,**kwargs):
        """
        Useful when you want to ignore some of the things
        in query,the exclude iverts the query
        """
        temp_q = ~Q(*args,**kwargs)
        
        if self.q:
            current_q = deepcopy(self.q)
        else:
            current_q = None
        
        if not self.q:
            current_q = temp_q
        else:
            current_q.add(temp_q,"AND")
        fresh_query = self._clone(q_object=current_q,pull_result=self.pull_result)
        return fresh_query
    
    def set_compexq(self,q_object,connector=None):
        """
        Sometimes we need some complex queries ORed
        ANDed and etc, that is for that
        """
        if not connector or not self.q:
            current_q = deepcopy(q_object)
        else:
            current_q = deepcopy(self.q)
            current_q.add(q_object,connector)
        fresh_query = self._clone(q_object=current_q,pull_result=self.pull_result)
        return fresh_query
    
    def __str__(self):
        return str(self.q)

class FuncLogicQuery(BaseFuncQuery):
    """
    Will be used to decide if a method will be
    invoked on minion side ...
    """
    def exec_query_with_facts(self):
        """
        Sometimes you may need to see facts as
        values ...
        """
        return (self.exec_query(),self.fact_dict)

    def exec_query(self):
        """
        The part that will say it is True or it is False
        """
        self.fact_dict = {}
        if not self.q:
            raise Exception("You should set up some query object before executing it")
        

        return self.__main_traverse(self.q)
    result = property(exec_query)

    def __traverse_query(self,node):
        logic_results=[] 
        for n in node.children:
            if not type(n) == tuple and not type(n) == list:
                result = self.__traverse_query(n)
                logic_results.append(self.logic_operation(n,result))
            else:
                #here you will do some work
                if not self.pull_result:
                    logic_results.append(n[1])
                else:
                    logic_pull = self.pull_result(n) 
                    #append the result if True or False
                    #print "What i append for logic ? ",logic_pull[0]
                    logic_results.append(logic_pull[0])
                    #keep also the fact value user may want to see em
                    for fact_name,fact_value in logic_pull[1].iteritems():
                        self.fact_dict[fact_name] = fact_value
        return logic_results

    def __main_traverse(self,q_ob):
        """
        Collects the final stuff
        """
        tmp_res = self.__traverse_query(q_ob)
        return self.logic_operation(q_ob,tmp_res)
    
    def logic_operation(self,node,logic_list):
        """
        Just computes the logic of current list
        """

        tmp_res = None
        for res in logic_list:
            if tmp_res == None:
                tmp_res = res
            else:
                if node.connector == "AND":
                    tmp_res = tmp_res & res
                else:
                    tmp_res = tmp_res | res
                if node.negated:
                    tmp_res = not tmp_res
        return tmp_res

class FuncDataQuery(BaseFuncQuery):
    """
    A class which is desgined with intention to be used
    for query minion results, and idea which will be cool
    but needs an extreme branch :)
    """
    pass

class IncompatibleTypeOperation(Exception):
    pass

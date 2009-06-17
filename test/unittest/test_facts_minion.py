from func.minion.facts.minion_query import *
from func.minion.facts.overlord_query import OverlordQuery
from func.minion.facts.query_utils import Q
from func.minion.facts.query import FuncLogicQuery 
import func.overlord.client as fc
from copy import copy
import socket

def test_load_facts():
    load_facts_modules()

def test_load_fact_methods():
    load_fact_methods()

def generate_queries(how_many):
    """
    Generate some queries 
    """
    import random

    final_list = []
    char_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    negated = [True,False]
    logic = ["OR","AND"]
    for now in xrange(0,how_many):
        #pull 3 chars 
        ch_dict = {}
        first = char_list[random.randint(0,len(char_list)-1)]
        second = char_list[random.randint(0,len(char_list)-1)]
        third = char_list[random.randint(0,len(char_list)-1)]
        ch_dict[first]=negated[random.randint(0,1)]
        ch_dict[second]=negated[random.randint(0,1)]
        ch_dict[third]=negated[random.randint(0,1)]

        #create a new QUERY here
        #print "The ch_dict is ",ch_dict
        tmp_q = Q(**ch_dict)
        tmp_q.connector = logic[random.randint(0,1)]
        if negated[random.randint(0,1)]:
            tmp_q = ~tmp_q
        
        final_list.append(tmp_q)

    real_final = [final_list[0]]
    for q in final_list[1:]:
        if q.connector == "OR":
            tmp_q = q|real_final[len(real_final)-1]
        else:
            tmp_q = q&real_final[len(real_final)-1]
        
        real_final.append(tmp_q)
    
    return real_final



class TestFactsMinion(object):
    """
    Test the minion side of the query proxy
    """
    # assume we are talking to localhost
    #th = "localhost.localdomain"
    th = socket.getfqdn()    
    #th = socket.getfqdn()
    nforks=1
    async=False


    def __init__(self):
        self.overlord = fc.Overlord(self.th,
                nforks=self.nforks,
                async=self.async)
        
        #load em
        self.fact_methods = load_fact_methods()
        
    def test_deserialize(self):
        """
        Test deserialization
        """
        HOW_MANY = 100
        counter = 0
        for query in generate_queries(HOW_MANY):
            #print query
            counter = counter +1
            self.tmp_proxy = OverlordQuery(fact_query=FuncLogicQuery(query))
            serialized = self.tmp_proxy.serialize_query()
            cp_serialized = copy(serialized)
            
            min_q = FactsMinion()
            de_q = min_q.deserialize(serialized)
            #print "From REAL_Q object",self.query
            self.tmp_proxy = OverlordQuery(fact_query=FuncLogicQuery(de_q))
            serialized_again = self.tmp_proxy.serialize_query()
            
            #print "BEFORE : ",cp_serialized
            #print "AFTER :",serialized_again
            if cp_serialized != serialized_again:
                print "We hve broken the stuff"
                print "BEFORE : ",cp_serialized
                print "AFTER :",serialized_again
            
            assert cp_serialized == serialized_again
            if counter%10 == 0:
                print "%d of %d completed "%(counter,HOW_MANY)

    def test_fact_pull(self):
        #here we assume overlord is sending the data ..
        q_d = {'hardware.run_level__lt':6,'hardware.run_level__gt':2}
        query = Q(**q_d)
        self.tmp_proxy = OverlordQuery(fact_query=FuncLogicQuery(query))
        serialized = self.tmp_proxy.serialize_query()
        
        min_q = FactsMinion(method_fact_list=self.fact_methods)
        final_query = min_q.exec_query(serialized)
        final_query_with_values = min_q.exec_query(serialized,True)

        #print "The result without values ",final_query
        #print "The result with values ",final_query_with_values
    
    #def test_longer_des(self):
    #    """
    #    Uncomment that method for longer tests 
    #    probably u wont need that sterss tessts
    #    """

     #   HOW_MANY = 50

     #   for x in xrange(0,50):
     #       self.test_deserialize()
     #       print "%d of %d completed of BIG TEST "%(x,HOW_MANY)

from func.minion.facts.minion_query import *
class TestQueryKeyword(object):
    """
    Testing the query words here when add a new keyword
    please add here its test ...
    """
    def __init__(self):
        self.fact_keyword = QueryKeyword()

    def __prepare_overlord_word(self,overlord_tuple):
        overlord_keyword = overlord_tuple[0].split("__")
        if len(overlord_keyword) > 1:
            self.keyword = overlord_keyword[1]
        else:
            self.keyword = ""
        self.overlord_value = overlord_tuple[1]



    def test_keyword_contains(self):
        """
        Test if it contains 
        """
        fact_value = "os f9 2.16"
        overlord_tuple = ("os__contains","f9")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__contains","nonexisting")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

    
    def test_keyword_icontains(self):
        """
        Test if it contains 
        """
        fact_value = "os f9 2.16"
        overlord_tuple = ("os__icontains","F9")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__icontains","nonexisting")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

    def test_keyword_iexact(self):
        """
        Test if it contains 
        """
        fact_value = "fedora9"
        overlord_tuple = ("os__iexact","FeDorA9")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__iexact","nonexisting")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

    def test_keyword_startswith(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os__startswith","fed")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__startswith","nonexisting")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

    
    def test_keyword_gt(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os__gt","fedora101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__gt","fedora")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True


        fact_value = 100
        overlord_tuple = ("os__gt",101)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__gt","101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__gt","100")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

        overlord_tuple = ("os__gt",100)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
    
    def test_keyword_gte(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os__gte","fedora10")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        #overlord_tuple = ("os__gte","fedora")
        #self.__prepare_overlord_word(overlord_tuple)
        #assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True


        fact_value = 100
        overlord_tuple = ("os__gte",100)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__gte","101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__gte","100")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True

    def test_keyword_lte(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os__lte","fedora10")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__lte","fedora")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False


        fact_value = 100
        overlord_tuple = ("os__lte",100)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__lte","101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__lte","100")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True

    def test_keyword_lt(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os__lt","fedora10")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__lt","fedora")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False


        fact_value = 100
        overlord_tuple = ("os__lt",100)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
        overlord_tuple = ("os__lt","101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os__lt","33")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False

    def test_keyword(self):
        """
        Test if it contains 
        """
        fact_value = "fedora10"
        overlord_tuple = ("os","fedora10")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os","fedora")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False


        fact_value = 100
        overlord_tuple = ("os",100)
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == True
        
        overlord_tuple = ("os","101")
        self.__prepare_overlord_word(overlord_tuple)
        assert self.fact_keyword.resolve(self.keyword,self.overlord_value,fact_value) == False
        
   

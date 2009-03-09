from func.minion.facts.minion_query import *
from func.minion.facts.overlord_query import OverlordQueryProxy
from func.minion.facts.query_utils import Q
from func.minion.facts.query import FuncLogicQuery 
import func.overlord.client as fc
from copy import copy

def test_load_facts():
    pass
    #print load_facts_modules()

def test_load_fact_methods():
    pass
    #print load_fact_methods()

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
    th = "localhost.localdomain"
    #th = socket.getfqdn()
    nforks=1
    async=False


    def __init__(self):
        self.overlord = fc.Overlord(self.th,
                nforks=self.nforks,
                async=self.async)
        
        
    def test_deserialize(self):
        """
        Test deserialization
        """
        HOW_MANY = 100
        counter = 0
        for query in generate_queries(HOW_MANY):
            #print query
            counter = counter +1
            self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=FuncLogicQuery(query))
            serialized = self.tmp_proxy.serialize_query()
            cp_serialized = copy(serialized)
            
            min_q = FactsMinion()
            de_q = min_q.deserialize(serialized)
            #print "From REAL_Q object",self.query
            self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=FuncLogicQuery(de_q))
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
    
    def test_longer_des(self):
        """
        Uncomment that method for longer tests 
        probably u wont need that sterss tessts
        """

        HOW_MANY = 50

        for x in xrange(0,50):
            self.test_deserialize()
            print "%d of %d completed of BIG TEST "%(x,HOW_MANY)


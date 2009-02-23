from func.minion.facts.query import FuncQuery 
from func.minion.facts.query_utils import Q

class TestFactsTree(object):
   
    def setUp(self):
        self.q1 = FuncQuery(Q(a=True,b=True))
        self.q2 = FuncQuery(Q(a=False,b=True))
        self.q3 = FuncQuery(Q(a=True,b=False))
        self.q4 = FuncQuery(Q(a=False,b=False))


    def test_print_facts_tree(self):
        #print q.children
        #print q
        print self.q1
        print self.q2
        print self.q3
        print self.q4


    def test_traverse_tree(self):
                
        assert self.q1.exec_query() == True
        assert self.q2.exec_query() == False
        assert self.q3.exec_query() == False
        assert self.q4.exec_query() == False


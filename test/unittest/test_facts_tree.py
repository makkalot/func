from func.minion.facts.query import FuncLogicQuery 
from func.minion.facts.query_utils import Q

class TestFactsTree(object):
   
    def setUp(self):
        self.q1 = FuncLogicQuery(Q(a=True,b=True))
        self.q2 = FuncLogicQuery(Q(a=False,b=True))
        self.q3 = FuncLogicQuery(Q(a=True,b=False))
        self.q4 = FuncLogicQuery(Q(a=False,b=False))
        self.q_negated = FuncLogicQuery(~Q(a=False,b=False))

    def test_print_facts_tree(self):
        """
        You will see those only with -s option of
        nosetests
        """
        #print q.children
        #print q
        print self.q1
        print self.q2
        print self.q3
        print self.q4
        print self.q_negated
    


    def test_traverse_logic_tree(self):
                
        assert self.q1.result == True
        assert self.q2.result == False
        assert self.q3.result == False
        assert self.q4.result == False
        assert self.q_negated.result == True
        
        q1_q2_or = self.q3 | self.q1
        q1_q2_and = self.q1 & self.q2
        
        assert q1_q2_or.result == True
        assert q1_q2_and.result == False
        
        tmp = q1_q2_or | q1_q2_and
        tmp2 = q1_q2_or & q1_q2_and

        assert tmp.result == True
        assert tmp2.result == False
        
        #lets do sth more more complex :)
        very_tmp = tmp & tmp
        very_tmp2 = tmp2 | tmp2 & tmp
        assert very_tmp.result == True
        assert very_tmp2.result == False

    def test_filter(self):
        """
        Do some testing on filtering the stuff
        """
        
        tmp_q = self.q1.filter(c=False,e=True)
        assert tmp_q.result == False

        tmp_q = self.q1.filter(c=True,e=True)
        assert tmp_q.result == True


        tmp_q=self.q2.filter(c=False,e=True)
        assert tmp_q.result == False


        tmp_q=self.q3.filter(c=False,e=True)
        assert tmp_q.result == False


        tmp_q=self.q4.filter(c=False,e=True)
        assert tmp_q.result == False

    
    def test_exclude(self):
        """
        Test the negated situations
        """
        tmp_q = self.q1.exclude(c=False,e=True)
        assert tmp_q.result == True
    
    def test_complex(self):
        """
        The complex thing
        """
        
        #what it does is creates a Q on the
        #fly and ORs it with set_compexq

        tmp_q=self.q1.set_compexq(
                (Q(a=True,b=True)|
                Q(c=False,d=True)),
                "OR"
                )
        assert tmp_q.result == True
        
        tmp_q=self.q1.set_compexq(
                (Q(a=True,b=False)|
                Q(c=False,d=False)),
                "AND"
                )
        assert tmp_q.result == False



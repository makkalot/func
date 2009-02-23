from func.minion.facts.query_utils import Q

class FuncQuery(object):
    def __init__(self,q_object=None):
        self.q = q_object

    def exec_query(self):
        if not self.q:
            raise Exception("You should set up some query object before executing it")
        return self.__main_traverse(self.q)

    def __traverse_query(self,node):
        x=[] 
        for n in node.children:
            if not type(n) == tuple and not type(n) == list:
                result = self.traverser(n)
                x.append(self.logic_operation(n,result))
            else:
                #here you will do some work
                x.append(n[1])
        return x

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
        #TODO add negate thing also

        tmp_res = None
        for res in logic_list:
            if tmp_res == None:
                tmp_res = res
            else:
                if node.connector == "AND":
                    tmp_res = tmp_res & res
                else:
                    tmp_re = tmp_res | res
        return tmp_res
    
    def __str__(self):
        return str(self.q)



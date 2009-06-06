#That module is going to contain the parts that
#hide (proxies) the Overlord and Minion work

from func.minion.facts.query import FuncLogicQuery

def display_active_facts(result,with_facts=False):
    """
    When we got all of the resultsfrom minions we may need
    to display only the parts that match the facts query
    """
    
    if type(result) != dict:
        return result
    
    final_display = {}
    for minion_name,minion_result in result.iteritems():
        #CAUTION ugly if statements around :)
        if type(minion_result) == list and type(minion_result[0]) == dict and minion_result[0].has_key('__fact__') :
            if minion_result[0]['__fact__'][0] == True:
                if with_facts:
                    final_display[minion_name] = minion_result
                else:
                    final_display[minion_name] = minion_result[1:][0]
        else:
            return result
    return final_display

class OverlordQuery(object):
    """
    That class will encapsulate the Overlord
    class and do the stuff invisibly to the
    user
    """
    def __init__(self,*args,**kwargs):
        """
        An object just responsible for Keeping
        overlord queries and doing some serialization
        stuff if any ...
        """
        #some initialization stuff here ...
        fact_query = None
        if kwargs.has_key('fact_query'):
            fact_query = kwargs['fact_query']
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
                if n.negated:
                    results.append(["NOT",[n.connector,self.__recurse_traverser(n)]])
                else:
                    results.append([n.connector,self.__recurse_traverser(n)])
            else:
                #here you will do some work
                for ch in xrange(0,len(n),2):
                    results.append(n[ch:ch+2])

        return results
    
    def display_active(self,result,with_facts=False):
        """
        Get active ones only
        """
        return display_active_facts(result,with_facts)




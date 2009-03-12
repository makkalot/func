from func.minion.facts.overlord_query import OverlordQueryProxy
from func.minion.facts.query_utils import Q
from func.minion.facts.query import FuncLogicQuery 
import func.overlord.client as fc
import socket

class TestOverlordQueryProxy(object):
    
    # assume we are talking to localhost
    #th = "localhost.localdomain"
    th = socket.getfqdn()
    nforks=1
    async=False

   
    def __init__(self):

        self.query = FuncLogicQuery(
                Q(a=True,b=True)|
                Q(c=True,b=False)
                )
        
        self.overlord = fc.Overlord(self.th,
                                    nforks=self.nforks,
                                    async=self.async)

        self.async_overlord = fc.Overlord(self.th,
                                    nforks=self.nforks,
                                    async=True)



        self.negated_q = FuncLogicQuery(
                (~Q(a=True,b=True)| Q(c=True,b=False))&
                Q(e=True,f=False)
                )
        
        self.negated_q2 = FuncLogicQuery(
                ~Q(a=True,b=True)| Q(c=True,b=False)
                )


    def test_serialize(self):
        """
        Testing the serialzation thing
        """
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.query)
        self.tmp_proxy.serialize_query()
        
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.negated_q)
        self.tmp_proxy.serialize_query()
    
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.negated_q2)
        self.tmp_proxy.serialize_query()
    


    def test_chain_send(self):
        query = FuncLogicQuery(Q(runlevel__lt=6,runlevel__gt=2)) 
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=query)
        res = self.tmp_proxy.hardware.info()
        self.tmp_proxy.display_active(res)
        self.tmp_proxy.display_active(res,with_facts=True)

    def test_async_chain_send(self):
        query = FuncLogicQuery(Q(runlevel__lt=6,runlevel__gt=2)) 
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.async_overlord,fact_query=query)
        res = self.tmp_proxy.hardware.info()
        print res
        import time
        time.sleep(5)
        self.tmp_proxy.job_status(res)
        self.tmp_proxy.job_status(res,with_facts=True)


class TestFactModule(object):
    # assume we are talking to localhost
    #th = "localhost.localdomain"
    th = socket.getfqdn()
    nforks=1
    async=False

    only_int_keywords = ["","gt","gte","lt","lte"]
    rest_keywords = ['contains','icontains','iexact','startswith']
    
    def __init__(self):
        self.overlord = OverlordQueryProxy(self.th,
                                    nforks=self.nforks,
                                    async=self.async)


        self.fact_methods = self.overlord.fact.list_fact_methods()[self.th]

    def setUp(self):
        """
        Setting up a new fresh instance
        """
        self.overlord_query = OverlordQueryProxy(self.th,
                                    nforks=self.nforks,
                                    async=self.async)
    

    def test_fact_module(self):

        for method in self.fact_methods:
            fact_value = self.overlord.fact.call_fact(method)[self.th]
            #print "The incoming fact value is ",fact_value
            if type(fact_value) == str:
                self.try_str_keywords(method,fact_value,self.only_int_keywords+self.rest_keywords)
            elif type(fact_value) == int:
                self.try_int_keywords(method,fact_value,self.only_int_keywords)
            else:
                raise Exception("Not supported type in that test u should update it before continue")

    def try_str_keywords(self,fact_method,fact_value,iter_value):
        """
        For the str keywords
        """
        for keyword in iter_value:
            #just reset the instance
            self.setUp()
            send_value = "".join([fact_method,"__",keyword])
            if keyword in ["gt","lt"]:
                tmp_fact_value= self.__make_it_less_or_greater(fact_value,keyword)
                #print "The query i'm sending is ",{send_value:tmp_fact_value}
                result = self.overlord_query.filter(**{send_value:tmp_fact_value}).echo.run_string("heyman")
            else:
                #print "The query i'm sending is ",{send_value:fact_value}
                result = self.overlord_query.filter(**{send_value:fact_value}).echo.run_string("heyman")
            #print "The result is ",result

            #do some assertion here ..
            active_res = self.overlord_query.display_active(result)
            self.assert_on_fault(active_res)
            active_res =  self.overlord_query.display_active(result,with_facts=True)
            assert active_res[self.th][0]['__fact__'][0] == True

    
    def __make_it_less_or_greater(self,value,type_cmp):
        if type_cmp == "lt":
            if type(value) == int:
                return value+1
            elif type(value)==str:
                return value + "aaa"
        elif type_cmp == "gt":
            if type(value) == int:
                return value-1
            elif type(value)==str:
                return value[:len(value)-1]
    
    def assert_on_fault(self, result):
        
        import func.utils
        assert func.utils.is_error(result[self.th]) == False

from func.minion.facts.overlord_query import OverlordQueryProxy
from func.minion.facts.query_utils import Q
from func.minion.facts.query import FuncLogicQuery 
import func.overlord.client as fc

class TestOverlordQueryProxy(object):
    
    # assume we are talking to localhost
    th = "localhost.localdomain"
    #th = socket.getfqdn()
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
        #print self.tmp_proxy.serialize_query()
        
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.negated_q)
        #print self.tmp_proxy.serialize_query()
    
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.negated_q2)
        #print self.tmp_proxy.serialize_query()
    


    def test_chain_send(self):
        query = FuncLogicQuery(Q(runlevel__lt=6,runlevel__gt=2)) 
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=query)
        res = self.tmp_proxy.hardware.info()
        print self.tmp_proxy.display_active(res)
        print self.tmp_proxy.display_active(res,with_facts=True)

    def test_async_chain_send(self):
        query = FuncLogicQuery(Q(runlevel__lt=6,runlevel__gt=2)) 
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.async_overlord,fact_query=query)
        res = self.tmp_proxy.hardware.info()
        print res
        import time
        time.sleep(5)
        print "The final stuff is ",self.tmp_proxy.job_status(res)
        print "The final stuff is ",self.tmp_proxy.job_status(res,with_facts=True)




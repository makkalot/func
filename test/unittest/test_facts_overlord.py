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


    def test_serialize(self):
        """
        Testing the serialzation thing
        """
        self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.query)
        print self.tmp_proxy.serialize_query()
    

    #def test_chain_send(self):
    #    self.tmp_proxy = OverlordQueryProxy(overlord_obj=self.overlord,fact_query=self.query)
    #    res = self.tmp_proxy.service.status("httpd")
    #    print res


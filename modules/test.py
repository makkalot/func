#!/usr/bin/python


from codes import *
from modules import web_svc



class Test(web_svc.WebSvc):
    def __init__(self):
        self.methods = {
            "test_add": self.add,
            "test_blippy": self.blippy,
        }
        web_svc.WebSvc.__init__(self)

    def add(self, numb1, numb2):
        return success(int(numb1) + int(numb2))

    def blippy(self, foo):
        fh = open("/tmp/blippy","w+")
        fh.close()
        return success(foo)

methods = Test()
register_rpc = methods.register_rpc

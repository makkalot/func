#!/usr/bin/python


import xmlrpclib

s = xmlrpclib.ServerProxy("http://127.0.0.1:51234")

print s.test_add(1, 2)




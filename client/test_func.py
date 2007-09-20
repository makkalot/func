#!/usr/bin/python


# FIXME: should import the client lib, not XMLRPC lib, when we are done

import xmlrpclib

s = xmlrpclib.ServerProxy("http://127.0.0.1:51234")

print s.test_add(1, 2)
print s.service_restart("httpd")




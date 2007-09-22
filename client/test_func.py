#!/usr/bin/python


# FIXME: should import the client lib, not XMLRPC lib, when we are done

import xmlrpclib

TEST_VIRT = True
TEST_SERVICES = True

# get a connecton (to be replaced by client lib logic)
s = xmlrpclib.ServerProxy("http://127.0.0.1:51234")

# here's the basic test...
print s.test.add(1, 2)

# here's the service module testing
if TEST_SERVICES:
    print s.service.restart("httpd")

# this is so I can remember how the virt module works
if TEST_VIRT:

   # example of using koan to install a virtual machine
   #s.virt_install("mdehaan.rdu.redhat.com","profileX")

   # wait ...
   vms = s.virt.list_vms()
   # example of stopping all stopped virtual machines
   print "list of virtual instances = %s" % vms
   for vm in vms:
       status = s.virt.status(vm)
       print status
       if status == "shutdown":
           s.virt.start(vm)

# add more tests here           


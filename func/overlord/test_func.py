#!/usr/bin/python


# FIXME: should import the client lib, not XMLRPC lib, when we are done

import xmlrpclib
import sys

TEST_GETATTR = True
TEST_PROCESS = False
TEST_VIRT = False
TEST_SERVICES = False
TEST_HARDWARE =  False
TEST_SMART = True

if TEST_GETATTR:
    import func.overlord.client as func_client
    print func_client.Client("*").hardware.pci_info()
    #print func_client.Client("*").test.add(1,2)
    #print func_client.Client("*").hardware.info()
    #print func_client.Client("*").run("hardware","info",[])
    #print func_client.Client(socket.gethostname(),noglobs=True).test.add("1","2")
    sys.exit(1)

# get a connecton (to be replaced by client lib logic)
s = xmlrpclib.ServerProxy("http://127.0.0.1:51234")

# here's the basic test...
print s.test.add(1, 2)

if TEST_SMART:
    print s.smart.info()

if TEST_PROCESS:
    print s.process.info()
    # print s.process.pkill("thunderbird")

# here's the service module testing
if TEST_SERVICES:
    print s.service.restart("httpd")

if TEST_HARDWARE:
    print s.hardware.info()

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

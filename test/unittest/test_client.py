#!/usr/bin/python

import os
import socket
import unittest
import xmlrpclib

import func.overlord.client as fc
import func.utils
import socket



class BaseTest:
    # assume we are talking to localhost
    th = socket.gethostname()
    nforks=1
    async=False

    def __init__(self):
        pass

    def setUp(self):
        self.client = fc.Client(self.th,
                                nforks=self.nforks,
                                async=self.async)

    def test_module_version(self):
        mod = getattr(self.client, self.module)
        result = mod.module_version()
        self.assert_on_fault(result)

    def test_module_api_version(self):
        mod = getattr(self.client, self.module)
        result = mod.module_api_version()        
        self.assert_on_fault(result)

    def test_module_description(self):
        mod = getattr(self.client, self.module)
        result = mod.module_description()
        self.assert_on_fault(result)

    def test_module_list_methods(self):
        mod = getattr(self.client, self.module)
        result = mod.list_methods()
        self.assert_on_fault(result)

    def test_module_inventory(self):
        mod = getattr(self.client, self.module)
        result = mod.list_methods()
        res = result[self.th]

        # not all modules have an inventory, so check for it
        # FIXME: not real happy about having to call list method for
        #        every module, but it works for now -akl
        if "inventory" in res:
            result = mod.inventory()
        self.assert_on_fault(result)


    # we do this all over the place...
    def assert_on_fault(self, result):
        assert func.utils.is_error(result[self.th]) == False
#        assert type(result[self.th]) != xmlrpclib.Fault

    # attrs set so we can skip these via nosetest
    test_module_version.intro = True
    test_module_api_version.intro = True
    test_module_description.intro = True
    test_module_list_methods.into = True
    test_module_module_intentory = True

class TestTest(BaseTest):
    module = "test"
    def test_add(self):
        result = self.client.test.add(1,5)
        self.assert_on_fault(result)
        assert result[self.th] == 6

    def test_add_string(self):
        result = self.client.test.add("foo", "bar")
        self.assert_on_fault(result)
        assert result[self.th] == "foobar"



class TestCommand(BaseTest):
    module = "command"
    def test_echo(self):
        result = self.client.command.run("echo -n foo")

        self.assert_on_fault(result)
        assert result[self.th][1] == "foo"

    def test_rpm(self):
        result = self.client.command.run("rpm -q func")

        self.assert_on_fault(result)
        assert result[self.th][1].split("-")[0] == "func"



class TestCopyfile(BaseTest):
    fn = "/tmp/func_test_file"
    dest_fn = "/tmp/func_test_file_dest"
    content = "this is a func test file"
    module = "copyfile"
    def create_a_file(self):
        f = open(self.fn, "w")
        f.write(self.content)
        f.close()

    def test_copyfile(self):
        self.create_a_file()
        fb = open(self.fn,"r").read()
        data = xmlrpclib.Binary(fb)
        result = self.client.copyfile.copyfile(self.dest_fn, data)
        self.assert_on_fault(result)
        assert result[self.th]  == 0
        
 
    def test_checksum(self):
        self.create_a_file()
        fb = open(self.fn,"r").read()
        data = xmlrpclib.Binary(fb)
        result = self.client.copyfile.copyfile(self.dest_fn, data)
        result = self.client.copyfile.checksum(self.dest_fn)
        self.assert_on_fault(result)
        assert result[self.th] == "b36a8040e44c16605d7784cdf1b3d9ed04ea7f55"
        

class TestHardware(BaseTest):
    module = "hardware"
    def test_inventory(self):
        result = self.client.hardware.inventory()
        self.assert_on_fault(result)

    def test_halinfo(self):
        result = self.client.hardware.hal_info()
        self.assert_on_fault(result)

    def test_info(self):
        result = self.client.hardware.info()
        self.assert_on_fault(result)


    def test_info_no_devices(self):
        result = self.client.hardware.info(False)
        self.assert_on_fault(result)

class TestFileTracker(BaseTest):
    fn = "/etc/hosts"
    module = "filetracker"
    def test_track(self):
        result = self.client.filetracker.track(self.fn)
        assert result[self.th] == 1
        self.assert_on_fault(result)

    def test_inventory(self):
        result = self.client.filetracker.track(self.fn)
        result = self.client.filetracker.inventory(False)
        self.assert_on_fault(result)
        assert result[self.th][0][0] == "/etc/hosts"
        assert result[self.th][0][3] == 0

    def test_untrack(self):
        result = self.client.filetracker.track(self.fn)
        result = self.client.filetracker.untrack(self.fn)
        self.assert_on_fault(result)
        result_inv = self.client.filetracker.inventory(False)
        tracked_files = result_inv[self.th]
        for i in tracked_files:
            if i[0] == self.fn:
                assert "%s was not properly untracked" % self.fn


class TestMount(BaseTest):
    module = "mount"
    def test_mount_list(self):
        result = self.client.mount.list()
        self.assert_on_fault(result)

    # INSERT some clever way to test mount here


class TestNetworkTest(BaseTest):
    module = "networktest"
    def test_ping(self):
        result = self.client.networktest.ping(self.th, "-c", "2")
        self.assert_on_fault(result)

    def test_ping_bad_arg(self):
         result = self.client.networktest.ping(self.th)
         # this should give us a FuncException
         foo = func.utils.is_error(result[self.th]) 
         
    def test_netstat(self):
        result = self.client.networktest.netstat("-n")
        self.assert_on_fault(result)

    def test_traceroute(self):
        result = self.client.networktest.traceroute(self.th)
        self.assert_on_fault(result)

    def test_dig(self):
        result = self.client.networktest.dig("redhat.com")
        self.assert_on_fault(result)

    def test_isportopen_closed_port(self):
        result = self.client.networktest.isportopen(self.th, 34251)
        self.assert_on_fault(result)

    def test_isportopen_open_port(self):
        result = self.client.networktest.isportopen(self.th, 51234)
        self.assert_on_fault(result)


class TestProcess(BaseTest):
    module = "process"
    def test_info(self):
        result = self.client.process.info()
        self.assert_on_fault(result)

    def test_mem(self):
        result = self.client.process.mem()
        self.assert_on_fault(result)

    # FIXME: how to test kill/pkill? start a process with
    #        command and then kill it?


class TestService(BaseTest):
    module = "service"
    def test_inventory(self):
        result = self.client.service.inventory()
        self.assert_on_fault(result)
    
    def test_get_enabled(self):
        result = self.client.service.get_enabled()
        self.assert_on_fault(result)

    def test_get_running(self):
        result = self.client.service.get_running()
        self.assert_on_fault(result)

    def test_get_status(self):
        running_data = self.client.service.get_running()[self.th]
        result = self.client.service.status(running_data[0][0])
        self.assert_on_fault(result)
        assert result[self.th] == 0

        #FIXME: whats a good way to test starting/stoping services without
        #       doing bad things? -akl

class TestRpm(BaseTest):
    module = "rpms"
    def test_inventory(self):
        result = self.client.rpms.inventory()
        self.assert_on_fault(result)


class TestSmart(BaseTest):
    module = "smart"
    def test_info(self):
        result = self.client.smart.info()
        self.assert_on_fault(result)
    

class TestSysctl(BaseTest):
    module = "sysctl"
    def test_list(self):
        result = self.client.sysctl.list()
        self.assert_on_fault(result)

    def test_get(self):
        result = self.client.sysctl.get("kernel.max_lock_depth")
        self.assert_on_fault(result)

class TestYum(BaseTest):
    module = "yumcmd"
    def test_check_update(self):
        result = self.client.yumcmd.check_update()
        self.assert_on_fault(result)

class TestSystem(BaseTest):
    module = "system"
    def test_list_methods(self):
        result = self.client.system.list_methods()
        self.assert_on_fault(result)

    
    def test_listMethods(self):
        result = self.client.system.listMethods()
        self.assert_on_fault(result)
    
    def test_list_modules(self):
        result = self.client.system.list_modules()
        self.assert_on_fault(result)


    #FIXME: we really should just implement these for the system stuff
    #       as well
    def test_module_version(self):
        pass

    def test_module_api_version(self):
        pass

    def test_module_description(self):
        pass



#import time
#class TestAsyncTest(BaseTest):
#    module = "async.test"
#    nforks=1
#    async=True
#    def test_sleep_async(self):
#        job_id = self.client.test.sleep(5)
#        print "job_id", job_id
#        time.sleep(5)
#        (return_code, results) = self.client.job_status(job_id)
#        print "return_code", return_code
#        print "results", results
#
#    def test_add_async(self):
#        job_id = self.client.test.add(1,5)
#        print "job_id", job_id
#        time.sleep(6)
#        (return_code, results) = self.client.job_status(job_id)
#        print "return_code", return_code
       # print "results", results

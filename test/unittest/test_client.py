#!/usr/bin/python

import os
import unittest
import xmlrpclib

import func.overlord.client as fc



class BaseTest:
    th = "grimlock.devel.redhat.com"
    def __init__(self):
        pass

    def setUp(self):
        self.client = fc.Client(self.th)

    def test_module_version(self):
        mod = getattr(self.client, self.module)
        result = mod.module_version()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_module_api_version(self):
        mod = getattr(self.client, self.module)
        result = mod.module_api_version()        
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_module_description(self):
        mod = getattr(self.client, self.module)
        result = mod.module_description()
        assert type(result[self.th]) != xmlrpclib.Fault

class TestTest(BaseTest):
    module = "test"
    def test_add(self):
        result = self.client.test.add(1,5)

        assert result[self.th] == 6

    def test_add_string(self):
        result = self.client.test.add("foo", "bar")

        assert result[self.th] == "foobar"

    def tearDown(self):
        pass


class TestCommand(BaseTest):
    module = "command"
    def test_echo(self):
        result = self.client.command.run("echo -n foo")

        assert result[self.th][1] == "foo"

    def test_rpm(self):
        result = self.client.command.run("rpm -q func")

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
        assert result[self.th]  == 0
 
    def test_checksum(self):
        self.create_a_file()
        fb = open(self.fn,"r").read()
        data = xmlrpclib.Binary(fb)
        result = self.client.copyfile.copyfile(self.dest_fn, data)
        result = self.client.copyfile.checksum(self.dest_fn)
        assert result[self.th] == "b36a8040e44c16605d7784cdf1b3d9ed04ea7f55"
        

class TestHardware(BaseTest):
    module = "hardware"
    def test_inventory(self):
        result = self.client.hardware.inventory()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_halinfo(self):
        result = self.client.hardware.hal_info()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_info(self):
        result = self.client.hardware.info()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_info_no_devices(self):
        result = self.client.hardware.info(False)
        assert type(result[self.th]) != xmlrpclib.Fault

class TestFileTracker(BaseTest):
    fn = "/etc/hosts"
    module = "filetracker"
    def test_track(self):
        result = self.client.filetracker.track(self.fn)
        assert result[self.th] == 1

    def test_inventory(self):
        result = self.client.filetracker.track(self.fn)
        result = self.client.filetracker.inventory(False)
        assert type(result[self.th]) != xmlrpclib.Fault 
        assert result[self.th][0][0] == "/etc/hosts"
        assert result[self.th][0][3] == 0

    def test_untrack(self):
        result = self.client.filetracker.track(self.fn)
        result = self.client.filetracker.untrack(self.fn)
        assert type(result[self.th]) != xmlrpclib.Fault
        result_inv = self.client.filetracker.inventory(False)
        tracked_files = result_inv[self.th]
        for i in tracked_files:
            if i[0] == self.fn:
                assert "%s was not properly untracked" % self.fn


class TestMount(BaseTest):
    module = "mount"
    def test_mount_list(self):
        result = self.client.mount.list()
        #FIXME: I probably should make the test for xmlrpclib faults a bit
        #       more automagic
        assert type(result[self.th]) != xmlrpclib.Fault

    # INSERT some clever way to test mount here


class TestNetworkTest(BaseTest):
    module = "networktest"
    def test_ping(self):
        result = self.client.networktest.ping(self.th, "-c", "2")
        assert type(result[self.th]) != xmlrpclib.Fault
    
    def test_ping_bad_arg(self):
         result = self.client.networktest.ping(self.th)
         # this should give us a FuncException
         assert type(result[self.th]) == xmlrpclib.Fault
         
    def test_netstat(self):
        result = self.client.networktest.netstat("-n")
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_traceroute(self):
        result = self.client.networktest.traceroute(self.th)
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_dig(self):
        result = self.client.networktest.dig("redhat.com")
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_isportopen_closed_port(self):
        result = self.client.networktest.isportopen(self.th, 34251)
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_isportopen_open_port(self):
        result = self.client.networktest.isportopen(self.th, 51234)
        assert type(result[self.th]) != xmlrpclib.Fault


class TestProcess(BaseTest):
    module = "process"
    def test_info(self):
        result = self.client.process.info()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_mem(self):
        result = self.client.process.mem()
        assert type(result[self.th]) != xmlrpclib.Fault

    # FIXME: how to test kill/pkill? start a process with
    #        command and then kill it?


class TestService(BaseTest):
    module = "service"
    def test_inventory(self):
        result = self.client.service.inventory()
        assert type(result[self.th]) != xmlrpclib.Fault
    
    def test_get_enabled(self):
        result = self.client.service.get_enabled()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_get_running(self):
        result = self.client.service.get_running()
        assert type(result[self.th]) != xmlrpclib.Fault

    def test_get_status(self):
        running_data = self.client.service.get_running()[self.th]
        result = self.client.service.status(running_data[0][0])
        assert type(result[self.th]) != xmlrpclib.Fault
        assert result[self.th] == 0

        #FIXME: whats a good way to test starting/stoping services without
        #       doing bad things? -akl

class TestRpm(BaseTest):
    module = "rpms"
    def test_inventory(self):
        result = self.client.rpms.inventory()
        assert type(result[self.th]) != xmlrpclib.Fault


class TestSmart(BaseTest):
    module = "smart"
    def test_info(self):
        result = self.client.smart.info()
        assert type(result[self.th]) != xmlrpclib.Fault
    

class TestYum(BaseTest):
    module = "yumcmd"
    def test_check_update(self):
        result = self.client.yumcmd.check_update()
        assert type(result[self.th]) != xmlrpclib.Fault
        print result

class TestSystem(BaseTest):
    module = "system"
    def test_list_methods(self):
        result = self.client.system.list_methods()
        assert type(result[self.th]) != xmlrpclib.Fault

    
    def test_listMethods(self):
        result = self.client.system.listMethods()
        assert type(result[self.th]) != xmlrpclib.Fault
    
    def test_list_modules(self):
        result = self.client.system.list_modules()
        assert type(result[self.th]) != xmlrpclib.Fault


    #FIXME: we really should just implement these for the system stuff
    #       as well
    def test_module_version(self):
        pass

    def test_module_api_version(self):
        pass

    def test_module_description(self):
        pass


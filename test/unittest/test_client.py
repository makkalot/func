#!/usr/bin/python

##
## Copyright 2008, Various
## Adrian Likins <alikins@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##

import os
import socket
import unittest
import xmlrpclib

import func.overlord.client as fc
import func.utils
import socket



class BaseTest:
    # assume we are talking to localhost
    # th = socket.gethostname()
    th = socket.getfqdn()
    nforks=1
    async=False

    def __init__(self):
        pass

    def setUp(self):
        self.overlord = fc.Overlord(self.th,
                                    nforks=self.nforks,
                                    async=self.async)

    def test_module_version(self):
        mod = getattr(self.overlord, self.module)
        result = mod.module_version()
        self.assert_on_fault(result)

    def test_module_api_version(self):
        mod = getattr(self.overlord, self.module)
        result = mod.module_api_version()        
        self.assert_on_fault(result)

    def test_module_description(self):
        mod = getattr(self.overlord, self.module)
        result = mod.module_description()
        self.assert_on_fault(result)

    def test_module_list_methods(self):
        mod = getattr(self.overlord, self.module)
        result = mod.list_methods()
        self.assert_on_fault(result)

    def test_module_get_method_args(self):
        mod = getattr(self.overlord,self.module)
        arg_result=mod.get_method_args()
        self.assert_on_fault(arg_result)

    def test_module_inventory(self):
        mod = getattr(self.overlord, self.module)
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
    test_module_list_methods.intro = True
    test_module_inventory.intro = True
    test_module_get_method_args.intro = True

class TestTest(BaseTest):
    module = "test"
    def test_add(self):
        result = self.overlord.test.add(1,5)
        self.assert_on_fault(result)
        assert result[self.th] == 6

    def test_add_string(self):
        result = self.overlord.test.add("foo", "bar")
        self.assert_on_fault(result)
        assert result[self.th] == "foobar"

    def test_sleep(self):
        result = self.overlord.test.sleep(1)
        self.assert_on_fault(result)

    def _echo_test(self, data):
        result = self.overlord.test.echo(data)
        self.assert_on_fault(result)
        assert result[self.th] == data
        
    # this tests are basically just to test the basic
    # marshalling/demarshaling bits
    def test_echo_int(self):
        self._echo_test(1)

    def test_echo_string(self):
        self._echo_test("caneatcheese")

    def test_echo_array(self):
        self._echo_test([1, 2, "three", "fore", "V",])

    def test_echo_hash(self):
        self._echo_test({"one":1, "too":2, "III":3, "many":8, "lots":12312})

    def test_echo_bool_false(self):
        self._echo_test(False)

    def test_echo_bool_true(self):
        self._echo_test(True)

    def test_echo_float(self):
        self._echo_test(123.456)

    def test_echo_big_float(self):
        self._echo_test(123121232.23)

    def test_echo_bigger_float(self):
        self._echo_test(234234234234234234234.234234234234234)

    def test_echo_little_float(self):
        self._echo_test(0.000000000000000000000000000000037)

    def test_echo_binary(self):
        blob = "348dshke354ts0d9urgk"
        import xmlrpclib
        data = xmlrpclib.Binary(blob)
        self._echo_test(data)

    def test_echo_date(self):
        import datetime
        dt = datetime.datetime(1974, 1, 5, 11, 59 ,0,0, None)
        import xmlrpclib
        data = xmlrpclib.DateTime(dt)
        self._echo_test(data)

    def test_config(self):
        result = self.overlord.test.configfoo()
        self.assert_on_fault(result)

        



class TestCommand(BaseTest):
    module = "command"
    def test_echo(self):
        result = self.overlord.command.run("echo -n foo")

        self.assert_on_fault(result)
        assert result[self.th][1] == "foo"

    def test_rpm(self):
        # looksing for some package that should be there, rh specific
        # ish at the moment
        result = self.overlord.command.run("rpm -q filesystem")

        self.assert_on_fault(result)
        assert result[self.th][1].split("-")[0] == "filesystem"


    def test_env(self):
	result = self.overlord.command.run("env",
				           {'BLIPPYFOO':'awesome'})
	self.assert_on_fault(result)
	assert result[self.th][1].strip() == "BLIPPYFOO=awesome"

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
        result = self.overlord.copyfile.copyfile(self.dest_fn, data)
        self.assert_on_fault(result)
        assert result[self.th]  == 0
        
 
    def test_checksum(self):
        self.create_a_file()
        fb = open(self.fn,"r").read()
        data = xmlrpclib.Binary(fb)
        result = self.overlord.copyfile.copyfile(self.dest_fn, data)
        result = self.overlord.copyfile.checksum(self.dest_fn)
        self.assert_on_fault(result)
        assert result[self.th] == "b36a8040e44c16605d7784cdf1b3d9ed04ea7f55"
        

class TestHardware(BaseTest):
    module = "hardware"
    def test_inventory(self):
        result = self.overlord.hardware.inventory()
        self.assert_on_fault(result)

    def test_halinfo(self):
        result = self.overlord.hardware.hal_info()
        self.assert_on_fault(result)

    def test_info(self):
        result = self.overlord.hardware.info()
        self.assert_on_fault(result)


    def test_info_no_devices(self):
        result = self.overlord.hardware.info(False)
        self.assert_on_fault(result)

class TestFileTracker(BaseTest):
    fn = "/etc/hosts"
    module = "filetracker"
    def test_track(self):
        result = self.overlord.filetracker.track(self.fn)
        assert result[self.th] == 1
        self.assert_on_fault(result)

    def test_inventory(self):
        result = self.overlord.filetracker.track(self.fn)
        result = self.overlord.filetracker.inventory(False)
        self.assert_on_fault(result)
        assert self.fn in result[self.th][0]
#        assert result[self.th][0][3] == 0

    def test_untrack(self):
        result = self.overlord.filetracker.track(self.fn)
        result = self.overlord.filetracker.untrack(self.fn)
        self.assert_on_fault(result)
        result_inv = self.overlord.filetracker.inventory(False)
        tracked_files = result_inv[self.th]
        for i in tracked_files:
            if i[0] == self.fn:
                assert "%s was not properly untracked" % self.fn


class TestMount(BaseTest):
    module = "mount"
    def test_mount_list(self):
        result = self.overlord.mount.list()
        self.assert_on_fault(result)

    # INSERT some clever way to test mount here


class TestNetworkTest(BaseTest):
    module = "networktest"
    def test_ping(self):
        result = self.overlord.networktest.ping(self.th, "-c", "2")
        self.assert_on_fault(result)

    def test_ping_bad_arg(self):
         result = self.overlord.networktest.ping(self.th)
         # this should give us a FuncException
         foo = func.utils.is_error(result[self.th]) 
         
    def test_netstat(self):
        result = self.overlord.networktest.netstat("-n")
        self.assert_on_fault(result)

    def test_traceroute(self):
        result = self.overlord.networktest.traceroute(self.th)
        self.assert_on_fault(result)

    def test_dig(self):
        result = self.overlord.networktest.dig("redhat.com")
        self.assert_on_fault(result)

    def test_isportopen_closed_port(self):
        result = self.overlord.networktest.isportopen(self.th, 34251)
        self.assert_on_fault(result)

    def test_isportopen_open_port(self):
        result = self.overlord.networktest.isportopen(self.th, 51234)
        self.assert_on_fault(result)


class TestProcess(BaseTest):
    module = "process"
    def test_info(self):
        result = self.overlord.process.info()
        self.assert_on_fault(result)

    def test_mem(self):
        result = self.overlord.process.mem()
        self.assert_on_fault(result)

    # FIXME: how to test kill/pkill? start a process with
    #        command and then kill it?


class TestService(BaseTest):
    module = "service"
    def test_inventory(self):
        result = self.overlord.service.inventory()
        self.assert_on_fault(result)
    
    def test_get_enabled(self):
        result = self.overlord.service.get_enabled()
        self.assert_on_fault(result)

    def test_get_running(self):
        result = self.overlord.service.get_running()
        self.assert_on_fault(result)

    def test_get_status(self):
        running_data = self.overlord.service.get_running()[self.th]
        result = self.overlord.service.status(running_data[0][0])
        self.assert_on_fault(result)

        #FIXME: whats a good way to test starting/stoping services without
        #       doing bad things? -akl

class TestRpm(BaseTest):
    module = "rpms"
    def test_inventory(self):
        result = self.overlord.rpms.inventory()
        self.assert_on_fault(result)

    def test_glob(self):
        # if func is running, there should at least be python installed ;->
        result = self.overlord.rpms.glob("python*", False)
        self.assert_on_fault(result)

    def test_glob_flatten(self):
        result = self.overlord.rpms.glob("python*", True)
        self.assert_on_fault(result)

    def test_glob_nomatch(self):
        # shouldn't be any rpms called "-" ;->
        result = self.overlord.rpms.glob("-*")
        self.assert_on_fault(result)

    def test_glob_gpg_pubkey(self):
        # gpg-pubkey packages are weird rpm virtual packages, and tend to do
        # weird things, so try that too
        result = self.overlord.rpms.glob("gpg-pubkey*")
        self.assert_on_fault(result)

    def test_glob_gpg_pubkey_no_flat(self):
        # gpg-pubkey packages are weird rpm virtual packages, and tend to do
        # weird things, so try that too
        result = self.overlord.rpms.glob("gpg-pubkey*", False)
        self.assert_on_fault(result)

    def test_glob_match_all(self):
        result = self.overlord.rpms.glob("*", False)
        self.assert_on_fault(result)



class TestSmart(BaseTest):
    module = "smart"
    def test_info(self):
        result = self.overlord.smart.info()
        self.assert_on_fault(result)
    

class TestSysctl(BaseTest):
    module = "sysctl"
    def test_list(self):
        result = self.overlord.sysctl.list()
        self.assert_on_fault(result)

    def test_get(self):
        result = self.overlord.sysctl.get("kernel.max_lock_depth")
        self.assert_on_fault(result)

class TestYum(BaseTest):
    module = "yumcmd"
    def test_check_update(self):
        result = self.overlord.yumcmd.check_update()
        self.assert_on_fault(result)

    def test_check_update_empty_filter(self):
        results = self.overlord.yumcmd.check_update([])
        self.assert_on_fault(results)
        results_no_filter = self.overlord.yumcmd.check_update()
        assert results == results_no_filter

    def test_check_update_splat_filter(self):
        results = self.overlord.yumcmd.check_update(['*'])
        self.assert_on_fault(results)
        results_no_filter = self.overlord.yumcmd.check_update()
        assert results == results_no_filter

# this fails on fc6, need to test on newer yum to see whats up
#    def test_update_non_existent_package(self):
#        result = self.overlord.yumcmd.update("thisisapackage-_-that_should==never+exist234234234")
#        self.assert_on_fault(result)
#        # hmm, that method always returns True... not much to test there... -akl

class TestIptables(BaseTest):
    module = "iptables"

    def test_dump(self):
        result = self.overlord.iptables.dump()

        # at the moment, we dont set anything up
        # to verify, so this is just a basic
        # "does it crash" test

    def test_policy(self):
        result = self.overlord.iptables.policy()


class TestIptablesPort(BaseTest):
    module = "iptables.port"

    def test_inventory(self):
        results = self.overlord.iptables.port.inventory()
        # doesnt have an inventory, so er... -akl

        
class TestEchoTest(BaseTest):
    module = "echo"

    def test_run_string(self):
        result=self.overlord.echo.run_string("heyman")
        self.assert_on_fault(result)
        
    def test_run_int(self):
        result=self.overlord.echo.run_int(12)
        self.assert_on_fault(result)
        
    def test_run_float(self):
        result=self.overlord.echo.run_float(12.0)
        self.assert_on_fault(result)
        
    def test_run_options(self):
        result=self.overlord.echo.run_options("hehehh")
        self.assert_on_fault(result)

    def test_run_list(self):
        result=self.overlord.echo.run_list(['one','two','three'])
        self.assert_on_fault(result)

    def test_run_hash(self):
        result=self.overlord.echo.run_hash({'one':1,'two':2})
        self.assert_on_fault(result)

    def test_run_boolean(self):
        result=self.overlord.echo.run_hash(True)
        self.assert_on_fault(result)





class TestSystem(BaseTest):
    module = "system"
    def test_list_methods(self):
        result = self.overlord.system.list_methods()
        self.assert_on_fault(result)

    
    def test_listMethods(self):
        result = self.overlord.system.listMethods()
        self.assert_on_fault(result)
    
    def test_list_modules(self):
        result = self.overlord.system.list_modules()
        self.assert_on_fault(result)


    #FIXME: we really should just implement these for the system stuff
    #       as well
    def test_module_version(self):
        pass

    def test_module_api_version(self):
        pass

    def test_module_description(self):
        pass

    def test_module_get_method_args(self):
        pass


#import time
#class TestAsyncTest(BaseTest):
#    module = "async.test"
#    nforks=1
#    async=True
#    def test_sleep_async(self):
#        job_id = self.overlord.test.sleep(5)
#        print "job_id", job_id
#        time.sleep(5)
#        (return_code, results) = self.overlord.job_status(job_id)
#        print "return_code", return_code
#        print "results", results
#
#    def test_add_async(self):
#        job_id = self.overlord.test.add(1,5)
#        print "job_id", job_id
#        time.sleep(6)
#        (return_code, results) = self.overlord.job_status(job_id)
#        print "return_code", return_code
       # print "results", results

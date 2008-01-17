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

        

class TestTest(BaseTest):
    def test_add(self):
        result = self.client.test.add(1,5)

        assert result[self.th] == 6

    def test_add_string(self):
        result = self.client.test.add("foo", "bar")

        assert result[self.th] == "foobar"

    def tearDown(self):
        pass


class TestCommand(BaseTest):
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
    def test_mount_list(self):
        result = self.client.mount.list()
        #FIXME: I probably should make the test for xmlrpclib faults a bit
        #       more automagic
        assert type(result[self.th]) != xmlrpclib.Fault

    # INSERT some clever way to test mount here

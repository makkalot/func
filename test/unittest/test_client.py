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
    content = "this is a func test file"
    def create_a_file(self):
        f = open(self.fn, "w")
        f.write(self.content)
        f.close()

    def test_copyfile(self):
        "run a test case"
        self.create_a_file()
        fb = open(self.fn,"r").read()
        print fb
        data = xmlrpclib.Binary(fb)
        result = self.client.copyfile.copyfile(self.fn, data)
        assert result[self.th]  == 0
 


#f = TestBar()
#f.test_add()

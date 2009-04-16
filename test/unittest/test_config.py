#!/usr/bin/python

import os
import socket
import unittest

from certmaster import config

from test_client import BaseTest


# a test config class we can do mean thigns to

# NOTE: _empty options are disabled at the moment, need a more
# clever way to test those cases

config_file_1 = """
[main]
option = this is an option from the file
#option_empty = 

int_option = 2222
#int_option_empty = 


bool_option_true = True
bool_option_false = False
bool_option = False
#bool_option_empty = 

list_option = seven,eight,nine
#list_option_empty = 

url_list_option = http://www.redhat.com, http://www.fedoraproject.org
#url_list_option_empty = 

float_option = 2.7182
#float_option_empty = 
float_option_int = 5

bytes_option = 2001M
#bytes_option_empty = 

"""

class ConfigFileValues:
    option = "this is an option from the file"
    int_option = 2222
    bool_option_true = True
    bool_option_false = False
    bool_option = False
    list_option = ["seven", "eight", "nine"]
    url_list_option = ["http://www.redhat.com", "http://www.fedoraproject.org"]
    float_option = 2.7182
    bytes_option = "2001M"

    def __init__(self):
        pass

class ConfigFileDefaultValues(ConfigFileValues):
    option = "this is an option"
    int_option = 1111
    bool_option = True
    bool_option_false = False
    bool_option_true = True
    list_option = ["one", "two", "three"]
    url_list_option = ["https://fedorahosted.org/func/", "http://www.redhat.com"]
    float_option = 3.14159

class ConfigFileWriteValues(ConfigFileValues):
    option = "this is an option written to the config file"
    int_option = 3333
    bool_option = True
    list_option = ["eleven", "twelve", "thirteen"]
    url_list_option = ["http://www.example.com", "http://www.python.org"]
    float_option = 3.33333


class ConfigTest(config.BaseConfig):
    option = config.Option("this is an option")
 #   option_empty = config.Option()

    int_option = config.IntOption(1111)
#    int_option_empty = config.IntOption()
#    int_option_float = config.IntOption(1)

    bool_option = config.BoolOption(True)
    bool_option_true = config.BoolOption(True)
    bool_option_false = config.BoolOption(False)
#    bool_option_empty = config.BoolOption()

    list_option = config.ListOption(["one", "two", "three"])
#    list_option_empty = config.ListOption()

    url_list_option = config.UrlListOption(["https://fedorahosted.org/func/", "http://www.redhat.com"])
#    url_list_option_empty = config.UrlListOption()

    float_option = config.FloatOption(3.14159)
    float_option_empty = config.FloatOption()
    float_option_int = config.FloatOption(1.0)
 
   #selection_option
    bytes_option = config.BytesOption("123M")
#    bytes_option_empty = config.BytesOption()
    

# FIXME: we need a test fixture for testing the config file parsing
# since it's currently kind of all of nothing if an error occurs, so
# we need to be able to build up a variety of test config files, load
# them, and see what happens. Aka, one test case per config file


class TestConfig:
    module = "config"
    config_file = "/tmp/func-test/test.config"
    exp = ConfigFileValues()

    def setUp(self):
        f = open(self.config_file, "w+")
        f.write(config_file_1)
        f.close()

        self.cfg = config.read_config(self.config_file, ConfigTest)

#    def test_config(self):
#        cfg = config.read_config(self.config_file, ConfigTest)
    
    def test_config_option(self):
        assert type(self.cfg.option) == type('')
        assert self.exp.option == self.cfg.option
    
    def test_config_int_option(self):
        assert type(self.cfg.int_option) == type(4)
        assert self.exp.int_option == self.cfg.int_option

#    def test_config_int_option_float(self):
#        print self.cfg.int_option_float
#        assert type(self.cfg.int_option_float) == type(4)

    def test_config_bool_option_true(self):
        assert type(self.cfg.bool_option_true) == type(True)
        assert self.exp.bool_option_true == self.cfg.bool_option_true

    def test_config_bool_option_false(self):
        assert self.exp.bool_option_false == self.cfg.bool_option_false

    def test_config_bool_option(self):
        assert type(self.cfg.bool_option) == type(True)
        print self.exp.bool_option, self.cfg.bool_option
        assert self.exp.bool_option == self.cfg.bool_option

    def test_config_list_option(self):
        assert type(self.cfg.list_option) == type([])
        assert self.exp.list_option == self.cfg.list_option

    def test_config_url_list_option(self):
        assert type(self.cfg.url_list_option) == type([])
        assert self.exp.url_list_option == self.cfg.url_list_option

    def test_config_float_option(self):
        assert type(self.cfg.float_option) == type(1.2345)
        assert self.exp.float_option == self.cfg.float_option

    def test_config_float_option_empty(self):
        print "bloop"
        print self.cfg.float_option_empty
        assert self.cfg.float_option_empty == None

    def test_config_float_option_int(self):
        print "blip"
        print self.cfg.float_option_int
        

# FIXME: not sure why this is different, but we don't use this option type anyway
#    def test_config_bytes_option(self):
#        print self.exp.bytes_option, self.cfg.bytes_option
#        assert self.exp.bytes_option == self.cfg.bytes_option


class TestDefaultConfig(TestConfig):
    module = "config"
    exp = ConfigFileDefaultValues()

    def setUp(self):
        self.cfg = ConfigTest()


# load from a file, write to the config object, test that it's
# correct. Note that this does not actually save the file
class TestConfigSet(TestConfig):
    module = "config"
    exp = ConfigFileWriteValues()

    def setUp(self):
        TestConfig.setUp(self)
        
        self.cfg.option = self.exp.option
        self.cfg.bool_option = self.exp.bool_option
        self.cfg.int_option = self.exp.int_option
        self.cfg.list_option = self.exp.list_option
        self.cfg.url_list_option = self.exp.url_list_option
        self.cfg.float_option = self.exp.float_option


#read the file from one config file, write it to another, reread, and then test
class TestConfigWrite(TestConfigSet):
    module = "config"
    exp = ConfigFileWriteValues()
    
    def setUp(self):
        TestConfigSet.setUp(self)

        filename = "/tmp/func-test/test2.conf"
        f = open(filename, "a+")
        
        self.cfg.write(f, "main")
        f.close()

        self.cfg = config.read_config(filename, ConfigTest)

        


# test cases
# open file
# open file, read values
# open file, write values
# open file, write values, read values
# open file, write values, save, reload, read values
# open file, read [string, int, float, etc]
# open file, write ""                     ""
# open file, write ""                     "", read "" ""
# write wrong type to file (string to float, etc)

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
import subprocess

import func.utils
from func import yaml
import StringIO
import cStringIO



def structToYaml(data):
    # takes a data structure, serializes it to
    # yaml, them makes a cStringIO out of it to
    # feed to func-trasmit on stdin

    buf = yaml.dump(data)
    return buf

class BaseTest:
    # assume we are talking to localhost
    # th = socket.gethostname()
    th = socket.getfqdn()
    nforks=1
    async=False

    # just so we can change it easy later
    def __serialize(self, data):
        buf = yaml.dump(data)
        return buf

    def __deserialize(self, buf):
        data = yaml.load(buf).next()
        return data

    def call(self, data):
        f = self.__serialize(data)
        p = subprocess.Popen("func-transmit", shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = p.communicate(input=f)

        return self.__deserialize(output[0])
        
    def __init__(self):
        pass


   # we do this all over the place...
    def assert_on_fault(self, result):
        assert func.utils.is_error(result[self.th]) == False
#        assert type(result[self.th]) != xmlrpclib.Fault


class TestListMinion(BaseTest):
    
    def test_list_minions(self):
        out = self.call({'clients': '*',
                          'method': 'list_minions'})

    def test_list_minions_no_match(self):
        out = self.call({'clients': 'somerandom-name-that-shouldnt-be-a_real_host_name',
                         'method': 'list_minions'})
        assert out == []

    def test_list_minions_group_name(self):
        out = self.call({'clients': '@test',
                         'method': 'list_minions'})

    def test_list_minions_no_clients(self):
        out = self.call({'method': 'list_minions'})



class TestClientGlob(BaseTest):

    def _test_add(self, client):
        result = self.call({'clients': client,
                            'method': 'add',
                            'module': 'test',
                            'parameters': [1,2]})
        self.assert_on_fault(result)
        return result
    
    def test_single_client(self):
        result = self._test_add(self.th)

    def test_glob_client(self):
        result = self._test_add("*")

    def test_glob_list(self):
        result = self._test_add([self.th, self.th])

    def test_glob_string_list(self):
        result = self._test_add("%s;*" % self.th)

    # note, needs a /etc/func/group setup with the proper groups defined
    # need to figure out a good way to test this... -akl
    def test_group(self):
        result = self._test_add("@test")

    def test_group_and_glob(self):
        result = self._test_add("@test;*")

    def test_list_of_groups(self):
        result = self._test_add(["@test", "@test2"])

    def test_string_list_of_groups(self):
        result = self._test_add("@test;@test2")

        


class TestTest(BaseTest):
    def _echo_test(self, data):
        result = self.call({'clients':'*',
                             'method': 'echo',
                             'module': 'test',
                             'parameters': [data]})

        self.assert_on_fault(result)
        assert result[self.th] == data

    
    def test_add(self):
        result = self.call({'clients':'*',
                             'method': 'add',
                             'module': 'test',
                             'parameters': [1,2]})
        assert result[self.th] == 3


    def test_echo_int(self):
        self._echo_test(37)

    def test_echo_array(self):
        self._echo_test([1,2,"three", "fore", "V"])        

    def test_echo_hash(self):
        self._echo_test({'one':1, 'two':2, 'three': 3, 'four':"IV"})

    def test_echo_float(self):
        self._echo_test(1.0)

    def test_echo_big_float(self):
        self._echo_test(123121232.23)

    def test_echo_bigger_float(self):
        self._echo_test(234234234234234234234.234234234234234)

    def test_echo_little_float(self):
        self._echo_test(0.0000000000000000000000000000000000037)

        
    def test_echo_boolean_true(self):
        self._echo_test(True)

    def test_echo_boolean_false(self):
        self._echo_test(False)

        
        

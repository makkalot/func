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
import subprocess
import time
import unittest

import simplejson

import func.utils
from func import yaml
from func import jobthing



def structToYaml(data):
    # takes a data structure, serializes it to
    # yaml
    buf = yaml.dump(data)
    return buf


def structToJSON(data):
    #Take data structure for the test
    #and serializes it using json
    
    serialized = simplejson.dumps(input)
    return serialized


class BaseTest(object):
    # assume we are talking to localhost
    # th = socket.gethostname()
    th = socket.getfqdn()
    nforks=1
    async=False
    ft_cmd = "func-transmit"

    # just so we can change it easy later
    def _serialize(self, data):
        raise NotImplementedError

    def _deserialize(self, buf):
        raise NotImplementedError


    def _call_async(self, data):
        data['async'] = True
        data['nforks'] = 4

        job_id = self._call(data)

        no_answer = True
        while (no_answer):
            out = self._call({'clients': '*',
                             'method':'job_status',
                             'parameters': job_id})
            if out[0] == jobthing.JOB_ID_FINISHED:
                no_answer = False
            else:
                time.sleep(.25)

        result = out[1]
        return result

    def _call(self, data):
        f = self._serialize(data)
        p = subprocess.Popen(self.ft_cmd,  shell=True,
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output = p.communicate(input=f)

        return self._deserialize(output[0])

    def call(self, data):
        if self.async:
            return self._call_async(data)
        return self._call(data)
        
    def __init__(self):
        pass


   # we do this all over the place...
    def assert_on_fault(self, result):
        assert func.utils.is_error(result[self.th]) == False
#        assert type(result[self.th]) != xmlrpclib.Fault


class YamlBaseTest(BaseTest):
    # i'd add the "yaml" attr here for nosetest to find, but it doesnt
    # seem to find it unless the class is a test class directly
    ft_cmd = "func-transmit --yaml"
    def _serialize(self, data):
        buf = yaml.dump(data)
        return buf

    def _deserialize(self, buf):
        data = yaml.load(buf).next()
        return data

class JSONBaseTest(BaseTest):
    ft_cmd = "func-transmit --json"
    def _serialize(self, data):
        buf = simplejson.dumps(data)
        return buf

    def _deserialize(self, buf):
        data = simplejson.loads(buf)
        return data

class ListMinion(object):
    
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
                        
              
class ListMinionAsync(ListMinion):
    async = True

class TestListMinionYaml(YamlBaseTest, ListMinion):
    yaml = True
    def __init__(self):
        super(TestListMinionYaml, self).__init__()

class TestListMinionJSON(JSONBaseTest, ListMinion):
    json = True
    def __init__(self):
        super(TestListMinionJSON, self).__init__()

# list_minions is a convience call for func_transmit, and doesn't
# really make any sense to call async

#class TestListMinionYamlAsync(YamlBaseTest, ListMinionAsync):
#    yaml = True
#    async = True
#    def __init__(self):
#        super(TestListMinionYamlAsync, self).__init__()

#class TestListMinionJSONAsync(JSONBaseTest, ListMinionAsync):
#    json = True
#    async = True
#    def __init__(self):
#        super(TestListMinionJSONAsync, self).__init__()


    
class ClientGlob(object):
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

#    def test_group_and_glob(self):
#        result = self._test_add("@test;*")

#    def test_list_of_groups(self):
#        result = self._test_add(["@test", "@test2"])

#    def test_string_list_of_groups(self):
#        result = self._test_add("@test;@test2")


# run all the same tests, but run then 
class ClientGlobAsync(ClientGlob):
    async = True

class TestClientGlobYaml(YamlBaseTest, ClientGlob):
    yaml = True
    def __init__(self):
        super(TestClientGlobYaml, self).__init__()

class TestClientGlobJSON(JSONBaseTest, ClientGlob):
    json = True
    def __init__(self):
        super(TestClientGlobJSON, self).__init__()

class TestClientGlobYamlAsync(YamlBaseTest, ClientGlobAsync):
    yaml = True
    async = True
    def __init__(self):
        super(TestClientGlobYamlAsync, self).__init__()

class TestClientGlobJSONAsync(JSONBaseTest, ClientGlobAsync):
    json = True
    async = True
    def __init__(self):
        super(TestClientGlobJSONAsync, self).__init__()




# why the weird T_est name? because nosetests doesn't seem to reliably
# respect the __test__ attribute, and these modules aren't meant to be
# invoked as test classes themselves, only as bases for other tests
class T_estTest(object):
    __test__ = False
    
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


    # NOTE/FIXME: the big float tests fail for yaml and json 
    def test_echo_big_float(self):
        self._echo_test(123121232.23)

    def test_echo_bigger_float(self):
        self._echo_test(234234234234234234234.234234234234234)

    def test_echo_little_float(self):
        self._echo_test(0.0000000000000000000000000000000000037)

    # Note/FIXME: these test currently fail for YAML
    def test_echo_boolean_true(self):
        self._echo_test(True)

    def test_echo_boolean_false(self):
        self._echo_test(False)


class T_estTestAsync(T_estTest):
    __test__ = False
    async = True

class TestTestYaml(YamlBaseTest, T_estTest):
    yaml = True
    def __init__(self):
        super(YamlBaseTest, self).__init__()

class TestTestJSON(JSONBaseTest, T_estTest):
    json = True
    def __init__(self):
        super(JSONBaseTest,self).__init__()

class TestTestAsyncJSON(JSONBaseTest, T_estTestAsync):
    json = True
    async = True
    def __init__(self):
        super(JSONBaseTest,self).__init__()
                               
class TestTestAsyncYaml(YamlBaseTest, T_estTestAsync):
    yaml = True
    async = True
    def __init__(self):
        super(YamlBaseTest,self).__init__()

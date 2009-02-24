#!/usr/bin/python


## Copyright 2008, Various
## Adrian Likins <alikins@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## (Mon 21 2009) - Original version of these unit tests added. (Gregory Masseau, gjmasseau@learn.senecac.on.ca)
##


import os
import socket
import unittest
import xmlrpclib

import func.overlord.client as fc
import func.utils
import socket

from test_client import BaseTest

class TestUsers(BaseTest):
    import random as r
    module    = "users"
    testuser1 = "func_users__testuser1"
    testuser2 = "func_users__testuser2"
    testgroup1 = "func_users__testgroup1"
    testgroup2 = "func_users__testgroup2"

    def __unused_gid__(self):
      potentialgid = self.r.randint(2,65535)
      return potentialgid if self.overlord.users.gid_exists(potentialgid) else self.__unused_gid__()

    def __unused_uid__(self):
      potentialuid = self.r.randint(2,65535)
      return potentialuid if self.overlord.users.uid_exists(potentialuid) else self.__unused_uid__()

    def __make_test_user__(self):
      return self.overlord.users.user_add(TestUsers.testuser1)

    def __make_test_user2__(self):
      return self.overlord.users.user_add(TestUsers.testuser2)

    def __make_test_group__(self):
      return self.overlord.users.group_add(TestUsers.testgroup1)

    def __make_test_group2__(self):
      self.overlord.users.group_add(TestUsers.testgroup2)

    def __cleanup__(self):
      self.overlord.users.user_del(TestUsers.testuser1) if self.overlord.users.user_exists(TestUsers.testuser1) else True
      self.overlord.users.user_del(TestUsers.testuser2) if self.overlord.users.user_exists(TestUsers.testuser2) else True
      self.overlord.users.group_del(TestUsers.testgroup1) if self.overlord.users.group_exists(TestUsers.testgroup1) else True
      self.overlord.users.group_del(TestUsers.testgroup2) if self.overlord.users.group_exists(TestUsers.testgroup2) else True

    def test_user_add(self):
      try: 
        result = self.__make_test_user__()
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally: 
        self.__cleanup__()

    def test_user_del(self):
      try: 
        self.__make_test_user__()
        result = self.overlord.users.user_del(TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()
 
    def test_group_add(self):
      try:
        result = self.__make_test_group__()
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_group_del(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.group_del(TestUsers.testgroup1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_groups_add(self):
      try:
        result = self.overlord.users.groups_add(TestUsers.testgroup1,TestUsers.testgroup2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_users_add(self):
      try:
        result = self.overlord.users.users_add(TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_groups_del(self):
      try:
        self.__make_test_group__()
        self.__make_test_group2__()
        result = self.overlord.users.groups_del(TestUsers.testgroup1,TestUsers.testgroup2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_users_del(self):
      try:
        self.__make_test_user__()
        self.__make_test_user2__()
        result = self.overlord.users.users_del(TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_group_set_gid_non_unique(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.group_set_gid_non_unique(TestUsers.testgroup1,self.__unused_gid__())
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_group_set_gid(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.group_set_gid(TestUsers.testgroup1,self.__unused_gid__())
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()
    
    def test_group_set_groupname(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.group_set_groupname(TestUsers.testgroup1,TestUsers.testgroup2)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()
    
    def test_group_add_non_unique(self):
      try:
        result = self.overlord.users.group_add_non_unique(TestUsers.testgroup1,self.__unused_gid__())
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_lock(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_lock(TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_lock(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_lock(TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_set_shell(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_shell(TestUsers.testuser1,"/bin/false")
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_set_shell(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_set_shell("/bin/false",TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_set_home(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_home(TestUsers.testuser1,"/home/"+TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_set_loginname(self):
      try:
        self.__make_test_user__()  
        self.overlord.users.user_set_loginname(TestUsers.testuser1,TestUsers.testuser2)
        result = self.overlord.users.user_set_loginname(TestUsers.testuser2,TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_set_comment(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_comment(TestUsers.testuser1,"zyxxyz")
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_set_expiredate(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_expiredate(TestUsers.testuser1,999999)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_set_expiredate(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_set_expiredate(999999,TestUsers.testuser1,TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_set_uid_non_unique(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_uid_non_unique(TestUsers.testuser1,self.__unused_uid__())
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_set_uid(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_uid(TestUsers.testuser1,self.__unused_uid__())
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_set_inactive(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_set_inactive(TestUsers.testuser1,999999)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_set_inactive(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_set_inactive(999999,TestUsers.testuser1,TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_move_home(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_move_home(TestUsers.testuser1,"/home/"+TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_unlock(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_unlock(TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_unlock(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_unlock(TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_users_add_to_group(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        self.__make_test_group__()
        result = self.overlord.users.users_add_to_group(TestUsers.testgroup1,TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_add_to_group(self):
      try:
        self.__make_test_user__()  
        self.__make_test_group__()
        result = self.overlord.users.user_add_to_group(TestUsers.testuser1,TestUsers.testgroup1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_set_gid(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        self.__make_test_group__()
        result = self.overlord.users.users_set_gid(self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th],TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_set_gid(self):
      try:
        self.__make_test_user__()  
        self.__make_test_group__()
        result = self.overlord.users.user_set_gid(TestUsers.testuser1,self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th])
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_set_group(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        self.__make_test_group__()
        result = self.overlord.users.users_set_group(TestUsers.testgroup1,TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_user_set_group(self):
      try:
        self.__make_test_user__()  
        self.__make_test_group__()
        result = self.overlord.users.user_set_group(TestUsers.testuser1,TestUsers.testgroup1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_passwd(self):
      try:
        self.__make_test_user__()  
        self.__make_test_group__()
        result = self.overlord.users.passwd(TestUsers.testuser1,"".join(self.r.sample([chr(x) for x in range(48,58)+range(65,91)+range(97,123)],8)))
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_user_exists(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.user_exists(TestUsers.testuser1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_uid_exists(self):
      try:
        self.__make_test_user__()  
        result = self.overlord.users.uid_exists(self.overlord.users.user_to_uid(TestUsers.testuser1)[self.th])
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_group_exists(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.group_exists(TestUsers.testgroup1)
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_gid_exists(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.gid_exists(self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th])
        self.assert_on_fault(result)
        assert result[self.th] == True
      finally:
        self.__cleanup__()

    def test_users_exist(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.users_exist(TestUsers.testuser1,TestUsers.testuser2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_uids_exist(self):
      try:
        self.__make_test_user__()  
        self.__make_test_user2__()  
        result = self.overlord.users.uids_exist(self.overlord.users.user_to_uid(TestUsers.testuser1)[self.th],self.overlord.users.user_to_uid(TestUsers.testuser2)[self.th])
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_groups_exist(self):
      try:
        self.__make_test_group__()
        self.__make_test_group2__()
        result = self.overlord.users.groups_exist(TestUsers.testgroup1,TestUsers.testgroup2)
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()

    def test_gids_exist(self):
      try:
        self.__make_test_group__()
        result = self.overlord.users.gids_exist(self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th],self.overlord.users.group_to_gid(TestUsers.testgroup2)[self.th])
        self.assert_on_fault(result)
        assert result[self.th] == [True,True]
      finally:
        self.__cleanup__()
    
    def __trivial_test__(self,function):
      def list_test():
        try:
          result = function()
          self.assert_on_fault(result)
        finally:
          self.__cleanup__()
      return list_test

    def test_user_list(self):    self.__trivial_test__(self.overlord.users.user_list)()
    def test_users_list(self):   self.__trivial_test__(self.overlord.users.users_list)()
    def test_group_list(self):   self.__trivial_test__(self.overlord.users.group_list)()
    def test_groups_list(self):  self.__trivial_test__(self.overlord.users.groups_list)()
    def test_uid_list(self):     self.__trivial_test__(self.overlord.users.uid_list)()
    def test_uids_list(self):    self.__trivial_test__(self.overlord.users.uids_list)()
    def test_gid_list(self):     self.__trivial_test__(self.overlord.users.gid_list)()
    def test_gids_list(self):    self.__trivial_test__(self.overlord.users.gids_list)()

    def __info_test__(self,function):
      def info_test(target):
        try:
          self.__make_test_user__()
          self.__make_test_user2__()
          self.__make_test_group__()
          self.__make_test_group2__()
          result = function(target)
          self.assert_on_fault(result)
        finally:
          self.__cleanup__()
      return info_test

    def test_user_info(self):  self.__info_test__(self.overlord.users.user_info)(TestUsers.testuser1)
    def test_group_info(self): self.__info_test__(self.overlord.users.group_info)(TestUsers.testgroup1)
    def test_uid_info(self):   self.__info_test__(self.overlord.users.uid_info)(self.overlord.users.user_to_uid(TestUsers.testuser1)[self.th])
    def test_gid_info(self):   self.__info_test__(self.overlord.users.gid_info)(self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th])

    def __plural_info_test__(self,function):
      def plural_info_test(*targets):
        try:
          self.__make_test_user__()
          self.__make_test_user2__()
          self.__make_test_group__()
          self.__make_test_group2__()
          result = function(*targets)
          self.assert_on_fault(result)
        finally:
          self.__cleanup__()
      return plural_info_test

    def test_users_info(self):  self.__plural_info_test__(self.overlord.users.users_info)(TestUsers.testuser1,TestUsers.testuser2)
    def test_groups_info(self): self.__plural_info_test__(self.overlord.users.groups_info)(TestUsers.testgroup1,TestUsers.testgroup2)
    def test_uids_info(self):   self.__plural_info_test__(self.overlord.users.uids_info)(self.overlord.users.user_to_uid(TestUsers.testuser1)[self.th],self.overlord.users.user_to_uid(TestUsers.testuser2)[self.th])
    def test_gids_info(self):   self.__plural_info_test__(self.overlord.users.gids_info)(self.overlord.users.group_to_gid(TestUsers.testgroup1)[self.th],self.overlord.users.group_to_gid(TestUsers.testgroup2)[self.th])

    def user_to_uid(self):      self.__info_test__(self.overlord.users.user_to_uid)(TestUsers.testuser1)
    def group_to_guid(self):    self.__info_test__(self.overlord.users.group_to_guid)(TestUsers.testgroup1)
    def users_to_uids(self):    self.__plural_info_test__(self.overlord.users.users_to_uids)(TestUsers.testuser1,TestUsers.testuser2)
    def groups_to_gids(self):   self.__plural_info_test__(self.overlord.users.groups_to_gids)(TestUsers.testgroup1,TestUsers.testgroup2)

"""
Virt-factory backend code.

Copyright 2006, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>
Scott Seago <sseago@redhat.com>

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import string
import exceptions
import os

class BaseObject(object):

   FIELDS = []  # subclasses should define a list of db column names here

   def load(self,hash,key,default=None):
      """
      Access a hash element safely...
      """
      # FIXME: it would be cool if load starts with a copy of the hash
      # and clears off entries as recieved, such that we can tell if any
      # entries are not loaded.  This should result in a warning in the return
      # object.
      assert hash is not None, "hash is None"
      assert key is not None, "key is None"
      if hash.has_key(key):
          return hash[key]
      else:
          return default

   def to_datastruct(self,to_caller=False):
      """
      Return a hash representation of this object.
      Defers to self.to_datastruct_internal which subclasses must implement.
      """
      ds = self.to_datastruct_internal()
      if to_caller:
          # don't send NULLs
          ds = self.remove_nulls(ds)
      return ds

   def to_datastruct_internal(self):
      """
      Subclasses:  implement this.
      """
      raise exceptions.NotImplementedError

   def deserialize(self, args):
      for x in self.FIELDS:
          if args.has_key(x):
              setattr(self, x, args[x])
          else:
              setattr(self, x, None)

   def serialize(self):
      result = {}
      for x in self.FIELDS:
         result[x] = getattr(self, x, None)
      return result

   def remove_nulls(self, x):
       """
       If any entries are None in the datastructure, prune them.
       XMLRPC can't marshall None and this is our workaround.  Objects
       that are None are removed from the hash -- including hash keys that
       are not None and have None for the value.  The WUI or other SW
       should know how to deal with these returns.
       """
       assert x is not None, "datastructure is None"
       if type(x) == list:
           newx = []
           for i in x:
               if type(i) == list or type(i) == dict:
                   newx.append(self.remove_nulls(i))
               elif i is not None:
                   newx.append(i)
           x = newx
       elif type(x) == dict:
           newx = {}
           for i,j in x.iteritems():
               if type(j) == list or type(j) == dict:
                   newx[i] = self.remove_nulls(x)
               elif j is not None:
                   newx[i] = j
           x = newx
       return x

    # ========================
    # random utility functions

   def is_printable(self, stringy):
        # FIXME: use regex package

        if stringy == None:
           return False
        if type(stringy) != str:
           stringy = "%s" % stringy
        try:
            for letter in stringy:
                if letter not in string.printable:
                    return False
            return True
        except:
            return False
 
        
        
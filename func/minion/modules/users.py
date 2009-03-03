###############################################################################
#
# Func Users and Group management module.
# Author: Gregory Masseau <gjmasseau@learn.senecac.on.ca>
#
###############################################################################
#
# Legal: 
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
###############################################################################
#
# Changelog:
#
# 0.5:
# - (Feature)  Implemented register_method_args.
# - (External) Unit tests added to test_client.py.
#
# 0.4:
# - (Feature)  Password alteration method added.
# - (Feature)  Pluralized methods for all applicable singular methods.
# - (Misc)     General API cleanup.
#
# 0.3:
# - (Feature)  Methods added to create, delete, and modify groups.
# - (Feature)  Methods added to create, delete, and modify users.
# - (Feature)  Manage the memberships of users within groups
#
# 0.2:
# - (Feature)  Most informational methods are complete and working for both 
#              users and groups at this point.
#
# 0.1:
# - (Feature)  Initial release, supporting only some informational query 
#              messages regarding user accounts on the target system.
#
###############################################################################
"""
User management module for func.
"""

from func.minion.modules import func_module
from func.minion import sub_process
import pwd
import grp
from os import system

class UsersModule(func_module.FuncModule):
  version     = "0,5"
  api_version = "0,5"
  description = "Nearly complete."

# INTERNALLY USED METHODS #####################################################
  def __command(self,*list):
    """
    This method is used internally by this module when invoking external commands. It should remain private.
    This method should probably be improved to check the elems for suspicious characters like ';','&&','||'.
    """
    cmd = ''
    for elem in list:
      if elem == '':
        pass
      else:
        cmd = cmd + " '" + str(elem.replace("'","") if (type(elem) == str) else elem) + "'"
#    print "\nCmd: [%s]"%cmd
    return False if system(cmd+" 2>/dev/null 1>/dev/null") else True

  def __plural(self,f):
    return (lambda xs: map(f,xs))

# GROUPADD METHODS ############################################################
  def __groupadd(self,group,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.group_exists(group):
      return False
    else:
      return self.__command("/usr/sbin/groupadd",group,*switches)

  def group_add(self,group,*gid):
     """Adds a group on the target system(s)."""
     if gid:
       if self.gid_exists(gid[0]):
         return False
       else:
         print str(gid[0]) + "<-"
         return self.__groupadd(group,"-g",gid[0])
     else:
       return self.__groupadd(group)

  def groups_add(self,*groups):
    """Adds a series of groups on the target system(s)."""
    return self.__plural(self.group_add)(groups)

  def group_add_non_unique(self,group,*gid):
    """Adds a group on the target system(s)."""
    if gid:
      if self.gid_exists(gid[0]):
        return False
      else:
        return self.__groupadd(group,"-o","-g",gid[0])
    else:
      return self.__groupadd(group,"-o")

# GROUPDEL METHODS ############################################################
  def __groupdel(self,group,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.group_exists(group):
      return self.__command("/usr/sbin/groupdel",group,*switches)
    else:
      return False

  def group_del(self,group):
    """Deletes a group on the target system(s)."""
    return self.__groupdel(group)
 
  def groups_del(self,*groups):
    """Adds a series of groups."""
    return self.__plural(self.group_del)(groups)

# GROUPMOD METHODS ############################################################
  def __groupmod(self,group,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.group_exists(group):
      if switches:
        return self.__command("/usr/sbin/groupmod",group,*switches)
      else:
        return self.__command("/usr/sbin/groupmod",group)
    else:
      return False

  def group_set_gid_non_unique(self,group,gid):
    """Changes the GID of the specified group on the target system(s), allowing non-unique GID."""
    return self.__groupmod(group,"-o","-g",gid)

  def group_set_gid(self,group,gid):
    """Changes the GID of the specified group on the target system(s)."""
    if self.gid_exists(gid):
      return False
    else:
      return self.__groupmod(group,"-g",gid)

  def group_set_groupname(self,group,groupname):
    """Changes the name of the specified group on the target system(s)."""
    if self.group_exists(groupname):
      return False
    else:
      return self.__groupmod(group,"-n",groupname)

# USERADD METHODS #############################################################
  def __useradd(self,user,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.user_exists(user):
      return False
    else:
      return self.__command("/usr/sbin/useradd",user)

  def user_add(self,user):
    """Adds a user on the target system(s)."""
    return self.__useradd(user) 

  def users_add(self,*users):
    """Adds a series of users on the target system(s)."""
    return self.__plural(self.user_add)(users)

# USERDEL METHODS #############################################################
  def __userdel(self,user,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.user_exists(user):
      return self.__command("/usr/sbin/userdel",user,*switches)
    else:
      return False

  def user_del(self,user,*options):
    """Deletes a user on the target system(s)."""
    switches=[]
    if options:
      for option in options:
        if   option == 'force':
          switches.append('-f')
        elif option == 'remove':
          switches.append('-r')
        else: 
          return False
    return self.__userdel(user,*switches) 

  def users_del(self,*users):
    """Deletes a series of users on the target system(s)."""
    return self.__plural(self.user_del)(users)

# USERMOD METHODS #############################################################
  def __usermod(self,user,*switches):
    """Constructs the proper argument sequence for self.__command and returns it's result."""
    if self.user_exists(user):
      command = []
      if switches:
        command = list(switches)
      command.append(user)
      return self.__command("/usr/sbin/usermod",*command)
    else:
      return False

  def user_lock(self,user):
    """Locks a user account on the target system(s)."""
    return self.__usermod(user,"-L")

  def users_lock(self,*users):
    """Locks a series of user accounts on the target system(s)."""
    return self.__plural(self.user_lock)(users)

  def user_set_shell(self,user,shell):
    """Set a specified user's shell on the target system(s)."""
    return self.__usermod(user,"-s",shell)

  def users_set_shell(self,shell,*users):
    """Set a specified list of users' shell on the target system(s)."""
    return self.__plural(lambda u: self.user_set_shell(u,shell))(users)

  def user_set_home(self,user,home):
    """Change (but don't move the contents of) a user's home folder on the target system(s)."""
    return self.__usermod(user,"-d",home)

  def user_set_loginname(self,user,loginname):
    """Change a user's login name on the target system(s)."""
    return self.__usermod(user,"-l",loginname)

  def user_set_comment(self,user,comment):
    """Change the value of a user's GECOS field -- maybe replace this with a field sensitive version?"""
    return self.__usermod(user,"-c",comment)

  def user_set_expiredate(self,user,expiredate):
    """Set the expity date for a specified user on the target system(s)."""
    return self.__usermod(user,"-e",expiredate)

  def users_set_expiredate(self,expiredate,*users):
    """Set a specified list of users' expiry date on the target system(s)."""
    return self.__plural(lambda u: self.user_set_expiredate(u,expiredate))(users)

  def user_set_uid_non_unique(self,user,uid):
    """Change a user's UID, allowing non-unique UIDs on the target system(s)."""
    return self.__usermod(user,"-u",uid,"-o")

  def user_set_uid(self,user,uid):
    """Change a user's UID on the target system(s)."""
    return self.__usermod(user,"-u",uid)

  def user_set_inactive(self,user,inactive):
    """Set the inactivity timer on a user on the target system(s)."""
    return self.__usermod(user,"-f",inactive)

  def users_set_inactive(self,inactive,*users):
    """Set the inactivity timer on a series of users on the target system(s)."""
    return self.__plural(lambda u: self.user_set_inactive(u,inactive))(users)

  def user_set_gid(self,user,gid):
    """Change a users primary group by GID on the target system(s)."""
    if self.gid_exists(gid):
      return self.__usermod(user,"-g",gid)
    else:
      return False

  def users_set_gid(self,gid,*users):
    """Set a specified list of users' primary GID on the target system(s)."""
    return self.__plural(lambda u: self.user_set_gid(u,gid))(users)

  def user_move_home(self,user,home):
    """Changes and moves a users home folder on the target system(s)."""
    return self.__usermod(user,"-d",home,"-m")

  def user_unlock(self,user):
    """Unlocks a specified user account on the target system(s)."""
    return self.__usermod(user,"-U")

  def users_unlock(self,*users):
    """Unlocks a specified list of users' accounts on the target system(s)."""
    return self.__plural(self.user_unlock)(users)

  def user_add_to_group(self,user,group):
    """Appends the user to a specified group on the target system(s)."""
    if self.group_exists(group):
      return self.__usermod(user,"-aG",group)
    else:
      return False

  def users_add_to_group(self,group,*users):
    """Appends the list of users to a specified group on the target system(s)."""
    return self.__plural(lambda u: self.user_add_to_group(u,group))(users)

  def user_set_group(self,user,group):
    """Changes a users primary group on the target system(s)."""
    if self.group_exists(group):
      gid = self.group_to_gid(group)
      return self.__usermod(user,"-g",gid)
    else:
      return False

  def users_set_group(self,group,*users):
    """Changes a series of users' primary group on the target system(s)."""
    return self.__plural(lambda u: self.user_set_group(u,group))(users)

# PASSWD/CHPASWD METHODS  #####################################################
  def passwd(self,user,passwd):
    """Changes a user's password on the target system(s)."""
    if self.user_exists(user):
      if system("echo "+passwd+" | passwd --stdin "+user):
        return False
      else:
        return True
    else:
      return False

# INFORMATIONAL METHODS #######################################################
# EXISTANCE TEST METHODS
  def user_exists(self,user):
    """Checks to see if a given user exists on the target system(s)."""
    try:
      if pwd.getpwnam(user):
        return True
    except KeyError:
      return False

  def users_exist(self,*users):
    """Checks to see if a series of users exists on the target system(s)."""
    return self.__plural(self.user_exists)(users)

  def uid_exists(self,uid):
    """Checks to see if a given UID exists on the target system(s)."""
    try:
      if pwd.getpwuid(int(uid)):
        return True
    except KeyError:
      return False

  def uids_exist(self,*uids):
    """Checks to see if a series of UIDs exists on the target system(s)."""
    return self.__plural(self.uid_exists)(uids)

  def group_exists(self,group):
    """Checks to see if a given group exists on the target system(s)."""
    try:
      if grp.getgrnam(group):
        return True
    except KeyError:
      return False

  def groups_exist(self,*groups):
    """Checks to see if a series of groups exist on the target system(s)."""
    return self.__plural(self.group_exists)(groups)

  def gid_exists(self,gid):
    """Checks to see if a given GID exists on the target system(s)."""
    try:
      if grp.getgrgid(int(gid)):
        return True
    except KeyError:
      return False

  def gids_exist(self,*gids):
    """Checks to see if a series of GIDs exist on the target system(s)."""
    return self.__plural(self.gid_exists)(gids)

# LISTING METHODS
  def user_list(self):
    """Lists all users on the target system(s)."""
    users = []
    for user in pwd.getpwall():
      users.append(user[0])
    return users

  def users_list(self):
    """Lists all users on the target system(s)."""
    return self.user_list()

  def uid_list(self):
    """Lists all UIDs on the target system(s)."""
    uids = []
    for user in pwd.getpwall():
      uids.append(user[2] if user[2] < 4294967294 else True)
    return uids

  def uids_list(self):
    """Lists all UIDs on the target system(s)."""
    return self.uid_list()

  def group_list(self):
    """Lists all groups on the target system(s)."""
    groups = []
    for group in grp.getgrall():
      groups.append(group[0])
    return groups

  def groups_list(self):
    """Lists all groups on the target system(s)."""
    return self.group_list()

  def gid_list(self):
    """Lists all GIDs on the target system(s)."""
    gids = []
    for group in grp.getgrall():
      gids.append(group[2] if group[2] < 4294967294 else True)
    return gids

  def gids_list(self):
    """Lists all GIDs on the target system(s)."""
    return self.gid_list()

# INFO METHODS
  def user_info(self,user):
    """Returns user info or false for a specified user on the target system(s)."""
    try:
      if pwd.getpwnam(user):
         info = pwd.getpwnam(user)
         return list(info) # I'm not sure why this has to be listed but the method fails to work if it isn't.
    except KeyError:
      return False

  def users_info(self,*users):
    """Returns a list of (group info or False) for a series of users on the target system(s)."""
    return self.__plural(self.user_info)(users)

  def uid_info(self,uid):
    """Returns user info or false for a specified user (by UID) on the target system(s)."""
    try:
      if pwd.getpwuid(uid):
        info = pwd.getpwuid(int(uid))
        return list(info)
    except KeyError:
      return False

  def uids_info(self,*uids):
    """Returns a list (group info or False) for a series of users (by UID) on the target system(s)."""
    return self.__plural(self.uid_info)(uids)

  def group_info(self,group):
    """Returns group info or false for a specified group on the target system(s)."""
    try:
      if grp.getgrnam(group):
        info = grp.getgrnam(group)
        return list(info) #for some reason this needs to be list-ed
    except KeyError:
      return False

  def groups_info(self,*groups):
    """Returns a list (group info or False) for a series of groups on the target system(s)."""
    return self.__plural(self.group_info)(groups)

  def gid_info(self,gid):
    """Returns group info or false for a specified group (by GID) on the target system(s)."""
    try:
      if grp.getgrgid(int(gid)):
        info = grp.getgrgid(int(gid))
        return list(info)
    except KeyError:
      return False

  def gids_info(self,*gids):
    """Returns a list (group info or False) for a series of groups (by GID) on the target system(s)."""
    return self.__plural(self.gid_info)(gids)

# INVENTORY METHODS
  def user_inventory(self):
    """Returns user info for all users on the target system(s)."""
    return pwd.getpwall()

  def users_inventory(self):
    """Returns user info for all users on the target system(s)."""
    return self.users_inventory()

  def group_inventory(self):
    """Returns group info for all users on the target system(s)."""
    return grp.getgrall()

  def groups_inventory(self):
    """Returns group info for all users on the target system(s)."""
    return self.groups_inventory()

# CONVERSION METHODS
  def user_to_uid(self,user):
    """Takes a user name and converts it to the matching UID."""
    try:
      username = pwd.getpwnam(user)[2]
      return username
    except KeyError:
      return False

  def users_to_uids(self,*users):
    """Takes a series of usernames and converts it to a list of matching UIDs."""
    return self.__plural(self.user_to_uid)(users)

  def uid_to_user(self,uid):
    """Takes a UID and converts it to the matching user name."""
    try:
      user = pwd.getpwuid(int(uid))[0]
      return user
    except KeyError:
      return False

  def uids_to_users(self,*uids):
    """Takes a series of UIDs and converts it to a list of matching user names."""
    return self.__plural(self.uid_to_user)(uids)

  def group_to_gid(self,group):
    """Takes a group name and converts it to the matching GID."""
    try:
      groupname = grp.getgrnam(group)[2]
      return groupname
    except KeyError:
      return False

  def groups_to_gids(self,*groups):
    """Takes a series of group names and converts it to a list of matching GIDs."""
    return self.__plural(self.group_to_gid)(groups)

  def gid_to_group(self,gid):
    """Takes a GID and converts it to the matching group name."""
    try:
      group = grp.getgrgid(int(gid))[0]
      return group
    except KeyError:
      return False

  def gids_to_groups(self,*gids):
    """Takes a series of GIDs and converts it to a list of matching group names."""
    return self.__plural(self.gid_to_groups)(gids)

######

  def register_method_args(self):
    password = {
      'type':'string',
      'optional':False,
      'description':'A password.'
    }
    cmdopt = {
      'type':'string',
      'optional':False,
      'description':'An option to the command.'
    }
    cmdopts = {
      'type':'list*',
      'optional':False,
      'description':'An series of options to the command.'
    }
    username = {
      'type':'string',
      'optional':False,
      'description':'A username.',
    }
    usernames = {
      'type':'list*',
      'optional':False,
      'description':'A series of usernames.',
    }
    group = {
      'type':'string',
      'optional':False,
      'description':'A group name.'
    }
    groups = {
      'type':'list*',
      'optional':False,
      'description':'A series of group names.'
    }
    gid = {
      'type':'int',
      'optional':False,
      'description':'A gid.'
    }
    gids = {
      'type':'list*',
      'optional':False,
      'description':'A series of gids.'
    }
    ogid = {
      'type':'list*',
      'optional':False,
      'description':'An optional gid.'
    }
    ouid = {
      'type':'list*',
      'optional':False,
      'description':'An optional uid.'
    }
    uid = {
      'type':'int',
      'optional':False,
      'description':'A uid.'
    }
    uids = {
      'type':'list*',
      'optional':False,
      'description':'A series of uids.'
    }

    return {
      #GROUPADD METHODS
      'group_add':{
        'args':{
          'group':group,
          'gid':ogid
        },
      'description':"Create a group."
      },

      'groups_add':{
        'args':{
          'groups':groups
        },
      'description':"Create series of groups."
      },

      'group_add_non_unique':{
        'args':{
          'group':group,
          'gid':ogid
        },
      'description':"Create a group."
      },

      #GROUPDEL METHODS
      'group_del':{
        'args':{
          'group':group
        },
      'description':"Delete a group."
      },

      'groups_del':{
        'args':{
          'groups':groups
        },
      'description':"Delete a series of groups."
      },

      #GROUPMOD METHODS
      'group_set_gid_non_unique':{
        'args':{
          'group':group,
          'gid':gid
        },
      'description':"Allows a groups gid to be non-unique."
      },

      'group_set_gid':{
        'args':{
          'group':group,
          'gid':gid
        },
      'description':"Set a group's gid."
      },

      'group_set_groupname':{
        'args':{
          'group':group,
          'groupname':group
        },
      'description':"Set a group's groupname."
      },

      #USERADD METHODS
      'user_add':{
        'args':{
          'user':username
        },
      'description':"Create a user."
      },

      'users_add':{
        'args':{
          'users':usernames
        },
      'description':"Create series of users."
      },

      #USERDEL METHODS
      'user_del':{
        'args':{
          'user':username,
          'options':cmdopts,
        },
      'description':"Delete a user's account."
      },

      'users_del':{
        'args':{
          'users':usernames,
        },
      'description':"Delete a series of users' accounts."
      },

      #USERMOD METHODS
      'user_lock':{
        'args':{
          'user':username,
        },
      'description':"Lock a user's account."
      },

      'users_lock':{
        'args':{
          'users':usernames,
        },
      'description':"Lock a series of users' accounts."
      },

      'user_set_shell':{
        'args':{
          'user':username,
          'shell':{
             'type':'string',
              'optional':False,
              'description':"A path to a shell."
          }
        },
      'description':"Set a user's shell."
      },

      'users_set_shell':{
        'args':{
          'users':usernames,
          'shell':{
             'type':'string',
              'optional':False,
              'description':"A path to a shell."
          }
        },
      'description':"Set a series of users' shell."
      },

      'user_set_home':{
        'args':{
          'user':username,
          'home':{
             'type':'string',
              'optional':False,
              'description':"A directory."
          }
        },
      'description':"Set a user's home folder."
      },

      'user_set_loginname':{
        'args':{
          'user':username,
          'loginname':username
        },
      'description':"Set a user's GECOS field."
      },

      'user_set_comment':{
        'args':{
          'user':username,
          'comment':cmdopt
        },
      'description':"Set a user's GECOS field."
      },

      'user_set_expiredate':{
        'args':{
          'user':username,
          'expiredate':cmdopt
        },
      'description':"Set a user's account's expiry date."
      },

      'users_set_expiredate':{
        'args':{
          'expiredate':cmdopt,
          'users':usernames
        },
      'description':"Set a series of users' accounts' expiry date."
      },

      'user_set_uid_non_unique':{
        'args':{
          'user':username,
          'uid':uid
        },
      'description':"Set a user's uid."
      },

      'user_set_uid':{
        'args':{
          'user':username,
          'uid':uid
        },
      'description':"Set a user's uid."
      },

      'user_set_inactive':{
        'args':{
          'user':username,
          'inactive':cmdopt
        },
      'description':"Set a user's inactivity timer."
      },

      'users_set_inactive':{
        'args':{
          'inactive':cmdopt,
          'users':usernames
        },
      'description':"Set a series of users' inactivity timer."
      },

      'user_set_gid':{
        'args':{
          'user':username,
          'gid':gid
        },
      'description':"Set a user's gid."
      },

      'users_set_gid':{
        'args':{
          'gid':gid,
          'users':usernames
        },
      'description':"Set a series of users' gids."
      },

      'user_move_home':{
        'args':{
          'user':username,
          'home':{
             'type':'string',
              'optional':False,
              'description':"A directory."
          }
        },
      'description':"Set a user's home folder and move the contents to the new folder."
      },

      'user_unlock':{
        'args':{
          'user':username,
        },
      'description':"Unlock a user's account."
      },

      'users_unlock':{
        'args':{
          'users':usernames,
        },
      'description':"Unlock a series of users' account."
      },

      'user_add_to_group':{
        'args':{
          'group':group,
          'user':username,
        },
      'description':"Append a user to a group."
      },

      'users_add_to_group':{
        'args':{
          'group':group,
          'users':usernames,
        },
      'description':"Append a series of users to a group."
      },

      'user_set_group':{
        'args':{
          'group':group,
          'user':username,
        },
      'description':"Set a user's group."
      },

      'users_set_group':{
        'args':{
          'group':group,
          'users':usernames,
        },
      'description':"Set a series of users' group."
      },

      #PASSWD METHODS
      'passwd':{
        'args':{
          'user':username,
          'passwd':password
        },
      'description':"Change a user's password."
      },

      #EXISTANCE TEST METHODS
      'uid_exists':{
        'args':{
          'uid':uid
        },
      'description':'Test the existance of a uids.'
      },

      'uids_exist':{
        'args':{
          'uids':uids
        },
      'description':'Test the existance of a series of uids.'
      },

      'gid_exists':{
        'args':{
          'gid':gid
        },
      'description':'Test the existance of a gids.'
      },

      'gids_exist':{
        'args':{
          'gids':gids
        },
      'description':'Test the existance of a series of groups.'
      },

      'user_exists':{
        'args':{
          'user':username
        },
      'description':'Test the existance of a users.'
      },

      'users_exist':{
        'args':{
          'users':usernames
        },
      'description':'Test the existance of a series of users.'
      },

      'group_exists':{
        'args':{
          'group':group
        },
      'description':'Test the existance of a groups.'
      },

      'groups_exist':{
        'args':{
          'groups':groups
        },
      'description':'Test the existance of a series of groups.'
      },

      #LISTING METHODS
      'uid_list':{
        'args':{},
      'description':'Get a list of all uids.'
      },

      'uids_list':{
        'args':{},
      'description':'Get a list of all uids.'
      },

      'gid_list':{
        'args':{},
      'description':'Get a list of all gids.'
      },

      'gids_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      'user_list':{
        'args':{},
      'description':'Get a list of all users.'
      },

      'users_list':{
        'args':{},
      'description':'Get a list of all users.'
      },

      'group_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      'groups_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      #INFO METHODS
      'user_info':{
        'args':{
          'user':username
        },
      'description':'Fetch info for a specified user.'
      },

      'users_info':{
        'args':{
          'users':usernames
        },
      'description':'Fetch info for a specified series of users.'
      },

      'uid_info':{
        'args':{
          'uid':uid
        },
      'description':'Fetch info for a specified uid.'
      },

      'uids_info':{
        'args':{
          'uids':uids
        },
      'description':'Fetch info for a specified series of uids.'
      },

      'group_info':{
        'args':{
          'group':group
        },
      'description':'Fetch info for a specified group.'
      },

      'groups_info':{
        'args':{
          'groups':groups
        },
      'description':'Fetch info for a specified series of groups.'
      },

      'gid_info':{
        'args':{
          'gid':gid
        },
      'description':'Fetch info for a specified gid.'
      },

      'gids_info':{
        'args':{
          'gids':gids
        },
      'description':'Fetch info for a specified series of gids.'
      },

      #INVENTORY METHODS
      'user_inventory':{
        'args':{},
      'description':'Get user info for all users.'
      },

      'users_inventory':{
        'args':{},
      'description':'Get user info for all users.'
      },

      'group_inventory':{
        'args':{},
      'description':'Get group info for all groups.'
      },

      'groups_inventory':{
        'args':{},
      'description':'Get group info for all groups.'
      },

      #CONVERSION METHODS
      'user_to_uid':{
        'args':{
          'user':username
        },
      'description':'Convert a username to a matching uid.'
      },

      'users_to_uids':{
        'args':{
          'users':usernames
        },
      'description':'Convert a series of usernames to a list of matching uids.'
      },

      'uid_to_user':{
        'args':{
          'uid':uid
        },
      'description':'Convert a uid to a username.'
      },

      'uids_to_users':{
        'args':{
          'uids':uids
        },
      'description':'Convert a series of uids to a list of matching usernames.'
      },

      'group_to_gid':{
        'args':{
          'group':group
        },
      'description':'Convert a group to a matching gid.'
      },

      'groups_to_gids':{
        'args':{
          'groups':groups
        },
      'description':'Converts a series of groups to a list of matching gids.'
      },

      'gid_to_group':{
        'args':{
          'gid':gid
        },
      'description':'Converts a gids to a matching groupname.'
      },

      'gids_to_groups':{
        'args':{
          'gids':gids
        },
      'description':'Converts a series of gids to a list of matching groupnames.'
      }

    }


  def ree(self):
    password = {
      'type':'string',
      'optional':False,
      'description':'A password.'
    }
    cmdopt = {
      'type':'string',
      'optional':False,
      'description':'An option to the command.'
    }
    cmdopts = {
      'type':'list*',
      'optional':False,
      'description':'An series of options to the command.'
    }
    username = {
      'type':'string',
      'optional':False,
      'description':'A username.',
    }
    usernames = {
      'type':'list*',
      'optional':False,
      'description':'A series of usernames.',
    }
    group = {
      'type':'string',
      'optional':False,
      'description':'A group name.'
    }
    groups = {
      'type':'list*',
      'optional':False,
      'description':'A series of group names.'
    }
    gid = {
      'type':'int',
      'optional':False,
      'description':'A gid.'
    }
    gids = {
      'type':'list*',
      'optional':False,
      'description':'A series of gids.'
    }
    ogid = {
      'type':'list*',
      'optional':False,
      'description':'An optional gid.'
    }
    ouid = {
      'type':'list*',
      'optional':False,
      'description':'An optional uid.'
    }
    uid = {
      'type':'int',
      'optional':False,
      'description':'A uid.'
    }
    uids = {
      'type':'list*',
      'optional':False,
      'description':'A series of uids.'
    }

    return {
      #GROUPADD METHODS
      'group_add':{
        'args':{
          'group':group,
          'gid':ogid
        },
      'description':"Create a group."
      },

      'groups_add':{
        'args':{
          'groups':groups
        },
      'description':"Create series of groups."
      },

      'group_add_non_unique':{
        'args':{
          'group':group,
          'gid':ogid
        },
      'description':"Create a group."
      },

      #GROUPDEL METHODS
      'group_del':{
        'args':{
          'group':group
        },
      'description':"Delete a group."
      },

      'groups_del':{
        'args':{
          'groups':groups
        },
      'description':"Delete a series of groups."
      },

      #GROUPMOD METHODS
      'group_set_gid_non_unique':{
        'args':{
          'group':group,
          'gid':gid
        },
      'description':"Allows a groups gid to be non-unique."
      },

      'group_set_gid':{
        'args':{
          'group':group,
          'gid':gid
        },
      'description':"Set a group's gid."
      },

      'group_set_groupname':{
        'args':{
          'group':group,
          'groupname':group
        },
      'description':"Set a group's groupname."
      },

      #USERADD METHODS
      'user_add':{
        'args':{
          'user':username
        },
      'description':"Create a user."
      },

      'users_add':{
        'args':{
          'users':usernames
        },
      'description':"Create series of users."
      },

      #USERDEL METHODS
      'user_del':{
        'args':{
          'user':username,
          'options':cmdopts,
        },
      'description':"Delete a user's account."
      },

      'users_del':{
        'args':{
          'users':usernames,
          'options':cmdopts,
        },
      'description':"Delete a series of users' accounts."
      },

      #USERMOD METHODS
      'user_lock':{
        'args':{
          'user':username,
        },
      'description':"Lock a user's account."
      },

      'users_lock':{
        'args':{
          'users':usernames,
        },
      'description':"Lock a series of users' accounts."
      },

      'user_set_shell':{
        'args':{
          'user':username,
          'shell':{
             'type':'string',
              'optional':False,
              'description':"A path to a shell."
          }
        },
      'description':"Set a user's shell."
      },

      'users_set_shell':{
        'args':{
          'users':usernames,
          'shell':{
             'type':'string',
              'optional':False,
              'description':"A path to a shell."
          }
        },
      'description':"Set a series of users' shell."
      },

      'user_set_home':{
        'args':{
          'user':username,
          'home':{
             'type':'string',
              'optional':False,
              'description':"A directory."
          }
        },
      'description':"Set a user's home folder."
      },

      'user_set_loginname':{
        'args':{
          'user':username,
          'loginname':username
        },
      'description':"Set a user's GECOS field."
      },

      'user_set_comment':{
        'args':{
          'user':username,
          'comment':cmdopt
        },
      'description':"Set a user's GECOS field."
      },

      'user_set_expiredate':{
        'args':{
          'user':username,
          'expiredate':cmdopt
        },
      'description':"Set a user's account's expiry date."
      },

      'users_set_expiredate':{
        'args':{
          'expiredate':cmdopt,
          'users':usernames
        },
      'description':"Set a series of users' accounts' expiry date."
      },

      'user_set_uid_non_unique':{
        'args':{
          'user':username
        },
      'description':"Set a user's uid."
      },

      'user_set_uid':{
        'args':{
          'user':username,
          'uid':uid
        },
      'description':"Set a user's uid."
      },

      'user_set_inactive':{
        'args':{
          'user':username,
          'inactive':cmdopt
        },
      'description':"Set a user's inactivity timer."
      },

      'users_set_inactive':{
        'args':{
          'inactive':cmdopt,
          'users':usernames
        },
      'description':"Set a series of users' inactivity timer."
      },

      'user_set_gid':{
        'args':{
          'user':username,
          'gid':gid
        },
      'description':"Set a user's gid."
      },

      'users_set_gid':{
        'args':{
          'gid':gid,
          'users':usernames
        },
      'description':"Set a series of users' gids."
      },

      'user_move_home':{
        'args':{
          'user':username,
          'home':{
             'type':'string',
              'optional':False,
              'description':"A directory."
          }
        },
      'description':"Set a user's home folder and move the contents to the new folder."
      },

      'user_unlock':{
        'args':{
          'user':username,
        },
      'description':"Unlock a user's account."
      },

      'users_unlock':{
        'args':{
          'users':usernames,
        },
      'description':"Unlock a series of users' account."
      },

      'user_add_to_group':{
        'args':{
          'group':group,
          'user':username,
        },
      'description':"Append a user to a group."
      },

      'users_add_to_group':{
        'args':{
          'group':group,
          'users':usernames,
        },
      'description':"Append a series of users to a group."
      },

      'user_set_group':{
        'args':{
          'group':group,
          'user':username,
        },
      'description':"Set a user's group."
      },

      'users_set_group':{
        'args':{
          'group':group,
          'users':usernames,
        },
      'description':"Set a series of users' group."
      },

      #EXISTANCE TEST METHODS
      'uid_exists':{
        'args':{
          'uid':uid
        },
      'description':'Test the existance of a uids.'
      },

      'uids_exist':{
        'args':{
          'uids':uids
        },
      'description':'Test the existance of a series of uids.'
      },

      'gid_exists':{
        'args':{
          'gid':gid
        },
      'description':'Test the existance of a gids.'
      },

      'gids_exist':{
        'args':{
          'gids':gids
        },
      'description':'Test the existance of a series of groups.'
      },

      'user_exists':{
        'args':{
          'user':username
        },
      'description':'Test the existance of a users.'
      },

      'users_exist':{
        'args':{
          'users':usernames
        },
      'description':'Test the existance of a series of users.'
      },

      'group_exists':{
        'args':{
          'group':group
        },
      'description':'Test the existance of a groups.'
      },

      'groups_exist':{
        'args':{
          'groups':groups
        },
      'description':'Test the existance of a series of groups.'
      },

      #LISTING METHODS
      'uid_list':{
        'args':{},
      'description':'Get a list of all uids.'
      },

      'uids_list':{
        'args':{},
      'description':'Get a list of all uids.'
      },

      'gid_list':{
        'args':{},
      'description':'Get a list of all gids.'
      },

      'gids_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      'user_list':{
        'args':{},
      'description':'Get a list of all users.'
      },

      'users_list':{
        'args':{},
      'description':'Get a list of all users.'
      },

      'group_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      'groups_list':{
        'args':{},
      'description':'Get a list of all groups.'
      },

      #INFO METHODS
      'user_info':{
        'args':{
          'user':username
        },
      'description':'Fetch info for a specified user.'
      },

      'users_info':{
        'args':{
          'users':usernames
        },
      'description':'Fetch info for a specified series of users.'
      },

      'uid_info':{
        'args':{
          'uid':uid
        },
      'description':'Fetch info for a specified uid.'
      },

      'uids_info':{
        'args':{
          'uids':uids
        },
      'description':'Fetch info for a specified series of uids.'
      },

      'group_info':{
        'args':{
          'group':group
        },
      'description':'Fetch info for a specified group.'
      },

      'groups_info':{
        'args':{
          'groups':groups
        },
      'description':'Fetch info for a specified series of groups.'
      },

      'gid_info':{
        'args':{
          'gid':gid
        },
      'description':'Fetch info for a specified gid.'
      },

      'gids_info':{
        'args':{
          'gids':gids
        },
      'description':'Fetch info for a specified series of gids.'
      },

      #INVENTORY METHODS
      'user_inventory':{
        'args':{},
      'description':'Get user info for all users.'
      },

      'users_inventory':{
        'args':{},
      'description':'Get user info for all users.'
      },

      'group_inventory':{
        'args':{},
      'description':'Get group info for all groups.'
      },

      'groups_inventory':{
        'args':{},
      'description':'Get group info for all groups.'
      },

      #CONVERSION METHODS
      'user_to_uid':{
        'args':{
          'user':username
        },
      'description':'Convert a username to a matching uid.'
      },

      'users_to_uids':{
        'args':{
          'users':usernames
        },
      'description':'Convert a series of usernames to a list of matching uids.'
      },

      'uid_to_user':{
        'args':{
          'uid':uid
        },
      'description':'Convert a uid to a username.'
      },

      'uids_to_users':{
        'args':{
          'uids':uids
        },
      'description':'Convert a series of uids to a list of matching usernames.'
      },

      'group_to_gid':{
        'args':{
          'groups':groups
        },
      'description':'Convert a group to a matching gid.'
      },

      'groups_to_gids':{
        'args':{
          'groups':groups
        },
      'description':'Converts a series of groups to a list of matching gids.'
      },

      'gid_to_group':{
        'args':{
          'gid':gid
        },
      'description':'Converts a gids to a matching groupname.'
      },

      'gids_to_groups':{
        'args':{
          'gids':gids
        },
      'description':'Converts a series of gids to a list of matching groupnames.'
      }

    }

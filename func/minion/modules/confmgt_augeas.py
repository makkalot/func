#!/usr/bin/env python

#
# Copyright 2008
# Louis Coilliot <louis.coilliot@wazemmes.org>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module
from os import path as ospath,getenv as osgetenv 
from time import strftime

def lstripstr(the_string,the_prefix):
    """Return a copy of the string with leading prefix removed."""
    if the_string.startswith(the_prefix):
        return the_string[len(the_prefix):]
    return the_string

def recurmatch(aug, path):
    """Generate all tree children of a start path."""
    #Function adapted from test_augeas.py in python-augeas-0.3.0
    #Original Author: Harald Hoyer <harald@redhat.com>"""
    if path:
        if path != "/":
            val = aug.get(path)
            if val:
                yield (path, val)
            # here is the modification to (almost) match augtool print behavior:
            else:
                yield (path, '(none)')
            # end of modification

        m = []
        if path != "/":
            aug.match(path)
        for i in m:
            for x in recurmatch(aug, i):
                yield x
        else:
            for i in aug.match(path + "/*"):
                for x in recurmatch(aug, i):
                    yield x


class confMgtAug(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Manage parameters in configuration files, with the help of Augeas."


    def get(self,entryPath,param='',hierarchy='/files'):
        """Get a value for a config. parameter in a config. file,
with the help of Augeas, a configuration API (cf http://augeas.net)"""
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)
        # yes, entryPath.rstrip('/')+'/' is really needed (i.e. entryPath=/)
        path=(hierarchy+entryPath.rstrip('/')+'/'+param).rstrip('/')
        try:
            matchtest=aug.match(path) 
        except Exception, e: return str(e)
        if matchtest:
            try:
                pvalue=aug.get(path) 
                #aug.close()
            except Exception, e: return str(e)
        else:
            # The node doesn't exist
            pvalue='(o)'

        if not pvalue:
            # The node doesn't have a value
            pvalue='(none)'

        return { 'path': entryPath, 'parameter': param, 'value': pvalue, 'hierarchy': hierarchy }


    def set(self,entryPath,param='',pvalue='',hierarchy='/files'):
        """Set/change a value for a config. parameter in a config. file,
with the help of Augeas, a configuration API (cf http://augeas.net)"""
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)

        path=(hierarchy+entryPath.rstrip('/')+'/'+param).rstrip('/')

        try:
            aug.set(path,pvalue)
        except Exception, e: return str(e)
        # Here is a little workaround for a bug in save for augeas.
        # In the future this won't be necessary anymore.
        try:
            aug.save()
        except:
            pass
        # End of workaround
        try:
            aug.save()
        except Exception, e: return str(e)

        try:
            pvalue=aug.get(path)
            #aug.close()
        except Exception, e: return str(e)

        return { 'path': entryPath, 'parameter': param, 'value': pvalue, 'hierarchy': hierarchy  }


    def match(self,entryPath,param='',pvalue='',hierarchy='/files'):
        """Match a value for a config. parameter in a config. file,
with the help of Augeas, a configuration API (cf http://augeas.net)"""
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)

        path=(hierarchy+entryPath.rstrip('/')+'/'+param).rstrip('/')
        childpath=(hierarchy+entryPath.rstrip('/')+'/*/'+param).rstrip('/')

        if pvalue:
            try:
                matchlist = [ ospath.dirname(lstripstr(item,'/files')) for item in aug.match(path) + aug.match(childpath) if ( aug.get(item) == pvalue ) ]
                #aug.close()
            except Exception, e: return str(e)
        else:
            try:
                matchlist = [ ospath.dirname(lstripstr(item,'/files')) for item in aug.match(path) + aug.match(childpath) ]
                #aug.close()
            except Exception, e: return str(e)
        return matchlist


    def ls(self,entryPath,hierarchy='/files'):
        """List the direct children of an entry in a config. file,
with the help of Augeas, a configuration API (cf http://augeas.net)"""
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)
        path=hierarchy+entryPath.rstrip('/')+'/*'
        # We can't use a dict here because the same key can appear many times.
        nodes=[]
        try:
            for match in aug.match(path):
                pvalue=aug.get(match)
                if not pvalue:
                    pvalue='(none)'
                nodes.append([ospath.basename(match),pvalue])
        except Exception, e: return str(e)
       
        #try:
        #    aug.close()
        #except Exception, e: return str(e)

        return { 'path': entryPath, 'nodes': nodes, 'hierarchy': hierarchy }


    # print is a reserved word so we use printconf instead
    def printconf(self,entryPath,hierarchy='/files'):
        """Print all tree children nodes from the path provided,
with the help of Augeas, a configuration API (cf http://augeas.net)""" 
        path=hierarchy+entryPath
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)
        matches = recurmatch(aug, path)
        # Here we loose the benefit of the generator function:
        return { 'path': entryPath, 'nodes':[ [lstripstr(p,'/files'),attr] for (p,attr) in matches ], 'hierarchy': hierarchy }



    def rm(self,entryPath,param='',hierarchy='/files'):
        """Delete a parameter (and all its children) in a config. file,
with the help of Augeas, a configuration API (cf http://augeas.net)"""
        try:
            from augeas import Augeas
            aug=Augeas()
        except Exception, e: return str(e)

        path=(hierarchy+entryPath.rstrip('/')+'/'+param).rstrip('/')
        
        try:
            result=aug.remove(path)
            #aug.close()
        except Exception, e: return str(e)
        # Here is a little workaround for a bug in save for augeas.
        # In the future this should not be necessary anymore. 
        try:
            aug.save()
        except:
            pass
        # End of workaround
        try:
            aug.save()
        except Exception, e: return str(e)
        if result == -1:
            msg = 'Invalid node'
        else:
            msg = repr(result)+' node(s) removed.'
        return msg 

    def getenv(self,varname):
        """Get an environment variable."""
        varvalue=osgetenv(varname)
        if varvalue == None:
            varvalue = '(none)'
        return { varname : varvalue  }

    def backup(self,entryPath):
        """Backup a file with a timestamp. Cautious before applying modifications on a configuration file."""
        try:
            import shutil 
        except Exception, e: return str(e)
        backupPath=entryPath+'.'+strftime('%Y%m%d-%H%M')
        try:
            if not ospath.exists(backupPath):
                shutil.copy(entryPath, backupPath)
                msg='File '+entryPath+' backed up to '+ backupPath
            else:
                msg='Backup file '+backupPath+' already exists'
        except (OSError, IOError), e: return str(e)
        return msg 
    

    def register_method_args(self):
        """
        Implementing the method arg getter
        """

        return {
                'get':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'param':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The target parameter in the config. file'
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"Get a value for a config. parameter in a config. file."
                    },
                'set':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'param':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The target parameter in the config. file'
                            },
                        'pvalue':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The value to set for the parameter in the config. file'
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"Set/change a value for a config. parameter in a config. file."
                    },
                'match':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'param':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The target parameter in the config. file'
                            },
                        'pvalue':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The value to set for the parameter in the config. file'
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"Match a value for a config. parameter in a config. file."
                    },
                'ls':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"List the direct children of an entry in a config. file."
                    },
                'printconf':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"Print all tree children nodes from the path provided."
                    },
                'rm':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file (fs or Augeas path)',
                            },
                        'param':{
                            'type':'string',
                            'optional':True,
                            'default':'',
                            'description':'The target parameter in the config. file'
                            },
                        'hierarchy':{
                            'type':'string',
                            'optional':True,
                            'default':'/files',
                            'description':'The augeas base path hierarchy'
                            }
                        },
                    'description':"Delete a parameter (and all its children) in a config. file."
                    },
                'getenv':{
                    'args':{
                        'varname':{
                            'type':'string',
                            'optional':False,
                            'description':'The name of the environment variable to get',
                            }
                        },
                    'description':"Get an environment variable."
                    },
                'backup':{
                    'args':{
                        'entryPath':{
                            'type':'string',
                            'optional':False,
                            'description':'The path to the config. file',
                            }
                        },
                    'description':"Backup a file with a timestamp."
                    }
                }


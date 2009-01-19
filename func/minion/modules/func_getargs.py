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

from platform import python_version_tuple as pv
import sys
import inspect
import func_module

class getArgs(func_module.FuncModule): 
    version = "0.0.1" 
    api_version = "0.0.1" 
    description = "Get args of methods of the class in a func module"

    def get(self, modname, methodname): 
        """Returns a list of args for the specified method in the class of a func module.
        This is useful when register_method_args is not defined (or not properly)
        """ 
        vtuple=pv()
        pyver=vtuple[0]+'.'+vtuple[1]
        sys.path.append('/usr/lib/python'+pyver+'/site-packages/func/minion/modules/') 
        the_mod=__import__(modname)

        name,data=inspect.getmembers(the_mod, inspect.isclass)[0] 
        the_class=modname+'.'+name

        c=getattr(the_mod, name)

        return [ arg for arg in inspect.getargspec(eval('c.'+methodname))[0] if arg != 'self' ]


    def register_method_args(self):
        """Implementing the method arg getter"""
        return {
            'get':{
                'args':{
                    'modname':{
                        'type':'string',
                        'optional':False,
                        'description':'The module name you want to check'
                        },
                    'methodname':{
                        'type':'string',
                        'optional':False,
                        'description':'The method name you want to check'
                        }
                    },
                'description':'Returns a list with the args of the method you checked'
                    }
                }


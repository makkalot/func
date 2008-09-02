# Copyright 2007, Red Hat, Inc
# James Bowes <jbowes@redhat.com>
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
Abitrary command execution module for func.
"""

import func_module
from func.minion import sub_process

class Command(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.2"
    description = "Works with shell commands."

    def run(self, command, env=None):
        """
        Runs a command, returning the return code, stdout, and stderr as a tuple.
        NOT FOR USE WITH INTERACTIVE COMMANDS.
        """

        
        if env:
            cmdref = sub_process.Popen(command.split(), stdout=sub_process.PIPE,
                                       stderr=sub_process.PIPE, shell=False, 
                                       close_fds=True, env=env)
        else:
            cmdref = sub_process.Popen(command.split(), stdout=sub_process.PIPE,
                                       stderr=sub_process.PIPE, shell=False, close_fds=True)
        data = cmdref.communicate()
        return (cmdref.returncode, data[0], data[1])

    def exists(self, command):
        """
        Checks to see if a command exists on the target system(s).
        """
        import os

        if os.access(command, os.X_OK):
            return True
        return False

    def register_method_args(self):
        """
        The argument export method
        """
        #common type in both descriptions
        command = {
                'type':'string',
                'optional':False,
                'description':'The command that is going to be used',
                }

        return {
                'run':{
                    'args':{
                        'command':command
                        },
                    'description':'Run a specified command'
                    },
                'exists':{
                    'args':{
                        'command':command
                        },
                    'description':'Check if specific command exists'
                    }
                }

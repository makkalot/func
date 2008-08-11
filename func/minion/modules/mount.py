##
## Mount manager
##
## Copyright 2007, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import os
import func_module
from func.minion import sub_process


class MountModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Mounting, unmounting and getting information on mounted filesystems."

    def list(self):
        cmd = sub_process.Popen(["/bin/cat", "/proc/mounts"], executable="/bin/cat", stdout=sub_process.PIPE, shell=False)
        data = cmd.communicate()[0]
        
        mounts = []
        lines = [l for l in data.split("\n") if l] #why must you append blank crap?

        for line in lines:
            curmount = {}
            tokens = line.split()
            curmount['device'] = tokens[0]
            curmount['dir'] = tokens[1]
            curmount['type'] = tokens[2]
            curmount['options'] = tokens[3]
            mounts.append(curmount)

        return mounts

    def mount(self, device, dir, type="auto", options=None, createdir=False):
        cmdline = ["/bin/mount", "-t", type]
        if options: 
            cmdline.append("-o")
            cmdline.append(options)
        cmdline.append(device)
        cmdline.append(dir)
        if createdir:
            try:
                os.makedirs(dir)
            except:
                return False
        cmd = sub_process.Popen(cmdline, executable="/bin/mount", stdout=sub_process.PIPE, shell=False)
        if cmd.wait() == 0:
            return True
        else:
            return False
        
    def umount(self, dir, killall=False, force=False, lazy=False):
        # succeed if its not mounted
        if not os.path.ismount(dir):
            return True

        if killall:
            cmd = sub_process.Popen(["/sbin/fuser", "-mk", dir], executable="/sbin/fuser", stdout=sub_process.PIPE, shell=False)
            cmd.wait()

        cmdline = ["/bin/umount"]
        if force:
            cmdline.append("-f")
        if lazy:
            cmdline.append("-l")
        cmdline.append(dir)

        cmd = sub_process.Popen(cmdline, executable="/bin/umount", stdout=sub_process.PIPE, shell=False)
        if cmd.wait() == 0:
            return True
        else:
            return False

    def inventory(self, flatten=True):
        return self.list()


    def register_method_args(self):
        """
        Implementing the method arg getter
        """

        return{
                'list':{'args':{},
                    'description':"Listing the mounting points"
                    },
                'mount':{
                    'args':{
                        'device':{
                            'type':'string',
                            'optional':False,
                            'description':'The device to be mounted',
                            },
                        'dir':{
                            'type':'string',
                            'optional':False,
                            'description':'The directory which will the device mounted under'
                            },
                        'type':{
                            'type':'string',
                            'optional':True,
                            'default':'auto',
                            'description':'The type of the mount'
                            },
                        'options':{
                            'type':'list',
                            'optional':True,
                            'description':"Some extra options to be added to mount command"
                            },
                        'createdir':{
                            'type':'boolean',
                            'optional':True,
                            'description':'Check if you want to create the dir place if not exist'
                            }
                        },
                    'description':"Mount the specified device under some directory"
                    },
                'umount':{'args':{
                    'dir':{
                        'type':'string',
                        'optional':False,
                        'description':'The directory which will be unmounted'
                         },
                    'killall':{
                        'type':'boolean',
                        'optional':True,
                        'description':'The killal option'
                        },
                    'force':{
                        'type':'boolean',
                        'optional':True,
                        'description':'To force operation check it'
                        },
                    'lazy':{
                        'type':'boolean',
                        'optional':True,
                        'description':'The lazy option'
                        }
                    },
                    'description':"Unmounting the specified directory."
                    },
                'inventory':{'args':{
                    'flatten':{
                        'type':'boolean',
                        'optional':True,
                        'description':"To flatten check."
                        }
                    },
                    'description':"Th einventory part of that module"
                    }
                }

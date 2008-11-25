## func
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##

import codes
import func_module

import sub_process
import os

class Service(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Allows for service control via func."

    def __command(self, service_name, command):
	
	service_name = service_name.strip() # remove useless spaces

        filename = os.path.join("/etc/rc.d/init.d/",service_name)
        if os.path.exists(filename):
            return sub_process.call(["/sbin/service", service_name, command], close_fds=True)
        else:
            raise codes.FuncException("Service not installed: %s" % service_name)

    def start(self, service_name):
        return self.__command(service_name, "start")

    def stop(self, service_name):
        return self.__command(service_name, "stop")

    def restart(self, service_name):
        return self.__command(service_name, "restart")

    def reload(self, service_name):
        return self.__command(service_name, "reload")

    def status(self, service_name):
        return self.__command(service_name, "status")

    def inventory(self):
        return {
            "running" : self.get_running(),
            "enabled" : self.get_enabled()
        }

    def get_enabled(self):
        """
        Get the list of services that are enabled at the various runlevels.  Xinetd services
        only provide whether or not they are running, not specific runlevel info.
        """

        chkconfig = sub_process.Popen(["/sbin/chkconfig", "--list"], stdout=sub_process.PIPE, close_fds=True)
        data = chkconfig.communicate()[0]
        results = []
        for line in data.split("\n"):
            if line.find("0:") != -1:
               # regular services
               tokens = line.split()
               results.append((tokens[0],tokens[1:]))
            elif line.find(":") != -1 and not line.endswith(":"):
               # xinetd.d based services
               tokens = line.split()
               tokens[0] = tokens[0].replace(":","")
               results.append((tokens[0],tokens[1]))
        return results

    def get_running(self):
        """
        Get a list of which services are running, stopped, or disabled.
        """
        chkconfig = sub_process.Popen(["/sbin/service", "--status-all"], stdout=sub_process.PIPE, close_fds=True)
        data = chkconfig.communicate()[0]
        results = []
        for line in data.split("\n"):
            if line.find(" is ") != -1:
                tokens = line.split()
                results.append((tokens[0], tokens[-1].replace("...","")))
        return results

    def register_method_args(self):
        """
        Implementing the argument getter
        """

        #service_name options they are same so use only one
        service_name =  {
                'type':'string',
                'optional':False,
                'description':'The name of the running services',
                'validator':'^[a-z\-\_0-9]+$'}

        return {
                'get_running':{'args':{}},
                'get_enabled':{'args':{}},
                'inventory':{'args':{}},
                'status':{'args':{
                    'service_name':service_name,   
                    },
                    'description':'Getting the status of the service_name'
                    },
                'reload':{'args':{'service_name':service_name}},
                'restart':{'args':{'service_name':service_name}},
                'stop':{'args':{'service_name':service_name}},
                'start':{'args':{'service_name':service_name}},


                }

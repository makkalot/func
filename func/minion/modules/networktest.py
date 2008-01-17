# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import func_module
from codes import FuncException

import sub_process

class NetworkTest(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Defines various network testing tools."

    def ping(self, *args):
        if '-c' not in args:
            raise(FuncException("You must define a count with -c!"))
        return self.__run_command('/bin/ping', self.__args_to_list(args))

    def netstat(self, *args):
        return self.__run_command('/bin/netstat',
                                  self.__args_to_list(args))

    def traceroute(self, *args):
         return self.__run_command('/bin/traceroute',
                                   self.__args_to_list(args))

    def dig(self, *args):
         return self.__run_command('/usr/bin/dig',
                                   self.__args_to_list(args))

    def isportopen(self, host, port):
        # FIXME: the return api here needs some work... -akl
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        timeout = 3.0
        sock.settimeout(timeout)
        try:
            sock.connect((host, int(port)))
        except socket.error, e:
            sock.close()
            return [1, ("connection to %s:%s failed" % (host, port), "%s" % e)]
        except socket.timeout:
            sock.close()
            return [2, ("connection to %s:%s timed out after %s seconds" % (host, port, timeout))]

        sock.close()
        return [0, "connection to %s:%s succeeded" % (host, port)]

    def __args_to_list(self, args):
        return [arg for arg in args]

    def __run_command(self, command, opts=[]):
        full_cmd = [command] + opts
        cmd = sub_process.Popen(full_cmd, stdout=sub_process.PIPE)
        return [line for line in cmd.communicate()[0].split('\n')]

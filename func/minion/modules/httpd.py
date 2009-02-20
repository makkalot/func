#
# Copyright 2009
# John Eckersberg <jeckersb@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import func_module

class ServerStatusUnavailable(Exception):
    pass

class MalformedServerStatus(Exception):
    pass

class Httpd(func_module.FuncModule):

    # Update these if need be.
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Gather information from and manipulate Apache HTTPD"

    import service
    import urllib2

    HTTPD_SERVICE_NAME = 'httpd'

    def server_status(self, host="localhost", request="server-status", ssl=False):
        """
        Returns a dictionary representing output from mod_status.

        :Parameters:
          - `host`: the hostname to query against.
          - `request`: the location of the mod_status handler.
          - `ssl`: whether or not to use HTTPS.
        """
        if ssl:
            proto = "https"
        else:
            proto = "http"

        try:
            status = self.urllib2.urlopen("%s://%s/%s?auto" % (proto, host, request)).read()
        except Exception, e:
            raise ServerStatusUnavailable, e

        result = {}
        for line in status.split('\n'):
            if not line:
                continue
            try:
                k,v = [foo.strip() for foo in line.split(':')]
            except ValueError:
                raise MalformedServerStatus
            result[k] = v

        return result

    def graceful(self):
        """
        Issue a graceful restart to the httpd service.
        """
        return self.service.Service()._Service__command(Httpd.HTTPD_SERVICE_NAME, 'graceful')


    def register_method_args(self):
        return {
                'graceful':{
                    'args':{},
                    'description':"Issue a graceful restart to the httpd service."
                    },
                'server_status':{
                    'args': {'host':{
                                'type':'string',
                                'optional':True,
                                'default':"localhost",
                                'description':'hostname of the http server to check status of'
                              },
                             'request':{
                                 'type':'string',
                                 'optional':True,
                                 'default':'server-status',
                                 'description':'path to the url server status page'
                                 },
                             'ssl': {
                                 'type':'boolean',
                                 'optional':True,
                                 'default':False,
                                 'description':'True if the server is an ssl server'
                                 }
                             },
                                 

                    'description':'Check the httpd status on a server'
                    }
                }

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Copyright 2005 Dan Williams <dcbw@redhat.com> and Red Hat, Inc.
# Modifications by Seth Vidal - 2007

import sys
import socket
import SimpleXMLRPCServer
from func import SSLCommon
import OpenSSL
import SocketServer


class AuthedSimpleXMLRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

    # For some reason, httplib closes the connection right after headers
    # have been sent if the connection is _not_ HTTP/1.1, which results in
    # a "Bad file descriptor" error when the client tries to read from the socket
    protocol_version = "HTTP/1.1"

    def setup(self):
        """
        We need to use socket._fileobject Because SSL.Connection
        doesn't have a 'dup'. Not exactly sure WHY this is, but
        this is backed up by comments in socket.py and SSL/connection.c
        """
        self.connection = self.request # for doPOST
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

    def do_POST(self):
        self.server._this_request = (self.request, self.client_address)
        try:
            SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.do_POST(self)
        except socket.timeout:
            pass
        except (socket.error, OpenSSL.SSL.SysCallError), e:
            print "Error (%s): socket error - '%s'" % (self.client_address, e)


class BaseAuthedXMLRPCServer(SocketServer.ThreadingMixIn):
    def __init__(self, address, authinfo_callback=None):
        self.allow_reuse_address = 1
        self.logRequests = 1
        self.authinfo_callback = authinfo_callback

        self.funcs = {}
        self.instance = None

    def get_authinfo(self, request, client_address):
        print 'down here'
        if self.authinfo_callback:
            return self.authinfo_callback(request, client_address)
        return None


class AuthedSSLXMLRPCServer(BaseAuthedXMLRPCServer, SSLCommon.BaseSSLServer, SimpleXMLRPCServer.SimpleXMLRPCServer):
    """ Extension to allow more fine-tuned SSL handling """

    def __init__(self, address, pkey, cert, ca_cert, authinfo_callback=None, timeout=None):
        BaseAuthedXMLRPCServer.__init__(self, address, authinfo_callback)
        SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, address, AuthedSimpleXMLRPCRequestHandler)
        SSLCommon.BaseSSLServer.__init__(self, address, AuthedSimpleXMLRPCRequestHandler, pkey, cert, ca_cert, timeout=timeout)



class AuthedXMLRPCServer(BaseAuthedXMLRPCServer, SSLCommon.BaseServer, SimpleXMLRPCServer.SimpleXMLRPCServer):

    def __init__(self, address, authinfo_callback=None):
        BaseAuthedXMLRPCServer.__init__(self, address, authinfo_callback)
        SSLCommon.BaseServer.__init__(self, address, AuthedSimpleXMLRPCRequestHandler)


###########################################################
# Testing stuff
###########################################################

class ReqHandler:
    def ping(self, callerid, trynum):
        print 'clearly not'
        print callerid
        print trynum
        return "pong %d / %d" % (callerid, trynum)

class TestServer(AuthedSSLXMLRPCServer):
    """
    SSL XMLRPC server that authenticates clients based on their certificate.
    """

    def __init__(self, address, pkey, cert, ca_cert):
        AuthedSSLXMLRPCServer.__init__(self, address, pkey, cert, ca_cert, self.auth_cb)

    def _dispatch(self, method, params):
        if method == 'trait_names' or method == '_getAttributeNames':
            return dir(self)
        # if we have _this_request then we get the peer cert from it
        # handling all the authZ checks in _dispatch() means we don't even call the method
        # for whatever it wants to do and we have the method name.

        if hasattr(self, '_this_request'):
            r,a = self._this_request
            p = r.get_peer_certificate()
            print dir(p)
            print p.get_subject()
        else:
            print 'no cert'

        return "your mom"

    def auth_cb(self, request, client_address):
        peer_cert = request.get_peer_certificate()
        return peer_cert.get_subject().CN


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: python AuthdXMLRPCServer.py key cert ca_cert"
        sys.exit(1)

    pkey = sys.argv[1]
    cert = sys.argv[2]
    ca_cert = sys.argv[3]

    print "Starting the server."
    server = TestServer(('localhost', 51234), pkey, cert, ca_cert)
    h = ReqHandler()
    server.register_instance(h)
    server.serve_forever()

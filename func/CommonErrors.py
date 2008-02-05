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

from exceptions import Exception

def canIgnoreSSLError(e):
    """
    Identify common network errors that mean we cannot connect to the server
    """

    # This is a bit complicated by the fact that different versions of
    # M2Crypto & OpenSSL seem to return different error codes for the
    # same type of error
    s = "%s" % e
    if e[0] == 104:     # Connection refused
        return True
    elif e[0] == 111:   # Connection reset by peer
        return True
    elif e[0] == 61:    # Connection refused
        return True
    elif e[0] == 54:    # Connection reset by peer
        return True
    elif s == "no certificate returned":
        return True
    elif s == "wrong version number":
        return True
    elif s == "unexpected eof":
        return True

    return False


def canIgnoreSocketError(e):
    """
    Identify common network errors that mean we cannot connect to the server
    """

    try:
        if e[0] == 111:     # Connection refused
            return True
        elif e[0] == 104:   # Connection reset by peer
            return True
        elif e[0] == 61:    # Connection refused
            return True
    except IndexError:
        return True

    return False

class Func_Client_Exception(Exception):
    def __init__(self, value=None):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return "%s" %(self.value,)


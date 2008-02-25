# -*- coding: utf-8 -*-
#
# Copyright © 2008  Red Hat, Inc. All rights reserved.
#
# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.  You should have
# received a copy of the GNU General Public License along with this program; if
# not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth
# Floor, Boston, MA 02110-1301, USA. Any Red Hat trademarks that are
# incorporated in the source code or documentation are not subject to the GNU
# General Public License and may only be used or replicated with the express
# permission of Red Hat, Inc.
#
# Author(s): Luke Macken <lmacken@redhat.com>

"""
This module contains an Identity Provider used by TurboGears to authenticate
users against PAM.  It utilizes the pam.py module written by Chris AtLee.
http://pypi.python.org/pypi/pam/0.1.2

To utilize, simply define the following in your app.cfg:

    identity.provider = 'pam'
"""

import pam
import logging

from turbogears import identity

log = logging.getLogger(__name__)

class User(object):
    def __init__(self, username):
        self.user_id = username
        self.user_name = username
        self.display_name = username

class Identity:

    def __init__(self, visit_key=None, username=None):
        self.username = username
        self.visit_key = visit_key
        self.expired = False

    def _get_user(self):
        try:
            return self._user
        except AttributeError:
            return None
        if not self.visit_key:
            self._user = None
            return None
        self._user = User(self.username)
        return self._user
    user = property(_get_user)

    def _get_anonymous(self):
        return not self.username
    anonymous = property(_get_anonymous)


    def logout(self):
        if not self.visit_key:
            return
        self.expired = True
        anon = Identity(None,None)
        identity.set_current_identity(anon)


class PAMIdentityProvider:
    """
        IdentityProvider that authenticates users against PAM.
    """
    users = {}

    def validate_identity(self, user_name, password, visit_key):
        if not self.validate_password(user_name, password):
            log.warning("Invalid password for %s" % user_name)
            return None
        log.info("Login successful for %s" % user_name)
        user = Identity(visit_key, user_name)
        self.users[visit_key] = user
        return user

    def validate_password(self,user_name, password):
        return pam.authenticate(user_name, password)

    def load_identity(self, visit_key):
        if self.users.has_key(visit_key):
            if self.users[visit_key].expired:
                del self.users[visit_key]
                return None
            return self.users[visit_key]
        return None

    def anonymous_identity(self):
        return Identity(None)

    def create_provider_model(self):
        pass

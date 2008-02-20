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

import logging

from model import *
from turbogears.identity.saprovider import *

log = logging.getLogger(__name__)

visit_identity_class = None

class PAMIdentityProvider(SqlAlchemyIdentityProvider):
    """
        IdentityProvider that authenticates users against PAM.
    """
    def validate_identity(self, user_name, password, visit_key):
        if not self.validate_password(user_name, password):
            log.warning("Invalid password for %s" % user_name)
            return None

        log.info("Login successful for %s" % user_name)

        try:
            link = VisitIdentity.by_visit_key(visit_key)
            #link.user_id = user.id
            log.debug("Found visit!")
        except Exception, e:
            log.debug("Cannot find visit")
            link = VisitIdentity(visit_key=visit_key, user_id=user_name)
            print "Exception: %s" % str(e)

        return SqlAlchemyIdentity(visit_key, user)

    def validate_password(self,user_name, password):
        import pam
        log.debug("Authenticating user '%s' against PAM" % user_name)
        assert pam
        return pam.authenticate(user_name, password)

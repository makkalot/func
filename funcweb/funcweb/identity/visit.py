from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import class_mapper

from turbogears import config
from turbogears.util import load_class
from turbogears.visit.api import BaseVisitManager, Visit
from turbogears.database import get_engine, metadata, session, mapper

import logging
log = logging.getLogger(__name__)


class FuncWebVisitManager(BaseVisitManager):

    def __init__(self, timeout):
        super(FuncWebVisitManager,self).__init__(timeout)
        self.visits = {}

    def create_model(self):
        pass

    def new_visit_with_key(self, visit_key):
        log.debug("new_visit_with_key(%s)" % visit_key)
        created = datetime.now()
        visit = Visit(visit_key, True)
        visit.visit_key = visit_key
        visit.created = created
        visit.expiry = created + self.timeout
        self.visits[visit_key] =  visit
        log.debug("returning %s" % visit)
        return visit

    def visit_for_key(self, visit_key):
        '''
        Return the visit for this key or None if the visit doesn't exist or has
        expired.
        '''
        log.debug("visit_for_key(%s)" % visit_key)
        if not self.visits.has_key(visit_key):
            return None
        visit = self.visits[visit_key]
        if not visit:
            return None
        now = datetime.now(visit.expiry.tzinfo)
        if visit.expiry < now:
            return None
        visit.is_new = False
        log.debug("returning %s" % visit)
        return visit

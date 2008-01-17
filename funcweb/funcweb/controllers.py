import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash
from func.overlord.client import Client

class Root(controllers.RootController):

    @expose(template="funcweb.templates.minions")
    def minions(self):
        """ Return a list of our minions """
        fc = Client("*")
        return dict(minions=fc.system.list_methods())

    @expose(template="funcweb.templates.minion")
    def minion(self, name):
        """ View all modules for a given minion """
        fc = Client(name)
        return dict(modules=fc.system.list_modules())

    index = minions

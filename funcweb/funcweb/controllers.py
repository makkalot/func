import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash
from func.overlord.client import Client

class Root(controllers.RootController):

    @expose(template="funcweb.templates.minions")
    def minions(self):
        """ Return a list of our minions """
        fc = Client("*")
        return dict(minions=fc.system.list_methods(), widgets=[])

    @expose(template="funcweb.templates.minion")
    def minion(self, name, module=None, method=None):
        """ View all modules for a given minion """
        fc = Client(name)
        if not module: # list all modules
            modules = fc.system.list_modules()
            return dict(modules=modules)
        else: # a module is specified
            if method: # minion.module.method specified; bring up execution form
                return dict(minion=name, module=module, method=method,
                            tg_template="funcweb.templates.method")
            else: # return a list of methods for specified module
                modules = getattr(fc, module).list_methods()
                return dict(modules=modules, module=module,
                            tg_template="funcweb.templates.module")

    index = minions # start with our minion view, for now

    @expose(template="funcweb.templates.run")
    def run(self, minion="*", module=None, method=None, arguments=None):
        fc = Client(minion)
        if arguments:
            results = getattr(getattr(fc, module), method)(*arguments.split())
        else:
            results = getattr(getattr(fc, module), method)()
        cmd = "%s.%s.%s(%s)" % (minion, module, method, arguments)
        return dict(cmd=cmd, results=results)

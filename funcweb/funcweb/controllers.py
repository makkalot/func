import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect
from func.overlord.client import Overlord, Minions

class Root(controllers.RootController):

    @expose(template="funcweb.templates.minions")
    @identity.require(identity.not_anonymous())
    def minions(self, glob='*'):
        """ Return a list of our minions that match a given glob """
        return dict(minions=Minions(glob).get_all_hosts())

    index = minions # start with our minion view, for now

    @expose(template="funcweb.templates.minion")
    @identity.require(identity.not_anonymous())
    def minion(self, name, module=None, method=None):
        """ Display module or method details for a specific minion.

        If only the minion name is given, it will display a list of modules
        for that minion.  If a module is supplied, it will display a list of
        methods.  If a method is supplied, it will display a method execution
        form.
        """
        fc = Overlord(name)
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


    @expose(template="funcweb.templates.run")
    @identity.require(identity.not_anonymous())
    def run(self, minion="*", module=None, method=None, arguments=''):
        fc = Overlord(minion)
        results = getattr(getattr(fc, module), method)(*arguments.split())
        cmd = "%s.%s.%s(%s)" % (minion, module, method, arguments)
        return dict(cmd=cmd, results=results)

    @expose(template="funcweb.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):
        from cherrypy import request, response
        if not identity.current.anonymous \
            and identity.was_login_attempted() \
            and not identity.get_identity_errors():
            raise redirect(forward_url)

        forward_url=None
        previous_url= request.path

        if identity.was_login_attempted():
            msg=_("The credentials you supplied were not correct or "
                   "did not grant access to this resource.")
        elif identity.get_identity_errors():
            msg=_("You must provide your credentials before accessing "
                   "this resource.")
        else:
            msg=_("Please log in.")
            forward_url= request.headers.get("Referer", "/")

        response.status=403
        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)

    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

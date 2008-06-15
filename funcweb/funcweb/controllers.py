import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect
from func.overlord.client import Overlord, Minions
from turbogears import mochikit

class Root(controllers.RootController):

    @expose(template="funcweb.templates.minions")
    #@identity.require(identity.not_anonymous())
    def minions(self, glob='*'):
        """ Return a list of our minions that match a given glob """
        return dict(minions=Minions(glob).get_all_hosts())

    index = minions # start with our minion view, for now

    @expose(template="funcweb.templates.minion")
    #@identity.require(identity.not_anonymous())
    def minion(self, name="*", module=None, method=None):
        """ Display module or method details for a specific minion.

        If only the minion name is given, it will display a list of modules
        for that minion.  If a module is supplied, it will display a list of
        methods.  If a method is supplied, it will display a method execution
        form.
        """
        fc = Overlord(name)
        if not module: # list all modules
            #just list those who have get_method_args
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
    #@identity.require(identity.not_anonymous())
    def run(self, minion="*", module=None, method=None, arguments=''):
        fc = Overlord(minion)
        results = getattr(getattr(fc, module), method)(*arguments.split())
        cmd = "%s.%s.%s(%s)" % (minion, module, method, arguments)
        return dict(cmd=cmd, results=results)


    @expose(template="funcweb.templates.method_args")
    #@identity.require(identity.not_anonymous())
    def method_display(self,minion=None,module=None,method=None):
    
        fc = Overlord(minion)
        method_args = getattr(fc,module).get_method_args()
        
        if not method_args.values():
            print "Not registered method here"
            return dict(minion_form = None)

        print method
        the_one = method_args[minion][method]['args']
        if the_one:

            from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory
            wlist_object = WidgetListFactory(the_one)
            wlist_object=wlist_object.get_widgetlist_object()
            minion_form =RemoteFormFactory(wlist_object).get_remote_form()
            #minion_form = RemoteFormAutomation(wlist_object)
            #print minion_form.fields

            #print minion_form
            return dict(minion_form=minion_form)
        else:
            return dict(minion_form = None)


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
        
    @expose(allow_json=True)
    def post_form(self,**kw):
        """
        Data processing part
        """
        return "I got that data from the remote minion form :<br/>%r"%kw


    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

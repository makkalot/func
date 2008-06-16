import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect
from func.overlord.client import Overlord, Minions
from turbogears import mochikit
from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory

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
            display_modules = []
            #FIXME slow really i know !
            for module in modules.itervalues():
                for mod in module:
                    #if it is not empty
                    if getattr(fc,mod).get_method_args()[name]:
                        display_modules.append(mod)
            modules = {}
            modules[name]=display_modules
            
            return dict(modules=modules)
        else: # a module is specified
            if method: # minion.module.method specified; bring up execution form
                return dict(minion=name, module=module, method=method,
                            tg_template="funcweb.templates.method")
            else: # return a list of methods for specified module
                modules = getattr(fc, module).list_methods()
                return dict(modules=modules, module=module,
                            tg_template="funcweb.templates.module")


    @expose(template="funcweb.templates.method_args")
    #@identity.require(identity.not_anonymous())
    def method_display(self,minion=None,module=None,method=None):
   
        fc = Overlord(minion)
        method_args = getattr(fc,module).get_method_args()
        
        if not method_args.values():
            print "Not registered method here"
            return dict(minion_form = None,minion=minion,module=module,method=method)

        the_one = method_args[minion][method]['args']
        if the_one:
            wlist_object = WidgetListFactory(the_one,minion=minion,module=module,method=method)
            wlist_object = wlist_object.get_widgetlist_object()
            #minion_form =RemoteFormFactory( wlist_object.get_widgetlist_object()).get_remote_form()
            
            minion_form = RemoteFormAutomation(wlist_object)

            del wlist_object
            del the_one
            #print minion_form.fields

            #print minion_form
            return dict(minion_form =minion_form,minion=minion,module=module,method=method)
        else:
            return dict(minion_form = None,minion=minion,module=module,method=method)


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
        if kw.has_key('minion') and kw.has_key('module') and kw.has_key('method'):
            #do the stuff here
            #assign them because we need the rest so dont control everytime
            #and dont make lookup everytime ...
            minion = kw['minion']
            del kw['minion']
            module = kw['module']
            del kw['module']
            method = kw['method']
            del kw['method']
            
            #everytime we do that should be a clever way for that ???
            fc = Overlord(minion)
            #get again the method args to get their order :
            arguments=getattr(fc,module).get_method_args()
            #so we know the order just allocate and put them there 
            cmd_args=['']*(len(kw.keys()))
            
            for arg in kw.keys():
                #wow what a lookup :)
                index_of_arg = arguments[minion][method]['args'][arg]['order']
                cmd_args[index_of_arg]=kw[arg]
           
            #now execute the stuff
            result = getattr(getattr(fc,module),method)(*cmd_args)
            return "The list to be executed is \n: %s"%str(result)

        else:
            return "Missing arguments sorry can not proceess the form"

    @expose(template="funcweb.templates.method_args")
    def execute_link(self,minion=None,module=None,method=None):
        """
        Method is fot those minion methods that dont accept any 
        arguments so they provide only some information,executed
        by pressing only the link !
        """
        fc = Overlord(minion)
        result = getattr(getattr(fc,module),method)()
        return str(result)



    @expose()
    def logout(self):
        identity.current.logout()
        raise redirect("/")

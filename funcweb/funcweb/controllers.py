import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect, error_handler,validate
from func.overlord.client import Overlord, Minions
from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory
from funcweb.widget_validation import WidgetSchemaFactory

# it is assigned into method_display on every request 
global_form = None 

def validate_decorator_updater(validator_value=None):
    """
    When we pass the global_form directly to 
    turbogears.validate it is not updated on 
    every request we should pass a callable
    to trigger it ;)

    @param :validator_value : Does nothing in the code
    of validate it is passed but is irrelevant in our case
    because we compute the global_form in the method_display

    @return : the current form and schema to validate the
    current input in cherrypy's request 
    """
    global global_form
    return global_form

class Root(controllers.RootController):
    
    
    #will be reused for widget validation

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
        
        global global_form
        fc = Overlord(minion)
        method_args = getattr(fc,module).get_method_args()
        
        if not method_args.values():
            print "Not registered method here"
            return dict(minion_form = None,minion=minion,module=module,method=method)

        minion_arguments = method_args[minion][method]['args']
        if minion_arguments:
            wlist_object = WidgetListFactory(minion_arguments,minion=minion,module=module,method=method)
            wlist_object = wlist_object.get_widgetlist_object()
            #create the validation parts for the remote form
            wf = WidgetSchemaFactory(minion_arguments)
            schema_man=wf.get_ready_schema()

            #create the final form
            minion_form = RemoteFormAutomation(wlist_object,schema_man)
            global_form = minion_form.for_widget
            #print global_form
            #i use that when something goes wrong to check the problem better to stay here ;)
            #self.minion_form =RemoteFormFactory(wlist_object,schema_man).get_remote_form()
            
            del wlist_object
            del minion_arguments

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
        
    
    @expose() 
    def handle_minion_error(self,tg_errors=None):
        """
        The method checks the result from turbogears.validate
        decorator so if it has the tg_errors we know that the
        form validation is failed. That prevents the extra traffic
        to be sent to the minions!
        """
        if tg_errors:
            #print tg_errors
            return str(tg_errors)
        

    @expose(allow_json=True)
    @error_handler(handle_minion_error)
    @validate(form=validate_decorator_updater)
    def post_form(self,**kw):
        """
        Data processing part
        """
        if kw.has_key('minion') and kw.has_key('module') and kw.has_key('method'):
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
            return str(result)

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

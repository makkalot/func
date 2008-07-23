import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect, error_handler,validate
from func.overlord.client import Overlord, Minions
from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory
from funcweb.widget_validation import WidgetSchemaFactory
from funcweb.async_tools import AsyncResultManager
from func.jobthing import purge_old_jobs,JOB_ID_RUNNING,JOB_ID_FINISHED,JOB_ID_PARTIAL

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

class Funcweb(object):
    #preventing the everytime polling and getting
    #func = Overlord("name") thing
    func_cache={          
                'fc_object':None,#the fc = Overlord() thing,
                'fc_async_obj':None,
                'glob':None,
                'minion_name':None,
                'module_name':None,
                'modules':None,
                'minions':None,
                'methods':None
            }
    async_manager = None
    #will be reused for widget validation

    @expose(allow_json=True)
    @identity.require(identity.not_anonymous())
    def minions(self, glob='*',submit=None):
        """ Return a list of our minions that match a given glob """
        #make the cache thing

        if self.func_cache['glob'] == glob:
            minions = self.func_cache['minions']
        else:
            #we dont have it it is for first time so lets pull it
            minions=Minions(glob).get_all_hosts()
            self.func_cache['glob']=glob
            self.func_cache['minions']=minions
        
        if not submit:
            return dict(minions=minions,tg_template="funcweb.templates.index")
        else:
            return dict(minions=minions,tg_template="funcweb.templates.minions")


    index = minions # start with our minion view, for now

    @expose(template="funcweb.templates.modules")
    @identity.require(identity.not_anonymous())
    def minion(self, name="*", module=None, method=None):
        """ Display module or method details for a specific minion.

        If only the minion name is given, it will display a list of modules
        for that minion.  If a module is supplied, it will display a list of
        methods.
        """
        #if we have it in the cache
        if self.func_cache['minion_name'] == name:
            fc = self.func_cache['fc_object']
        else:
            fc = Overlord(name)
            self.func_cache['fc_object']=fc
            self.func_cache['minion_name']=name
            #reset the children :)
            self.func_cache['module_name']=None
            self.func_cache['modules']=None
            self.func_cache['methods']=None

            #should also reset the other fields or not ?

        
        if not module:
            if not self.func_cache['modules']:
                modules = fc.system.list_modules()
                display_modules = []

                for module in modules.itervalues():
                    for mod in module:
                        #if it is not empty
                        if getattr(fc,mod).get_method_args()[name]:
                            display_modules.append(mod)

                #put it into the cache to make that slow thing faster
                self.func_cache['modules']=display_modules
                
            else:
                #print "Im in the cache"
                #just list those who have get_method_args
                display_modules = self.func_cache['modules']
            
            modules = {}
            modules[name]=display_modules
            
            return dict(modules=modules)
        else: # a module is specified
            if not method: # return a list of methods for specified module
                #first check if we have it into the cache
                if self.func_cache['module_name'] == module and self.func_cache['methods']:
                    modules = self.func_cache['methods']
                    #print "Im in the cache"

                else:
                    self.func_cache['module_name']= module
                    #display the list only that is registered with register_method template !
                    registered_methods=getattr(fc,module).get_method_args()[name].keys()
                    modules = getattr(fc, module).list_methods()
                    for mods in modules.itervalues():
                        from copy import copy
                        cp_mods = copy(mods)
                        for m in cp_mods:
                            if not m in registered_methods:
                                mods.remove(m)

                    #store into cache if we get it again 
                    self.func_cache['methods'] = modules
                #display em
                return dict(modules=modules, module=module,
                            tg_template="funcweb.templates.methods")
            else:
                return "Wrong place :)"


    @expose(template="funcweb.templates.widgets")
    @identity.require(identity.not_anonymous())
    def method_display(self,minion=None,module=None,method=None):
        """
        That method generates the input widget for givent method.
        """
        
        global global_form
        if self.func_cache['minion_name'] == minion:
            fc = self.func_cache['fc_object']
        else:
            fc = Overlord(minion)
            self.func_cache['fc_object']=fc
            self.func_cache['minion_name']=minion
            #reset the children :)
            self.func_cache['module_name']=module
            self.func_cache['modules']=None
            self.func_cache['methods']=None

        #get the method args
        method_args = getattr(fc,module).get_method_args()
        
        if not method_args.values():
            #print "Not registered method here"
            return dict(minion_form = None,minion=minion,module=module,method=method)

        minion_arguments = method_args[minion][method]['args']
        #the description of the method we are going to display
        if method_args[minion][method].has_key('description'):
            description = method_args[minion][method]['description']
        else:
            description = None
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

            return dict(minion_form =minion_form,minion=minion,module=module,method=method,description=description)
        else:
            return dict(minion_form = None,minion=minion,module=module,method=method,description = description)



    @expose(template="funcweb.templates.login")
    def login(self, forward_url=None, previous_url=None, *args, **kw):
        """
        The login form for not registered users
        """
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
            print "I use that thing here"
            forward_url= request.headers.get("Referer", ".")

        response.status=403

        return dict(message=msg, previous_url=previous_url, logging_in=True,
                    original_parameters=request.params,
                    forward_url=forward_url)
        
    
    @expose() 
    @identity.require(identity.not_anonymous())
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
    @identity.require(identity.not_anonymous())
    def post_form(self,**kw):
        """
        Data processing part for methods that accept some inputs.
        Method recieves the method arguments for minion method then
        orders them into their original order and sends the xmlrpc
        request to the minion !
        """
        if kw.has_key('minion') and kw.has_key('module') and kw.has_key('method'):
            #assign them because we need the rest so dont control everytime
            #and dont make lookup everytime ...
            #the del statements above are important dont remove them :)
            minion = kw['minion']
            del kw['minion']
            module = kw['module']
            del kw['module']
            method = kw['method']
            del kw['method']

            if self.func_cache['minion_name'] == minion:
                fc = self.func_cache['fc_object']
            else:
                fc = Overlord(minion)
                self.func_cache['fc_object']=fc
                self.func_cache['minion_name']=minion
                #reset the children :)
                self.func_cache['module_name']=module
                self.func_cache['modules']=None
                self.func_cache['methods']=None


            #get again the method args to get their order :
            arguments=getattr(fc,module).get_method_args()
            #so we know the order just allocate and put them there 
            cmd_args=['']*(len(kw.keys()))
            
            for arg in kw.keys():
                #wow what a lookup :)
                index_of_arg = arguments[minion][method]['args'][arg]['order']
                cmd_args[index_of_arg]=kw[arg]
           
            #now execute the stuff
            #at the final execute it as a multiple if the glob suits for that
            #if not (actually there shouldnt be an option like that but who knows :))
            #it will run as a normal single command to clicked minion
            if self.func_cache['glob']:
                fc_async = Overlord(self.func_cache['glob'],async=True)
            
            result_id = getattr(getattr(fc_async,module),method)(*cmd_args)
            result = "".join(["The id for current job is :",str(result_id)," You will be notified when there is some change about that command !"])
            import time 
            time.sleep(4)
            tmp_as_res = fc_async.job_status(result_id)
            if tmp_as_res[0] == JOB_ID_FINISHED:
                result = tmp_as_res[1]
                
            return str(result)

        else:
            return "Missing arguments sorry can not proceess the form"
    
    @expose(template="funcweb.templates.result")
    @identity.require(identity.not_anonymous())
    def execute_link(self,minion=None,module=None,method=None):
        """
        Method is fot those minion methods that dont accept any 
        arguments so they provide only some information,executed
        by pressing only the link !
        """
        if self.func_cache['glob']:
            print "Yeni overlord ile execution yapiyoz ya"
            fc = Overlord(self.func_cache['glob'],async = True)
        else:
            if self.func_cache['minion_name'] == minion:
                fc = self.func_cache['fc_async_obj']
            else:
                fc = Overlord(minion,async = True)
                self.func_cache['fc_async_obj']=fc
                self.func_cache['minion_name']=minion
                #reset the children :)
                self.func_cache['module_name']=module
                self.func_cache['modules']=None
                self.func_cache['methods']=None

        result_id = getattr(getattr(fc,module),method)()
        result = "".join(["The id for current id is :",str(result_id)," You will be notified when there is some change about that command !"])
        return dict(result=str(result))

    @expose(format = "json")
    @identity.require(identity.not_anonymous())
    def check_async(self,check_change = False):
        """
        That method is polled by js code to see if there is some
        interesting change in current db
        """
        changed = False

        if not check_change :
            msg = "Method invoked with False parameter which makes it useless"
            return dict(changed = False,changes = [],remote_error=msg)
        
        if not self.async_manager:
            #cleanup tha database firstly 
            purge_old_jobs()
            self.async_manager = AsyncResultManager()
        changes = self.async_manager.check_for_changes()
        if changes:
            changed = True
        
        
        return dict(changed = changed,changes = changes)

    
    @expose(template="funcweb.templates.result")
    @identity.require(identity.not_anonymous())
    def check_job_status(self,job_id):
        """
        Checking the job status for specific job_id
        that method will be useful to see the results from
        async_results table ...
        """
        if not job_id:
            return dict(result = "job id shouldn be empty!")

        if not self.func_cache['fc_async_obj']:
            if self.func_cache['glob']:
                fc_async = Overlord(self.func_cache['glob'],async=True)
                #store also into the cache
            else:
                fc_async = Overlord("*",async=True)
            
            self.func_cache['fc_async_obj'] = fc_async

        else:
            fc_async = self.func_cache['fc_async_obj']

        id_result = fc_async.job_status(job_id)

        #the final id_result
        return dict(result=id_result)

    @expose(template="funcweb.templates.async_table")
    @identity.require(identity.not_anonymous())
    def display_async_results(self):
        """
        Displaying the current db results that are in the memory
        """
        if not self.async_manager:
            #here should run the clean_old ids
            print "I dont have another copy ?"
            purge_old_jobs()
            self.async_manager = AsyncResultManager()
        else:
            #make a refresh of the memory copy
            print "I refreshed the list"
            self.async_manager.refresh_list()
        #get the actual db    
        func_db = self.async_manager.current_db()
        
        for job_id,code_status_pack in func_db.iteritems():
            parsed_job_id = job_id.split("-")
            func_db[job_id].extend(parsed_job_id)

        #print func_db
        return dict(func_db = func_db)

    @expose()
    def logout(self):
        """
        The logoout part 
        """
        identity.current.logout()
        raise redirect("/")



class Root(controllers.RootController):
    
    @expose()
    def index(self):
        raise redirect("/funcweb")
    
    index = index # start with our minion view, for now
    funcweb = Funcweb()

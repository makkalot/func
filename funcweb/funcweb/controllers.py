import logging
log = logging.getLogger(__name__)

from turbogears import controllers, expose, flash, identity, redirect, error_handler,validate
from func.overlord.client import Overlord, Minions
from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory
from funcweb.widget_validation import WidgetSchemaFactory
from funcweb.async_tools import AsyncResultManager
from func.jobthing import purge_old_jobs,JOB_ID_RUNNING,JOB_ID_FINISHED,JOB_ID_PARTIAL
from func.utils import is_error
# it is assigned into method_display on every request 
global_form = None 

####**NOTE : All flash messages are used for error and some weird sitaution's reporting be careful when using
#that turbogears functionality !

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
    first_run = True
    group_name = None # a cache variable for current group_name
    #will be reused for widget validation

    def get_current_minion_list(self,glob):
        """
        That method will not be reachable from web interface it just 
        a util method that gives back the current minion list back, 
        we use that minion glob form in lots of places so it is a hack
        to avoid writing stupid code again and again :)
        """
        
        if self.func_cache['glob'] == glob:
            minions = self.func_cache['minions']
        else:
            #we dont have it it is for first time so lets pull it
            try:
                minions=Minions(glob).get_all_hosts()
                self.func_cache['glob']=glob
                self.func_cache['minions']=minions
            except Exception,e:
                #TODO log here
                minions = []
        
        return minions

    @expose(allow_json=True)
    @identity.require(identity.not_anonymous())
    def minions(self, glob='*',submit=None):
        """ Return a list of our minions that match a given glob """
        #make the cache thing
        minions = self.get_current_minion_list(glob) 
        if not submit:
            return dict(minions=minions,submit_adress="/funcweb/minions",tg_template="funcweb.templates.index")
        else:
            return dict(minions=minions,submit_adress="/funcweb/minions",tg_template="funcweb.templates.minions")


    index = minions # start with our minion view, for now

    @expose(allow_json = True)
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
                try :
                    modules = fc.system.list_modules()
                    if modules.has_key(name) and is_error(modules[name]):
                        #TODO put logger here!
                        flash("Some exception while getting the module list for %s minion"%(name))
                        return dict()
                        
                except Exception,e:
                    flash("Some exception while getting the module list for %s minion"%(name))
                    #it is an error case
                    return dict()
                display_modules = []

                for module in modules.itervalues():
                    for mod in module:
                        #if it is not empty
                        try :
                            if getattr(fc,mod).get_method_args()[name]:
                                display_modules.append(mod)
                        except Exception,e:
                            #TODO logger
                            flash("Some exception while getting the argument list for %s module"%(mod))
                            return dict()

                #put it into the cache to make that slow thing faster
                self.func_cache['modules']=display_modules
                
            else:
                #print "Im in the cache"
                #just list those who have get_method_args
                display_modules = self.func_cache['modules']
            
            modules = {}
            modules[name]=display_modules
          
            return dict(modules=modules,tg_template = "funcweb.templates.modules")
        else: # a module is specified
            if not method: # return a list of methods for specified module
                #first check if we have it into the cache
                if self.func_cache['module_name'] == module and self.func_cache['methods']:
                    modules = self.func_cache['methods']
                    #print "Im in the cache"

                else:
                    self.func_cache['module_name']= module
                    #display the list only that is registered with register_method template !
                    try:
                        registered_methods=getattr(fc,module).get_method_args()[name].keys()
                        modules = getattr(fc, module).list_methods()
                    except Exception,e:
                        flash("Some error in getting method list for %s module "%(module))
                        return dict()

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
        try:
            method_args = getattr(fc,module).get_method_args()
            if method_args.has_key(minion) and is_error(method_args[minion]):
                flash("We encountered some error when getting method args for %s.%s.%s"%(minion,module,method))
                return dict()

        except Exception,e:
            flash("We encountered some error when getting method args for %s.%s.%s"%(minion,module,method))
            return dict()

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
            try:
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
            except Exception,e:
                flash("We got some exception when rendering the %s.%s.%s"%(minion,module,method))
                return dict()

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
            try:
                arguments=getattr(fc,module).get_method_args()
                if arguments.has_key(minion) and is_error(arguments[minion]):
                    flash("Encountered some error when trying to get method arguments for %s.%s.%s"%(minion,module,method))
                    return dict()

            except Exception,e:
                flash("Encountered some error when trying to get method arguments for %s.%s.%s"%(minion,module,method))
                return dict()
            #so we know the order just allocate and put them there 
            cmd_args=[]
           
            #firstly create a better dict to lookup
            sorted_args = {}
            for arg in kw.keys():
                #wow what a lookup :)
                tmp_arg_num  = arguments[minion][method]['args'][arg]['order']
                sorted_args[tmp_arg_num] = []
                sorted_args[tmp_arg_num].append(arg)
                sorted_args[tmp_arg_num].append(kw[arg])

            #now append them to main cmd args
            #not a very efficient algorithm i know i know :|
            ordered_keys = sorted_args.keys()
            ordered_keys.sort()
            for order_key in ordered_keys:
                current_argument_name = sorted_args[order_key][0]
                current_argument = sorted_args[order_key][1]
                current_type = arguments[minion][method]['args'][current_argument_name]['type']
                #for *args types
                if current_type == "list*":
                    for list_arg in current_argument:
                        cmd_args.append(list_arg)
                else:
                    cmd_args.append(current_argument)
          
            #print "The list to be send is : ",cmd_args
            #now execute the stuff
            #at the final execute it as a multiple if the glob suits for that
            #if not (actually there shouldnt be an option like that but who knows :))
            #it will run as a normal single command to clicked minion
            try:
                if self.func_cache['glob']:
                    fc_async = Overlord(self.func_cache['glob'],async=True)
            
                result_id = getattr(getattr(fc_async,module),method)(*cmd_args)
                result = "".join(["The id for current job is :",str(result_id)," You will be notified when there is some change about that command !"])
            
            except Exception,e:
                flash("We got some error while trying to send command for %s.%s.%s"%(module,minion,method))
                return dict()
            
            #TODO reformat that returning string to be more elegant to display :)
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

        #i assume that they are long enough so dont poll here
        try:
            result_id = getattr(getattr(fc,module),method)()
        except Exception,e:
            flash("Error when executing link command for %s.%s.%s"%(minion,module,method))
            return dict()

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
            if not self.first_run:
                changed = True
            else:
                self.first_run = False
        
        return dict(changed = changed,changes = changes)

    
    @expose(format = "json")
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
        
        try:
            id_result = fc_async.job_status(job_id)
            #parse the comming data in a better looking way :)
            from funcweb.result_handler import produce_res_rec
            minion_result = produce_res_rec(id_result[1])
            #print "The current minion_result is : ",minion_result
            global_result = {'id':0,'item':[]}
            global_result['item'].extend(minion_result)

        except Exception,e:
            flash("We encountered some error while getting the status for %s job id"%(job_id))
            return dict()

        #the final id_result
        return dict(minion_result = global_result)

    @expose(template="funcweb.templates.async_table")
    @identity.require(identity.not_anonymous())
    def display_async_results(self):
        """
        Displaying the current db results that are in the memory
        """
        if not self.async_manager:
            #here should run the clean_old ids
            purge_old_jobs()
            self.async_manager = AsyncResultManager()
        else:
            #make a refresh of the memory copy
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
 
################################ Groups API methods here #############################    
    @expose(template="funcweb.templates.groups_main")
    @identity.require(identity.not_anonymous())
    def groups_main(self):
        """
        The main page of the groups
        """
        #a dummy object to let us to get the groups api
        #we dont supply a new group file it will handle the default
        minion_api = Minions("*")
        groups = minion_api.group_class.get_group_names()
        del minion_api
        #result to the template please :)
        return dict(groups = groups)

    @expose(template="funcweb.templates.list_group")
    @identity.require(identity.not_anonymous())
    def add_new_group(self,group_name,submit):
        """
        Adding a new group
        """
        minion_api = Minions("*")
        minion_api.group_class.add_group(group_name,save=True)
        groups = minion_api.group_class.get_group_names()
        del minion_api
        return dict(groups = groups)

    @expose(template="funcweb.templates.list_group")
    @identity.require(identity.not_anonymous())
    def remove_group(self,**kw):
        """
        Adding a new group
        """
        minion_api = Minions("*")
        minion_api.group_class.remove_group(kw['group_name'],save=True)
        groups = minion_api.group_class.get_group_names()
        del minion_api
        return dict(groups = groups)

    @expose(template="funcweb.templates.group_minion")
    @identity.require(identity.not_anonymous())
    def list_host_by_group(self,group_name):
        """
        Get the hosts for the specified group_name
        """
        from copy import copy
        copy_group_name = copy(group_name)
        if not group_name.startswith('@'):
            group_name = "".join(["@",group_name.strip()])
       
        try:
            minion_api = Minions("*")
            hosts = minion_api.group_class.get_hosts_by_group_glob(group_name)
            all_minions = minion_api.get_all_hosts()
            del minion_api
        except Exception,e:
            flash("We encountered some error while getting host list for %s "%(copy_group_name))
            return dict()

        #store the current group_name in cache variable 
        self.group_name = copy_group_name
        return dict(hosts = hosts,all_minions = all_minions,group_name = copy_group_name,submit_adress="/funcweb/filter_group_minions")

    @expose(template="funcweb.templates.group_small")
    @identity.require(identity.not_anonymous())
    def add_minions_togroup(self,**kw):
        """
        Add or remove multiple minions to given group
        """
        #print "The dict value is : ",kw
        minion_api = Minions("*")
        hosts = []
        if not kw.has_key('group_name') or not kw.has_key('action_name'):
            return dict(hosts =hosts,group_name = None)
        
        current_host_list = None

        #if we are adding some hosts 
        if kw['action_name'] == "add":
            if not kw.has_key('checkminion'):
                return dict(hosts =hosts,group_name = kw['group_name'])
            current_host_list = kw['checkminion']
        else:#it is a remove action
            if not kw.has_key('rmgroup'):
                return dict(hosts =hosts,group_name = kw['group_name'])
            current_host_list = kw['rmgroup']
        #sanity checks
        if type(current_host_list)!=list:
            hosts.extend(current_host_list.split(","))
        else:
            hosts.extend(current_host_list)
        
        if kw['action_name'] == "add":
            minion_api.group_class.add_host_list(kw['group_name'],hosts,save = True)
        else:#remove them
            minion_api.group_class.remove_host_list(kw['group_name'],hosts,save = True)

        from copy import copy
        #we need that check because @ is a sign for group search
        group_name = copy(kw['group_name'])
        if not group_name.startswith('@'):
            group_name = "".join(["@",group_name.strip()])
        
        hosts = minion_api.group_class.get_hosts_by_group_glob(group_name)
        return dict(hosts =hosts,group_name = kw['group_name'])
    
    @expose(allow_json=True)
    @identity.require(identity.not_anonymous())
    def filter_group_minions(self,glob='*',submit=None):
        """ Return a list of our minions that match a given glob """
        #make the cache thing

        minions = self.get_current_minion_list(glob) 
        if submit:
            return dict(all_minions=minions,submit_adress="/funcweb/filter_group_minions",tg_template="funcweb.templates.minion_small",group_name= self.group_name)
        else:
            return str("Wrong way :)")



############################# END of GROUPS API METHODS ############################
class Root(controllers.RootController):
    
    @expose()
    def index(self):
        raise redirect("/funcweb")
    
    index = index # start with our minion view, for now
    funcweb = Funcweb()

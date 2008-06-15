#the purpose of that module is to make widget automation 
#for registered minion modules so we dont hace to write
#that same boring stuff for every added module !

from turbogears.widgets.base import Widget,WidgetsList
from turbogears import widgets

class WidgetListFactory(object):
    """
    The class is responsible for taking the method arguments
    and converting them to the appropriate widget equivalents

    Examples :
    """
    #which type matches for which InputWidget
    __convert_table={
            'int':{
                'default_value':"TextField",
                },
            'string':{
                'default_value':"TextField",
                'options':"SingleSelectField"},
            'boolean':{
                'default_value':"CheckBox"},
            'float':{
                'default_value':"TextField",
                },
            'hash':{
                'default_value':"TextArea"},
            'list':{
                'default_value':"TextArea"} 
            }
    #will contain the input widget created in that class

    def __init__(self,argument_dict,minion=None,module=None,method=None):
        """
        Initiated with argument_dict of a method to return back
        a WidgetsList object to be placed into a form object

        @param:argument_dict : The structure we got here is like
        {'arg1':{'type':'int'..},'arg2':{'min':111} ...}
        """

        self.__argument_dict = argument_dict
        self.__widget_list={}

        #these fields will be passed ass hidden so we need them
        self.minion = minion
        self.module = module
        self.method = method
    
    def __add_general_widget(self):

        #key is the argument_name and the argument are options
        for key,argument in self.__argument_dict.iteritems():
            #get the type of the argument
            current_type = argument['type']
            
            act_special = False #if it has some special parameters
            #it should be passed to its specialized method,if it has
            #for example options in its key it should be shown as a
            #SingleSelectField not a TextFiled
            
            for type_match in self.__convert_table[current_type].keys():
                if type_match!='default_value' and argument.has_key(type_match):
                    act_special = True

           # print key,argument

            if act_special:
                #calling for example __add_specialized_string(..)
                getattr(self,"_%s__add_specialized_%s"%(self.__class__.__name__,current_type))(argument,key)
            else:
                temp_object = getattr(widgets,self.__convert_table[current_type]['default_value'])()
                #add common options to it
                self.__add_commons_to_object(temp_object,argument,key)
                #add a new entry to final list
                self.__widget_list[key]=temp_object
                #print "That have the object :",getattr(self.__widget_list[key],"default")
                del temp_object

                #print "That have the object :",getattr(self.__widget_list["list_default"],"default")

        #adding the hidden fields (that part wass adde later can be made more generic)
        if self.minion:
            self.__widget_list['minion']= getattr(widgets,'HiddenField')(name="minion",value=self.minion,default=self.minion)
        if self.module:
            self.__widget_list['module']= getattr(widgets,'HiddenField')(name="module",value=self.module,default=self.module)
        if self.method:
            self.__widget_list['method']= getattr(widgets,'HiddenField')(name="method",value=self.method,default=self.method)



    def __add_specialized_string(self,argument,argument_name):
        """
        Specialized option adder, called when the type:string is used
        with option 'options' so we should create a new SingleSelectField
        that one canno be created like others because user should supply options
        in the constructor of the SingleSelectField so it becomes a special one

        @param : argument : the argument options,
        @param : argument_name : the name of the argument also the name of the widget
        @return : Nothing
        """
        
        #allittle bit difficult to follow but that structure does
        #temp_object = SingleSelectField() for example
        
        temp_object = getattr(widgets,self.__convert_table[argument['type']]['options'])(options = argument['options'])
        self.__add_commons_to_object(temp_object,argument,argument_name)
        #add a new entry to final list
        self.__widget_list[argument_name]=temp_object
        del temp_object
    
    def __add_commons_to_object(self,object,argument,argument_name):
        """
        As it was thought all input widgets have the same
        common parameters they take so that method will add
        them to instantiated object for ex (TextField) if they 
        occur into the argument ...

        @param object : instantiated inputwidget object
        @param method argument to lookup {type:'int','max':12 ...}
        @return :None
        """
        #firstly set the name of the argument 
        setattr(object,"name",argument_name)
        
        #print "The argument name is :",argument_name
        #print "The argument options are :",argument

        if argument.has_key('default'):
            setattr(object,"default",argument["default"])
        if argument.has_key('description'):
            setattr(object,'help_text',argument['description'])
    
    def get_widgetlist(self):
        """
        Return back a dictionay with argument_name : input_widget
        pairs. That method may not be called directly,get_widgetlist_object
        is better for using in web interface
        """
        #compute the list
        self.__add_general_widget()
        return self.__widget_list

    def get_widgetlist_object(self):
        """
        Method return back the final widgetlist object
        which is turbogears.widgets.WidgetsList
        """

        #print self.__widget_list
        if len(self.__widget_list.keys())==0:
            self.__add_general_widget() #not very efficient
    
        widget_list_object = widgets.WidgetsList()
        for name,input_widget in self.__widget_list.iteritems():
            #it is a list indeed
            widget_list_object.append(input_widget)

        #get the object back
        #print widget_list_object
        return widget_list_object

####################################################################################################################
from turbogears.widgets.base import CoreWD
from turbogears.widgets import RemoteForm
from turbogears import validators, expose

class RemoteFormAutomation(CoreWD):
    """
    Base class for ajaxian Form creation
    """

    name = "Ajaxian Minion Submit Form"

    template = """ 
    <div>
       ${for_widget.display()}
        <div id="loading"></div>
        <div id="post_data"></div>
    </div>
    """

    full_class_name = "funcweb.controllers.Root"

    def __init__(self,generated_fields,*args,**kwarg):
        """
        The constructor part same as normal one except
        it takes a WidgetsList object into generated_fields
        which is generated by WidgetListFactory
        """
        #call the master :)
        super(RemoteFormAutomation,self).__init__(*args,**kwarg)
        self.for_widget = RemoteForm(
                fields = generated_fields,
                name = "minion_form",
                update = "post_data",
                before='getElement(\'loading\').innerHTML=\'Submiting form!\';',
                on_complete='getElement(\'loading\'  ).innerHTML=\'Done!\';',
                action = "/post_form"
        )

    def post_form(self,**kw):
        """
        Data processing part
        """
        return "I got that data from the remote minion form :<br/>%r"%kw

    post_form = expose()(post_form)

####################################################################################################
class RemoteFormFactory(object):
    """
    Gets the WidgetListFactory object
    and return back a RemoteForm
    """
    #some values that may want to change later 
    name = 'minion_form'
    before='MochiKit.DOM.getElement(\'loading\').innerHTML=\'Submiting form!\';',
    on_complete='MochiKit.DOM.getElement(\'loading\'  ).innerHTML=\'Done!\';',
    update = "post_data"
    submit_text = "Send Minion Form"
    action = "/post_form"

    def __init__(self,wlist_object):
        self.wlist_object = wlist_object

    def get_remote_form(self):
        
        #print self.wlist_object

        return RemoteForm(
                name = self.name,
                fields = self.wlist_object,
                before = self.before,
                on_complete = self.on_complete,
                update = self.update,
                submit_text = self.submit_text,
                action = self.action
                )

class RemoteLinkFactory(CoreWD):
    """
    A rpc executer for the methods without arguments
    """

    name = "Minion Remote Link Executer"

    template =""" 
    <div>
        ${for_widget.display()}
        <div id="items">Minion Result</div>
    </div>
    """

    def __init__(self,*args,**kwargs):
        """The init part here"""
        super(SomeRemoteLink,self).__init__(*args,**kwargs)
        self.for_widget = LinkRemoteFunction(
                name = "catexecuter",
                action = "/catlister",
                data = dict(give_all="all"),
                update = "items"
                )



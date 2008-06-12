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
    __widget_list={}

    def __init__(self,argument_dict):
        """
        Initiated with argument_dict of a method to return back
        a WidgetsList object to be placed into a form object

        @param:argument_dict : The structure we got here is like
        {'arg1':{'type':'int'..},'arg2':{'min':111} ...}
        """

        self.__argument_dict = argument_dict

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
        Return the final list back
        """
        #compute the list
        self.__add_general_widget()
        return self.__widget_list

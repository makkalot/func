##
## Copyright 2007, Red Hat, Inc
## see AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

class ArgCompatibility(object):
    """ 
    That class is going to test if the module that was created by module
    writer if he/she obeys to the rules we put here
    """

    #these are the common options can be used with all types
    __common_options = ('optional','default','description','order')
    __method_options = ('description','args') #making method declarations more generic like method_name:{'args':{...},'description':"bla bla"}

    #basic types has types also
    __basic_types={
            'range':[1,],
            'min':0,
            'max':0,
            'optional':False,
            'description':'',
            'options':[1,],
            'min_length':0,
            'max_length':0,
            'validator':'',
            'type':'',
            'default':None, #its type is unknown,
            'order':0
            }

    def __init__(self,get_args_result):
        """
        The constructor initilized by the get_method_args()(the dict to test)
        @param : get_args_result : The dict with all method related info
        """
        self.__args_to_check = get_args_result
        
        #what options does each of the basic_types have :
        self.__valid_args={
                'int':('range','min','max',),
                'string':('options','min_length','max_length','validator',),
                'boolean':(),
                'float':('range','min','max'),
                'hash':('validator',),
                'list':('validator',),
                'list*':('validator',),
            }


    def _is_type_options_compatible(self,argument_dict):
        """
        Checks the method's argument_dict's options and looks inside
        self.__valid_args to see if the used option is there 

        @param : argument_dict : current argument to check
        @return : True of raises IncompatibleTypesException

        """
        #did module writer add a key 'type'
        if not argument_dict.has_key('type') or not self.__valid_args.has_key(argument_dict['type']):
            raise IncompatibleTypesException("%s is not in valid options,possible ones are :%s"%(argument_dict['type'],str(self.__valid_args)))
    
        #we need some specialization about if user has defined options
        #there is no need for using validator,min_lenght,max_length
        if argument_dict.has_key('options'):
            for arg_option in argument_dict.keys():
                if arg_option!='options' and arg_option in self.__valid_args['string']:
                    raise IncompatibleTypesException('The options keyword should be used alone in a string cant be used with min_length,max_length,validator together')
        
        #if range keyword is used into a int argument the others shouldnt be there
        if argument_dict.has_key('range'):
            if len(argument_dict['range'])!=2:
                raise IncompatibleTypesException('The range option should have 2 members [min,max]')
            if not argument_dict['range'][0] < argument_dict['range'][1]:
                raise IncompatibleTypesException('In the range option first member should be smaller than second [min,max]')
            #check if another option was used there ...
            for arg_option in argument_dict.keys():
                if arg_option!='range' and arg_option in self.__valid_args['int']:
                    raise IncompatibleTypesException('The options range should be used alone into a int argument')
        

        # we will use it everytime so not make lookups
        the_type = argument_dict['type']
        from itertools import chain #may i use chain ?

        for key,value in argument_dict.iteritems():
            
            if key == "type":
                continue
            if key not in chain(self.__valid_args[the_type],self.__common_options):
                raise IncompatibleTypesException("There is no option like %s in %s"%(key,the_type))

        return True


    def _is_basic_types_compatible(self,type_dict):
        """
        Validates that if the types that were submitted with 
        get_method_args were compatible with our format above
        in __basic_types

        @param : type_dict : The type to examine 
        @return : True or raise IncompatibleTypesException Exception
        """
        #print "The structure we got is %s:"%(type_dict)
        for key,value in type_dict.iteritems():

            #do we have that type 
            if not self.__basic_types.has_key(key):
                raise IncompatibleTypesException("%s not in the basic_types"%key)
    
            #if  type matches and dont match default
            #print "The key: %s its value %s and type %s"%(key,value,type(value))
            if key!='default' and type(value)!=type(self.__basic_types[key]):
                raise IncompatibleTypesException("The %s keyword should be in that type %s"%(key,type(self.__basic_types[key])))

        return True

    def is_all_arguments_registered(self,cls,method_name,arguments):
        """
        Method inspects the method arguments and checks if the user
        has registered all the arguments succesfully and also adds a
        'order' keyword to method arguments to 
        """
        import inspect
        from itertools import chain
        #get the arguments from real object we have [args],*arg,**kwarg,[defaults]
        tmp_arguments=inspect.getargspec(getattr(cls,method_name))
        check_args=[arg for arg in chain(tmp_arguments[0],tmp_arguments[1:3]) if arg and arg!='self']
        #print "The arguments taken from the inspect are :",check_args 
        #the size may change of the hash so should a copy of it 
        copy_arguments = arguments.copy()
        for compare_arg in copy_arguments.iterkeys():
            if not compare_arg in check_args:
                raise ArgumentRegistrationError("The argument %s is not in the %s"%(compare_arg,method_name))
            else:
                #should set its ordering thing
                arguments[compare_arg]['order']=check_args.index(compare_arg)

        return True

    def validate_all(self):
        """
        Validates the output for minion module's
        get_method_args method
        
        The structure that is going to be validated is in that format :
        
        {
        method_name1 : {'args':{...},
                      'description':"wowo"},
        method_name12 : {...}
        }
        
        @return : True or raise IncompatibleTypesException Exception
        """
        
        for method in self.__args_to_check.iterkeys():
            #here we got args or description part
            #check if user did submit something not in the __method_options
            for method_option in self.__args_to_check[method].iterkeys():
                if method_option not in self.__method_options:
                    raise IncompatibleTypesException("There is no option for method_name like %s,possible ones are : %s"%(method_option,str(self.__method_options)))
                #check what is inside the args
                if method_option == "args":
                    for argument in self.__args_to_check[method][method_option].itervalues():
                        #print argument
                        #check if user registered all the args and add to them ordering option!
                        self._is_basic_types_compatible(argument)
                        self._is_type_options_compatible(argument)

        return True


###The Exception classes here they will be raised during the validation part
###If a module passes all the tests it is ready tobe registered


class IncompatibleTypesException(Exception):
    """
    Raised when we assign some values that breaksour rules 
    @see ArgCompatibility class for allowed situations
    """
    def __init__(self, value=None):
        Exception.__init__(self)
        self.value = value
    def __str__(self):
        return "%s" %(self.value,)

class NonExistingMethodRegistered(IncompatibleTypesException):
    """
    That Exception is raised when a non existent module is
    tried to be registerd we shouldnt allow that
    """
    pass

class UnregisteredMethodArgument(IncompatibleTypesException):
    """
    That exception is to try to remove the errors that user may
    do during method registration process. If a argument is missed
    to be registerted in the method that exception is Raised!
    """
    pass


class NonExistingMethodRegistered(IncompatibleTypesException):
    """
    Raised when module writer registers a method that doesnt
    exist in his/her module class (probably by mistake)
    """
    pass

class ArgumentRegistrationError(IncompatibleTypesException):
    """
    When user forgets to register soem of the arguments in the list
    or adds some argument that is not there 
    """
    pass

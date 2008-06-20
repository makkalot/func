from turbogears import validators #the shiny validator part

class WidgetSchemaFactory(object):
    """
    The purpose of the class is to produce a
    validators.Schema object according to method
    arguments that are retrieved from minions
    """

    def __init__(self,method_argument_dict):
        """
        @param method_argument_dict : The dict that is 
        from minion in format of {'arg':{'type':'string','options':[...]}}
        the format is defined in func/minion/func_arg.py
        """

        self.method_argument_dict = method_argument_dict
        self.validator_list = {} #the validator that will create final schema

    def _add_validators(self):
        """
        Method is an entry point of factory iters over the all arguments
        and according to their types it sends the process to more specialized
        validator adders 
        """
        
        for argument_name,argument_values in self.method_argument_dict.iteritems():
            #some lazy stuff :)
            #for ex : _add_int_validator(some_arg)
            getattr(self,"_add_%s_validator"%(argument_values['type']))(argument_name)

    def _add_int_validator(self,argument_name):
        """
        Gets the options of the int type and adds a
        new validator to validator_list
        """
        #the initializer for the int_validator
        int_data_set = {}
        
        if self.method_argument_dict[argument_name].has_key('range'):
            #because the range is [min,max] list the 0 is min 1 is the max
            int_data_set['min']=self.method_argument_dict[argument_name]['range'][0]
            int_data_set['max']=self.method_argument_dict[argument_name]['range'][1]
        if self.method_argument_dict[argument_name].has_key('min'):
            int_data_set['min']=self.method_argument_dict[argument_name]['min']
        if self.method_argument_dict[argument_name].has_key('max'):
            int_data_set['max']=self.method_argument_dict[argument_name]['max']

        #add the validator to the list
        if int_data_set:
            self.validator_list[argument_name]=MinionIntValidator(**int_data_set)
        else:
            self.validator_list[argument_name]=MinionIntValidator()



    
    def _add_string_validator(self,argument_name):
        """
        Gets the options of the string type and adds a
        new validator to validator_list
        """

        string_data_set={}
        str_validator_list =[]
        
        if self.method_argument_dict[argument_name].has_key('optional'):
            if self.method_argument_dict[argument_name]['optional']:
                string_data_set['not_empty']=False
            else:
                string_data_set['not_empty']=True

        if self.method_argument_dict[argument_name].has_key('min_length'):
            string_data_set['min']=self.method_argument_dict[argument_name]['min_length']
        if self.method_argument_dict[argument_name].has_key('max_length'):
            string_data_set['max']=self.method_argument_dict[argument_name]['max_length']
        if self.method_argument_dict[argument_name].has_key('validator'):
            str_validator_list.append(getattr(validators,'Regex')(self.method_argument_dict[argument_name]['validator']))

        #if we have set a string_data_set
        if string_data_set:
            str_validator_list.append(getattr(validators,'String')(**string_data_set))
        
        #if true it should be a validator.All thing
        if len(str_validator_list)>1:
            self.validator_list[argument_name]=getattr(validators,'All')(*str_validator_list)
        elif str_validator_list:
            self.validator_list[argument_name]=str_validator_list[0]
        else: #if there is no option
            self.validator_list[argument_name]=getattr(validators,'String')()




    def _add_float_validator(self,argument_name):
        """
        Gets the options of the float type and adds a
        new validator to validator_list
        """
        pass

    def _add_list_validator(self,argument_name):
        """
        Gets the options of the list type and adds a
        new validator to validator_list
        """
        pass

    def _add_hash_validator(self,argument_name):
        """
        Gets the options of the hash type and adds a
        new validator to validator_list
        """
        pass


    def get_ready_schema(self):
        """
        Get the final validator schema
        """
        final_schema = validators.Schema()
        if not self.validator_list:
            self._add_validators()

        for vd_name,vd in self.validator_list.iteritems():
            setattr(final_schema,vd_name,vd)

        return final_schema

########################################################################
class MinionIntValidator(validators.FancyValidator):

    """
    Confirms that the input/output is of the proper type of int.
    
    """
    #automatically will be assigned
    min = None
    max = None

    def _to_python(self,value,state):
        """
        Will check just the type here and return
        value to be validated in validate_python
        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise validators.Invalid('The field should be integer',value,state)

        return int(value)
        
    
    def validate_python(self,value,state):
        """
        The actual validator
        """
       #firstly run the supers one
        if self.min and self.min:
            if value < self.min:
                raise validators.Invalid('The number you entered should be bigger that %d'%(self.min),value,state)
        
        if self.max and self.max:
            if value > self.max:
                raise validators.Invalid('The number you entered exceeds the %d'%(self.max),value,state)

        
##################################################################
class MinionFloatValidator(MinionIntValidator):
    
    def _to_python(self,value,state):
        """
        Will check just the type here and return
        value to be validated in validate_python
        """
        try:
            value = float(value)
        except (ValueError, TypeError):
            raise validators.Invalid('The field should be a float',value,state)

        return float(value)
 

class MinionListValidator(validators.FancyValidator):
    pass

class MinionHashValidator(validators.FancyValidator):
    pass


if __name__ == "__main__":
    pass

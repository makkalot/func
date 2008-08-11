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
        # a mirror var to show that these are same things 
        mirror_case = {'list*':'list'}
        for argument_name,argument_values in self.method_argument_dict.iteritems():
            #some lazy stuff :)
            #for ex : _add_int_validator(some_arg)
            current_type = argument_values['type']
            if current_type == "list*":
                getattr(self,"_add_%s_validator"%(mirror_case[current_type]))(argument_name)
            else:
                getattr(self,"_add_%s_validator"%(current_type))(argument_name)

    def _add_boolean_validator(self,argument_name):
        bool_data_set = {}
        
        #the optional keyword
        if self.method_argument_dict[argument_name].has_key('optional'):
            if self.method_argument_dict[argument_name]['optional']:
                bool_data_set['not_empty']=False
            else:
                bool_data_set['not_empty']=True
                
        
        if bool_data_set:
            self.validator_list[argument_name]=validators.Bool(**bool_data_set)
        else:
            self.validator_list[argument_name]=validators.Bool()


 

    def _add_int_validator(self,argument_name):
        """
        Gets the options of the int type and adds a
        new validator to validator_list
        """
        #the initializer for the int_validator
        int_data_set = {}
        
        #the optional keyword
        if self.method_argument_dict[argument_name].has_key('optional'):
            if self.method_argument_dict[argument_name]['optional']:
                int_data_set['not_empty']=False
            else:
                int_data_set['not_empty']=True
                
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

        #the initializer for the float_validator
        float_data_set = {}
        
        #is it optional
        if self.method_argument_dict[argument_name].has_key('optional'):
            if self.method_argument_dict[argument_name]['optional']:
                float_data_set['not_empty']=False
            else:
                float_data_set['not_empty']=True
         

        if self.method_argument_dict[argument_name].has_key('min'):
            float_data_set['min']=self.method_argument_dict[argument_name]['min']
        if self.method_argument_dict[argument_name].has_key('max'):
            float_data_set['max']=self.method_argument_dict[argument_name]['max']

        #add the validator to the list
        if float_data_set:
            self.validator_list[argument_name]=MinionFloatValidator(**float_data_set)
        else:
            self.validator_list[argument_name]=MinionFloatValidator()



    def _add_list_validator(self,argument_name,the_type='list'):
        """
        Gets the options of the list type and adds a
        new validator to validator_list
        """
        list_data_set = {}
        
        #is it optional
        if self.method_argument_dict[argument_name].has_key('optional'):
            if self.method_argument_dict[argument_name]['optional']:
                list_data_set['not_empty']=False
            else:
                list_data_set['not_empty']=True
                
        if self.method_argument_dict[argument_name].has_key('validator'):
            list_data_set['regex_string'] = self.method_argument_dict[argument_name]['validator']
            
        if list_data_set:
            if the_type == 'list':
                self.validator_list[argument_name]=MinionListValidator(**list_data_set)
            else:
                self.validator_list[argument_name]=MinionHashValidator(**list_data_set)

        else:
            if the_type == 'list':
                self.validator_list[argument_name]=MinionListValidator()
            else:
                self.validator_list[argument_name]=MinionHashValidator()



    def _add_hash_validator(self,argument_name):
        """
        Gets the options of the hash type and adds a
        new validator to validator_list
        """
        self._add_list_validator(argument_name,the_type = 'hash')


    def get_ready_schema(self):
        """
        Get the final validator schema
        """
        final_schema = validators.Schema()
        if not self.validator_list:
            self._add_validators()

        for vd_name,vd in self.validator_list.iteritems():
            #setattr(final_schema,vd_name,vd)
            getattr(final_schema,'fields')[vd_name]= vd

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
 
#################################################################
class MinionListValidator(validators.FancyValidator):
    
    regex_string = None

    def _to_python(self,value,state):
        """
        Will check just the type here and return
        value to be validated in validate_python
        """
        #will add more beautiful validation here after 
        #integrate the complex widgets for lists and dicts
        #print "Im in the list validator the value i recieved is : ",value

        if self.not_empty:
            if len(value)==0:
                raise validators.Invalid('Empty list passed when not_empty is set',value,state)


        tmp = []
        if type(tmp) != type(value):
            value = list(value)
        
        #concert the data to proper format 
        final_list = []
        for hash_data in value:
            final_list.extend(hash_data.values())
    
        return final_list

    def validate_python(self,value,state):
        import re
        if self.regex_string:
            try:
                compiled_regex = re.compile(self.regex_string)
            except Exception,e:
                raise validators.Invalid('The passed regex_string is not a valid expression'%self.regex_string,value,state)
            
            for list_value in value:
                if not re.match(compiled_regex,str(list_value)):
                    raise validators.Invalid('The %s doesnt match to the regex expression that was supplied'%list_value,value,state)

        #there is no else for now :) 

class MinionHashValidator(validators.FancyValidator):
    
    regex_string = None

    def _to_python(self,value,state):
        """
        Will check just the type here and return
        value to be validated in validate_python
        """
        #will add more beautiful validation here after 
        #integrate the complex widgets for lists and dicts
        #print "Im in hash validator the value i recieved is ",value

        if self.not_empty:
            if len(value)==0:
                raise validators.Invalid('Empty hash passed when not_empty is set',value,state)
            
        #concert the data to proper format 
        final_hash = {}
        for hash_data in value:
            final_hash[hash_data['keyfield']] = hash_data['valuefield']

    

       #check the type firstly
        tmp = {}
        if type(tmp) != type(final_hash):
            raise validators.Invalid('The value passed to MinionHashValidator should be a dict object',final_hash,state)
        
        #print value
        return final_hash

    def validate_python(self,value,state):
        #print value
        import re
        if self.regex_string:
            try:
                compiled_regex = re.compile(self.regex_string)
            except Exception,e:
                raise validators.Invalid('The passed regex_string is not a valid expression'%self.regex_string,value,state)
            for dict_value in value.itervalues():
                if not re.match(compiled_regex,str(dict_value)):
                    raise validators.Invalid('The %s doesnt match to the regex expression that was supplied'%dict_value,value,state)



if __name__ == "__main__":
    pass

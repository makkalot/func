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
        self.validator_list = [] #the validator that will create final schema

    def _add_validators(self):
        """
        Method is an entry point of factory iters over the all arguments
        and according to their types it sends the process to more specialized
        validator adders 
        """
        pass

    def _add_int_validator(self):
        """
        Gets the options of the int type and adds a
        new validator to validator_list
        """
        pass

    def _add_string_validator(self):
        """
        Gets the options of the string type and adds a
        new validator to validator_list
        """
        pass

    def _add_float_validator(self):
        """
        Gets the options of the float type and adds a
        new validator to validator_list
        """
        pass

    def _add_list_validator(self):
         """
        Gets the options of the list type and adds a
        new validator to validator_list
        """
        pass

    def _add_hash_validator(self):
         """
        Gets the options of the hash type and adds a
        new validator to validator_list
        """
        pass


    def get_ready_schema(self):
        """
        Get the final validator schema
        """
        pass




if __name__ == "__main__":
    pass

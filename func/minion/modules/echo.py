"""
Test module for rendering funcweb
(We can remove this module once other modules are instrumented)
"""

import func_module

class EchoTest(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Module that all of its methods returns back the same thing it recieves!"

    def run_string(self, command):
        """
        Run String
        """
        return str(command)

    def run_int(self,command):
        """
        Run Integer
        """
        return int(command)

    def run_float(self,command):
        """
        Run float
        """
        return float(command)

    def run_options(self,command):
        """
        Run options
        """
        return str(command)

    def run_list(self,command):
        """
        Run a list
        """
        return command
    
    
    def run_list_star(self,*command):
        """
        Run a star list :)
        """
        return command

    
    def run_hash(self,command):
        """
        Run hash
        """

        return command
    
    
  
    def run_boolean(self,command):
        """
        Run boolean
        """
        return command

    def register_method_args(self):
        """
        Implementing the argument getter
        """
        return {
                'run_string':{
                    'args':
                    {
                        'command':{
                            'type':'string',
                            'optional':False
                            }
                        },
                    'description':'Returns back a string'
                    },
                'run_int':{
                    'args':
                    {
                        'command':{
                            'type':'int',
                            'optional':False
                            }
                        },
                    'description':'Returns back an integer'
                    },
                'run_float':{
                    'args':
                    {
                        'command':{
                            'type':'float',
                            'optional':False
                        },
                    },
                    'description':'Returns back a float'
                    },
                'run_options':{
                    'args':{
                        'command':{
                            'type':'string',
                            'optional':False,
                            'options':['first_option','second_option','third_option']
                            },   
                    },
                    'description':'Getting the status of the service_name'
                    },
                'run_list':{
                    'args':
                    {
                        'command':{
                            'type':'list',
                            'optional':False
                            }
                        },
                    'description':'Returns back a list'
                    },
                'run_list_star':{
                    'args':
                    {
                        'command':{
                            'type':'list*',
                            'optional':False
                            }
                        },
                    'description':'Prototype for *args'
                    },

                'run_hash':{
                    'args':
                    {
                        'command':{
                            'type':'hash',
                            'optional':False
                            }
                        },
                    'description':'Returns back a hash'
                    },
   

                'run_boolean':{
                    'args':
                    {
                        'command':{
                            'type':'boolean',
                            'optional':False
                            }
                        },
                    'description':'Returns back a boolean'
                    }
                 }

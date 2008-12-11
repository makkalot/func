import func_module
import time
import exceptions
from certmaster.config import BaseConfig, Option, IntOption, FloatOption, BoolOption

class Test(func_module.FuncModule):
    version = "11.11.11"
    api_version = "0.0.1"
    description = "Just a very simple example module"

    class Config(BaseConfig):
        example = Option('1')
        string_option = Option('some string here')
        int_option = IntOption(37)
        bool_option = BoolOption(True)
        float_option = FloatOption(3.14159)
        testvalue = 'this is a test. It is only a test'
        

    def add(self, numb1, numb2):
        return numb1 + numb2

    def ping(self):
        return 1

    def sleep(self,t):
        """
        Sleeps for t seconds, and returns time of day.
        Simply a test function for trying out async and threaded voodoo.
        """
        t = int(t)
        time.sleep(t)
        return time.time()


    def explode(self):
        """
        Testing remote exception handling is useful
        """
        raise exceptions.Exception("khhhhhhaaaaaan!!!!!!")


    def explode_no_string(self):
        """
        Testing remote exception handling is useful
        """
        raise exceptions.Exception()


    def echo(self, data):
        """
        Returns whatever was passed into it
        """
        return data

    def bigint(self):
        """
        Returns an integer greater than 2^32-1
        """
        return 2**32


    def configfoo(self):
        """
        Returns the options config
        """
        return self.options

    def config_save(self):
	"""
	Saves the options config
	"""
	self.save_config()
	return self.options

    def config_set(self, key_name, value):
        setattr(self.options,key_name, value)
        self.save_config()
        return self.options

    def config_get(self, key_name):
	return getattr(self.options, key_name)

    def config_get_test(self):
	return self.options.testvalue

    def register_method_args(self):
        """
        Implementing method argument getter
        """

        return {
                'add':{
                    'args':{
                        'numb1':{
                            'type':'int',
                            'optional':False,
                            'description':'An int'
                            },
                        'numb2':{
                            'type':'int',
                            'optional':False,
                            'description':'An int'
                                }

                        },
                    'description':'Gives back the sum of 2 integers'
                    },
                'ping':{
                    'args':{},
                    'description':"Ping the minion"
                    },
                'sleep':{
                    'args':{
                        't':{
                            'type':'int',
                            'optional':False,
                            'description':'Num of sec'
                            }
                        },
                    'description':"Sleep for a while"
                    },
                'explode':{
                    'args':{},
                    'description':"Raises an exception"
                    },
                'echo':{
                    'args':{
                        'data':{
                            'type':'string',
                            'optional':False,
                            'description':"The message to send"
                            }
                        },
                    'description':"Echoes back the sent data "
                    },
                'bigint':{
                    'args':{},
                    'description':"Returns a number greater than 2^32-1"
                    }
                }

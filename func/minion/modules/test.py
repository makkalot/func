import func_module
import time
import exceptions

class Test(func_module.FuncModule):
    version = "11.11.11"
    api_version = "0.0.1"
    description = "Just a very simple example module"

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

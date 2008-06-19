import unittest
import turbogears
from turbogears import testutil
from funcweb.widget_validation import WidgetSchemaFactory

class TestWidgetValidator(unittest.TestCase):

    def test_string_validator(self):
        wf = WidgetSchemaFactory(self.get_string_params())
        schema_man=wf.get_ready_schema()
        
        conversion_schema = {
                'max_length':'max',
                'min_length':'min',
                'validator':'regex'
                }

        #do better test here
        for argument_name,arg_options in self.get_string_params().iteritems():
            #print argument_name
            assert hasattr(schema_man,argument_name)==True
            #not very efficient but it si just a test :)
            if argument_name != 'string_mix':
                for arg,value in arg_options.iteritems():
                    print getattr(schema_man,argument_name)
                    if conversion_schema.has_key(arg):
                        if hasattr(getattr(schema_man,argument_name),conversion_schema[arg]):
                            print arg,value
                            #couldnt find a way to test it !??
                            if arg != 'validator':
                                assert getattr(getattr(schema_man,argument_name),conversion_schema[arg])==value
                                print getattr(getattr(schema_man,argument_name),conversion_schema[arg])
            else:
                #just print it to see what is inside because the test will be very hardcoded otherwise
                print getattr(schema_man,argument_name)
                continue
        print "Happy tests !"

    def get_string_params(self):
        return {
                'string_default':{
                    'type':'string',
                    'default':'default string',
                    'description':'default description'
                    },
                'string_regex':{
                    'type':'string',
                    'default':'some',
                    'validator':'^[a-z]*$'
                    }
                    ,
                #will be converted to dropdown
                'min_max_string':{
                    'type':'string',
                    'default':'myfirst',
                    'optional':False,
                    'description':'default dropdown list',
                    'max_length':12,
                    'min_length':5
                    },
                'string_mix':{
                    'type':'string',
                    'optional':False,
                    'max_length':123,
                    'min_length':12,
                    'validator':'^[A-Z]+$'
                    }
                }
 

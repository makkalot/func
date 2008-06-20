import unittest
import turbogears
from turbogears import testutil
from funcweb.widget_validation import WidgetSchemaFactory,MinionIntValidator
from turbogears import validators 

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
                    #print getattr(schema_man,argument_name)
                    if conversion_schema.has_key(arg):
                        if hasattr(getattr(schema_man,argument_name),conversion_schema[arg]):
                            #print arg,value
                            #couldnt find a way to test it !??
                            if arg != 'validator':
                                assert getattr(getattr(schema_man,argument_name),conversion_schema[arg])==value
                                #print getattr(getattr(schema_man,argument_name),conversion_schema[arg])
            else:
                #just print it to see what is inside because the test will be very hardcoded otherwise
                #print getattr(schema_man,argument_name)
                continue
        print "Happy tests !"


    def test_minion_int_validator(self):
        mv=MinionIntValidator(max_int = 44,min_int=2)
        self.assertRaises(validators.Invalid,mv.to_python,100)
        self.assertRaises(validators.Invalid,mv.to_python,1)
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        #dont use the min
        mv=MinionIntValidator(max_int = 44)
        self.assertRaises(validators.Invalid,mv.to_python,100)
        assert mv.to_python(1)==1
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        mv=MinionIntValidator(min_int=12)
        self.assertRaises(validators.Invalid,mv.to_python,10)
        assert mv.to_python(14)==14
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        mv=MinionIntValidator()
        assert mv.to_python(14)==14
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        
        
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
 

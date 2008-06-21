import unittest
import turbogears
from turbogears import testutil
from funcweb.widget_validation import WidgetSchemaFactory,MinionIntValidator,MinionFloatValidator,MinionListValidator
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

    def test_int_validator(self):
        wf = WidgetSchemaFactory(self.get_int_params())
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in self.get_int_params().iteritems():  
            #print argument_name
            assert hasattr(schema_man,argument_name)==True
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            
            #if the argument includes some range
            if arg_options.has_key('range'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'max') == arg_options['range'][1]
                assert getattr(getattr(schema_man,argument_name),'min') == arg_options['range'][0]
            if arg_options.has_key('min'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'min') == arg_options['min']
                
            if arg_options.has_key('max'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'max') == arg_options['max']
            
            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(getattr(schema_man,argument_name),'not_empty') == arg_options['optional']


        print "Happy test!"
        
    def test_float_validator(self):
        wf = WidgetSchemaFactory(self.get_float_params())
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in self.get_float_params().iteritems():  
            #print argument_name
            assert hasattr(schema_man,argument_name)==True
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            
            if arg_options.has_key('min'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'min') == arg_options['min']
                
            if arg_options.has_key('max'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'max') == arg_options['max']

            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(getattr(schema_man,argument_name),'not_empty') == arg_options['optional']


        print "Happy test!"

    def test_list_validator(self):
        wf = WidgetSchemaFactory(self.get_list_params())
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in self.get_list_params().iteritems():  
            #print argument_name
            #should all the argument names really
            assert hasattr(schema_man,argument_name)==True
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            
            if arg_options.has_key('validator'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(getattr(schema_man,argument_name),'regex_string') == arg_options['validator']

            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(getattr(schema_man,argument_name),'not_empty') == arg_options['optional']


        print "Happy test!"



    def test_minion_int_validator(self):
        mv=MinionIntValidator(max = 44,min=2)
        self.assertRaises(validators.Invalid,mv.to_python,100)
        self.assertRaises(validators.Invalid,mv.to_python,1)
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        #dont use the min
        mv=MinionIntValidator(max = 44)
        self.assertRaises(validators.Invalid,mv.to_python,100)
        assert mv.to_python(1)==1
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        mv=MinionIntValidator(min=12)
        self.assertRaises(validators.Invalid,mv.to_python,10)
        assert mv.to_python(14)==14
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21) == 21
        
        mv=MinionIntValidator()
        assert mv.to_python(14)==14
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')

    def test_minion_float_validator(self):
        mv=MinionFloatValidator(max = 44.0,min=2.0)
        self.assertRaises(validators.Invalid,mv.to_python,100.0)
        self.assertRaises(validators.Invalid,mv.to_python,1.0)
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21.0) == 21.0
        
        #dont use the min
        mv=MinionFloatValidator(max = 44.0)
        self.assertRaises(validators.Invalid,mv.to_python,100.0)
        assert mv.to_python(1.0)==1.0
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21.0) == 21.0
        
        mv=MinionFloatValidator(min=12.0)
        self.assertRaises(validators.Invalid,mv.to_python,10.0)
        assert mv.to_python(14.0)==14.0
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
        assert mv.to_python(21.0) == 21.0
        
        mv=MinionFloatValidator()
        assert mv.to_python(14.0)==14.0
        self.assertRaises(validators.Invalid,mv.to_python,'some_string')
    
    def test_minion_list_validator(self):
        
        #test default
        mv = MinionListValidator()
        assert mv.to_python(['fedora','debian','others']) == ['fedora','debian','others']
        del mv

        #test with regex
        mv = MinionListValidator(regex_string='^[A-Z]+$',not_empty=True)
        assert mv.to_python(['FEDORA','MACOSX']) == ['FEDORA','MACOSX']
        self.assertRaises(validators.Invalid,mv.to_python,[])
        self.assertRaises(validators.Invalid,mv.to_python,['hey_error'])


        print "Happy testing !"
        
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
  
    def get_int_params(self):
        return {
                'int_default':{
                    'type':'int',
                    'default':2,
                    'description':'default integer'
                    },
                 'min_max':{
                    'type':'int',
                    'default':12,
                    'optional':False,
                    'description':'default dropdown list',
                    'max':12,
                    'min':5
                    },
                'range_int':{
                    'type':'int',
                    'optional':False,
                    'range':[1,55]
                    }
                }
    
    def get_float_params(self):
        return {
                'float_default':{
                    'type':'float',
                    'default':2.0,
                    'description':'default float'
                    },
                 'min_max':{
                    'type':'float',
                    'default':11.0,
                    'optional':False,
                    'description':'default dropdown list',
                    'max':12.0,
                    'min':5.0
                    },
                }
        
    def get_list_params(self):
        return {
                'list_default':{
                    'type':'list',
                    'default':'cooler',
                    'description':'default list'
                    },
                 'list_regex':{
                    'type':'list',
                    'default':'hey',
                    'optional':False,
                    'description':'default regex list',
                    'validator':'^[A-Z]$'
                    },
                }


 

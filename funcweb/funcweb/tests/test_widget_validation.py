import unittest
import turbogears
from turbogears import testutil
from funcweb.widget_validation import WidgetSchemaFactory,MinionIntValidator,MinionFloatValidator,MinionListValidator,MinionHashValidator
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
            #print getattr(schema_man,'fields')
            assert getattr(schema_man,'fields').has_key(argument_name) == True
            current_schema_object = getattr(schema_man,'fields')[argument_name]
            #not very efficient but it si just a test :)
            if argument_name == 'string_mix':
                continue
            if arg_options.has_key('max_length'):
                assert  getattr(current_schema_object,'max') == arg_options['max_length']
            if arg_options.has_key('min_length'):
                assert  getattr(current_schema_object,'min') == arg_options['min_length']
            if arg_options.has_key('validator'):
                assert getattr(current_schema_object,'regex')
            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(current_schema_object,'not_empty') == arg_options['optional']
           
        print "Happy tests !"

    def test_int_validator(self):
        wf = WidgetSchemaFactory(self.get_int_params())
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in self.get_int_params().iteritems():  
            #print argument_name
            assert getattr(schema_man,'fields').has_key(argument_name)==True
            current_schema_object = getattr(schema_man,'fields')[argument_name]
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            
            #if the argument includes some range
            if arg_options.has_key('range'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'max') == arg_options['range'][1]
                assert getattr(current_schema_object,'min') == arg_options['range'][0]
            if arg_options.has_key('min'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'min') == arg_options['min']
                
            if arg_options.has_key('max'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'max') == arg_options['max']
            
            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(current_schema_object,'not_empty') == arg_options['optional']


        print "Happy test!"
        
    def test_float_validator(self):
        wf = WidgetSchemaFactory(self.get_float_params())
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in self.get_float_params().iteritems():  
            #print argument_name
            assert getattr(schema_man,'fields').has_key(argument_name)==True
            current_schema_object = getattr(schema_man,'fields')[argument_name]
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            
            if arg_options.has_key('min'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'min') == arg_options['min']
                
            if arg_options.has_key('max'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'max') == arg_options['max']

            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(current_schema_object,'not_empty') == arg_options['optional']


        print "Happy test!"
    
    def test_bool_validator(self):
        testing_data = self.get_bool_params()
        wf = WidgetSchemaFactory(testing_data)
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in testing_data.iteritems():  
            #print argument_name
            #should all the argument names really
            assert getattr(schema_man,'fields').has_key(argument_name)==True
            current_schema_object = getattr(schema_man,'fields')[argument_name]
        
            #print " ",argument_name," : ",getattr(schema_man,argument_name)

            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(current_schema_object,'not_empty') == arg_options['optional']
                
        print "Happy test!"



    def test_list_validator(self,the_type='list'):
        if the_type == 'list':
            testing_data = self.get_list_params()
        else:
            testing_data = self.get_hash_params()

        wf = WidgetSchemaFactory(testing_data)
        schema_man=wf.get_ready_schema()
        
        for argument_name,arg_options in testing_data.iteritems():  
            #print argument_name
            #should all the argument names really
            #print " ",argument_name," : ",getattr(schema_man,argument_name)
            assert getattr(schema_man,'fields').has_key(argument_name)==True
            current_schema_object = getattr(schema_man,'fields')[argument_name]
        
 
            if arg_options.has_key('validator'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert getattr(current_schema_object,'regex_string') == arg_options['validator']

            if arg_options.has_key('optional'):
                #print " ",argument_name," : ",getattr(schema_man,argument_name)
                assert not getattr(current_schema_object,'not_empty') == arg_options['optional']


        print "Happy test!"


    def test_hash_validator(self):
        self.test_list_validator(the_type = 'hash')

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
        [{'listfield': u'listone'}, {'listfield': u'listtwo'}]
        assert mv.to_python([{'listfield': u'listone'}, {'listfield': u'listtwo'}]) == ['listone','listtwo']
        del mv

        #test with regex
        mv = MinionListValidator(regex_string='^[A-Z]+$',not_empty=True)
        assert mv.to_python([{'listfield': u'LISTONE'}, {'listfield': u'LISTTWO'}]) == ['LISTONE','LISTTWO']
        self.assertRaises(validators.Invalid,mv.to_python,[])
        self.assertRaises(validators.Invalid,mv.to_python,[{'listfield':'hey_error'}])
        self.assertRaises(validators.Invalid,mv.to_python,{})
        del mv


        print "Happy testing !"
        
    
    def test_minion_hash_validator(self):
        
        #test default
        mv = MinionHashValidator()
        assert mv.to_python([{'keyfield':'keyvalue','valuefield':'valuehere'}]) == {'keyvalue':'valuehere'}
        del mv

        #test with regex
        mv = MinionHashValidator(regex_string='^[A-Z]+$',not_empty=True)
        assert mv.to_python([{'keyfield':'FEDORA','valuefield':'MACOSX'}]) == {'FEDORA':'MACOSX'}
        self.assertRaises(validators.Invalid,mv.to_python,{})
        self.assertRaises(validators.Invalid,mv.to_python,[{'keyfield':12,'valuefield':123}])
        self.assertRaises(TypeError,mv.to_python,"hwy")
        del mv

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
                    'validator':'^[A-Z]+$'
                    },
                }

    def get_hash_params(self):
        return {
                'hash_default':{
                    'type':'hash',
                    'default':{'hey':12},
                    'description':'default hash'
                    },
                 'hash_regex':{
                    'type':'hash',
                    'default':{'hey':12},
                    'optional':False,
                    'description':'default regex hash',
                    'validator':'^[A-Z]+$'
                    },
                }
        
    def get_bool_params(self):
        return {
                'bool_default':{
                    'type':'boolean',
                    'default':{'hey':12},
                    'description':'default hash',
                    'optional':False,
                    },
                }


 

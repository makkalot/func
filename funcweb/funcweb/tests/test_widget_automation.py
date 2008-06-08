import unittest
import turbogears
from turbogears import testutil
from funcweb.controllers import Root
import cherrypy

cherrypy.root = Root()

class TestWidgetListFactory(unittest.TestCase):
    
    def setUp(self):
        self.widget_factory = WidgetListFactory(self.get_test_default_args())
    
        
    def tearDown(self):
        pass

    def test_default_args(self):
        """
        Simple test to see if all arguments are assigned into
        input widget objects
        """
        compare_with = self.get_test_default_args()
        widget_list=self.widget_factory.get_widgetlist()

        for argument_name,argument_options in compare_with:
            assert widget_list.has_key(argument) == True

            #because some of them dont have it like boolean
            if argument_options.has_key('default'):
                assert argument_options['default'] == getattr(widget_list[argument_name],'default')

            #if it is optional it should ne is_required = True
            assert not argument_options['optional']== getattr(widget_list[argument_name],'is_required')

            assert argument_options['description']==getattr(widget_list[argument_name],'help_text')

        #that should be enough

    def get_test_default_args(self):
        """
        Simple testing case to see if have all the 
        things working properly ...
        """
        return {
                'string_default':{
                    'type':'string',
                    'default':'default string',
                    'optional':False,
                    'description':'default description'
                    },
                'int_default':{
                    'type':'int',
                    'default':'default int',
                    'optional':False,
                    'description':'default description'
                   },
                #no sense to have default
                'boolean_default':{
                    'type':'boolean'
                    'optional':False,
                    'description':'default description'
                   },
                'float_default':{
                    'type':'float'
                    'default':'default float',
                    'optional':False,
                    'description':'default description'
                   
                    },
                'hash_default':{
                    'type':'hash'
                    'default':'default hash',
                    'optional':False,
                    'description':'default description'
                   
                    },
                'list_default':{
                    'type':'list'
                    'default':'default list',
                    'optional':False,
                    'description':'default description'
                   
                    }
                
                }

    def get_test_specialized_case(self):
        pass

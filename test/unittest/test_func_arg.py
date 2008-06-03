##
## Copyright 2007, Red Hat, Inc
## see AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

#tester module for ArgCompatibility
from func.minion.func_arg import ArgCompatibility

class TestArgCompatibility:
   
    def setUp(self):
        #create the simple object 
        self.ac = ArgCompatibility(self.dummy_arg_getter())

    def test_arg_compatibility(self):
        """
        Testing the method argument compatiblity
        """
        result = self.ac.validate_all()
        assert result == True

    def dummy_arg_getter(self):
        """
        A simple method to test the stuff we have written for 
        arg compatiblity. I just return a dict with proper stuff
        Should more an more tests here to see if didnt miss something
        """
        return {
            'hifunc':{
                
                'app':{
                    'type':'int',
                    'range':(0,100),
                    'optional':False,
                    'default' : 12
                    },
                
                'platform':{
                    'type':'string',
                    'min_length':5,
                    'max_length':100,
                    'options':('fedora8','fedora9','some_other'),'description':"Hey im a fedora fan",
                    'default':'fedora8',
                        },
                
                'is_independent':{
                    'type':'boolean',
                    'default' :False,
                    'description':'Are you independent ?',
                    'optional':False
                    },
                                
                'some_string':{
                    'type':'string',
                    'validator': "^[a-zA-Z]$",
                    'description':'String to be validated',
                    'default':'makkalot',
                    'optional':False}, # validator is a re string for those whoo need better validation,so when we have options there is no need to use validator and reverse is True
                #to define also a float we dont need it actually but maybe useful for the UI stuff.
                'some_float':{
                    'type':'float',
                    'description':'The float point value',
                    'default':33.44,
                    'optional':False
                    },

                'some_iterable':{
                    'type':'iterable',
                    'description':'The value and description for *arg',
                    'optional':True, #that is where it makes sense
                    'validator':'^[0-9]+$',#maybe useful to say it is to be a number for example
                    },

                'some_hash':{
                    'type':'hash',
                    'description':'The value and description for **kwarg',
                    'optional':True, #of course it is,
                    'validator':'^[a-z]*$',#only for values not keys
                    
                    }
              }
              }

   

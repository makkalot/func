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
from func.minion.modules.func_arg import ArgCompatibility

class TestArgCompatibility:
   
    def setUp(self):
        #create the simple object 
        self.ac = ArgCompatibility(self.dummy_arg_getter())

    def test_arg_compatibility(self):
        """
        Testing the method argument compatiblity
        """
        result = self.ac.validate_all()
        #self.assert_on_fault(result)
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
                    'min_length':50,
                    'max_length':100,
                    'options':('fedora8','fedora9','some_other'),'description':"Hey im a fedora fan"
                        },
                
                'is_independent':{
                    'type':'boolean',
                    'default' :False,
                    'description':'Are you independent ?'
                    },
                                
                'some_string':{
                    'type':'string',
                    'validator': "^[a-zA-Z]$",} # validator is a re string for those whoo need better validation...
                        
              }
              }

   

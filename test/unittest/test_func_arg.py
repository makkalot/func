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

class ArgCompatibilityTest:
   
    def setUp(self):
        #create the simple object 
        ac = ArgCompatibility(self.dummy_arg_getter())
        print self.dummy_arg_getter()

    def dummy_arg_getter(self):
        """
        A simple method to test the stuff we have written for 
        arg compatiblity. I just return a dict with proper stuff
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
                    'validato': "^[a-zA-Z]$",} # validator is a re string for those whoo need better validation...
                        
              }
              }

    def test_arg_compatibility(self):
        """
        Simple test
        """
        result = self.ac.validate_all()
        #self.assert_on_fault(result)
        assert result == False


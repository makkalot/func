"""
grep utility

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


import pprint
import sys

from func.overlord import client
from func.overlord import base_command


class Grep(base_command.BaseCommand):
    name = "grep"
    usage = "grep [--modules = 'module1,module2'] search_term"
    summary = "Greps for some keyword in modules useful for troubleshooting"
    
    def addOptions(self):
        """
        Add options for grep utility ...
        """
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               default=self.verbose,
                               action="store_true")
        self.parser.add_option("-a", "--async", dest="async",
                               help="Use async calls?  (default 0)",
                               default=self.async,
                               action="store_true")
        self.parser.add_option('-d', '--delegate', dest="delegate",
                               help="use delegation to make function call",
                               default=self.delegate,
                               action="store_true")
        self.parser.add_option('-m', '--modules', dest="modules",
                               help="a list of modules to be searched",
                               default=self.delegate,
                               action="store",
                               type="string")
        
              
    def handleOptions(self, options):
        self.options = options
        self.verbose = options.verbose

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def parse(self, argv):
        self.argv = argv
        return base_command.BaseCommand.parse(self, argv)
        

    
    def do(self, args):
        """
        Grepping the stuf real part
        """
        
        if not args:
            self.outputUsage()
            return
        
        #the search keyword
        self.word = args[0]
        
        self.async = self.options.async
        self.delegate = self.options.delegate
        
        self.server_spec = self.parentCommand.server_spec
        self.getOverlord()
        
        if not self.options.modules: #pull all of the modules
            self.options.modules = self._get_modules()
            #print self.options.modules
        else:
            self.options.modules = self.options.modules.split(",")
            
        results = {}
        
        for module in self.options.modules:
            if self.options.verbose:
                print "Scanning module :",module
                
            tmp_res = self.overlord_obj.run(module,"grep",[self.word])
            
            if self.options.async:
                tmp_res = self.overlord_obj.local.utils.async_poll(tmp_res,None)
            
            for minion_name,minion_value in tmp_res.iteritems():
                if results.has_key(minion_name) and minion_value:
                    results[minion_name].append(minion_value)
                elif minion_value:
                    results[minion_name]=[minion_value]
                    
        
        print  pprint.pformat(results)
        

    def _get_modules(self):
        """
        In cases when user doesnt supply the module list
        we have to consider that all of the modules are
        chosen so that method will return a list of them
        """
        from func.overlord.client import Minions,Overlord
        
        #insetad of getting all of the modules we consider
        #that all of machines has the same modules ...
        m = Minions("*")
        hosts = m.get_all_hosts()
        if hosts:
            fc = Overlord(hosts[0], noglobs=True)
            return fc.system.list_modules()
        else:
            raise Exception("No minions on system !")
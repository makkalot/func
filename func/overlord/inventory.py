##
## func inventory app.
## use func to collect inventory data on anything, yes, anything
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
## +AUTHORS
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import os.path
import time
import optparse
import sys
import pprint
import xmlrpclib
from func.minion import sub_process
import func.overlord.client as func_client
import func.utils as utils

DEFAULT_TREE = "/var/lib/func/inventory/"


class FuncInventory(object):

    def __init__(self):
        pass 

    def run(self,args): 

        p = optparse.OptionParser()
        p.add_option("-v", "--verbose",
                     dest="verbose",
                     action="store_true",
                     help="provide extra output")
        p.add_option("-s", "--server-spec",
                     dest="server_spec",
                     default="*",
                     help="run against specific servers, default: '*'")
        p.add_option("-m", "--methods",
                     dest="methods",
                     default="inventory",
                     help="run inventory only on certain function names, default: 'inventory'")
        p.add_option("-M", "--modules",
                     dest="modules",
                     default="all",
                     help="run inventory only on certain module names, default: 'all'")
        p.add_option("-t", "--tree",
                     dest="tree",
                     default=DEFAULT_TREE,
                     help="output results tree here, default: %s" % DEFAULT_TREE)
        p.add_option("-n", "--no-git",
                     dest="nogit",
                     action="store_true",
                     help="disable useful change tracking features")
        p.add_option("-x", "--xmlrpc", dest="xmlrpc",
                     help="output data using XMLRPC format",
                     action="store_true")
        p.add_option("-j", "--json", dest="json",
                     help="output data using JSON",
                     action="store_true")


        (options, args) = p.parse_args(args)
        self.options = options

        filtered_module_list = options.modules.split(",")
        filtered_function_list = options.methods.split(",")

        self.git_setup(options)

        # see what modules each host provides (as well as what hosts we have)
        host_methods = func_client.Client(options.server_spec).system.list_methods()
       
        # call all remote info methods and handle them
        if options.verbose:
            print "- scanning ..."
        # for (host, modules) in host_modules.iteritems():

        for (host, methods) in host_methods.iteritems():

            if utils.is_error(methods):
                print "-- connection refused: %s" % host 
                break 

            for each_method in methods:

                #if type(each_method) == int:
                #    if self.options.verbose:
                #        print "-- connection refused: %s" % host
                #    break

                tokens = each_method.split(".")
                module_name = ".".join(tokens[:-1])
                method_name = tokens[-1]

                if not "all" in filtered_module_list and not module_name in filtered_module_list:
                    continue

                if not "all" in filtered_function_list and not method_name in filtered_function_list:
                    continue
               
                client = func_client.Client(host,noglobs=True) # ,noglobs=True)
                results = getattr(getattr(client,module_name),method_name)()
                if self.options.verbose:
                    print "-- %s: running: %s %s" % (host, module_name, method_name)
                self.save_results(options, host, module_name, method_name, results)
        self.git_update(options)
        return 1

    def format_return(self, data):
        """
        The call module supports multiple output return types, the default is pprint.
        """

        # special case... if the return is a string, just print it straight
        if type(data) == str:
            return data

        if self.options.xmlrpc:
            return xmlrpclib.dumps((data,""))

        if self.options.json:
            try:
                import simplejson
                return simplejson.dumps(data)
            except ImportError:
                print "ERROR: json support not found, install python-simplejson"
                sys.exit(1)

        return pprint.pformat(data)

    # FUTURE: skvidal points out that guest symlinking would be an interesting feature       

    def save_results(self, options, host_name, module_name, method_name, results):
        dirname = os.path.join(options.tree, host_name, module_name)
        if not os.path.exists(dirname):
             os.makedirs(dirname)
        filename = os.path.join(dirname, method_name)
        results_file = open(filename,"w+")
        data = self.format_return(results)
        results_file.write(data)
        results_file.close()

    def git_setup(self,options):
        if options.nogit:
            return  
        if not os.path.exists("/usr/bin/git"):
            print "git-core is not installed, so no change tracking is available."
            print "use --no-git or, better, just install it."
            sys.exit(411) 
            
        if not os.path.exists(options.tree):
            os.makedirs(options.tree)
        dirname = os.path.join(options.tree, ".git")
        if not os.path.exists(dirname):
            if options.verbose:
                print "- initializing git repo: %s" % options.tree
            cwd = os.getcwd()
            os.chdir(options.tree)
            rc1 = sub_process.call(["/usr/bin/git", "init"], shell=False)
            # FIXME: check rc's
            os.chdir(cwd)
        else:
            if options.verbose:
                print "- git already initialized: %s" % options.tree

    def git_update(self,options):
        if options.nogit:
            return
        else:
            if options.verbose:
               print "- updating git"
        mytime = time.asctime()
        cwd = os.getcwd()
        os.chdir(options.tree)
        rc1 = sub_process.call(["/usr/bin/git", "add", "*" ], shell=False)
        rc2 = sub_process.call(["/usr/bin/git", "commit", "-a", "-m", "Func-inventory update: %s" % mytime], shell=False)
        # FIXME: check rc's
        os.chdir(cwd)


if __name__ == "__main__":
    inv = FuncInventory()
    inv.run(sys.argv)

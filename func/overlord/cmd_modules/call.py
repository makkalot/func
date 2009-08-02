"""
call func method invoker

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


import optparse
import pprint
import xmlrpclib
import sys

from func.overlord import client
from func.overlord import base_command
from certmaster.config import read_config, BaseConfig, ListOption

import func.jobthing as jobthing

DEFAULT_FORKS = 1
config_file = '/etc/func/async_methods.conf'

class CallConfig(BaseConfig):
    force_async = ListOption('')

#Facts parser and utility class

class FactsCommand(object):
    """
    That class takes the params that are entered from commandline for
    facts and parses and converts them to usable Overlord fact arguments
    """

    __valid_operators = {
                        "=":"",
                        "<":"lt",
                        ">":"gt",
                        } 
    __valid_c_operators={
            
                        "<=":"lte",
                        ">=":"gte"
                        }

    __valid_keywords = {
                        "in":"contains",
                        "ini":"icontains",
                        }

    def do(self,filter,filteror,*args,**kwargs ):
        """
        The action part
        """
        if not filter and not filteror:
            return False
        elif filter and filteror:
            return False
        
        tmp_arg = filter or filteror
        parse_result = self.__parse_fact_args(tmp_arg)
        if not parse_result:
            return False
        return parse_result


    def __parse_fact_args(self,args):
        """
        Parses the format of the arguments which is like 
        keyword=value,keyword<value,value in keyword
        """
        comma_separated = args.split(",")
        if not self.__is_coma_ok(comma_separated):
            return False
        
        final_dict = {}

        for com_key in comma_separated:
            res = self.__convert_keyword(com_key)
            if not res:
                #self.outputUsage()
                return False

            final_dict[res[0]]=res[1]
        
        return final_dict


    def __is_coma_ok(self,comma_list):
        """
        Chechs if the comma separated expression is ok
        """
        for c in comma_list:
            if not c:
                #self.outputUsage()
                return False
        return True
    
    def __convert_keyword(self,keyword):
        """
        Convert keyword to a ready to use Overlord parameter
        """
        keyword = keyword.strip()
        
        #check for space first
        if keyword.find(" ")!=-1:
            #do the keyword operations first
            tmp_kw = keyword.split()
            return self.__join_keyword(tmp_kw,self.__valid_keywords)
           
        else:
            for op in self.__valid_c_operators:
                if keyword.find(op)!=-1:
                    tmp_kw = keyword.split(op)
                    return self.__join_keyword(tmp_kw,self.__valid_c_operators,op) 
            #do the operator things
            for op in self.__valid_operators:
                if keyword.find(op)!=-1:
                    tmp_kw = keyword.split(op)
                    return self.__join_keyword(tmp_kw,self.__valid_operators,op) 
        return False
    
    def __join_keyword(self,tmp_kw,valid_set,operator=None):
        """
        A common util operation we do
        """
        if not operator:
            if not len(tmp_kw) == 3:
                return False
            else:
                value = tmp_kw[2]
                operator = tmp_kw[1]

        else:
            if not len(tmp_kw) == 2:
                return False
            else:
                value = tmp_kw[1]
        

        #doing that trick to not to loose some of the oprators when showing
        if not operator.strip() in valid_set.keys():
                return False
        
        if operator in self.__valid_keywords.keys():
            return "".join([value.strip(),"__",valid_set[operator.strip()]]),tmp_kw[0].strip()
        else:
            return "".join([tmp_kw[0].strip(),"__",valid_set[operator.strip()]]),value.strip()


class Call(base_command.BaseCommand):
    name = "call"
    usage = "call module method name arg1 arg2..."
    summary = "allows a specific module and method to be called"
    def addOptions(self):
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               default=self.verbose,
                               action="store_true")
        self.parser.add_option("-x", "--xmlrpc", dest="xmlrpc",
                               help="output return data in XMLRPC format",
                               action="store_true")
        self.parser.add_option("", "--raw", dest="rawprint",
                               help="output return data using Python print",
                               action="store_true")
        self.parser.add_option("-j", "--json", dest="json",
                               help="output return data using JSON",
                               action="store_true")
        self.parser.add_option("-p", "--pickle", dest="pickle",
                               help="output return data in python pickle format",
                               action="store_true")
        self.parser.add_option("-b", "--basic", dest="basic",
                               help="output return data with minimal, basic formating",
                               action="store_true")
        self.parser.add_option("-f", "--forks", dest="forks",
                               help="how many parallel processes?  (default 1)",
                               default=self.forks)
        self.parser.add_option("-a", "--async", dest="async",
                               help="Use async calls?  (default 0)",
                               default=self.async,
                               action="store_true")
        self.parser.add_option("-n", "--nopoll", dest="nopoll",
                               help="Don't wait for async results",
                               action="store_true")
        self.parser.add_option("", "--sort", dest="sort",
                               help="In async mode, wait for all results and print them sorted.",
                               action="store_true")
        self.parser.add_option("-s", "--jobstatus", dest="jobstatus",
                               help="Do not run any job, just check for status.",
                               action="store_true")
        self.parser.add_option('-d', '--delegate', dest="delegate",
                               help="use delegation to make function call",
                               default=self.delegate,
                               action="store_true")
        self.parser.add_option('-l', '--logpoll', dest="logpoll",
                               help="Polls for that call for minion side to get some useful output info.",
                               action="store_true")
        self.parser.add_option('-o', '--logone', dest="logone",
                               help="Polls for that call for minion side to get some useful output info,for only one host,must suply job_id;host as parameter",
                               action="store")
        
        self.parser.add_option('-r', '--progress', dest="progress",
                               help="Polls for that call for minion side to get the progress.",
                               action="store")
        self.parser.add_option("", "--filter", dest="filter",
                               help="use filter to and minion facts",
                               action="store")
        self.parser.add_option("", "--filteror", dest="filteror",
                               help="use filteror to or minion facts",
                                action="store")
        
    def handleOptions(self, options):
        self.options = options
        self.verbose = options.verbose

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def parse(self, argv):
        self.argv = argv

        return base_command.BaseCommand.parse(self, argv)
        

    def format_return(self, data):
        """
        The call module supports multiple output return types, the default is pprint.
        """
        
        if self.options.xmlrpc:
            return xmlrpclib.dumps((data,""))

        if self.options.json:
            try:
                import simplejson
                return simplejson.dumps(data)
            except ImportError:
                sys.stderr.write("WARNING: json support not found, install python-simplejson\n")
                return data

        if self.options.rawprint:
            return data

        if self.options.pickle:
            import pickle
            return pickle.dumps(data)

        if self.options.basic:
            output = ""
            (minion,results) = data
            output += '**** Results for %s (return value: %d) ****\n' % (minion, results[0])
            output += results[1]
            if results[2].strip() not in (None, ''):
                output += '**** Output to STDERR ****\n'
                output += results[2]
            return output

        return  pprint.pformat(data)

    def do(self, args):

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

        # I kind of feel like we shouldn't be parsing args here, but I'm
        # not sure what the write place is -al;

        if not args:
            self.outputUsage()
            return
        
        self.module           = args[0]
        if len(args) > 1:
            self.method       = args[1]
        else:
            self.method       = None
        if len(args) > 2:
            self.method_args  = args[2:]
        else:
            self.method_args  = []

        # this could get weird, sub sub classes might be calling this
        # this with multiple.parentCommand.parentCommands...
        # maybe command.py needs a way to set attrs on subCommands?
        # or some sort of shared datastruct?
        #        self.getOverlord()

        call_config = read_config(config_file, CallConfig)
        if self.method and (self.module+"."+self.method in call_config.force_async):
            self.options.async=True

        self.interactive = False
        self.async = self.options.async
        self.forks = self.options.forks
        self.delegate = self.options.delegate
        
        self.server_spec = self.parentCommand.server_spec
        #do we have exclude option activated ?
        self.exclude_spec = self.parentCommand.exclude_spec
        
        self.getOverlord()
        
        #the facts part inserted here
        if self.options.filter or self.options.filteror:
            facts = FactsCommand()
            result_fact = facts.do(self.options.filter,self.options.filteror)
            if not result_fact:
                self.outputUsage()
                return
        
        if self.options.filter:
            #print "The result facts are : ",result_fact
            self.overlord_obj=self.overlord_obj.filter(**result_fact)
        elif self.options.filteror:
            self.overlord_obj=self.overlord_obj.filter_or(**result_fact)
        

        #end of the facts parsing

        if not self.options.jobstatus:
            if self.options.filter or self.options.filteror:
                results = self.overlord_obj.run(self.module, self.method,[{'__fact__':self.overlord_obj.overlord_query.serialize_query()}]+list(self.method_args))
            else:
                results = self.overlord_obj.run(self.module, self.method, self.method_args)
        else:
            (return_code, async_results) = self.overlord_obj.job_status(self.module)
            res = self.format_return((return_code, async_results))
            print res
            return async_results

        #log for only one machine which is more reasonable instead
        #of doing it for thousands ... 
        if self.options.logone:
            self._poll_logs(self.module,self.options.logone)
            return #terminate no need for more
        
        if self.options.progress:
            self._print_progress(self.module,self.options.progress)
            return #terminate no need for more

        if self.options.async:
            self.partial = {}
            if self.options.nopoll:
                print "JOB_ID:", pprint.pformat(results)
                return results
            else:
                if self.options.logpoll:
                    self._poll_logs(results)
                return self.overlord_obj.local.utils.async_poll(results, self.print_results)
        # dump the return code stuff atm till we figure out the right place for it
        foo =  self.format_return(results)
        print foo

        # nothing really makes use of this atm -akl
        return results

    def print_results(self, res):
        for i in res.iteritems():
            print self.format_return(i)

    #do it only for some of the hosts if needed !
    def _poll_logs(self,job_id,host=None):
        """
        Here the method polls for log and prints some
        logs on the screen,which is kind of informative
        action for other apps and users also !
        """
        import time
        from func.minion.modules.jobs import NUM_OF_LINES
        #a constant that will tell us from how many same 
        # logs we will accept that the rest of logs is the
        #same we should stop somewhere !
        print_result = {}
        to_print = {}
        poll_res = (None,False)#initial state
        print_first_time = True
        while not poll_res[1]:#while the job_id is not finished
            if print_first_time and host:
                poll_res = self.overlord_obj.tail_log(job_id,host,True)
            else:
                poll_res = self.overlord_obj.tail_log(job_id,host)
                
            if not poll_res[0]:
                print "Logging data is initializing ..."
                time.sleep(0.5)
                poll_res = self.overlord_obj.tail_log(job_id,host)
                continue
            
            #print the stuff you collected
            for minion,log in poll_res[0].iteritems():
                log = self._convert_log_to_list(log)

                if not print_result.has_key(minion):
                    print_result[minion]=log
                    to_print[minion]=log

                else:
                    #print "---------------------------------------------"
                    #print "PRINT_RESULT :  ",print_result[minion]
                    #print "LOG IS ",log
                    
                    to_print[minion]=list(set(log).difference(set(print_result[minion])))
                    print_result[minion]=list(set(print_result[minion]).union(set(to_print[minion])))
                    #should empty the buffer a little bit
                    #think if you have a file which is 1 GB :)
                    #print_result[minion] = print_result[minion][-NUM_OF_LINES:]
                    #print "PRINT_RESULT :  ",print_result[minion]
                    
                    #print "to_print ",to_print
                    #print "---------------------------------------------"
                    #raw_input()
                    
            self._print_dict_result(to_print,print_first_time)
            if print_first_time and host:
                print_first_time = False
                
            time.sleep(0.5)
    
    def _print_progress(self,job_id,host):
        """
        Gets the progress for job_id and host
        """
        import time
        from func.utils import ProgressBar,TerminalController 
        
        poll_res = (None,False)#initial state
        first_time = True
        while not poll_res[1]:#while the job_id is not finished
            poll_res = self.overlord_obj.check_progress(job_id,host)
            #print poll_res    
            if not poll_res[0]:
                time.sleep(0.5)
                continue
            
            if first_time:
                
                term = TerminalController()
                progress = ProgressBar(term, 'Progress Status',minValue=poll_res[0][host][0],maxValue=poll_res[0][host][1])
                first_time = False
            
            #update the progress bar
            progress.update(poll_res[0][host][0])
            #sleep a little bit
            time.sleep(0.5)

        if first_time:
            print "Method has no progress ability or some remote error occured"
        else:
            #clear the progress bar and say it is done
            progress.clear()
            print "JOB FINISHED : ",job_id
    

    def _print_dict_result(self,result,print_host=True):
        """
        An util method that just prints info 
        in a result dictionary ...
        """
        for minion,logs in result.iteritems():
            if logs:
                if print_host:
                    print "------HOST : %s -------"%minion
                print "\n".join(logs)
        

    def _convert_log_to_list(self,log):
        res = []
        for l in log:
            if l:
                res.extend(l.split("\n"))
        return res
